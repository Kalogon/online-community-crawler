from bs4 import BeautifulSoup
from time import sleep
from datetime import date, timedelta, datetime
from writer import Writer
import random
import requests
import csv
import pathlib
import os
import json

PATH = pathlib.Path(__file__, "../board_lst.csv").resolve()
PATH2 = pathlib.Path(__file__, "../setting/setting.json").resolve()


class Setter:
    def __init__(self, syear, smonth, sday, fyear, fmonth, fday, setting):
        self.sleep_time = 2
        self.board_lst = list()
        with open(PATH, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                self.board_lst.append(line[:2])
        self.start = date(syear, smonth, sday)
        self.finish = date(fyear, fmonth, fday)

        self.setting = setting
        self.setting_lst = dict()
        self.current = None
        self.total_lst = dict()
        if not setting:
            with open(PATH2, "r") as jsonfile:
                self.setting_dict = json.load(jsonfile)

    def request_url(self, url):
        coin = 7
        headers = {'User-Agent': 'Mozilla/5.0'}
        while coin > 0:
            try:
                sleep(self.sleep_time * random.uniform(0.7, 1.3))
                aa = requests.get(url, headers=headers)
                return aa
            except:
                sleep(self.sleep_time)
            coin -= 1
        raise Exception("Too many tries")

    def multi_wrapper(self, args):
        return self.get_statistic(*args)

    def parse_date(self, aa):
        a3 = aa.replace('분 전', '').strip()
        a4 = aa.replace('시간 전', '').strip()
        a5 = aa.replace('일 전', '').strip()
        aaa = aa.split(' ')[0]
        a2 = aaa.replace(':', '')
        a1 = aaa.replace('.', '').replace('/', '').replace('-', '')
        if (a3 != aa) or (a4 != aa) or (a2 != aaa):
            return datetime.now().date()
        elif a5 != aa:
            return datetime.now().date() - timedelta(days=int(a5))
        else:
            if len(a1) == 8:
                return datetime.strptime(a1, '%Y%m%d').date()
            elif len(a1) == 6:
                return datetime.strptime('20'+a1, '%Y%m%d').date()
            elif len(a1) == 4:
                return datetime.strptime('2021'+a1, '%Y%m%d').date()
            else:
                return None

    def indate(self, date):
        if self.start > date:
            return 1
        elif self.start <= date and date <= self.finish:
            return 2
        else:
            return 3

    def page_fail(self, board, reason):
        tmp_dict2 = dict()
        tmp_dict2["success"] = False
        tmp_dict2["reason"] = reason
        self.setting_lst[str(board)] = tmp_dict2

    def page_success(self, board, lst, path):
        tmp_dict2 = dict()
        tmp_dict2["success"] = True
        tmp_dict2["date_path"] = path
        tmp_dict2["format"] = lst
        self.setting_lst[str(board)] = tmp_dict2

    def page_statistic(self, url_lst, path):
        res = self.request_url(
            url_lst[0] + url_lst[1] + url_lst[2] + str(url_lst[3]) + url_lst[4])
        soup = BeautifulSoup(res.content, 'html.parser')
        date_result = soup.select(path)
        change_result = list()
        for i in date_result:
            aa = i.get('title')
            if aa != None:
                try:
                    a1 = aa.split(' ')[0]
                    change_result.append(
                        datetime.strptime(a1, '%Y-%m-%d').date())
                except:
                    aa = i.get_text().strip()
                    date_output = self.parse_date(aa)
                    if date_output != None:
                        change_result.append(date_output)
            else:
                aa = i.get_text().strip()
                date_output = self.parse_date(aa)
                if date_output != None:
                    change_result.append(date_output)
        if len(change_result) == 0:
            return -1
        res, cnt = self.judge_date(change_result)
        if res == None:
            return -2
        return cnt

    def get_pagenum(self, url_lst, date_path, front):
        i1 = url_lst[0]
        i2 = url_lst[1]
        i4 = url_lst[4]
        page_range = url_lst[5]
        standard = url_lst[2]
        front_page = url_lst[3]
        initial_page = url_lst[3]
        back_page = url_lst[3] + 10000 * page_range
        page_num = url_lst[3]
        rng = 1
        check = False
        while (rng):
            url = i1 + i2 + standard + str(page_num) + i4
            right_page = False
            if page_num > 10000000:
                return -1
            res = self.request_url(url)
            soup = BeautifulSoup(res.content, 'html.parser')
            for tag in soup.find_all():
                if tag.name == '[document]':
                    break
                if tag.name == 'a':
                    tmp = tag.get('href')
                    try:
                        if standard in tmp:
                            xx = tmp.split(standard)
                            if xx[0][:4] == 'java':
                                continue
                            num, _ = self.get_integer(xx[1])
                            if num == page_num:
                                right_page = True
                                break
                    except:
                        pass
            if right_page:
                date_result = soup.select(date_path)
                change_result = list()
                for i in date_result:
                    aa = i.get('title')
                    if aa != None:
                        try:
                            a1 = aa.split(' ')[0]
                            change_result.append(
                                datetime.strptime(a1, '%Y-%m-%d').date())
                        except:
                            aa = i.get_text().strip()
                            date_output = self.parse_date(aa)
                            if date_output != None:
                                change_result.append(date_output)
                    else:
                        aa = i.get_text().strip()
                        date_output = self.parse_date(aa)
                        if date_output != None:
                            change_result.append(date_output)
                if len(change_result) == 0:
                    back_page = page_num
                    rng = (back_page - front_page) // (2 * page_range)
                    page_num -= (rng * page_range)
                    if not check:
                        check = True
                else:
                    dd = self.indate(change_result[-1])
                    if front:
                        if dd == 3:
                            front_page = page_num
                            if check:
                                rng = (back_page -
                                       front_page) // (2 * page_range)
                            else:
                                rng *= 2
                            page_num += (rng * page_range)
                        else:
                            back_page = page_num
                            rng = (back_page - front_page)//(2 * page_range)
                            page_num -= (rng * page_range)
                            if not check:
                                check = True
                    else:
                        if dd == 1:
                            back_page = page_num
                            rng = (back_page - front_page)//(2 * page_range)
                            page_num -= (rng * page_range)
                            if not check:
                                check = True
                        else:
                            front_page = page_num
                            if check:
                                rng = (back_page -
                                       front_page) // (2 * page_range)
                            else:
                                rng *= 2
                            page_num += (rng * page_range)
            else:
                back_page = page_num
                rng = (back_page - front_page)//(2 * page_range)
                page_num -= (rng * page_range)
                if not check:
                    check = True
        if front and front_page != url_lst[3]:
            return front_page + 1
        if front:
            return front_page
        else:
            return back_page

    def get_statistic(self, start, finish):
        statistic_lst = list()
        board_lst = self.board_lst[start:finish]
        fail_cnt = 0
        # print(f"start: {start}, finish: {finish}, pid: {os.getpid()}")
        for cur, lst in enumerate(board_lst):
            # print(f"cur: {cur}, pid: {os.getpid()}, lst: {lst}, time: {datetime.now()}")
            try:
                if self.setting:
                    if self.current == None:
                        self.current = lst[0]

                    if self.current != lst[0]:
                        self.total_lst[self.current] = self.setting_lst
                        self.current = lst[0]
                        self.setting_lst = dict()

                    result = self.get_URLformat(lst)

                    if result == None:
                        self.page_fail(lst[1], 'fail to find page')
                        fail_cnt += 1
                        continue

                    initial_page = result[3]
                    page_range = result[5]

                    result2 = self.get_postpath(
                        result[0] + result[1] + result[2] + str(result[3]) + result[4])

                    if result2 == None:
                        self.page_fail(lst[1], 'fail to find post path')
                        fail_cnt += 1
                        continue
                else:
                    tmp1 = self.setting_dict['application'][lst[0]][lst[1]]
                    if tmp1['success']:
                        result = tmp1['format']
                        result2 = tmp1['date_path']
                        page_range = result[5]
                    else:
                        fail_cnt += 1
                        continue

                start_page = self.get_pagenum(result, result2, True)
                result[3] = start_page
                back_page = self.get_pagenum(result, result2, False)
                if (start_page == -1) or (back_page == -1):
                    if self.setting:
                        self.page_fail(lst[1], 'too many page number')
                    fail_cnt += 1
                    continue

                if start_page == back_page:
                    pair = (lst[0], lst[1], 0, start_page)
                    statistic_lst.append(pair)

                else:
                    cnt1 = self.page_statistic(result, result2)
                    result[3] = back_page + page_range
                    cnt2 = self.page_statistic(result, result2)
                    if (cnt1 < 0) or (cnt2 < 0):
                        fail_cnt += 1
                        if (cnt1 == -1) or (cnt2 == -1):
                            if self.setting:
                                self.page_fail(lst[1], 'wrong date format')
                        else:
                            if self.setting:
                                self.page_fail(lst[1], 'fail to judge')
                        continue

                    total_cnt = cnt1 + cnt2
                    if start_page != back_page:
                        result[3] = back_page - page_range
                        cnt = self.page_statistic(result, result2)
                        total_cnt += cnt * \
                            ((back_page - start_page - page_range) // page_range)
                    pair = (lst[0], lst[1], total_cnt //
                            ((self.finish - self.start).days + 1), start_page)
                    statistic_lst.append(pair)
                if self.setting:
                    result[3] = initial_page
                    self.page_success(lst[1], result, result2)
                print(
                    f"[current/total]: [{cur + 1}/{len(board_lst)}], finish_page:{back_page}, Pid: {os.getpid()}")
            except Exception as e:
                if self.setting:
                    self.page_fail(lst[1], str(e))
                fail_cnt += 1
        if self.setting:
            self.total_lst[str(self.current)] = self.setting_lst
        return statistic_lst, self.total_lst, finish - start + 1, fail_cnt, self.current

    def judge_date(self, lst):
        cnt = 0
        try:
            standard = lst[len(lst) - 1]
        except:
            return None, None
        if self.start > standard:
            res = -1
        elif self.finish < standard:
            return 1, 0
        else:
            res = 0
        for i in lst:
            if self.start <= i and i <= self.finish:
                cnt += 1
        return res, cnt

    def get_URLformat(self, lst):
        site_url = lst[0]
        board_url = lst[1]
        res = self.request_url(board_url)
        soup = BeautifulSoup(res.content, 'html.parser')
        tmp_lst = dict()
        num_lst = dict()
        standard = ""
        for (i, tag) in enumerate(soup.find_all()):
            if tag.name == '[document]':
                break
            if tag.name == 'a':
                tmp = tag.get('href')
                try:
                    if 'page=' in tmp:
                        xx = tmp.split('page=')
                        if xx[0][:4] == 'java':
                            continue
                        standard = 'page='
                        num, place = self.get_integer(xx[1])
                        if place == len(xx[1]):
                            add_url = ""
                        else:
                            add_url = xx[1][place:]
                        tmp_url = xx[0] + 'page=' + add_url
                        if num in num_lst:
                            num_lst[num] += 1
                        else:
                            num_lst[num] = 1

                        if tmp_url in tmp_lst:
                            tmp_lst[tmp_url] += 1

                        else:
                            tmp_lst[tmp_url] = 1
                    elif 'p=' in tmp:
                        xx = tmp.split('p=')
                        if xx[0][:4] == 'java':
                            continue
                        standard = 'p='
                        num, place = self.get_integer(xx[1])
                        if place == len(xx[1]):
                            add_url = ""
                        else:
                            add_url = xx[1][place:]
                        tmp_url = xx[0] + 'p=' + add_url
                        if num in num_lst:
                            num_lst[num] += 1
                        else:
                            num_lst[num] = 1

                        if tmp_url in tmp_lst:
                            tmp_lst[tmp_url] += 1

                        else:
                            tmp_lst[tmp_url] = 1
                except:
                    pass
        if len(tmp_lst) == 0:
            return None

        cnt = 0
        form = str()
        for i in tmp_lst:
            if tmp_lst[i] > cnt:
                form = i
                cnt = tmp_lst[i]
        form = form.replace('¬', '&not')
        fst = ""
        snd = ""
        for i in num_lst:
            if num_lst[i] <= 2:
                if i != 0:
                    if fst == "":
                        fst = i
                    elif snd == "":
                        snd = i
                        break

        page_range = snd - fst
        initial_page = fst - page_range

        aa = form.split(standard)
        add_url = aa[1]

        if aa[0][:4] == 'http':
            site_url = ""
        elif aa[0][:1] == '.':
            aa[0] = aa[0][1:]
            site_url = board_url.split(aa[0][:-1])[0]
        elif aa[0][:1] != '/':
            site_url += '/'
        if standard == 'page=':
            url_format = "{i1}{i2}page={i3}{i4}"
        elif standard == 'p=':
            url_format = "{i1}{i2}p={i3}{i4}"
        page_num = initial_page
        return [site_url, aa[0], standard, page_num, add_url, page_range]

    def get_postpath(self, url):
        res = self.request_url(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        total_lst = list()
        for tag in soup.find_all():
            if tag.name == '[document]':
                break
            if len(total_lst) != 0:
                break
            aa = tag.get('class')
            if aa != None:
                for cname in aa:
                    if 'date' in cname:
                        k = tag
                        asdf = k.get_text().strip().replace('분 전', '').replace('시간 전', '').replace(
                            '일 전', '').replace(':', '').replace('.', '').replace('/', '').replace('-', '')
                        if k.get_text().strip() == asdf:
                            continue
                        if len(k.get_text().strip()) > 30:
                            continue
                        try:
                            while k.name != 'body':
                                total_lst.insert(0, str(k.name))
                                k = k.parent
                            class_name = aa
                            break
                        except:
                            continue
        if len(total_lst) == 0:
            for tag in soup.find_all():
                if tag.name == '[document]':
                    break
                if len(total_lst) != 0:
                    break
                aa = tag.get('class')
                if aa != None:
                    for cname in aa:
                        if 'time' in cname:
                            k = tag
                            asdf = k.get_text().strip().replace('분 전', '').replace('시간 전', '').replace(
                                '일 전', '').replace(':', '').replace('.', '').replace('/', '').replace('-', '')
                            if k.get_text().strip() == asdf:
                                continue
                            if len(k.get_text().strip()) > 30:
                                continue
                            try:
                                while k.name != 'body':
                                    total_lst.insert(0, str(k.name))
                                    k = k.parent
                                class_name = aa
                                break
                            except:
                                continue
        if len(total_lst) == 0:
            return None

        length = len(total_lst)
        a = str()
        for i, v in enumerate(total_lst):
            a += v
            if v == 'a':
                b = i + 1
            if i != length - 1:
                a += '>'
        for i in class_name:
            a += '.'
            a += i
        return (a)

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
