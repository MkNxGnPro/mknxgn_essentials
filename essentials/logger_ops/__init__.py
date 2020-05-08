from essentials import run_data
from essentials import file_ops
import os, datetime

user_desc = """What to print while running your program
Level  |  Description
  0    |  Nothing (Default)
  1    |  Error
  2    |  Info
  3    |  Errors and Info 
"""


ERROR = 1
INFO = 2

file_run_info = run_data.Run_Data(__name__)
debug_level = file_run_info.add_arg(run_data.Default_Arg("debug", 0, run_data.INT, user_desc, False, [0,1,2,3]))


class Logger(object):
    def __init__(self, name="Main", print_level=0, dating="%H:%M:%S  %Y-%m-%d", filing="%Y-%m-%d"):
        self.name = name
        self.workDir = os.path.join("logs", name)
        self.print_level = print_level
        self.filing = filing
        self.dating = dating
        os.makedirs("logs", exist_ok=True)
        os.makedirs(self.workDir, exist_ok=True)

    def log(self, data, level=2):
        NOW = datetime.datetime.now()
        if level == 1:
            ex = "ERROR"
        elif level == 2:
            ex = "INFO"
        full_data = "[ " + ex + " ] - " + NOW.strftime(self.dating) + " >> " + str(data)
        if self.print_level == level or self.print_level == 3 or debug_level == 3 or debug_level == level:
            print(full_data)
        file_ops.write_file(os.path.join(self.workDir, NOW.strftime(self.filing) + ".log"), full_data + "\n", True)
        



