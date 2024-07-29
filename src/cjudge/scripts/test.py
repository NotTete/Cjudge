from pathlib import Path
import argparse

from ..tester import Tester
from ..terminal_utils import *
from ..error import *
from ..config import Config

def cli_test():
    # Argument parser
    parser = argparse.ArgumentParser(
        prog="cjudge-test",
        description="Run problem test cases from 'samples' folder",
    )

    parser.add_argument(
        "path",
        type=Path,
        nargs="?",        
        default=Path("."),
        help="The problem folder"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        metavar="choice",
        dest="output",
        choices=["minimal", "error", "full"],
        default=None,
        help="Information to be displayed. quiet: Only test results. error: Error outputs. full: All the outputs. (Default can be changed on config file)"
    )

    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        dest="interactive",
        default=False,
        help="Run an interactive test case"
    )

    parser.add_argument(
        "-nf", "--nofile",
        action="store_false",
        dest="create_files",
        default=True,
        help="Doesn't create result files"
    )

    args = parser.parse_args()
    output = args.output
    interactive = args.interactive
    create_files = args.create_files
    path = args.path

    if(output == None):
        output = Config.get_test_output()

    if(not path.exists()):
        display_error("The selected path doesn't exists")
        exit()

    try:
        tester = Tester(path, output, create_files)
        tester.run_tests()

    except CompilationError as e:
        print(e)
        display_error("Couldn't compile your program")
    except FileNotFoundError as e:
        display_error(f"Problem folder '{path}' is not valid")
        display_warning("Check you have a 'samples' folder and a 'main.cpp' file")
