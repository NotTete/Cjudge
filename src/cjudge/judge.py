from abc import ABC, abstractmethod
from pathlib import Path
import shutil 

from .config import Config

class Judge(ABC):
    """
        Abstract Class that represent a judge
    """

    @property
    @abstractmethod
    def name(self):
        """Judge name"""
        raise NotImplementedError

    @property
    @abstractmethod
    def url(self):
        """Problem url"""
        raise NotImplementedError  

    @property
    @abstractmethod
    def problem(self):
        """Problem id"""
        raise NotImplementedError  

    @abstractmethod
    def __init__(problem: str):
        """
        Create a Judge with an associated problem

        Args:
            problem (str): problem id of the judge
        """
        raise NotImplementedError

    @abstractmethod
    def create_statement(self, problem: str, path: Path):
        """
        Download problem statement in a path

        Args:
            problem (str): problem id
            path (Path): download destination path
        """
        raise NotImplementedError

    @abstractmethod
    def create_samples(self, problem: str, path: Path, force: bool = False):
        """
        Create problem samples in a desired folder

        Args:
            problem (str): problem id
            path (Path): download destination path
            force(bool): forces to continue even if the directory exists
        """
        raise NotImplementedError

    def create_template(self, path: Path):
        """
        Create a template from config folder.
        If it cant get the template it reconstructs the config folder
        Args:
            path (Path): destination path
        """   

        Config.copy_template(path)
        
    def create_metadata(self, path: Path):
        """
        Create a metadata file
        Args:
            path (Path): destination path
        """   

        with open(path, "w") as file:
            file.write(self.name + "\n")
            file.write(self.problem + "\n")
            file.write(self.url + "\n")
        
   
