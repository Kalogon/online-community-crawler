import sys, requests,json, os, csv, pathlib
from datetime import date, timedelta, datetime
from main import total_statistic
from main2 import total_content
from main3 import finish_content
from time import sleep
from split import split
from merge import merge
from merge_log import merge_log


PATH = pathlib.Path(__file__, "../../setting/setting_number.json").resolve()
PATH2 = pathlib.Path(__file__, "..").resolve()

if __name__ == "__main__":

    with open(PATH, "r") as jsonfile:
        one_line = json.load(jsonfile)
        unique_number = int(one_line['unique-number'])

    # if len(sys.argv) == 10:
    #     Syear = int(sys.argv[1])
    #     Smonth = int(sys.argv[2])
    #     Sday = int(sys.argv[3])
    #     Fyear = int(sys.argv[4])
    #     Fmonth = int(sys.argv[5])
    #     Fday = int(sys.argv[6])
    #     setting = int(sys.argv[7])
    #     threshold = int(sys.argv[8])
    #     selenium = int(sys.argv[9])
    # else:
    #     a = datetime.now() - timedelta(days = 1)
    #     if unique_number == 9:
    #         a = a + timedelta(hours = 9)
    #     Syear = int(a.date().year)
    #     Fyear = int(a.date().year)
    #     Smonth = int(a.date().month)
    #     Fmonth = int(a.date().month)
    #     Sday = int(a.date().day)
    #     Fday = int(a.date().day)
    #     if a.weekday() == 0:
    #         setting = 1
    #     else:
    #         setting = 0
    #     threshold = 1000
    #     selenium = 0
    Syear = 2020
    Smonth = 5
    Sday = 15
    Fyear = 2020
    Fmonth = 5
    Fday = 21
    setting = 0
    threshold = 1000
    selenium = 0

    time1 = datetime.now()
    statistic_log = total_statistic(Syear, Smonth, Sday, Fyear, Fmonth, Fday, unique_number, setting)
    print(f"unique_num {unique_number} finish to get statistic")
    time2 = datetime.now()
    if unique_number == 9:
        length = 0
        while (length != 10):
            length = 0
            for i in range(0,10):
                if os.path.isfile(f"{PATH2}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_Statistic{i}.csv"):
                    length += 1
            sleep(60)
        print(f"start split")
        split(Syear, Smonth, Sday, Fyear, Fmonth, Fday, threshold, setting)
    else:
        check = os.path.isfile(f"{PATH2}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_Statistic.csv")
        while (not check):
            check = os.path.isfile(f"{PATH2}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_Statistic.csv")
            sleep(60)
    print(f"finish to split")
    time3 = datetime.now()
    total_content(Syear, Smonth, Sday, Fyear, Fmonth, Fday, unique_number)
    print(f"unique_num {unique_number} finish to get url")
    time4 = datetime.now()
    if unique_number == 9:
        length = 0
        while (length != 10):
            length = 0
            for i in range(0,10):
                if os.path.isfile(f"{PATH2}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_check{i}.csv"):
                    length += 1
            sleep(60)
        merge(Syear, Smonth, Sday, Fyear, Fmonth, Fday)
    else:
        check = os.path.isfile(f"{PATH2}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_check.csv")
        while (not check):
            check = os.path.isfile(f"{PATH2}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_check.csv")
            sleep(60)
    print(f"finish to merge")
    time5 = datetime.now()
    content_log = finish_content(Syear, Smonth, Sday, Fyear, Fmonth, Fday, unique_number, selenium)
    time6 = datetime.now()

    total_log = dict()
    total_log['statistic'] = statistic_log
    total_log['content'] = content_log

    with open(f"{PATH2}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_log{unique_number}.json", 'w', encoding='utf-8') as f:
        json.dump(total_log, f, ensure_ascii=False, indent=2)

    if unique_number == 9:
        length = 0
        while (length != 10):
            length = 0
            for i in range(0,10):
                if os.path.isfile(f"{PATH2}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_log{i}.json"):
                    length += 1
            sleep(60)
        merge_log(Syear, Smonth, Sday, Fyear, Fmonth, Fday)

    if unique_number == 0:
        if os.path.isfile(f"{PATH2}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_check.csv"):
            os.remove(f"{PATH2}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_check.csv")
        for j in range(10):
            if os.path.isfile(f"{PATH2}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_list{j}.csv"):
                os.remove(f"{PATH2}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_list{j}.csv")


    print(f"{time1}, {time2}, {time3}, {time4}, {time5}, {time6}")
    print(f"Statistic take {time2 - time1}")
    print(f"Get URL take {time4 - time3}")
    print(f"Get content take {time6 - time5}")
    





    

    
    
