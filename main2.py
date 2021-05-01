from writer import Writer
from third import Setter
from multiprocessing import Pool
from datetime import date, timedelta, datetime
import time
import json
import csv
import pathlib

PATH = pathlib.Path(__file__, "../").resolve()

def total_content(Syear, Smonth, Sday, Fyear, Fmonth, Fday, unique_number):
    length = 0
    first = ""
    start_lst = list()
    finish_lst = list()

    with open(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_TStatistic.csv", newline='') as csvfile:
        reader = csv.reader(csvfile)
        for i, line in enumerate(reader):
            length += 1
            if first == "":
                first = line[0]
                start_lst.append(i)
            else:
                if first != line[0]:
                    first = line[0]
                    start_lst.append(i)
                    finish_lst.append(i)
        finish_lst.append(length)

    final_lst = list()
    for i in range(len(start_lst)):
        dif = finish_lst[i] - start_lst[i]
        mine = dif // 10
        left = dif % 10
        start = start_lst[i] + mine * unique_number
        if left > unique_number:
            start += unique_number
        else:
            start += left
        if left > unique_number:
            mine += 1
        if mine != 0:
            final_lst.append((start, start + mine))

    setter = Setter(Syear, Smonth, Sday, Fyear, Fmonth, Fday, unique_number)
    with Pool(processes=50) as pool:
        a = pool.map(setter.multi_wrapper, final_lst)


    site_lst = list()
    for i in a:
        try:
            site = i[0][1].replace('/', '')
            site_lst.append(site)
            success_writer = Writer(f'{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_{site}url{unique_number}')
            for j in i:
                success_writer.write_line(j)
            success_writer.close()
        except:
            print(f"Fail {i}")
    writer = Writer(f'{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_check{unique_number}')
    writer.close()
    return site_lst