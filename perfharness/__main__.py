import sys

from .run import main as run_main
from .viz import main as viz_main
from .delete import main as delete_main

def main(args):
    if not args:
        args = [None]

    if args[0] == 'run':
        run_main(args[1:])
    elif args[0] == 'viz':
        viz_main(args[1:])
    elif args[0] == 'delete':
        delete_main(args[1:])
    else:
        print('Usage: python -m perfharness [command] [args]')
        print('Commands: run, viz, delete')

if __name__ == '__main__':
    main(sys.argv[1:])