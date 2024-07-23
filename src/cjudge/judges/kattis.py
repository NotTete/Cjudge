from pathlib import Path
from zipfile import ZipFile 
import requests
import kattispdf
import shutil

from ..error import InvalidProblemException
from .judge import Judge

class KattisJudge(Judge):

    @property
    def problem(self):
        return self._problem

    @property
    def url(self):
        return f"https://open.kattis.com/problems/{self._problem}"

    @problem.setter
    def problem(self, problem: str):
        """
        Set the problem number after validating it

        Args:
            problem (str): Problem number
        """

        self._problem = problem

        # We request the problem page to validate it is a valid problem
        request = requests.get(self.url)
        error_code = request.status_code
        if(error_code != 200):
            raise InvalidProblemException(self.name, problem)
        

    @property
    def name(self):
        return "kattis"

    def __init__(self, problem: str):
        self.problem = problem

    def create_statement(self, path: Path):
        kattispdf.generate_pdf(self.problem, path)
    
    def create_samples(self, path: Path, force: bool = False):
        # Request sample
        samples_url = f"{self.url}/file/statement/samples.zip"
        request = requests.get(samples_url, stream=True)
        
        # Create folder
        try:
            path.mkdir()
        except FileExistsError as e:
            if(not force):
                raise e

        if(request.status_code == 404):
            # If no sample, we create an empty sample
            with open(Path(path, "1.in"), "w") as file:
                pass
            with open(Path(path, "1.out"), "w") as file:
                pass
            
            return

        # Download samples
        zip_path = Path(path, "samples.zip")
        with open(zip_path, "wb") as file:
            for chunk in request.iter_content(1024):
                file.write(chunk)

        # Extract samples
        with ZipFile(zip_path, 'r') as zip_file:  
            zip_file.extractall(path) 

        # Clean up download
        zip_path.unlink()

        # If no sample, we create an empty sample
        if(len(list(path.iterdir())) == 0):
            with open(Path(path, "1.in"), "w") as file:
                pass
            with open(Path(path, "1.out"), "w") as file:
                pass

        # Change .ans for .out
        for file in path.glob("*.ans"):
            file.rename(file.with_suffix(".out"))
