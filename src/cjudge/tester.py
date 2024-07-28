from pathlib import Path
import re
import subprocess
import tempfile
import threading
import time
import queue

from .terminal_utils import *
from .config import Config
from .error import CompilationError

class Tester():
    def __init__(self, path, output, create_files):
        self.cpp_file = Path(path, "main.cpp")
        self.sample_folder = Path(path, "samples")
        self.temporary_path = tempfile.TemporaryDirectory()

        self.output_type = output
        self.create_files = create_files

        self.compile_source()
        self.get_samples()

    def get_samples(self):
        if(not self.sample_folder.exists()):
            raise FileNotFoundError
        
        input_set = set()
        output_set = set()

        for file in self.sample_folder.iterdir():
            name = file.stem
            suffix = file.suffix
            
            if(suffix == ".in"):
                input_set.add(name)
            elif(suffix == ".out"):
                output_set.add(name)

        full_samples = list(input_set.intersection(output_set))
        half_samples = list(input_set.difference(output_set))

        regex = re.compile(r'(\d+)')
        sort_function = lambda l: [int(s) if s.isdigit() else s.lower() for s in re.split(regex, l)]

        full_samples.sort(key=sort_function)
        half_samples.sort(key=sort_function)

        self.samples = []
        for sample in full_samples:
            self.samples.append((True, sample))
        for sample in half_samples:
            self.samples.append((False, sample))

    def compile_source(self):
        loader = Loader("Compiling source...", end_description="", color=Color("#00FFFF"))
        loader.start()
        try:
            self.source = Path(self.temporary_path.name, "main")
            compiler = Config.get_compiler()

            if(not self.cpp_file.exists()):
                raise FileNotFoundError("Couldn't find problem file")

            sub = subprocess.run([compiler, "-o", self.source, self.cpp_file], capture_output=True) 
            if sub.returncode != 0:
                raise CompilationError(sub.stderr.decode())

        finally:
            loader.stop()

    def test_sample(self, sample, full):
        result = None
        answer = None

        input_file = open(Path(self.sample_folder, f"{sample}.in"), "r")
        
        if self.create_files:
            result_file = open(Path(self.sample_folder, f"{sample}.res"), "w+")
        else:
            result_file = tempfile.TemporaryFile("w+")

        if(full):
            output_file = open(Path(self.sample_folder, f"{sample}.out"), "r")

            try:
                sub = subprocess.run(self.source, stdin=input_file, stdout=result_file, timeout=3)
            except subprocess.TimeoutExpired:
                result = "TLE"
            else:
                if(sub.returncode != 0):
                    result = "RTE"

            if(result == None):
                result_file.seek(0)
                is_correct_answer, answer = self.compare_files(result_file, output_file)
                if(is_correct_answer):
                    result = "AC"
                else:
                    result = "WA"
                
            output_file.close()  
        else:
            result = "NI"
            try:
                sub = subprocess.run(self.source, stdin=input_file, stdout=result_file, timeout=3)
            except subprocess.TimeoutExpired:
                result = "TLE"
            else:
                if(sub.returncode != 0):
                    result = "RTE"

            result_file.seek(0)
            answer = [ ('S', result.strip("\n")) for result in result_file.readlines()]

        input_file.close()
        result_file.close()

        return result, answer   

    def compare_files(self, file1, file2):
        strip_endline = lambda x: x.strip("\n")
        file1_lines = list(map(strip_endline, file1.readlines()))
        file2_lines = list(map(strip_endline, file2.readlines()))


        length1 = len(file1_lines) + 1
        length2 = len(file2_lines) + 1

        memo_dis = [[0 for i in range(length1)] for j in range(length2)]
        memo_op = [['E' for i in range(length1)] for j in range(length2)]

        for i in range(length1):
            memo_dis[0][i] = 0
            memo_op[0][i] = 'D'

        for j in range(length2):
            memo_dis[j][0] = 0
            memo_op[j][0] = 'I'

        memo_op[0][0] = 'S'

        for i2 in range(1, length2):
            for i1 in range(1, length1):
                res = memo_dis[i2 - 1][i1]
                op = 'I'

                if(res < memo_dis[i2][i1 - 1]):
                    res = memo_dis[i2][i1 - 1]
                    op = 'D'

                if(file1_lines[i1 - 1] == file2_lines[i2 - 1] and res < memo_dis[i2 - 1][i1 - 1] + 1):
                    res = memo_dis[i2 - 1][i1 - 1] + 1
                    op = 'S'

                memo_dis[i2][i1] = res
                memo_op[i2][i1] = op

        answer = []
        i1 = length1 - 1
        i2 = length2 - 1
        while i1 != 0 or i2 != 0:
            if(memo_op[i2][i1] == 'S'):
                i1 -= 1
                i2 -= 1
                answer.append(('S', file1_lines[i1]))
            elif(memo_op[i2][i1] == 'D'):
                i1 -= 1
                answer.append(('D', file1_lines[i1]))
            else:
                i2 -= 1
                answer.append(('I', file2_lines[i2]))
        answer.reverse()

        is_correct_answer = memo_dis[length2 - 1][length1 - 1] == length1 - 1 and length1 == length2
        return is_correct_answer, answer

    def print_answer(self, answer):
        for op, line in answer:
            color = ""
            char = " "
            if(op == 'D'):
                char = "-"
                color = bold + rgb(Color("#ff7777"))
            elif(op == 'I'):
                char = "+"
                color = bold + rgb(Color("#77ff78"))

            line = line.replace(" ", f"{dim}·{clear}{color}")
            print(f"{color}{char} {line}{clear}")

    def run_tests(self):
        correct_test = 0
        run_test = 0
        fail_test = 0

        # Test full tests
        for full, sample in self.samples:
            loader = Loader(f"Running test {sample}...", end_description="", color=Color("#00FFFF"))
            loader.start()
            result, asnwer = self.test_sample(sample, full)
            loader.stop()
            if(result == "AC"):
                correct_test += 1
                print(f"{bold}Test {sample}: {rgb(color_dic["AC"])}PASSED {check}")
            elif(result == "NI"):
                run_test += 1
                print(f"{bold}Test {sample}: {rgb(color_dic["CE"])}RAN{clear}")
            else:
                fail_test += 1
                print(f"{bold}Test {sample}: {rgb(color_dic["WA"])}FAILED {cross}")

            if(self.output_type == "full" or self.output_type == "error"):
                if(result == "TLE"):
                    print(f"  Your program ran out of time {bold}{rgb(color_dic[result])}{result}{clear}")
                elif(result == "RTE"):
                    print(f"  Your program crashed during execution {bold}{rgb(color_dic[result])}{result}{clear}")
                elif(result == "WA"):
                    self.print_answer(asnwer)
                    print(f"  Your output is incorrect {bold}{rgb(color_dic[result])}{result}{clear}")

            if(self.output_type == "full"):
                if(result == "AC"):
                    self.print_answer(asnwer)
                    print(f"  Your output is correct {bold}{rgb(color_dic[result])}{result}{clear}")
                elif(result == "NI"):
                    self.print_answer(asnwer)
                    print(f"  This is your program output")
            
            print_line()

        summary = []
        if(correct_test > 0):
            summary.append(f"{bold}{rgb(color_dic["AC"])}{correct_test} PASSED{clear}")
        if(fail_test > 0):
            summary.append(f"{bold}{rgb(color_dic["WA"])}{fail_test} FAILED{clear}")
        if(run_test > 0):
            summary.append(f"{bold}{rgb(color_dic["CE"])}{run_test} RAN{clear}")

        if(len(summary) > 0):
            print(f"{bold}Summary: " + f"{bold}, ".join(summary))
        else:
            print(f"{bold}Summary:{clear} No test ran")
        return correct_test, fail_test, run_test

    def run_interactive(self):
        print(f"{bold}Running interactive your interactive program:{clear}")
        print_line()

        def populate_queue(stream, myqueue):
            while True:
                line = stream.readline()
                if(line == None or line == b''):
                    #print("Exit", stream.name)
                    stream.close()
                    break
                else:
                    print(f"{rgb(Color("#9972CC"))}{bold}{line.decode("UTF-8")}{clear}", end="")
                    myqueue.put(line)
                time.sleep(0.001)

        def get_input(stream, thread):
            while True:
                data = input() + "\n"
                stream.write(data.encode("UTF-8"))
                stream.flush()
                time.sleep(0.025)

        process = subprocess.Popen(self.source,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_queue = queue.Queue()
        thread1 = Thread(target=populate_queue, daemon=True, args=(process.stdout, output_queue))
        thread2 = Thread(target=populate_queue, daemon=True, args=(process.stderr, output_queue))
        thread3 = Thread(target=get_input, daemon=True, args=(process.stdin, "a"))

        threads = [thread1, thread2, thread3]
        for thread in threads:
            thread.start()

        while(process.poll() == None and threads[0].is_alive):
            time.sleep(0.1)
        
        print_line()
        print(f"{bold}Program exited {process.poll()}{clear}")
        if(thread3.is_alive):
            print("(Press Enter)", end="")

                

        

