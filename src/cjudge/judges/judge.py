from abc import ABC, abstractmethod
from pathlib import Path
import shutil 

from ..terminal_utils import *
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
        title, user, submission = self.get_stadistics()

        color_dict = {
            'AC':'#55B369',
            'WA':'#E84F67',
            'TLE':'#F3B74D',
            'MLE':'#75A9D4',
            'CE':'#C45A9C',
            'PE':'#FF9966',
            'RTE':'#CC99FF',
            'OT':'#000000'
        }

        submission_data = [(veredict, value, Color(color_dict[veredict])) for veredict, value in submission.items()]
        submission_data = list(zip(*submission_data))
        submission_bar = Bar(names=submission_data[0], values=submission_data[1], colors=submission_data[2], title="Submissions:")

        user_data = [(veredict, value, Color(color_dict[veredict])) for veredict, value in user.items()]
        user_data = list(zip(*user_data))
        user_bar = Bar(names=user_data[0], values=user_data[1], colors=user_data[2], title="Users:      ")

        print(f" {bold}{title}{clear} ".center(113, "┈"))
        print(f"{bold}Judge:{clear}   {self.fullname}")
        print(f"{bold}Problem:{clear} {self.problem}")
        print(f"{bold}URL:{clear}     {self.url}")
        print(f" {bold}Stadistics{clear} ".center(113, "┈"))
        user_bar.display(show_legend=False, columns=105)
        print("")
        submission_bar.display(show_legend=True, columns=105)


    @abstractmethod
    def get_stadistics(self):
        """
        Gets problem stadistics and return them
        """
        raise NotImplementedError