import configparser
import fnmatch
import os
from typing import Iterable
import subprocess

# https://www.thepythoncode.com/article/get-hardware-system-information-python
def format_size(size, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if size < factor:
            return f"{size:.0f}{unit}{suffix}"
        size /= factor

def parse_size(size_str: str):
    suffices = {x: 1024**i for i, x in enumerate(["b", "kb", "mb", "gb", "tb", "pb"])}
    suffices[""] = 1
    size_str = size_str.lower()
    numpart = ""
    while size_str and size_str[0].isdigit():
        numpart += size_str[0]
        size_str = size_str[1:]

    if size_str not in suffices:
        raise Exception("Invalid size suffix %r" % size_str)

    return int(numpart) * suffices[size_str]

def load_config():
    config = configparser.ConfigParser(default_section='perfharness', defaults={
        'sources_root': '.',
        'sources': '',
        'sources_ignore': '',
        'cpu_percent_less_than': '50',
        'mem_available_less_than': '1gb'
    })

    files = config.read(['.perfharness.ini', '../.perfharness.ini', '../../.perfharness.ini', '../../../.perfharness.ini', '../../../../.perfharness.ini', '../../../../../.perfharess.ini'])

    if files:
        config["perfharness"]['config_root'] = os.path.dirname(os.path.abspath(files[0]))
    else:
        config["perfharness"]['config_root'] = '.'

    return config["perfharness"]

def all_sources(config) -> Iterable[str]:
    for source_dir in config["sources"].split(","):
        source_dir = source_dir.strip()
        full_path = os.path.join(config["config_root"], config["sources_root"], source_dir)
        for root, dirs, files in os.walk(full_path):
            dirs[:] = sorted(x for x in dirs if not any(fnmatch.fnmatch(x, pattern.strip()) for pattern in config["sources_ignore"].split(',')))
            files[:] = sorted(x for x in files if not any(fnmatch.fnmatch(x, pattern.strip()) for pattern in config["sources_ignore"].split(',')))

            for file in files:
                yield os.path.join(root, file)

def run_build(config):
    if 'build' not in config:
        return

    subprocess.check_call(config['build'], cwd=os.path.join(config['config_root'], config['sources_root']), shell=True)

