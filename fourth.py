from bs4 import BeautifulSoup
from time import sleep
from datetime import date, timedelta, datetime
from selenium import webdriver
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
PATH3 = pathlib.Path(__file__, "../path.csv").resolve()


class Setter:
    def __init__(self, Syear, Smonth, Sday, Fyear, Fmonth, Fday, unique_number, selenium):
        self.unique_number = unique_number
        self.sleep_time = 2
        self.site = str()
        self.board_lst = list()
        with open(f"{PATH}/{Syear}{Smonth}{Sday}_{Fyear}{Fmonth}{Fday}_list{unique_number}.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                self.board_lst.append(line)
        self.start = date(Syear, Smonth, Sday)
        self.finish = date(Fyear, Fmonth, Fday)
        self.content_lst = list()
        self.content_dict = dict()
        #self.selenium = selenium
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
                    tmp_dict['comment_list'] = line[9]
                    self.content_dict[line[0]] = tmp_dict
        '''
        if selenium:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('user-agent=Mozilla/5.0')
            self.driver = webdriver.Chrome('/home/seunghwan/NFS/chromedriver', chrome_options=options)'''

        
    def request_url(self, url):
        coin = 7
        headers = {'User-Agent':'Mozilla/5.0'}
        while coin > 0:
            try:
                '''
                if self.selenium:
                    self.driver.get(url)
                    sleep(self.sleep_time  * random.uniform(0.8, 1.2))
                    html = self.driver.page_source
                    return html
                else:
                    aa = requests.get(url, headers=headers)
                    sleep(self.sleep_time  * random.uniform(0.7, 1.3))
                    return aa'''
                aa = requests.get(url, headers=headers)
                sleep(self.sleep_time  * random.uniform(0.7, 1.3))
                return aa
            except:
                sleep(self.sleep_time) 
            coin -= 1
        raise Exception("Too many tries")

    def multi_wrapper(self, args):
        return self.get_result(*args)

    def get_result(self, start, finish):
        post_lst = self.board_lst[start:finish]
        self.site = post_lst[0][1]
        fail_cnt = 0
        for num2, i in enumerate(post_lst):
            try:
                res = self.request_url(i[0])
                '''
                if self.selenium:
                    soup = BeautifulSoup(res, 'html.parser')
                else:
                    soup = BeautifulSoup(res.content, 'html.parser')'''
                soup = BeautifulSoup(res.content, 'html.parser')
                json_object = dict()
                json_object['site'] = self.content_dict[self.site]['name']
                json_object['board'] = i[2]
                json_object['title'] = self.parse_path(soup, self.content_dict[self.site]['title'], 0)
                date_string = self.parse_path(soup, self.content_dict[self.site]['date'], 0).split(' ')
                date = date_string[0].replace('.', '-').replace('/', '-')
                time = date_string[1]
                for number, j in enumerate(time):
                    if j.isdigit():
                        num = number
                        break
                time = time[num : num + 5]
                json_object['date'] = date
                json_object['time'] = time
                json_object['content'] = self.parse_path(soup, self.content_dict[self.site]['content'], 0)
                json_object['view'] = self.parse_path(soup, self.content_dict[self.site]['view'], 0)
                json_object['recommendation'] = self.parse_path(soup, self.content_dict[self.site]['recommendation'], 0)
                json_object['comments'] = self.parse_path(soup, self.content_dict[self.site]['comment'], 0)
                '''
                if self.selenium:
                    json_object['comment_list'] =  self.parse_path(soup, self.content_dict[self.site]['comment_list'], 1)'''
                self.content_lst.append(json_object)
            except:
                fail_cnt += 1
                print(f"fail {i}, ")
            print(f"[current/total]: [{num2}/{len(post_lst)}]")
        #self.driver.quit()
        
        json_object = dict()
        json_object['last-modified'] = str(datetime.now().date())
        json_object['application'] = self.content_lst
        with open(f"{PATH}/{self.start}_{self.finish}_{self.content_dict[self.site]['name']}{self.unique_number}.json", 'w', encoding='utf-8') as f:
            json.dump(json_object, f, ensure_ascii=False, indent=2)
        return len(post_lst), fail_cnt, self.site
        

    def parse_path(self, soup, path, comment):
        try:
            if path == 'None':
                return None
            b = path.split(';')
            if comment:
                cmt_list = list()
                content = soup.select(b[0])
                for k in content:
                    if len(b) == 1:
                        cmt_list.append(k.get_text())
                        continue
                    num = 1
                    while len(b) - num >= 1:
                        order = b[num].split(' ')[0]
                        if order == 'find':
                            for number, i in enumerate(k):
                                if number == int(b[num].split(' ')[1]):
                                    k = i.strip()
                        elif order == 'split':
                            try:
                                k = k.get_text().strip()
                            except:
                                pass
                            k = k.split(' ')[int(b[num].split(' ')[1])].strip()
                        elif order == 'delete':
                            try:
                                k = k.get_text()
                            except:
                                pass
                            min_value = 10000
                            max_value = -1
                            for number, i in enumerate(k):
                                if i.isdigit():
                                    if number < min_value:
                                        min_value = number
                                    if number > max_value:
                                        max_value = number
                            k = k[min_value: max_value+1]
                        num += 1
                    cmt_list.append(k)
                return cmt_list
            else:
                content = soup.select(b[0])[0]
                if len(b) == 1:
                    return content.get_text()
                num = 1
                while len(b) - num >= 1:
                    order = b[num].split(' ')[0]
                    if order == 'find':
                        for number, i in enumerate(content):
                            if number == int(b[num].split(' ')[1]):
                                content = i.strip()
                    elif order == 'split':
                        try:
                            content = content.get_text().strip()
                        except:
                            pass
                        content = content.split(' ')[int(b[num].split(' ')[1])].strip()
                    elif order == 'delete':
                        try:
                            content = content.get_text()
                        except:
                            pass
                        min_value = 10000
                        max_value = -1
                        for number, i in enumerate(content):
                            if i.isdigit():
                                if number < min_value:
                                    min_value = number
                                if number > max_value:
                                    max_value = number
                        content = content[min_value: max_value+1]
                    num += 1
                return content
        except:
            return None
        
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
