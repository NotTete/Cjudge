import argparse
from pathlib import Path
from requests import exceptions
from shutil import copytree, rmtree

from ..judges.judge import Judge
from ..problem import get_judge
from ..error import *
from ..terminal_utils import *


def cli_create():
    parser = argparse.ArgumentParser(
        prog="cjudge-create",
        description="create a problem from an online judge",
    )

    parser.add_argument(
        "judge",
        metavar="judge",
        nargs="?",
        help="online judge from 'uva', 'aer', 'kattis'. If none leave empty",
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
        help="force the creation of the problem even if the folder exists"
    )

    parser.add_argument(
        '--nostatement',  
        default=True, 
        action='store_false',
        dest="statement",
        help="Doesn't create the problem statement"
    )

    parser.add_argument(
        '--nosample',  
        default=True, 
        action='store_false',
        dest="sample",
        help="Create a sample folder with empty sample cases"
    )

    # Get cli arguments
    args = parser.parse_args()
    
    path: Path = args.path
    force: bool = args.force
    sample: bool = args.sample
    statement: bool = args.statement
    problem: str = args.problem
    judge_name: str = args.judge

    # Default path
    if(path == None):
        path = Path(Path(".", args.problem))

    # Start the creation of the problem
    loader = Loader(
        "Creating folder...", 
        f"Problem created sucessfully {check}",
        color=Color("#00ffff")
    )
    loader.start()

    error_msg = None
    remove_dir = False


    try:
        # Get problem
        judge = get_judge(judge_name, problem, path)

        # Check if the judge was correct and warn the user
        if(judge.name == "none" and judge_name != None):
            loader.send_warning("Invalid judge creating an empty problem")

        # Create the problem folder
        path.mkdir(parents=True, exist_ok=force)
        remove_dir = True

        # Download problem statement
        if(statement):
            loader.change_description("Downloading statement...")
            judge.create_statement()

        # Download problem samples
        if(sample):
            loader.change_description("Downloading samples...")
        judge.create_samples(force, sample)

        # Create extra files
        loader.change_description("Creating extra files...")
        judge.create_template()
        judge.create_metadata()

    # Error handling
    except FileExistsError:
        error_msg = "Folder already exists"
    except (exceptions.HTTPError, InvalidProblemException):
        error_msg = f"Problem '{problem}' isn't a {judge_name} problem"
    except (exceptions.ConnectTimeout, exceptions.ConnectionError):
        error_msg = f"Couldn't connect to {judge_name}"
    except Exception as e:
        error_msg = str(e)
    else:    
        remove_dir = False

    # Clean up
    if(remove_dir):
        rmtree(path)
    loader.stop(error_msg)