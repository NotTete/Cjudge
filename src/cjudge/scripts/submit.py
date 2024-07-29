from pathlib import Path
from requests import exceptions
import argparse

from ..tester import Tester
from ..terminal_utils import *
from ..error import *
from ..config import Config
from ..judges.nonejudge import NoneJudge
from ..problem import get_judge_from_file

def cli_submit():
    # Argument parser
    parser = argparse.ArgumentParser(
        prog="cjudge-submit",
        description="Submit the corresponding problem to the judge",
    )

    parser.add_argument(
        "path",
        type=Path,
        nargs="?",        
        default=Path("."),
        help="The problem folder"
    )

    parser.add_argument(
        "-n", "--notest",
        action="store_true",
        dest="notest",
        default=False,
        help="Don't check your program before sending it"
    )
    args = parser.parse_args()
    path = args.path
    notest = args.notest

    if(not path.exists()):
        display_error("The selected path doesn't exists")
        exit()

    try:
        judge = get_judge_from_file(path)
        if(judge.name == NoneJudge.name):
            raise InvalidJudgeException(judge)

        if(not notest):
            tester = Tester(path, "minimal", False)
            _, wa, _ = tester.run_tests()
            if(wa > 0):
                display_error("Your program didn't pass all test cases")
                exit()
            print("")

        judge.submit()
        
    except CompilationError as e:
        print(e)
        display_error("Couldn't compile your program")
    except FileNotFoundError as e:
        display_error(f"Problem folder '{path}' is not valid")
        display_warning("Check you have a 'samples' folder and a 'main.cpp' file")
    except InvalidProblemException as e: 
        display_error(f"Problem '{e.problem}' isn't a {e.judge} problem")
    except CorruptedMetafileError:
        display_error("Your metadata file is corrupted")
    except exceptions.HTTPError as e:
        error_msg = f"Problem '{judge.problem}' isn't a {judge.name} problem"
        if(problem == None):
            error_msg += ". Your metadata file migth be corrupted"
        display_error(error_msg)
    except (exceptions.ConnectTimeout, exceptions.ConnectionError):
        display_error(f"Couldn't connect to {judge.name}")
    except InvalidJudgeException as e:
        display_error(f"'{judge.name}' is an invalid judge")
    except Exception as e:
        display_error(str(e))