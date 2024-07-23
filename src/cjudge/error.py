from pathlib import Path

class InvalidJudgeException(Exception):
    """
    Exception raised when a judge is invalid

    Attributes:
        judge (str): selected judge
    """

    def __init__(self, judge):
        self.judge = judge
        super().__init__(f"'{judge}' is an invalid judge")

class InvalidProblemException(Exception):
    """
    Exception raised when a problem from a judge doesn't exist

    Attributes:
        problem (str): selected problem
        judge (str): selected judge
    """

    def __init__(self, judge, problem):
        self.judge = judge
        self.problem = problem
        super().__init__(f"Problem '{problem}' from '{judge}' doesn't exist")