from datetime import date, timedelta, datetime
from writer import Writer
import time
import json
import csv
import pathlib
import os

PATH = pathlib.Path(__file__, "..").resolve()
except_lst = ['https://arca.live/b/breaking', 'https://tdgall.com/?best=10', 'https://www.ddanzi.com/new_all', 'https://hygall.com/?best=10']

def split(Syear, Smonth, Sday, Fyear, Fmonth, Fday, threshold, setting):
    total_lst = list()
    target_lst = dict()
    startTime = datetime.now()

    if setting:
        total_dict = dict()
        for i in range(0, 10):
            with open(f"{PATH}/setting/setting{i}.json","r", encoding='utf-8') as csvfile:
                tmp_dict = json.load(csvfile)
                if i == 0:
                    total_dict = tmp_dict
                else:
                    for j in tmp_dict['application'].keys():
                        for k in tmp_dict['application'][j].keys():
                            total_dict['application'][j][k] = tmp_dict['application'][j][k]
            os.remove(f"{PATH}/setting/setting{i}.json")
        with open(f"{PATH}/setting/setting.json", 'w', encoding='utf-8') as f:
            json.dump(total_dict, f, ensure_ascii=False, indent=2)
        del total_dict

    for i in range(0, 10):
        with open(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_Statistic{i}.csv", newline='') as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                if (int(line[2]) >= int(threshold)) and (line[1] not in except_lst):
                    site = line[0]
                    if site in target_lst:
                        key_lst = target_lst[site]
                        key_lst.append(line)
                        target_lst[site] = key_lst
                    else:
                        target_lst[site] = [line]
                total_lst.append(line)

        os.remove(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_Statistic{i}.csv")

    writer = Writer(f'{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_Statistic')
    for i in total_lst:
        writer.write_line(i)
    writer.close()

    writer = Writer(f'{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_TStatistic')
    for i in target_lst:
        for j in target_lst[i]:
            writer.write_line(j)
    writer.close()
    endTime = datetime.now()
