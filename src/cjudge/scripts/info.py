import argparse
from pathlib import Path
from requests import exceptions

from ..problem import *
from ..error import InvalidJudgeException, InvalidProblemException
from ..terminal_utils import display_error

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
        "path / judge",
        type=None,
        nargs="?",        
        default=Path("."),
        help="If just one argument is given it must be the problem folder. \nIf two arguments are given this is the selected judge"
    )

    parser.add_argument(
        "problem",
        type=str,
        nargs="?",        
        default=None,
        help="Problem name"
    )
    args: argparse.Namespace = parser.parse_args()
    path = args._get_kwargs()[0][1]
    problem = args.problem

    judge = None
    error_msg = None
    try:    
        if(problem == None):
            path = Path(path)
            judge = get_judge_from_file(path)
        else:
            judge = get_judge(path, problem, None)
            if(judge.name == NoneJudge.name):
                raise InvalidJudgeException(judge)

        judge.display_info()
    except InvalidProblemException as e: 
        error_msg = f"Problem '{e.problem}' isn't a {e.judge} problem"
    except exceptions.HTTPError:
        error_msg = f"Problem '{judge.problem}' isn't a {judge.name} problem"
        if(problem == None):
            error_msg += ". Your metadata file migth be corrupted"
    except (exceptions.ConnectTimeout, exceptions.ConnectionError):
        error_msg = f"Couldn't connect to {judge.name}"
    except InvalidJudgeException as e:
        error_msg = f"'{judge.name}' is an invalid judge"
    except Exception as e:
        error_msg = str(e)

    if(error_msg != None):
        display_error(error_msg)
