from pathlib import Path

from .judges.kattis import KattisJudge
from .judges.uva import UvaJudge
from .judges.aceptaelreto import AerJudge
from .judges.nonejudge import NoneJudge

def get_judge(judge_name: str, problem: str, path: Path):
    """
    Create a problem from a judge

    Args:
        judge (str): Selected judge
        problem (str): Selected problem
        path (Path): Destination path
    """    

    # Get the judge
    # if the judge is incorrect you get a problem from no judge
    if judge_name == "kattis":
        return KattisJudge(problem, path)
    elif judge_name == "uva":
        return UvaJudge(problem, path)
    elif judge_name == "aer":
        return AerJudge(problem, path)
    else: 
        return NoneJudge(problem, path)