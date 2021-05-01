from datetime import date, timedelta, datetime
from writer import Writer
import time
import json
import csv
import pathlib
import os

PATH = pathlib.Path(__file__, "..").resolve()


def merge(Syear, Smonth, Sday, Fyear, Fmonth, Fday):
    total_lst = dict()
    startTime = datetime.now()
    site_lst = list()
    with open(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_TStatistic.csv", newline='') as csvfile:
        reader = csv.reader(csvfile)
        for line in reader:
            if line[0] not in site_lst:
                site_lst.append(line[0])

    for num, i in enumerate(site_lst):
        site_lst[num] = i.replace('/','')

    print(f"site list is {site_lst}")

    for i in site_lst:
        site_list = list()
        for j in range(0, 10):
            tmp_list = list()
            if os.path.isfile(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_{i}url{j}.csv"):
                with open(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_{i}url{j}.csv", newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    for line in reader:
                        tmp_list.append(line)
                site_list.extend(tmp_list)
                os.remove(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_{i}url{j}.csv")
        total_lst[i] = site_list

    print(f"total list length is {len(total_lst)}")

    for i in range(0,10):
        tmp_list = list()
        for j in total_lst:
            dif = len(total_lst[j])
            mine = dif // 10
            left = dif % 10
            start = mine * i
            if left > i:
                start += i
            else:
                start += left
            if left > i:
                mine += 1
            if mine != 0:
                tmp_list.extend(total_lst[j][start: start + mine])
        
        writer = Writer(f'{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_list{i}')
        for k in tmp_list:
            writer.write_line(k)
        writer.close()

    for i in range(0,10):
        os.remove(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_check{i}.csv")

    writer = Writer(f'{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_check')
    for i in total_lst:
        writer.write_line(i)
    writer.close()
    endTime = datetime.now()

