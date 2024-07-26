from pathlib import Path
from bs4 import BeautifulSoup
import requests
import json

from ..error import InvalidProblemException
from .judge import Judge
from ..terminal_utils import *

class AerJudge(Judge):    
    
    @property
    def url(self):
        return f"https://aceptaelreto.com/problem/statement.php?id={self._problem}"

    name = "aer"
    fullname = f"{bold}{rgb(Color("#99ccff"))}¡Acepta el Reto!{clear}"

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
        self.check_if_valid(request)
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
    
    def check_if_valid(self, request):
        request.raise_for_status()
        parser = BeautifulSoup(request.text, "html.parser")
        
        button = parser.find("div", {"class": "alert alert-danger"})
        if button != None:
            button_text = button.get_text().strip()
            if button_text.find("ERROR") != -1:
                raise InvalidProblemException(self.name, self.problem)

    def get_stadistics(self):
        stadistics_url = self.url.replace("statement", "statistics")
        request = requests.get(stadistics_url)
        self.check_if_valid(request)

        parser = BeautifulSoup(request.text, "html.parser")
        parser = parser.find("div", {"class": "col-md-10"})

        title = f"{self.problem} - {parser.find("h1").get_text()}"

        user_data_tag = parser.find("table", {"class": "problemGlobalStatistics"}).find_all("tr", limit=2)[-1].find_all("td")[1:]
        user_data = {"AC": int(user_data_tag[1].get_text()), "WA": int(user_data_tag[0].get_text()) - int(user_data_tag[1].get_text())}

        submission_raw_text = parser.find("script").get_text()
        look_index = submission_raw_text.find("];") + 2
        submission_raw_text = submission_raw_text[look_index:]

        first_index = submission_raw_text.find("[")
        second_index = submission_raw_text.find("];") + 1

        submission_raw_data = submission_raw_text[first_index:second_index]
        submission_raw_data = submission_raw_data.replace("[", "").replace("]", "").replace("'", "").split(",")[2:]

        labels_dic = {
            "Accepted": "AC",
            "Presentation Error": "PE",
            "Wrong Answer": "WA",
            "Time limit exceeded": "TLE",
            "Memory limit exceeded": "MLE",
            "Output limit exceeded": "OT",
            "Restricted function": "OT",
            "Run-time error": "RTE",
            "Compilation error": "CE",
            "Internal error": "OT",
        }

        submission_data = {}

        for i in range(0, len(submission_raw_data), 2):
            label = submission_raw_data[i].strip()
            label = labels_dic[label]
            value = int(submission_raw_data[i + 1])

            if(submission_data.get(label) != None and value != 0):
                submission_data[label] += value
            elif (value != 0):
                submission_data[label] = value

        return title, user_data, submission_data
