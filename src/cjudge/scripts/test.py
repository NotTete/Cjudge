from pathlib import Path
import subprocess
import argparse
import tempfile


from ..terminal_utils import Loader, Color
from ..config import Config

def compile_source(temp_folder, problem_folder):
    binary_path = Path(temp_folder, "main")
    cpp_file = Path(problem_folder, "main.cpp")
    compiler = Config.get_compiler()

    if(not cpp_file.exists()):
        raise FileNotFoundError("Couldn't find problem file")

    sub = subprocess.run([compiler, "-o", binary_path, cpp_file]) 
    sub.check_returncode()

    return binary_path

def cli_test():
    # Argument parser
    parser = argparse.ArgumentParser(
        prog="cjudge-test",
        description="run problem test cases locally",
    )

    parser.add_argument(
        "path",
        type=Path,
        nargs="?",        
        default=Path("."),
        help="The problem folder"
    )

    args = parser.parse_args()
    path = args.path

    loader = Loader("Compiling program...", "", color=Color("#00FFFFF"))
    loader.start()
    with tempfile.TemporaryDirectory() as temp_folder:
        source = compile_source(temp_folder, path)

        with open(Path(path, "1.res"), "w") as file:
            with open(Path(path, "samples", "1.in"), "r") as sample:
                sub = subprocess.run([source], stdin=sample, stdout=file) 
        
    loader.stop()
