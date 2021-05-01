from datetime import date, timedelta, datetime
from writer import Writer
import time
import json
import csv
import pathlib
import os

PATH = pathlib.Path(__file__, "..").resolve()


def merge_log(Syear, Smonth, Sday, Fyear, Fmonth, Fday):
    total_dict = dict()
    for j in range(0, 10):
        if os.path.isfile(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_log{j}.json"):
            with open(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_log{j}.json", "r", encoding='utf-8') as jsonfile:
                setting_dict = json.load(jsonfile)

            if j == 0:
                total_dict = setting_dict
            else:
                statistic = setting_dict['statistic']
                content = setting_dict['content']
                for k in statistic:
                    total_dict['statistic'][k]['total'] += statistic[k]['total']
                    total_dict['statistic'][k]['fail'] += statistic[k]['fail']
                for k in content:
                    total_dict['content'][k]['total'] += content[k]['total']
                    total_dict['content'][k]['fail'] += content[k]['fail']
            os.remove(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_log{j}.json")
    with open(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_log.json", 'w', encoding='utf-8') as f:
        json.dump(total_dict, f, ensure_ascii=False, indent=2)
    del total_dict
        