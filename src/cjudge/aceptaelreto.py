from pathlib import Path
import requests
from bs4 import BeautifulSoup

from .error import *
from .judge import Judge

class AerJudge(Judge):    
    url = "https://aceptaelreto.com"
    name = "AceptaElReto"
    
    def __init__(self, problem):
        self.problem = problem
        folder = problem[:-2]

        self.pdf_url = f"{self.url}/pub/problems/v{folder.zfill(3)}/{problem[-2:]}/st/problem.pdf"
        self.url = f"{self.url}/problem/statement.php?id={self.problem}"

        request = requests.get(self.pdf_url)
        error_code = request.status_code
        if(error_code != 200):
            InvalidProblemException(self.name, self.problem)

    def create_statement(self, path: Path):
        request = requests.get(self.pdf_url, stream=True)
        request.raise_for_status()

        with open(path, "wb") as file:
            for chunk in request.iter_content(1024):
                file.write(chunk)
    
    def create_samples(self, path):
        request = requests.get(self.url, stream=True)
        request.raise_for_status()
        parser = BeautifulSoup(request.text, "html.parser")

        input_tag = parser.find("div", attrs={"id": "sampleIn"}).find("pre")
        input_text = input_tag.get_text()

        output_tag = parser.find("div", attrs={"id": "sampleOut"}).find("pre")
        output_text = output_tag.get_text()

        path.mkdir()
        with open(Path(path, "1.in"), "w") as file:
            file.write(input_text)

        with open(Path(path, "1.out"), "w") as file:
            file.write(output_text)    







