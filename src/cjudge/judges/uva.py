from pathlib import Path
from pypdf import PdfReader
import requests
import json

from .judge import Judge
from ..error import InvalidProblemException

class UvaJudge(Judge):


    @property
    def url(self):
        return f"https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem={self._problem_id}"

    @property
    def name(self):
        return "uva"

    @property
    def fullname(self):
        return "UvaJudge"

    def __init__(self, problem: str, path: Path):
        self.path = path
        self.problem = problem

        # Problem number must be bigger than 100
        if len(problem) <= 2:
            raise InvalidProblemException(self.name, problem)

        # Get problem_id for problem url
        request = requests.get(f"https://uhunt.onlinejudge.org/api/p/num/{self._problem}")
        request.raise_for_status()
        data = json.loads(request.text)
        self._problem_id = data.get("pid")

        if(self._problem_id == None):
            raise InvalidProblemException(self.name, problem)

    def create_statement(self): 
        # Get pdf url
        folder = self.problem[:-2]
        pdf_url = f"https://onlinejudge.org/external/{folder}/p{self.problem}.pdf"

        # Download and save pdf directly from uva
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
        
        # Open problem pdf
        reader = PdfReader(Path(self.path, f"{self.problem}.pdf"))

        # Extract text from every page
        text = ""
        for page in reader.pages:
            text += page.extract_text()
            text += "\n"

        # Search for input and output header
        input_index = text.find("Sample Input\n")
        output_index = text[input_index:].find("Sample Output\n")

        # If no sample, we create an empty sample
        if(input_index == -1 or output_index == -1):
            self.create_samples_empty(force)
            return

        output_index += input_index

        # Obtain sample input and output  
        input_text = text[input_index + len("Sample Input"):output_index].strip()
        output_text = text[output_index + len("Sample Output"):].strip()

        # Save sample input and output
        path = Path(self.path, "samples")
        path.mkdir(exist_ok=force)

        with open(Path(path, "1.in"), "w") as file:
            file.write(input_text)

        with open(Path(path, "1.out"), "w") as file:
            file.write(output_text)         

    def create_metadata(self):
        super().create_metadata()
        # We also want to save the problem id
        path = Path(self.path, ".meta")
        with open(path, "a") as file:
            file.write(f"{self._problem_id}\n")