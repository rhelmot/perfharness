import os
import parsedatetime
import argparse
from datetime import datetime
import colorsys
import random

from sqlalchemy.sql import expression as ex
try:
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError:
    pd = None
    plt = None

from .argparse_set_ops import install_set_ops
from .config import load_config
from .db import db_connect, db_close, Run

def random_color():
    h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return r, g, b

def main(args):
    if pd is None:
        print("Cannot import pandas and matplotlib. Install these to visualize results.")
        return

    parser = argparse.ArgumentParser(description='Visualize performance results over time')
    install_set_ops(parser)
    default_colors = {'testcase', 'hostname', 'python', 'os'}
    parser.add_argument('--color', nargs=1, action='add_to_set', default=default_colors,
        help='color the data differently for different values of the given column')
    parser.add_argument('--no-color', nargs=1, action='remove_from_set', default=default_colors,
        help='do not color the data differently for different values of the given column')
    parser.add_argument('--since', nargs=1, type=str,
        help='only show time on or after the given date (parsed in natural language with parsedatetime)')
    parser.add_argument('testcase', nargs='+', type=str,
        help='show results for these testcases')

    args = parser.parse_args(args)

    if args.since is not None:
        time_struct, parse_status = parsedatetime.Calendar().parse(args.since)
        if parse_status == 0:
            raise ValueError("Could not parse time")
        args.since = datetime(*time_struct[:6])

    config = load_config()
    db_connect(config)

    query = ex.select([Run]).where(Run.testcase.in_([os.path.basename(t) for t in args.testcase]))
    if args.since is not None:
        query = query.where(Run.timestamp >= args.since)

    data = pd.read_sql(query, config['database'])
    if data.empty:
        print("No data matched :(")
        db_close()
        return

    colorcolumns = list(default_colors)
    colorkey = lambda row: tuple(row[col] for col in colorcolumns)
    colordata = data[colorcolumns].drop_duplicates()

    ax = None
    for _, row in colordata.iterrows():
        nameparts = []
        key = colorkey(row)
        condition = None
        for col in colorcolumns:
            ok = data[col] == row[col]
            condition = ok if condition is None else ok & condition

        for col in colorcolumns:
            # if every single other row contains the same value as us,
            # discard the attribute
            # TODO also discard if this attribute is redundant given another attribute. maybe use a decision tree?
            other_values = data[~condition][col].unique()
            if len(other_values) == 1 and row[col] in other_values:
                continue

            nameparts.append(row[col])

        ax = data[condition].plot.scatter(x="timestamp", y="runtime", color=random_color(), label=' '.join(nameparts), ax=ax)

    plt.show()

    db_close()