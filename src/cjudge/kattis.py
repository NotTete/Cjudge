from pathlib import Path
import requests
import kattispdf
import shutil
from zipfile import ZipFile 

from .error import *
from .judge import Judge

def _problem_url(problem: str):
    """Given a problem id returns its url"""
    return f"{KattisJudge.url}/problems/{problem}"

class KattisJudge(Judge):    
    url = "https://open.kattis.com"
    name = "kattis"
    
    def __init__(self, problem):
        self.problem = problem
        self.url = f"{self.url}/problems/{problem}"
        request = requests.get(self.url)

        error_code = request.status_code
        if(error_code != 200):
            InvalidProblemException(self.name, self.problem)

    

    def create_statement(self, path: Path):
        kattispdf.generate_pdf(self.problem, path)
    
    def create_samples(self, path):
        # Request files
        samples_url = f"{self.url}/file/statement/samples.zip"
        request = requests.get(samples_url, stream=True)
        
        if(request.status_code == 404):
            # No samples
            return

        # Create folder
        path.mkdir()

        zip_path = Path(path, "samples.zip")
        with open(zip_path, "wb") as file:
            for chunk in request.iter_content(1024):
                file.write(chunk)

        # Extract samples
        with ZipFile(zip_path, 'r') as zip_file:  
            zip_file.extractall(path) 

        # Clean up download
        zip_path.unlink()

        # Remove dir if no samples
        if(len(list(path.iterdir())) == 0):
            shutil.rmtree(path)

        # Change .ans for .out
        for file in path.glob("*.ans"):
            file.rename(file.with_suffix(".out"))






