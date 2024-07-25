from abc import ABC, abstractmethod
from pathlib import Path
import shutil 

from ..config import Config

class Judge(ABC):
    """
        Abstract Class that represent a judge
    """

    @property
    @abstractmethod
    def name(self):
        """Judge short name"""
        raise NotImplementedError

    @property
    @abstractmethod
    def fullname(self):
        """Judge fullname"""
        raise NotImplementedError

    @property
    @abstractmethod
    def url(self):
        """Problem url"""
        raise NotImplementedError  

    @property
    def problem(self):
        return self._problem

    @problem.setter
    def problem(self, problem: str):
        self._problem = problem

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path: Path):
        self._path = path

    @abstractmethod
    def __init__(problem: str, path: Path):
        """
        Create a Judge with an associated problem

        Args:
            problem (str): problem id of the judge
            path (Path): Problem destination path
        """
        raise NotImplementedError

    @abstractmethod
    def create_statement(self):
        """
        Download problem statement in a path
        """
        raise NotImplementedError

    @abstractmethod
    def create_samples(self, force: bool = False, create_sample: bool = True):
        """
        Create problem samples in a desired folder

        Args:
            force(bool): forces to continue even if the directory exists
            create_sample(bool): False in order to create empty samples
        """
        raise NotImplementedError
    
    def create_samples_empty(self, force: bool = False):
        """
        Create empty samples
        Args:
            force(bool): forces to continue even if the directory exists
        """

        path = Path(self.path, "samples")
        path.mkdir(exist_ok=force)

        with open(Path(path, "1.in"), "w") as file:
            pass
        with open(Path(path, "1.out"), "w") as file:
            pass

    def create_template(self):
        """
        Create a template from config folder.
        If it cant get the template it reconstructs the config folder
        Args:
            path (Path): destination path
        """   

        path = Path(self.path, "main.cpp")
        Config.copy_template(path)
        
    def create_metadata(self):
        """
        Create a metadata file
        Args:
            path (Path): destination path
        """   
        
        path = Path(self.path, ".meta")
        with open(path, "w") as file:
            file.write(self.name + "\n")
            file.write(self.problem + "\n")

    def display_info(self):
        """Display info to stdout"""
        print("\33[1mProblem Information")
        print(f"\33[1mJudge:\33[0m {self.name.capitalize()}")
        print(f"\33[1mName:\33[0m {self.problem}")
        print(f"\33[1mURL:\33[0m {self.url if self.url != "none" else "None"}")