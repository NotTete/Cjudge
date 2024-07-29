from pathlib import Path
from bs4 import BeautifulSoup
from getpass import getpass
import requests
import json

from ..error import *
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

    def login(self):
        self.session = requests.Session()
        post_data = {"commit": "Entrar", "loginForm_currentPage": "/"}

        logged = False
        print(f"{bold}Logging in {self.fullname}{clear}")
        print_line()
        for i in range(3):
            user = input("User: ")
            pwd = getpass("Password: ")

            post_data[b"loginForm_username"] = user.encode("UTF-8")
            post_data[b"loginForm_password"] = pwd.encode("UTF-8")
            login_url = "https://aceptaelreto.com/bin/login.php"

            loader = Loader("Logging in...", "", color=Color("#00FFFFF"))
            loader.start()
            r = self.session.post(login_url, data=post_data)
            r.raise_for_status()

            if(r.text.find("<strong>ERROR: </strong>") == -1):
                loader.stop()
                logged = True
                break
            
            if(i != 2):
                loader.stop("Incorrect username or password. Please try again")
            else:
                loader.stop("Couldn't log in")


        return logged
    
    def get_result(self):
        submission = None

        loader = Loader("Getting result...", "", color=Color("#00FFFFF"))
        loader.start()
        while submission == None or submission["result"] == "IQ":
            time.sleep(0.25)
            r = self.session.get("https://aceptaelreto.com/ws/user/30966/submissions")
            r.raise_for_status()
            data = json.loads(r.text)
            submission = data["submission"][0]


        loader.stop()

        result = submission["result"]
        time_result = submission.get("executionTime")
        memory = submission.get("memoryUsed")
        ranking = submission.get("ranking")

        color = rgb(color_dic.get(result, color_dic["OT"]))
        result = veredict_dict.get(result, result)
        result_str = f"  {bold}{color}{result}{clear}"

        if(time_result != None):
            result_str += f" {time_result} secs"
        
        if(memory != None):
            result_str += f" {memory} KiB"
        
        if(ranking != None):
            result_str += f" {bold}#{ranking}{clear}"

        print_line()
        print(f"{bold}Result in problem {self.problem}:{clear}")
        print(result_str)

    def submit(self):
        file_path = Path(self.path, "main.cpp")

        if(not file_path.is_file()):
            raise FileNotFoundError
        
        with open(file_path, "r") as file:
            src_code = file.read()

        if(not self.login()):
            return

        url = f"https://aceptaelreto.com/bin/submitproblem.php"

        data = {
            "currentPage": (None, "/"),
            "cat": (None, -1),
            "id": (None, self.problem),
            "language": (None, "CPP"),
            "comment": (None, ""),
            "inputFile": ("", ""),
            "sentCode": (None, "inlineSentCode"),
            "immediateCode": (None, src_code),
        }

        loader = Loader("Submitting problem...", "", color=Color("#00FFFFF"))
        loader.start()
        r = self.session.post(url, files=data)
        r.raise_for_status()
        loader.stop()

        if(r.text.find("El problema no existe") != -1):
            raise CorruptedMetafileError

        self.get_result()