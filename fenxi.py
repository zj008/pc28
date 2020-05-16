from lib.get import get
from lib.parse import Parser
from conn import Sql
import time

big_url = [
    "http://www.28fenxi.com/index.php?s=pc28yc&type=2&i=1",
    "http://www.28fenxi.com/index.php?s=pc28yc&type=2&i=2",
    "http://www.28fenxi.com/index.php?s=pc28yc&type=2&i=3",
    "http://www.28fenxi.com/index.php?s=pc28yc&type=2&i=4",
    "http://www.28fenxi.com/index.php?s=pc28yc&type=2&i=5",
    "http://www.28fenxi.com/index.php?s=pc28yc&type=2&i=6",
    "http://www.28fenxi.com/index.php?s=pc28yc&type=2&i=7",
    "http://www.28fenxi.com/index.php?s=pc28yc&type=2&i=8",
]

double_url = [
    "http://www.28fenxi.com/index.php?s=pc28yc&type=3&i=1",
    "http://www.28fenxi.com/index.php?s=pc28yc&type=3&i=2",
    "http://www.28fenxi.com/index.php?s=pc28yc&type=3&i=3",
    "http://www.28fenxi.com/index.php?s=pc28yc&type=3&i=4",
    "http://www.28fenxi.com/index.php?s=pc28yc&type=3&i=5",
    "http://www.28fenxi.com/index.php?s=pc28yc&type=3&i=6",
    "http://www.28fenxi.com/index.php?s=pc28yc&type=3&i=7",
    "http://www.28fenxi.com/index.php?s=pc28yc&type=3&i=8",
]


# 13小 ， 14 大
def get_big(history):
    for index, url in enumerate(big_url, 1):
        ret = get(url)
        p = Parser(ret)
        p.parse_fenxi(history, index)
    for id in history.keys():
        c1 = 0
        for i in range(1, 8):
            c1 += 1 if history[id].get("alg" + str(i)) == "大" else 0
        print(c1)
        alg0big = "大" if c1 >= 4 else "小"
        history[id]["alg0"] = alg0big
        res = "大" if int(history[id].get("result").split("=")[-1]) >= 14 else "小"
        history[id]["res0"] = "对" if alg0big == res else "错"


def get_double(history):
    for index, url in enumerate(double_url, 1):
        ret = get(url)
        p = Parser(ret)
        p.parse_fenxi(history, index)
    for id in history.keys():
        c1 = 0
        for i in range(1, 8):
            c1 += 1 if history[id].get("alg" + str(i)) == "单" else 0
        print(c1)
        alg0double = "单" if c1 >= 4 else "双"
        history[id]["alg0"] = alg0double
        res = "单" if int(history[id].get("result").split("=")[-1]) % 2 else "双"
        history[id]["res0"] = "对" if alg0double == res else "错"


def get_history():
    # 大小历史数据
    history = dict()
    get_big(history)
    for k, v in history.items():
        item_fenxi = dict(table="fenxi", id=k, pub_time=v.pop("pub_time"), result=v.pop("result"))
        v["table"] = "fenxi_big"
        v["id"] = k
        item_fenxi_big = v
        sql = Sql()
        print(item_fenxi)
        print(item_fenxi_big)
        sql.save(item_fenxi)
        sql.save(item_fenxi_big)
        sql.close()

    # 单双历史数据
    history = dict()
    get_double(history)
    for k, v in history.items():
        item_fenxi = dict(table="fenxi", id=k, pub_time=v.pop("pub_time"), result=v.pop("result"))
        v["table"] = "fenxi_double"
        v["id"] = k
        item_fenxi_double = v
        sql = Sql()
        print(item_fenxi)
        print(item_fenxi_double)
        sql.save(item_fenxi_double)
        sql.close()


def parse_alg0double(data, is_now=False):
    c1 = 0
    for i in range(1, 8):
        c1 += 1 if data.get("alg" + str(i)) == "单" else 0
    print(c1)
    alg0double = "单" if c1 >= 4 else "双"
    data["alg0"] = alg0double
    if not is_now:
        res = "单" if int(data.get("result").split("=")[-1]) % 2 else "双"
        data["res0"] = "对" if alg0double == res else "错"


def parse_alg0big(data, is_now=False):
    c1 = 0
    for i in range(1, 8):
        if data.get("alg" + str(i)) == "大":
            c1 += 1
    alg0big = "大" if c1 >= 4 else "小"
    data["alg0"] = alg0big
    if not is_now:
        res = "大" if int(data.get("result").split("=")[-1]) >= 14 else "小"
        data["res0"] = "对" if alg0big == res else "错"


def get_now_big():
    history = dict()
    for index, url in enumerate(big_url, 1):
        ret = get(url)
        p = Parser(ret)
        try:
            p.parse_fenxi_now(history, index, "big")
        except Exception as e:
            print(e)
    parse_alg0big(history.get("now"), True)
    parse_alg0big(history.get("last"))
    sql = Sql()
    now = history.get("now")
    now_fenxi_item = dict(table="fenxi", id=now.get("id"))
    now["table"] = "fenxi_big"
    if not sql.is_exists(now):
        sql.save(now)
    if not sql.is_exists(now_fenxi_item):
        sql.save(now_fenxi_item)
    last = history.get("last")
    last_fenxi_item = dict(table="fenxi", id=last.get("id"), pub_time=last.pop("pub_time"), result=last.pop("result"))
    sql.update_fields(last_fenxi_item)
    last["table"] = "fenxi_big"
    sql.update_fields(last)
    sql.close()


def get_now_double():
    history = dict()
    for index, url in enumerate(double_url, 1):
        ret = get(url)
        p = Parser(ret)
        try:
            p.parse_fenxi_now(history, index, "double")
        except Exception as e:
            print(e)
    parse_alg0double(history.get("now"), True)
    parse_alg0double(history.get("last"))
    sql = Sql()
    now = history.get("now")
    now_fenxi_item = dict(table="fenxi", id=now.get("id"))
    now["table"] = "fenxi_double"
    if not sql.is_exists(now):
        sql.save(now)
    if not sql.is_exists(now_fenxi_item):
        sql.save(now_fenxi_item)
    last = history.get("last")
    last_fenxi_item = dict(table="fenxi", id=last.get("id"), pub_time=last.pop("pub_time"), result=last.pop("result"))
    sql.update_fields(last_fenxi_item)
    last["table"] = "fenxi_double"
    sql.update_fields(last)
    sql.close()


if __name__ == '__main__':
    try:
        get_history()
    except Exception as e:
        print(e)
        pass
    while 1:
        try:
            get_now_big()
            get_now_double()
        except Exception as e:
            print(e)
            time.sleep(20)
            continue
        print("----------")
        time.sleep(20)

