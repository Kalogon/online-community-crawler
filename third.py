from bs4 import BeautifulSoup
from time import sleep
from datetime import date, timedelta, datetime
from writer import Writer
import random
import re
import requests
import json
import csv
import pathlib
import time
import os
import chardet

PATH = pathlib.Path(__file__, "..").resolve()
PATH2 = pathlib.Path(__file__, "../setting/setting.json").resolve()
PATH3 = pathlib.Path(__file__, "../path.csv").resolve()


class Setter:
    def __init__(self, Syear, Smonth, Sday, Fyear, Fmonth, Fday, unique_number):
        self.unique_number = unique_number
        self.sleep_time = 2
        self.board_lst = list()
        with open(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_TStatistic.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                self.board_lst.append(line)
        self.start = date(Syear, Smonth, Sday)
        self.finish = date(Fyear, Fmonth, Fday)
        self.post_lst = list()
        with open(PATH2, "r", encoding='utf-8') as jsonfile:
            self.setting_dict = json.load(jsonfile)
        self.content_dict = dict()
        with open(PATH3, newline='', encoding='euc-kr') as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                if line[0] != 'site':
                    tmp_dict = dict()
                    tmp_dict['title'] = line[1]
                    tmp_dict['date'] = line[2]
                    tmp_dict['content'] = line[3]
                    tmp_dict['view'] = line[4]
                    tmp_dict['recommendation'] = line[5]
                    tmp_dict['comment'] = line[6]
                    tmp_dict['url-path'] = line[7]
                    tmp_dict['name'] = line[8]
                    self.content_dict[line[0]] = tmp_dict
        
    def request_url(self, url):
        coin = 7
        headers = {'User-Agent':'Mozilla/5.0'}
        while coin > 0:
            try:
                aa = requests.get(url, headers=headers)
                sleep(self.sleep_time  * random.uniform(0.7, 1.3))
                return aa
            except:
                sleep(self.sleep_time) 
            coin -= 1
        raise Exception("Too many tries")

    def multi_wrapper(self, args):
        self.get_posturl(*args)
        self.get_unique()
        return self.post_lst


    def parse_date (self,aa):
        a3 = aa.replace('분 전','').strip()
        a4 = aa.replace('시간 전', '').strip()
        a5 = aa.replace('일 전', '').strip()
        aaa = aa.split(' ')[0]
        a2 = aaa.replace(':', '')
        a1 = aaa.replace('.', '').replace('/', '').replace('-', '')
        if (a3 != aa) or (a4 != aa) or (a2 != aaa):
            return datetime.now().date()
        elif a5 != aa:
            return datetime.now().date()- timedelta(days=int(a5))
        else:
            if len(a1) == 8:
                return datetime.strptime(a1, '%Y%m%d').date()
            elif len(a1) == 6:
                return datetime.strptime('20'+a1, '%Y%m%d').date()
            elif len(a1) == 4:
                return datetime.strptime('2021'+a1, '%Y%m%d').date()
            else:
                return None

    def get_posturl(self, start, finish):
        fail_lst = list()
        board_lst = self.board_lst[start:finish]
        #print(f"{board_lst}, start: {start}, finish: {finish}")
        for cur, lst in enumerate(board_lst):
           # print(f"cur: {cur}, pid: {os.getpid()}, lst: {lst}, time: {datetime.now()}")
            try:
                tmp1 = self.setting_dict['application'][lst[0]][lst[1]]
                if tmp1['success']:
                    result = tmp1['format']
                    result2 = tmp1['date_path']
                    url_path = self.content_dict[lst[0]]['url-path']
                else:
                    continue
                url1 = result[0] + result[1] + result[2]
                page_num = int(lst[3])
                page_range = int(result[5])
                while(1):
                    html = self.request_url(url1 + str(page_num) + result[4])
                    soup = BeautifulSoup(html.content, 'html.parser')
                    date_result = soup.select(result2)
                    url_result = soup.select(url_path)
                    change_result = list()
                    dif = len(date_result) - len(url_result)
                    for (num, i) in enumerate(date_result):
                        if num >= dif:
                            aa = i.get('title')
                            if aa != None:
                                try:
                                    a1 = aa.split(' ')[0]
                                    change_result.append((datetime.strptime(a1, '%Y-%m-%d').date(), url_result[num - dif].get('href'), lst[1]))
                                except:
                                    aa = i.get_text().strip()
                                    date_output = self.parse_date(aa)
                                    if date_output != None:
                                        change_result.append((date_output, url_result[num - dif].get('href'), lst[1]))
                            else:
                                aa = i.get_text().strip()
                                date_output = self.parse_date(aa)
                                if date_output != None:
                                    change_result.append((date_output, url_result[num - dif].get('href'), lst[1]))
                    res, url_lst = self.judge_date(change_result, lst[0])
                    self.post_lst.extend(url_lst)
                    if res == -1:
                        #print(f"[current/total]: [{cur}/{len(board_lst)}], finish_page:{page_num}, Pid: {os.getpid()}")
                        break
                    page_num += page_range
                    
            except Exception as e:
                tmp_lst = list()
                tmp_lst.append(lst[1])
                tmp_lst.append(str(e))
                fail_lst.append(tmp_lst)

    def judge_date(self, lst, site):
        cnt = list()
        try:
            standard = lst[len(lst) - 1][0]
        except:
            return None, None
        if self.start > standard : res = -1
        elif self.finish < standard : return 1, cnt
        else: res = 0
        for i in lst:
            if self.start <= i[0] and i[0] <= self.finish:
                if i[1][:4] == 'http':
                    parsed = i[1]   
                else:
                    parsed = site + i[1]
                cnt.append((parsed, site, i[2]))
        return res, cnt

    def get_unique(self):
        self.post_lst = list(set(self.post_lst))

    @staticmethod
    def get_integer(p_string):
        length = len(p_string)
        place = -1
        for i in range(length):
            if p_string[i].isdigit():
                place = i
            else:
                break
        return int(p_string[:place + 1]), place + 1
    
