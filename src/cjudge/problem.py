from pathlib import Path


from .error import *
from .judges.kattis import KattisJudge
from .judges.uva import UvaJudge
from .judges.aceptaelreto import AerJudge
from .judges.nonejudge import NoneJudge
from .judges.judge import Judge

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
    if judge_name == KattisJudge.name:
        return KattisJudge(problem, path)
    elif judge_name == UvaJudge.name:
        return UvaJudge(problem, path)
    elif judge_name == AerJudge.name:
        return AerJudge(problem, path)
    else: 
        return NoneJudge(problem, path)
    
def get_judge_from_file(path: Path) -> Judge:
    """
    Create a problem from a problem folder

    Args:
        path (Path): problem folder
    
    Returns:
        Judge: Desired problem
    """

    # Check if the path exists
    if(not path.is_dir()):
        FileNotFoundError(f"'{path}' folder doesnt' exist")
    
    # Check if it is a valid problem path
    path = Path(path, ".meta")
    if(not path.is_file()):
        raise FileNotFoundError(f"'{path.parent}' folder isn't a problem folder")
    
    # Get data from file
    lines = []
    with(open(path, "r")) as file:
        lines = list(map(lambda x: x[:-1], file.readlines()))

    if(not(len(lines) == 2 and lines[0] != UvaJudge.name or len(lines) == 3 and lines[0] == UvaJudge.name)):
        raise CorruptedMetafileError("Metadata file is corrupted")

    judge = lines[0]
    problem = lines[1]

    # Get judge
    if judge == KattisJudge.name:
        return KattisJudge(problem, path.parent)
    elif judge == AerJudge.name:
        return AerJudge(problem, path.parent)
    elif judge == NoneJudge.name:
        return NoneJudge(problem, path.parent)
    elif judge == UvaJudge.name:
        problem_id = lines[2]
        return UvaJudge(problem, path.parent, problem_id)
    else:
        raise CorruptedMetafileError("Metadata file is corrupted")




