import argparse
from pathlib import Path
from shutil import copytree, rmtree

import cjudge
from .problem import Problem

import itertools
import threading
import time
import sys

done = False
#here is the animation
def animate(text):
    for c in itertools.cycle(['.', '..', '...']):
        if done:
            break
        sys.stdout.write(f'\r{text}' + c)
        sys.stdout.flush()
        time.sleep(0.25)
    sys.stdout.write('\rDone!               ')



def cli_create():
    global done
    parser = argparse.ArgumentParser(
        prog="cjudge-create",
        description="Create a problem from an online judge",
    )

    parser.add_argument(
        "judge",
        choices=["uva", "kattis", "aer"],
        metavar="judge",
        help="Online judge",
    )

    parser.add_argument(
        "problem",
        metavar="problem",
        help="Selected problem",
    )

    parser.add_argument(
        "-p", "--path",
        type=Path,
        default=None,
        dest="path",
        help="Problem destination location"
    )

    parser.add_argument(
        '-q', 
        '--quiet', 
        default=False, 
        action='store_true',
        dest="quiet",
    )

    args = parser.parse_args()
    t = threading.Thread(target=animate, args=("Validating problem",))
    t.start()
    problem = Problem(args.judge, args.problem)
    done = True
    problem.create(args.path)

