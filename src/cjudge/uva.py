from .judge import Judge
import requests
from pathlib import Path
import json
from pypdf import PdfReader


class UvaJudge(Judge):
    url = "https://onlinejudge.org"
    name = "uva"
    
    def __init__(self, problem):
        self.problem = problem

        folder = problem[:-2]
        
        self.pdf_url = f"{self.url}/external/{folder}/{problem}.pdf"

        request = requests.get(f"https://uhunt.onlinejudge.org/api/p/num/{self.problem}")
        request.raise_for_status()
        data = json.loads(request.text)

        self.problem_id = data["pid"]
        self.url = f"{self.url}/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem={self.problem_id}"

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
        parts = []

        def visitor_body(text, cm, tm, font_dict, font_size):
            if tm[5] != 40.329:
                parts.append(text)

        reader = PdfReader(Path(path.parent, f"{self.problem}.pdf"))
        text = ""
        for page in reader.pages:
            parts.clear()
            page.extract_text(visitor_text=visitor_body)
            text += "".join(parts)
            text += "\n"

        input_index = text.find("Sample Input\n")
        output_index = text[input_index:].find("Sample Output\n")

        if(input_index == -1 or output_index == -1):
            return
                
        output_index += input_index

        input_text = text[input_index + len("Sample Input"):output_index].strip()
        output_text = text[output_index + len("Sample Output"):].strip()

        path.mkdir()
        with open(Path(path, "1.in"), "w") as file:
            file.write(input_text)

        with open(Path(path, "1.out"), "w") as file:
            file.write(output_text)         
