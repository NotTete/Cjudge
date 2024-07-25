from threading import Thread
from shutil import get_terminal_size
import time

class Color():
    def __init__(self, *args):
        if(len(args) == 3):
            self.r = args[0]
            self.g = args[1]
            self.b = args[2]
        elif(len(args) == 1 and type(args[0]) == str):

            string = args[0].lower()
            if(string[0] == "#"):
                string = string[1:]
            hex_int = int(string, base=16)
            self.r = hex_int // (256 ** 2)        
            self.g = (hex_int // 256) % 256  
            self.b = hex_int % 256
        elif(len(args) == 1):
            rgb_list = args[0]
            self.r = args[0]
            self.g = args[1]
            self.b = args[2]  
        else:
            raise ValueError("Arguments must be r, g, b integers or one rgb string")
    
    def __repr__(self):
        return f"Color({self.r},{self.g},{self.b})"

def rgb(color: Color) -> str:
    """
    Args:
        r (int): red
        g (int): green
        b (int): blue

    Returns:
        str: Return rgb ansi escape code
    """
    return f"\33[38;2;{color.r};{color.g};{color.b}m"

def rgb_bg(color: Color) -> str:
    """
    Args:
        r (int): red
        g (int): green
        b (int): blue

    Returns:
        str: Return rgb background ansi escape code
    """
    return f"\33[48;2;{color.r};{color.g};{color.b}m"

clear = "\33[0m"
bold = "\33[1m"

check = f"{rgb(Color("#88ff73"))}{bold}✓{clear}"

def display_warning(msg: str, sameline: bool = False):
    """Display a warning msg"""
    error_color = Color("#F3B74D")
    c = ""
    if(sameline):
        c = "\r"
    print(f"{c}{bold}{rgb(error_color)}[WARNING]{clear} {msg}")

def display_error(msg: str):
    """Display a warning msg"""
    error_color = Color("#E84F67")
    print(f"{bold}{rgb(error_color)}[ERROR]{clear} {msg}")

class Loader():
    def __init__(self, description: str, end_description: str, sequence: list = ["⡇","⠏", "⠛", "⠹", "⢸", "⣰", "⣤", "⣆"], color = None):
        self.description = description
        self.end_description = end_description
        self.sequence = sequence
        self.done = False
        self.thread = Thread(target=self._animate, daemon=True)
        self.color = color

    def start(self):
        self.done = False
        self.thread.start()

    def stop(self, error = None):
        self.done = True
        print(f"\r{ " " * get_terminal_size((80, 20)).columns }", end="")

        if(error == None):
            print(f"\r{self.end_description}")
        else:
            print(f"\r", end="")
            display_error(error)

    def change_description(self, description: str):
        self.description = description
    
    def send_warning(self, description: str):
        display_warning(description, True)

    def _animate(self):
        index = 0
        cycle_length = len(self.sequence)
        last_description = self.description

        color = rgb(self.color) if self.color != None else ""

        while not self.done:

            # If the description has changed we clear the line before printing
            if(self.description != last_description):
                print(f"\r{ " " * get_terminal_size((80, 20)).columns }", end="", flush = False)

            print(f"\r{color}{self.sequence[index]}{clear} {self.description}", end="", flush=True)
            index = (index + 1) % cycle_length
            last_description = self.description
            time.sleep(0.1)
        
class Bar:
    def __init__(self, values, names, colors, title = None):
        total_sum = sum(values)
        self.values = [value / total_sum for value in  values]
        self.colors = colors
        self.names = names
        self.title = title
    
    def display(self, show_legend: bool = True, columns = 100):
        # Offset due to the title
        title_offset = len(f"{self.title} ")
        if(self.title != None):
            columns -= title_offset 

        # Convert percentages to number of characters
        ceil_chars_index = []
        lower_chars_index = []
        number_chars = []
        chars_number_sum = 0

        for index, value in enumerate(self.values):
            value *= columns
            rounded_value = round(value)

            chars_number_sum += rounded_value
            number_chars.append(rounded_value)

            if(rounded_value > value):
                ceil_chars_index.append(index)
            elif(rounded_value < value):
                lower_chars_index.append(index)

        if(chars_number_sum < columns):
            number = columns - chars_number_sum
            lower_chars_index.sort(key=lambda x: self.values[x], reverse=True)
            for i in range(number):
                index = lower_chars_index[i]
                number_chars[index] -= 1

        elif(chars_number_sum > columns):
            number = chars_number_sum - columns 
            ceil_chars_index.sort(key=lambda x: self.values[x], reverse=True)
            for i in range(number):
                index = ceil_chars_index[i]
                number_chars[index] -= 1

        # Get bar string
        color = []
        for i, value in enumerate(number_chars):
            color += value * [self.colors[i]]
        bar = ""
        for i in range(0, len(color)):
            char = "█"
            if(i in [0,len(color) - 1]):
                char = "░"
            elif(i in [1,len(color) - 2]):
                char = "▒"
            elif(i in [2,len(color) - 3]):
                char = "▓"
            bar += rgb(color[i]) + char
        bar += clear

        # Show bar
        if(self.title != None):
            print(f"{bold}{self.title} {clear}", end="")    
        print(bar)
        
        # Show legend
        if(show_legend):
            # Calculate center offset and create legend
            legend = ""
            length = 0
            for color, value, name, char in zip(self.colors, self.values, self.names, number_chars):
                percent = str(round(value * 100, 2))
                length += len(name + percent) + 4
                legend += f"{bold}{rgb(color)}{name}:{clear}{percent}%  "
            length -= 2

            # Print title and center offset
            print("\n" + " " * (title_offset + (columns - length) // 2), end="")
            # Print legend
            print(legend)
            print("")

    