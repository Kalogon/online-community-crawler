from writer import Writer
from fourth import Setter
from multiprocessing import Pool
from datetime import date, timedelta, datetime
import time
import json
import csv
import pathlib

PATH = pathlib.Path(__file__, "../").resolve()

def finish_content(Syear, Smonth, Sday, Fyear, Fmonth, Fday, unique_number, selenium):
    length = 0
    first = ""
    start_lst = list()
    finish_lst = list()

    with open(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_list{unique_number}.csv", newline='') as csvfile:
        reader = csv.reader(csvfile)
        for i, line in enumerate(reader):
            length += 1
            if first == "":
                first = line[1]
                start_lst.append(i)
            else:
                if first != line[1]:
                    first = line[1]
                    start_lst.append(i)
                    finish_lst.append(i)
        finish_lst.append(length)

    final_lst = list()
    for i in range(len(start_lst)):
        final_lst.append((start_lst[i], finish_lst[i]))

    setter = Setter(Syear, Smonth, Sday, Fyear, Fmonth, Fday, unique_number, selenium)
    with Pool(processes=50) as pool:
        a = pool.map(setter.multi_wrapper, final_lst)

    log_dict = dict()
    for i in a:
        if str(i[2]) in log_dict:
            log_dict[str(i[2])]['total'] =  log_dict[str(i[2])]['total'] + i[0]
            log_dict[str(i[2])]['fail'] =  log_dict[str(i[2])]['fail'] + i[1]
        else:
            log_dict[str(i[2])] = {'total': i[0], 'fail': i[1]}
    return log_dict
    
