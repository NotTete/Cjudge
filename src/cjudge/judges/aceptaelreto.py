from pathlib import Path
from bs4 import BeautifulSoup
import requests

from ..error import InvalidProblemException
from .judge import Judge
from ..terminal_utils import *

class AerJudge(Judge):    
    
    @property
    def url(self):
        return f"https://aceptaelreto.com/problem/statement.php?id={self._problem}"

    name = "aer"
    fullname = f"{bold}{rgb(Color("#99ccff"))}Acepta el Reto{clear}"

    def __init__(self, problem: str, path: Path):
        self.path = path
        self.problem = problem

        # Problem number must be bigger than 100
        if len(problem) <= 2:
            raise InvalidProblemException(self.name, problem)

    def create_statement(self):
        # Get url
        folder = self.problem[:-2].zfill(3)
        pdf_url = f"https://aceptaelreto.com/pub/problems/v{folder}/{self.problem[-2:]}/st/problem.pdf"

        # Download and save pdf directly from Acepta el Reto
        request = requests.get(pdf_url, stream=True)
        request.raise_for_status()

        path = Path(self.path, f"{self.problem}.pdf")
        with open(path, "wb") as file:
            for chunk in request.iter_content(1024):
                file.write(chunk)
    
    def create_samples(self, force: bool = False, create_sample: bool = True):
        # Check if the user want to create empty samples
        if(not create_sample):
            self.create_samples_empty(force)
            return

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
        path = Path(self.path, "samples")
        path.mkdir(exist_ok=force)
        
        with open(Path(path, "1.in"), "w") as file:
            file.write(input_text)

        with open(Path(path, "1.out"), "w") as file:
            file.write(output_text)    
