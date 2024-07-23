from pathlib import Path
import shutil

from .error import *
from .kattis import KattisJudge
from .uva import UvaJudge
from .aceptaelreto import AerJudge

class Problem:
    def __init__(self, judge, problem):
        self.problem = problem

        # Check if the judge and problem is valid
        if judge == "kattis":
            self.judge = KattisJudge(problem)
        elif judge == "uva":
            self.judge = UvaJudge(problem)
        elif judge == "aer":
            self.judge = AerJudge(problem)
        else:
            raise InvalidJudgeException(judge)

    def create(self, path: Path = None, force: bool = False):
        try:
            path.mkdir(parents=True)
        except FileExistsError as e:
            if(not force):
                raise e

        # Download and create files
        self.judge.create_statement(Path(path, f"{self.problem}.pdf"))
        self.judge.create_samples(Path(path, "samples"), force)
        self.judge.create_template(Path(path, "main.cpp"))
        self.judge.create_metadata(Path(path, ".meta"))