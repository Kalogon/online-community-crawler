from writer import Writer
from second import Setter
from multiprocessing import Pool
from datetime import date, timedelta, datetime
import time
import json
import csv
import pathlib

PATH = pathlib.Path(__file__, "../board_lst.csv").resolve()
PATH2 = pathlib.Path(__file__, "../setting/").resolve()

def total_statistic(Syear, Smonth, Sday, Fyear, Fmonth, Fday, unique_number, setting):
    length = 0
    first = ""
    start_lst = list()
    finish_lst = list()

    with open(PATH, newline='') as csvfile:
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

    setter = Setter(Syear, Smonth, Sday, Fyear, Fmonth, Fday, setting)
    with Pool(processes=50) as pool:
        a = pool.map(setter.multi_wrapper, final_lst)
    
    success_writer = Writer(f'{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_Statistic{unique_number}')
    merged_dict = dict()
    log_dict = dict()
    for i in a:
        for j in i[0]:
            success_writer.write_line(j)
        if setting:
            merged_dict = {**merged_dict, **i[1]}
        if str(i[4]) in log_dict:
            log_dict[str(i[4])]['total'] =  log_dict[str(i[4])]['total'] + i[2]
            log_dict[str(i[4])]['fail'] =  log_dict[str(i[4])]['fail'] + i[3]
        else:
            log_dict[str(i[4])] = {'total': i[2], 'fail': i[3]}
        
    success_writer.close()

    if setting:
        json_object = dict()
        json_object['last-modified'] = str(datetime.now().date())
        json_object['application'] = merged_dict
        with open(f"{PATH2}/setting{unique_number}.json", 'w', encoding='utf-8') as f:
            json.dump(json_object, f, ensure_ascii=False, indent=2)
    
    return log_dict