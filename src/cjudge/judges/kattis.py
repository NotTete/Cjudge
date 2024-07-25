from pathlib import Path
from zipfile import ZipFile 
import requests
import kattispdf
import shutil

from ..terminal_utils import *
from ..error import InvalidProblemException
from .judge import Judge

class KattisJudge(Judge):
    @property
    def url(self):
        return f"https://open.kattis.com/problems/{self._problem}"

    name = "kattis"
    fullname = f"{bold}{rgb(Color("#ff9933"))}Kattis{clear}"

    def __init__(self, problem: str, path: Path):
        self.path = path
        self.problem = problem

    def create_statement(self):
        path = Path(self.path, f"{self.problem}.pdf")
        kattispdf.generate_pdf(self.problem, path)
    
    def create_samples(self, force: bool = False, create_sample: bool = True):
        
        # Check if the user want to create empty samples
        if(not create_sample):
            self.create_samples_empty(force)
            return

        # Request sample
        samples_url = f"{self.url}/file/statement/samples.zip"
        request = requests.get(samples_url, stream=True)

        # If problem not found create empty samples
        if(request.status_code == 404):
            self.create_samples_empty(force)
            return
        request.raise_for_status()

        # Create folder
        path = Path(self.path, "samples")
        path.mkdir(exist_ok=force)

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
