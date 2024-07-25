from pathlib import Path

from .judge import Judge
from ..terminal_utils import *

class NoneJudge(Judge):    

    @property
    def url(self):
        return f"None"

    name = "none"
    fullname = f"{bold}{rgb(Color("#666699"))}None{clear}"
    fullname = "None"

    def __init__(self, problem: str, path: Path):
        self.path = path
        self.problem = problem

    def create_statement(self):
        # No problem statement
        pass
    
    def create_samples(self, force: bool = False, create_sample: bool = True):
        # Create empty input and output
        self.create_samples_empty(force)