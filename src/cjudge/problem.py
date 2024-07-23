from pathlib import Path
import shutil

from .error import *
from .judges.kattis import KattisJudge
from .judges.uva import UvaJudge
from .judges.aceptaelreto import AerJudge

class Problem:
    def __init__(self, judge: str, problem: str):
        """
        Create a problem from a judge

        Args:
            judge (str): Selected judge
            problem (str): Selected problem
        """
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

    def create(self, path, force: bool = False):
        """
        Given a path create a problem folder in the destination

        Args:
            path (Path): Destination folder. Defaults to None.
            force (bool, optional): Force to create the folder. Defaults to False.

        """

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