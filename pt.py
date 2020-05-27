from lib.get import get
from lib.parse import Parser
from conn import Sql
import time
from threading import Thread
import logging
import json

zuhe = [
    "https://www.pt008.com/jnd.php?type=1&i=1",
    "https://www.pt008.com/jnd.php?type=1&i=2",
    "https://www.pt008.com/jnd.php?type=1&i=3",
    "https://www.pt008.com/jnd.php?type=1&i=4",
    "https://www.pt008.com/jnd.php?type=1&i=5",
    "https://www.pt008.com/jnd.php?type=1&i=6",
    "https://www.pt008.com/jnd.php?type=1&i=7",
    "https://www.pt008.com/jnd.php?type=1&i=8",
]

big = [
    "https://www.pt008.com/jnd.php?type=2&i=1",
    "https://www.pt008.com/jnd.php?type=2&i=2",
    "https://www.pt008.com/jnd.php?type=2&i=3",
    "https://www.pt008.com/jnd.php?type=2&i=4",
    "https://www.pt008.com/jnd.php?type=2&i=5",
    "https://www.pt008.com/jnd.php?type=2&i=6",
    "https://www.pt008.com/jnd.php?type=2&i=7",
    "https://www.pt008.com/jnd.php?type=2&i=8",
]

double = [
    "https://www.pt008.com/jnd.php?type=3&i=1",
    "https://www.pt008.com/jnd.php?type=3&i=2",
    "https://www.pt008.com/jnd.php?type=3&i=3",
    "https://www.pt008.com/jnd.php?type=3&i=4",
    "https://www.pt008.com/jnd.php?type=3&i=5",
    "https://www.pt008.com/jnd.php?type=3&i=6",
    "https://www.pt008.com/jnd.php?type=3&i=7",
    "https://www.pt008.com/jnd.php?type=3&i=8",
]


def get_zuhe():
    item = dict(now=dict(table="pt_zuhe"), last=dict(table="pt_zuhe"))
    for no, url in enumerate(zuhe, 1):
        ret = get(url)
        if not ret:
            continue
        parser = Parser(ret)
        parser.parse_pt_zuhe(item, no)
    Parser.pt_pre(item)
    now = item.get("now")
    last = item.get("last")

    sql = Sql()
    ret = sql.get_pre("pt_zuhe", last.get("id"))
    Parser.parse_earn(last, ret)
    pt = dict(table="pt", id=last.get("id"), pub_time=last.pop("pub_time"), result=last.pop("result"))
    sql.save_or_update(pt)
    sql.save_or_update(now)
    sql.save_or_update(last)
    sql.close()


def get_big(t):
    item = dict(now=dict(table=f"pt_{t}"), last=dict(table=f"pt_{t}"))
    if t == "big":
        urls = big
    if t == "double":
        urls = double
    for no, url in enumerate(urls, 1):
        ret = get(url)
        if not ret:
            continue
        parser = Parser(ret)
        parser.parse_pt_big(item, no)
    Parser.pt_pre(item)
    now = item.get("now")
    last = item.get("last")

    sql = Sql()
    ret = sql.get_pre(f"pt_{t}", last.get("id"))
    Parser.parse_earn(last, ret)
    pt = dict(table="pt", id=last.get("id"), pub_time=last.pop("pub_time"), result=last.pop("result"))
    # sql.save_or_update(pt)
    logging.error(json.dumps(now, ensure_ascii=False))
    logging.error(json.dumps(last, ensure_ascii=False))
    sql.save_or_update(now)
    sql.save_or_update(last)
    sql.close()

def target_zuhe():
    while 1:
        try:
            get_zuhe()
        except Exception as e:
            logging.error(e)
        time.sleep(60)

def target_big():
    while 1:
        try:
            get_big("big")
        except Exception as e:
            logging.error(e)
        time.sleep(5)

def target_double():
    while 1:
        try:
            get_big("double")
        except Exception as e:
            logging.error(e)
        time.sleep(5)


if __name__ == '__main__':
    t = []
    target = Thread(target=target_zuhe)
    t.append(target)
    target = Thread(target=target_big)
    t.append(target)
    target = Thread(target=target_double)
    t.append(target)
    for tar in t:
        tar.start()
    for tar in t:
        tar.join()
