import requests
from requests.exceptions import ReadTimeout
from lib.get import get
from lxml import etree
import datetime
from conn import Sql
import time


jnd = [
    "https://www.pt008.com/jnd.php?type=1&i=1",
    "https://www.pt008.com/jnd.php?type=1&i=2",
    "https://www.pt008.com/jnd.php?type=1&i=3",
    "https://www.pt008.com/jnd.php?type=1&i=4",
    "https://www.pt008.com/jnd.php?type=1&i=5",
    "https://www.pt008.com/jnd.php?type=1&i=6",
    "https://www.pt008.com/jnd.php?type=1&i=7",
    "https://www.pt008.com/jnd.php?type=1&i=8",
]

def parseAll(text, type, no):
    html = etree.HTML(text)
    trs = html.xpath("//tbody//tr")
    for tr in trs:
        tds = tr.xpath("./td")
        item = dict(table="lottery")
        try:
            item["id"] = tds[0].xpath("./text()")[0]
            pre1 = tds[3].xpath("./span[1]/text()")[0]
            pre2 = tds[3].xpath("./span[2]/text()")[0]
            item[type + str(no) + "big"] = pre1
            item[type + str(no) + "double"] = pre2
        except Exception as e:
            print(e)
        try:
            item["pub_time"] = datetime.datetime.now().strftime("%Y:%m:%d") + tds[1].xpath("./text()")[0]
            item["result"] = tds[2].xpath("./text()")[0]
            item[f"res{no}"] = tds[4].xpath(".//text()")[0]
        except Exception as e:
            print(e)
        print(item)
        sql = Sql()
        if no == 1:
            sql.save(item)
        else:
            sql.update_fields(item)
        sql.close()


def parseOne(text, type, no):
    html = etree.HTML(text)
    trs = html.xpath("//tbody//tr")
    l = []
    for tr in trs[:2]:
        tds = tr.xpath("./td")
        item = dict()
        try:
            item["id"] = tds[0].xpath("./text()")[0]
            pre1 = tds[3].xpath("./span[1]/text()")[0]
            pre2 = tds[3].xpath("./span[2]/text()")[0]
            item[type + str(no) + "big"] = pre1
            item[type + str(no) + "double"] = pre2
        except Exception as e:
            print(e)
        try:
            item["pub_time"] = datetime.datetime.now().strftime("%Y:%m:%d") + tds[1].xpath("./text()")[0]
            item["result"] = tds[2].xpath("./text()")[0]
            item[f"res{no}"] = tds[4].xpath(".//text()")[0]
        except Exception as e:
            print(e)
        # print(item)
        l.append(item)
    return l

def get_jnd():
    # jnd28 历史数据
    for no, url in enumerate(jnd, 1):
        ret = get(url)
        parseAll(ret, "alg", no)

def get_dd():
    # dd 历史数据
    for no, url in enumerate(dd, 9):
        ret = get(url)
        parseAll(ret, "alg", no)

if __name__ == '__main__':
    try:
        get_jnd()
    except:
        pass
    while 1:
        try:
            l_item = dict(table="lottery")
            t_item = dict(table="lottery")
            for no, url in enumerate(jnd, 1):
                text = get(url)
                if not next:
                    continue
                try:
                    t, l = parseOne(text, "alg", no)
                except Exception as e:
                    print(e)
                    continue
                # print(t, l)
                for k, v in t.items():
                    t_item[k] = v
                for k, v in l.items():
                    l_item[k] = v
            sql = Sql()
            if sql.is_exists(t_item, "id"):
                sql.update_fields(t_item)
            else:
                sql.save(t_item)
            sql.update_fields(l_item)
            time.sleep(20)
        except:
            time.sleep(120)