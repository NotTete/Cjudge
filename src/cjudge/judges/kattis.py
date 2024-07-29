from pathlib import Path
from zipfile import ZipFile 
from bs4 import BeautifulSoup
import requests
import kattispdf
import shutil

from ..terminal_utils import *
from ..error import *
from ..config import Config
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

    def get_stadistics(self):
        stadistics_url = self.url + "/statistics"
        request = requests.get(stadistics_url)
        request.raise_for_status()

        parser = BeautifulSoup(request.text, "html.parser")

        title = parser.find("h1").get_text().strip()

        parser = parser.find("div", {"class": "flex flex-wrap w-full gap-3"})
        data = parser.find("div", {"class": "w-full basis-full basis-2/3@md mt-5"}).find("script").get_text()
        first_index = data.find("[")
        second_index = first_index + data[first_index:].find("]") + 1

        submission_data = data[first_index:second_index].strip("][").replace("'", "").split(',')
        submission_data = [ int(value) for value in submission_data ]

        first_index = data[second_index:].find("[") + second_index
        second_index = first_index + data[first_index:].find("]") + 1

        submission_labels = data[first_index:second_index].strip("][").replace("'", "").split(',')

        labels_dic = {
            "Accepted": "AC",
            "Wrong Answer": "WA",
            "Run-Time Error": "RTE",
            "Compile Error": "CE",
            "Time Limit Exceeded": "TLE",
            "Memory Limit Exceeded": "MLE",
            "Other": "OT",
            "Output Limit Exceeded": "OT",
            "Judge Error": "OT",
        }

        submission_labels = [labels_dic[label] for label in submission_labels ]
        submission_data = {label:value for value, label in zip(submission_data, submission_labels)}

        table = parser.find("table", {"class": "table2 condensed mt-5"})
        labels = table.find_all("td", limit=10)
        user_data = {"AC": int(labels[9].get_text()), "WA": int(labels[7].get_text()) - int(labels[9].get_text())}


        return title, user_data, submission_data

    def login(self):
        username = Config.get_kattis_name()
        token = Config.get_kattis_token()

        if(username == None or token == None):
            raise Exception("Kattis logging information not be found check your config file")
        
        login_url = "https://open.kattis.com/login"
        args = {
            'user': username, 
            'token': token,
            'script': 'true'
        }

        loader = Loader("Logging in...", "", color=Color("#00FFFFF"))
        loader.start()

        self.session = requests.Session()
        r = self.session.post(login_url, data=args)

        loader.stop()

        if(r.status_code != 200):
            raise Exception("Kattis logging information is not valid check your config file")
            
    def get_result(self):
        status = None
        loading_status = ["Compiling", "New", "Running"]

        loader = Loader("Getting result...", "", color=Color("#00FFFFF"))
        loader.start()
        while status == None or status in loading_status:
            time.sleep(0.75)
            r = self.session.get(self.result_url)
            parser = BeautifulSoup(r.text, "html.parser")
            status = parser.find("td", {"data-type": "status"}).get_text()
        loader.stop()

        time_result = parser.find("td", {"data-type": "cpu"}).get_text()
        cases = parser.find("td", {"data-type": "testcases"}).get_text()

        if status.find("Accepted") != -1:
            color = rgb(color_dic["AC"])
        else:
            color = rgb(color_dic["WA"])

        result_str = f"  {bold}{color}{status}{clear}"

        if(time_result != ""):
            result_str += f" {time_result}"
        
        if(cases != ""):
            result_str += f" Cases: {bold}{cases}{clear}"

        print_line()
        print(f"{bold}Result in problem {self.problem}:{clear}")
        print(result_str)

    def submit(self):
        self.login()

        data = {
            'submit': 'true',
            'submit_ctr': 2,
            'language': "C++",
            'mainclass': "",
            'problem': self.problem,
            'tag': "",
            'script': 'true'
        }

        files = []
        with open(Path(self.path, "main.cpp"), 'rb') as file:
            files.append((
                'sub_file[]', (
                    "main.cpp",
                    file.read(),
                    'application/octet-stream'
                )
            ))
        
        submit_url = "https://open.kattis.com/submit"
        loader = Loader("Submitting problem...", "", color=Color("#00FFFFF"))
        loader.start()
        r = self.session.post(submit_url, data=data, files=files)
        r.raise_for_status()
        loader.stop()

        if(r.text == "Problem not found"):
            raise CorruptedMetafileError
        
        self.result_url = r.text[5 + r.text.find("URL: "):]
        self.get_result()
