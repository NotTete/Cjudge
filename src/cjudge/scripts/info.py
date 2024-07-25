import argparse
from pathlib import Path

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
        "-p", "--path",
        type=Path,
        dest="path",
        default=Path("."),
        help="problem location"
    )

    args = parser.parse_args()
    path: Path = args.path

    # Check if the path exists
    if(not path.is_dir()):
        display_path = get_display_path(path)
        display_error(f"'{display_path}' folder doesnt' exist")
        exit()
    
    # Check if it is a valid problem path
    path = Path(path, ".meta")
    if(not path.is_file()):
        display_path = get_display_path(path.parent)
        display_error(f"'{display_path}' folder isn't a problem folder")
        exit()

    # Tries to create a problem validating it
    try:
        problem = Problem.load_from_file(path)
    except InvalidJudgeException:
        display_error("Invalid judge your metadata file might be corrupted")
    except InvalidProblemException:
        display_error("Invalid problem your metadata file might be corrupted")
    except Exception as e:
        display_error("An unexpected error has ocurred")
        raise e
    else:
        problem.display_info()