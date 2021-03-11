import os
import time
import importlib.util
import argparse

from .machine import fingerprint_machine, check_load
from .config import load_config, run_build, all_sources
from .db import db_connect, db_close, Run
from .hash import Hash


def load_test(name):
    # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
    spec = importlib.util.spec_from_file_location("perfharness.tests.%s" % name.replace('/', '.'), name)
    if spec is None:
        raise Exception("Not a python module: %s", name)

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, 'main') or not callable(mod.main):
        raise Exception("Does not have a main() function")

    return mod.main

def timeit(test):
    tstart = time.time()
    test()
    tend = time.time()
    return tend - tstart

def main(args):
    parser = argparse.ArgumentParser(description='Run the given performance tests and record or visualize results')
    parser.add_argument('--num', '-n', type=int, default=1, help="Number of times to run each test")
    parser.add_argument('--warmup', '-w', type=int, default=0, help="Number of times to run each test before main runs")
    parser.add_argument('--note', type=str, default="", help="Arbitrary text to associate with these runs")
    parser.add_argument('testcase', nargs='+', type=str, default=[], help="Run these tests")

    args = parser.parse_args(args)

    config = load_config()
    db_connect(config)
    check_load(config)

    run_build(config)
    source_hash = Hash.hash_files(all_sources(config))
    machine = fingerprint_machine()

    # import everything before we test anything
    tests = [load_test(testcase) for testcase in args.testcase]
    for file, test in zip(args.testcase, tests):
        basename = os.path.basename(file)
        print('Testing', basename)

        file_hash = Hash.hash_files([file])

        for i in range(args.warmup):
            print('Warmup %d' % (i + 1))
            test()
        for i in range(args.num):
            check_load(config)
            print("Test %d" % (i + 1))
            t = timeit(test)
            print('...time elapsed: %f sec' % t)
            Run.record_test(basename, file_hash, t, source_hash, machine, args.note)

    db_close()
