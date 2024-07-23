from pathlib import Path
from pypdf import PdfReader
import requests
import json

from .judge import Judge
from .error import InvalidProblemException

class UvaJudge(Judge):

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

        # We also set problem_id
        request = requests.get(f"https://uhunt.onlinejudge.org/api/p/num/{self._problem}")
        request.raise_for_status()
        data = json.loads(request.text)

        self._problem_id = data["pid"]

    @property
    def url(self):
        return f"https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem={self._problem_id}"

    @property
    def name(self):
        return "uva"

    def __init__(self, problem: str):
        # Problem number must be bigger than 100
        if len(problem) <= 2:
            raise InvalidProblemException(self.name, problem)

        folder = problem[:-2]
        self.pdf_url = f"https://onlinejudge.org/external/{folder}/{problem}.pdf"
        self.problem = problem

    def create_statement(self, path: Path): 

        # Download and save pdf directly from uva
        request = requests.get(self.pdf_url, stream=True)
        request.raise_for_status()

        with open(path, "wb") as file:
            for chunk in request.iter_content(1024):
                file.write(chunk)
    
    def create_samples(self, path: Path, force: bool = False):
        
        parts = []
        def eliminate_header(text, cm, tm, font_dict, font_size):
            """ Eliminates the header from the pdf """
            if 40.2 > tm[5] or tm[5] > 40.4:
                parts.append(text)

        # Open problem pdf
        reader = PdfReader(Path(path.parent, f"{self.problem}.pdf"))

        # Extract text from every page
        text = ""
        for page in reader.pages:
            parts.clear()
            page.extract_text(visitor_text=eliminate_header)
            text += "".join(parts)
            text += "\n"

        # Search for input and output header
        input_index = text.find("Sample Input\n")
        output_index = text[input_index:].find("Sample Output\n")

        # Skip if not found
        if(input_index == -1 or output_index == -1):
            return
        output_index += input_index

        # Obtain sample input and output  
        input_text = text[input_index + len("Sample Input"):output_index].strip()
        output_text = text[output_index + len("Sample Output"):].strip()

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
