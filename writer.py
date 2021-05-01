import csv
import os
import pathlib
import platform
PATH = pathlib.Path(__file__, "../").resolve()

class Writer:
    def __init__(self, fname):
        self.csv = None
        self.fname = fname
        self.initialize()  
        self.writer = csv.writer(self.csv)

    #Setting directory and open scv file
    def initialize(self):
        if not(os.path.exists(PATH)):
            os.mkdir(PATH)
        filename = f"{self.fname}.csv"

        if os.path.isfile(f"{PATH}/{filename}"):
            raise Exception('File already exist')
        user_os = str(platform.system())
        if user_os == "Windows":
            self.csv = open(f"{PATH}/{filename}",'wt', encoding='euc-kr',newline='')
        else:
            self.csv = open(f"{PATH}/{filename}",'wt', encoding='utf-8',newline='')
    
    def write_line(self, arg):
        self.writer.writerow(arg)

    def close(self):
        self.csv.close()
