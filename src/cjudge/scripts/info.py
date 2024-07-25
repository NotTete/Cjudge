import argparse
from pathlib import Path

from ..problem import get_judge_from_file
from ..error import InvalidJudgeException, InvalidProblemException
from ..terminal_utils import display_error, Bar, Color

def get_display_path(path: Path):

    if(not path.is_absolute()):
        path = Path(Path.cwd().name, path)

    return path

def cli_info():
    
    # Argument parser
    parser = argparse.ArgumentParser(
        prog="cjudge-create",
        description="display information about the problem",
    )

    parser.add_argument(
        "path",
        type=Path,
        nargs="?",        
        default=Path("."),
        help="problem location"
    )

    args = parser.parse_args()
    path = args.path

    judge = get_judge_from_file(path)
    judge.display_info()
