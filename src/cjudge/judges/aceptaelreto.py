from pathlib import Path
from bs4 import BeautifulSoup
import requests

from ..error import InvalidProblemException
from .judge import Judge

class AerJudge(Judge):    
    @property
    def problem(self):
        return self._problem

    @problem.setter
    def problem(self, problem: str):
        """
        Set the problem number after validating it

        Args:
            problem (str): Problem number
        """

        # We request the pdf of the problem to validate it is a valid problem
        request = requests.get(self.pdf_url)
        error_code = request.status_code

        # If the requests isn't sucessful we raise an error
        if(error_code != 200):
            raise InvalidProblemException(self.name, problem)
        self._problem = problem

    @property
    def url(self):
        return f"https://aceptaelreto.com/problem/statement.php?id={self._problem}"

    @property
    def name(self):
        return "aer"

    def __init__(self, problem: str, check: bool = True):
        # Problem number must be bigger than 100
        if len(problem) <= 2:
            raise InvalidProblemException(self.name, problem)
        
        folder = problem[:-2]
        self.pdf_url = f"https://aceptaelreto.com/pub/problems/v{folder.zfill(3)}/{problem[-2:]}/st/problem.pdf"
        if(check):
            self.problem = problem
        else:
            self._problem = problem


    def create_statement(self, path: Path):

        # Download and save pdf directly from Acepta el Reto
        request = requests.get(self.pdf_url, stream=True)
        request.raise_for_status()

        with open(path, "wb") as file:
            for chunk in request.iter_content(1024):
                file.write(chunk)
    
    def create_samples(self, path: Path, force: bool = False):
        
        # Request problem html
        request = requests.get(self.url, stream=True)
        request.raise_for_status()
        parser = BeautifulSoup(request.text, "html.parser")

        # Find input text
        input_tag = parser.find("div", attrs={"id": "sampleIn"}).find("pre")
        input_text = input_tag.get_text()


        # Find output text
        output_tag = parser.find("div", attrs={"id": "sampleOut"}).find("pre")
        output_text = output_tag.get_text()

        # Save sample input and output
        try:
            path.mkdir()
        except FileExistsError as e:
            if(not force):
                raise e
        
        with open(Path(path, "1.in"), "w") as file:
            file.write(input_text)

        with open(Path(path, "1.out"), "w") as file:
            file.write(output_text)    
