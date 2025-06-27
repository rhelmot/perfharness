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

from .config import load_config
from .db import db_connect, db_close, Run, get_engine

def random_color():
    h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return r, g, b

def main(args):
    if pd is None:
        print("Cannot import pandas and matplotlib. Install these to visualize results.")
        return

    parser = argparse.ArgumentParser(description='Visualize performance results over time')
    default_colors = {'testcase', 'hostname', 'python', 'os'}
    parser.add_argument('--color', type=str, default='testcase,python',
        help='color the data differently for each of the given comma-separated database fields')
    parser.add_argument('--since', type=str,
        help='only show tests on or after the given date (parsed in natural language with parsedatetime)')
    parser.add_argument('--note', type=str,
        help='only show tests with the given note string')
    parser.add_argument('--note-like', nargs=1, type=str,
        help='only show tests that with notes that contains the given string')
    parser.add_argument('--host', nargs='+', type=str, action='append', default=[],
        help='only show tests that ran on the machine with the given hostname(s)')
    parser.add_argument('--save', type=str,
        help='save the plot to the given file instead of displaying it')
    parser.add_argument('testcase', nargs='+', type=str,
        help='show results for these testcases')

    args = parser.parse_args(args)

    if args.since is not None:
        time_struct, parse_status = parsedatetime.Calendar().parse(args.since)
        if parse_status == 0:
            raise ValueError("Could not parse time")
        args.since = datetime(*time_struct[:6])

    config = load_config()
    db_connect(config, create_session=False)

    query = ex.select(Run).where(Run.testcase.in_([os.path.basename(t) for t in args.testcase]))
    if args.since is not None:
        query = query.where(Run.timestamp >= args.since)
    if args.note is not None:
        query = query.where(Run.note == args.note)
    if args.note_like is not None:
        query = query.where(Run.note.like(args.note_like))
    if args.host:
        query = query.where(Run.hostname.in_(args.host))

    data = pd.read_sql(query, get_engine())
    if data.empty:
        print("No data matched :(")
        db_close()
        return

    colorcolumns = args.color.split(',')
    colordata = data[colorcolumns].drop_duplicates()

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 1, 1)

    for _, row in colordata.iterrows():
        condition = None
        for col in colorcolumns:
            ok = data[col] == row[col]
            condition = ok if condition is None else ok & condition

        nameparts = []
        for col in colorcolumns:
            nameparts.append(row[col])

        relevant_data = data[condition]
        relevant_avg = relevant_data.set_index("timestamp")[["runtime"]].rolling(5).mean().reset_index()
        color = random_color()
        relevant_data.plot.scatter(x="timestamp", y="runtime", color=color, label=' '.join(nameparts), ax=ax)
        relevant_avg.plot(x="timestamp", y="runtime", color=color, ax=ax, label='_', legend=False)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.6, box.height])
    ax.legend(loc="upper left", bbox_to_anchor=(1.1, 0.0, 1.0, 1.0))
    ax.set_title("Nightly Performance")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Runtime (sec)")

    if args.save is None:
        plt.show()
    else:
        plt.savefig(args.save)

    db_close()
