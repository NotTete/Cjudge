import argparse
from pathlib import Path
from shutil import copytree, rmtree

import cjudge
from .problem import Problem
from .error import *

import itertools
import threading
import time

status = 0
#here is the animation
def animate(text):
    for c in itertools.cycle(['.  ', '.. ', '...']):
        if status != 0:
            break
        print(f'{text}{c}', end="\r")
        time.sleep(0.25)
    if(status == 1):
        print('Done!                 ')


def cli_create():
    global status
    parser = argparse.ArgumentParser(
        prog="cjudge-create",
        description="create a problem from an online judge",
    )

    parser.add_argument(
        "judge",
        metavar="judge",
        help="online judge",
    )

    parser.add_argument(
        "problem",
        metavar="problem",
        help="selected problem",
    )

    parser.add_argument(
        "-p", "--path",
        type=Path,
        default=None,
        dest="path",
        help="problem destination location"
    )

    parser.add_argument(
        '-f', 
        '--force', 
        default=False, 
        action='store_true',
        dest="force",
        help="if the destination folder already exists it deletes it"
    )

    args = parser.parse_args()
    path = args.path
    # Check if the path is valid
    if(path == None):
        path = Path(".", args.problem)
    t = threading.Thread(target=animate, args=("Creating problem",))
    t.start()
    try:
        problem = Problem(args.judge, args.problem)
        problem.create(path, args.force)
    except InvalidProblemException as e:
        status = -1
        print(f"\033[1m\033[91m[ERROR]\033[0m '{e.problem}' isn't a valid problem from {e.judge}")
    except InvalidJudgeException as e:
        status = -2
        print(f"\033[1m\033[91m[ERROR]\033[0m '{e.judge}' isn't a valid judge. Valid judges are: aer, kattis, uva")
    except FileExistsError as e:
        status = -3
        print(f"\033[1m\033[91m[ERROR]\033[0m '{e.filename}' folder already exists")        
    except Exception as e:
        status = -4
        rmtree(path)
        print(f"\033[1m\033[91m[ERROR]\033[0m an unexpected error has ocurred")
        raise(e)
    else:
        status = 1


