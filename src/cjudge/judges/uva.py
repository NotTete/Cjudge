from pathlib import Path
from pypdf import PdfReader
from bs4 import BeautifulSoup
from getpass import getpass
import requests
import json
import time

from ..terminal_utils import *
from ..error import *
from .judge import Judge
from ..error import InvalidProblemException

class UvaJudge(Judge):


    @property
    def url(self):
        return f"https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem={self._problem_id}"

    name = "uva"
    fullname = f"{bold}{rgb(Color("#ff3399"))}UvaJudge{clear}"

    def __init__(self, problem: str, path: Path, problem_id = None):
        self.path = path
        self.problem = problem

        # Problem number must be bigger than 100
        if len(problem) <= 2:
            raise InvalidProblemException(self.name, problem)


        if(problem_id == None):
            # Get problem_id for problem url
            request = requests.get(f"https://uhunt.onlinejudge.org/api/p/num/{self._problem}")
            request.raise_for_status()
            data = json.loads(request.text)
            self._problem_id = data.get("pid")
        else:
            self._problem_id = problem_id

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

    def get_stadistics(self):
        stadistics_url = self.url.replace("show_problem", "problem_stats").replace("&problem=", "&problemid=")
        request = requests.get(stadistics_url)
        request.raise_for_status()

        parser = BeautifulSoup(request.text, "html.parser")
        parser = parser.find("div", {"id": "col3_content_wrapper"})

        title = parser.find("div", {"class":"componentheading"}).get_text()

        data = parser.find_all("script", limit=4)[-1].get_text()
        first_index = data.find("{")
        second_index = first_index + data[first_index:].find("}") + 1
        parse_data = lambda x: x.replace(")", "").replace("(","").split(" ")
        submission_data = list(map(parse_data, json.loads(data[first_index:second_index].replace("'", '"')).keys()))
        submission_data = {data[0]: int(data[1]) for data in submission_data}

        user_data_tag = parser.find_all("table", limit=2)[-1].find_all("tr", limit=2)[-1].find_all("td")[1:]
        user_data = {"AC": int(user_data_tag[1].get_text()), "WA": int(user_data_tag[0].get_text()) - int(user_data_tag[1].get_text())}

        try:
            submission_data["MLE"] = submission_data.pop("ML")
        except KeyError:
            pass

        try:
            submission_data["TLE"] = submission_data.pop("TL")
        except KeyError:
            pass
        valid_keys = ["AC", "WA", "PE", "MLE", "CE", "TLE", "OT", "RTE"]
        invalid_keys = list(filter(lambda x: not x in valid_keys, submission_data.keys()))
        
        if(len(invalid_keys) > 0):
            submission_data["OT"] = 0
            for key in invalid_keys:
                submission_data["OT"] += submission_data.pop(key)

        return title, user_data, submission_data

    def validate_problem(self):
        url = f"https://uhunt.onlinejudge.org/api/p/num/{self.problem}"
        r = requests.get(url)
        r.raise_for_status()
        
        if(r.text == "{}"):
            raise CorruptedMetafileError

    def login(self):
        self.session = requests.Session()
        post_data = {}

        login_page = self.session.get('https://onlinejudge.org/')
        login_page.raise_for_status()
        soup = BeautifulSoup(login_page.text, "html.parser")

        try:
            form = soup.find('form', attrs={'id': 'mod_loginform'})
            inputs = form.find_all('input')
        except Exception:
            return None
        for i in inputs:
            if i.has_attr('value'):
                post_data[i['name'].encode('ascii','ignore')] = i['value'].encode('ascii','ignore')

        logged = False
        print(f"{bold}Logging in {self.fullname}{clear}")
        print_line()
        for i in range(3):
            user = input("User: ")
            pwd = getpass("Password: ")

            post_data[b"username"] = user.encode("UTF-8")
            post_data[b"passwd"] = pwd.encode("UTF-8")
            post_data[b'remember'] = b'no'
            login_url = form.attrs["action"]

            loader = Loader("Logging in...", "", color=Color("#00FFFFF"))
            loader.start()
            r = self.session.post(login_url, data=post_data)
            r.raise_for_status()

            if(r.text.find("Incorrect username or password. Please try again.") == -1):
                loader.stop()
                logged = True
                break
            
            if(i != 2):
                loader.stop("Incorrect username or password. Please try again")
            else:
                loader.stop("Couldn't log in")


        return logged
    
    def get_result(self):
        entries = None

        loader = Loader("Getting result...", "", color=Color("#00FFFFF"))
        loader.start()
        while entries == None or entries[3].get_text() == "In judge queue":
            time.sleep(0.25)
            r = self.session.get("https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=9")
            r.raise_for_status()
            parser = BeautifulSoup(r.text, "html.parser")
            entry = parser.find("tr", {"class": "sectiontableentry1"})
            entries = entry.find_all("td")
        
        loader.stop()

        result = entries[3].get_text()
        if result == "Accepted":
            color = rgb(color_dic["AC"])
        else:
            color = rgb(color_dic["WA"])

        time_result = entries[5].get_text()

        print_line()
        print(f"{bold}Result in problem {self.problem}:{clear}")
        print(f"  {bold}{color}{result}{clear} {time_result} secs")

    def submit(self):
        file_path = Path(self.path, "main.cpp")

        if(not file_path.is_file()):
            raise FileNotFoundError
        
        with open(file_path, "r") as file:
            src_code = file.read()

        self.validate_problem()
        if(not self.login()):
            return

        url = "https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=25&page=save_submission"

        data = {
            'problemid':	'',
            'category':		'',
            'localid':		self.problem,
            'language':		5,
            'code':			src_code
        }

        loader = Loader("Submitting problem...", "", color=Color("#00FFFFF"))
        loader.start()
        r = self.session.post(url, data=data)
        r.raise_for_status()
        loader.stop()

        self.get_result()
