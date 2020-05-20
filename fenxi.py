from lib.get import get
from lib.parse import Parser
from conn import Sql
import time
import logging
import datetime
import json

loger = logging.getLogger(__name__)

big_url = [
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=2&i=1",
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=2&i=2",
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=2&i=3",
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=2&i=4",
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=2&i=5",
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=2&i=6",
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=2&i=7",
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=2&i=8",
]

double_url = [
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=3&i=1",
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=3&i=2",
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=3&i=3",
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=3&i=4",
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=3&i=5",
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=3&i=6",
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=3&i=7",
    "http://www.28fenxi.com/index.php?s=jnd28yc&type=3&i=8",
]


# 13小 ， 14 大
def get_big(history):
    for index, url in enumerate(big_url, 1):
        ret = get(url)
        if not ret:
            return
        p = Parser(ret)
        p.parse_fenxi(history, index)
    for id in history.keys():
        c1 = 0
        for i in range(1, 8):
            c1 += 1 if history[id].get("alg" + str(i)) == "大" else 0
        # print(c1)
        alg0big = "大" if c1 >= 4 else "小"
        history[id]["alg0"] = alg0big
        res = "大" if int(history[id].get("result").split("=")[-1]) >= 14 else "小"
        history[id]["res0"] = "对" if alg0big == res else "错"


def get_double(history):
    for index, url in enumerate(double_url, 1):
        ret = get(url)
        if not ret:
            return
        p = Parser(ret)
        p.parse_fenxi(history, index)
    for id in history.keys():
        c1 = 0
        for i in range(1, 8):
            c1 += 1 if history[id].get("alg" + str(i)) == "单" else 0
        # print(c1)
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
        # print(item_fenxi)
        # print(item_fenxi_big)
        # print("fenxi", item_fenxi)
        # print("big", item_fenxi_big)
        sql.save_or_update(item_fenxi)
        sql.save_or_update(item_fenxi_big)
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
        # print(item_fenxi)
        # print(item_fenxi_double)
        # print(item_fenxi_double)

        sql.save_or_update(item_fenxi_double)
        sql.close()


def parse_alg0double(data, is_now=False):
    c1 = 0
    for i in range(1, 8):
        c1 += 1 if data.get("alg" + str(i)) == "单" else 0
    # print(c1)
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
        if not ret:
            return
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
    parse_earn_now("big", last)
    last_fenxi_item = dict(table="fenxi", id=last.get("id"), pub_time=last.pop("pub_time"), result=last.pop("result"))
    sql.save_or_update(last_fenxi_item)
    last["table"] = "fenxi_big"
    loger.error(datetime.datetime.now().strftime("%Y-%m-%d %X") + "; fenxi_now:" + json.dumps(last, ensure_ascii=False))
    sql.save_or_update(last)
    sql.close()


def parse_earn_now(t, last):
    sql = Sql()
    ret = sql.execute(
        f"select res0, pet1, pet2, pet3, pet4 from fenxi_{t} where id = (select id from fenxi_{t} where id < {last.get('id')} order by id desc limit 1)")
    sql.close()
    res0, pet1, pet2, pet3, pet4 = ret[0][0]
    print(ret)
    print(res0)
    print(pet1)
    print(pet2)
    print(pet3)
    print(pet4)
    if pet1 is None or pet2 is None or pet3 is None or pet4 is None:
        pet1, pet2, pet3, pet4 = 100, 100, 100, 100
    res = last.get("result")
    if res0 == "对":
        last["pet1"] = 100
        last["pet2"] = 100
        last["pet3"] = 100
        last["pet4"] = 100
    elif res0 == "错":
        last["pet1"] = int(pet1) * 2 if int(pet1) < 800 else 0
        last["pet2"] = int(pet2) * 2 if int(pet2) < 1600 else 0
        last["pet3"] = int(pet3) * 2 if int(pet3) < 3200 else 0
        last["pet4"] = int(pet4) * 2 if int(pet4) < 6400 else 0

    if last.get("res0") == "对":
        num = res.split("=")[-1]
        if num.strip() == "13" or num.strip() == "14":
            last["gain1"] = last["pet1"] * 0.6
            last["gain2"] = last["pet2"] * 0.6
            last["gain3"] = last["pet3"] * 0.6
            last["gain4"] = last["pet4"] * 0.6
        else:
            last["gain1"] = last["pet1"]
            last["gain2"] = last["pet2"]
            last["gain3"] = last["pet3"]
            last["gain4"] = last["pet4"]
    elif last.get("res0") == "错":
        last["gain1"] = -int(last["pet1"])
        last["gain2"] = -int(last["pet2"])
        last["gain3"] = -int(last["pet3"])
        last["gain4"] = -int(last["pet4"])


def get_now_double():
    history = dict()
    for index, url in enumerate(double_url, 1):
        ret = get(url)
        p = Parser(ret)
        try:
            p.parse_fenxi_now(history, index, "double")
        except Exception as e:
            loger.error(e)
    parse_alg0double(history.get("now"), True)
    parse_alg0double(history.get("last"))
    sql = Sql()
    now = history.get("now")
    now_fenxi_item = dict(table="fenxi", id=now.get("id"))
    now["table"] = "fenxi_double"
    sql.save_or_update(now)
    sql.save_or_update(now_fenxi_item)
    last = history.get("last")
    parse_earn_now("double", last)
    last_fenxi_item = dict(table="fenxi", id=last.get("id"), pub_time=last.pop("pub_time"), result=last.pop("result"))
    sql.save_or_update(last_fenxi_item)
    last["table"] = "fenxi_double"
    loger.error(datetime.datetime.now().strftime("%Y-%m-%d %X") + "  double_now: " + json.dumps(last,ensure_ascii=False))
    sql.save_or_update(last)
    sql.close()


# 更新投注
def update_earn(t):
    sql = Sql()
    ret, err = sql.execute(f"""
    select a.id, a.result, b.res0
    from fenxi a 
    left join fenxi_{t} b
    on a.id = b.id
    where a.result != "" and b.res0 != ""
    """)
    if err != 0:
        print(err)
    sql.close()
    datas = []
    p = "对"
    for i, r in enumerate(ret, 0):
        # print(ret)
        num = r[1].split("=")[-1]

        if i == 0:
            last = dict(res0="对", pet1=100, pet2=100, pet3=100, pet4=100)
        else:
            last = datas[-1]
        item = dict(table=f"fenxi_{t}", id=r[0])
        if p == "对":
            item["pet1"], item["pet2"], item["pet3"], item["pet4"] = 100, 100, 100, 100
        elif p == "错":
            item["pet1"] = last.get("pet1") * 2 if last.get("pet1") < 800 else 0
            item["pet2"] = last.get("pet2") * 2 if last.get("pet2") < 1600 else 0
            item["pet3"] = last.get("pet3") * 2 if last.get("pet3") < 3200 else 0
            item["pet4"] = last.get("pet4") * 2 if last.get("pet4") < 6400 else 0
        if r[2] == "对":
            if num.strip() == "13" or num.strip() == "14":
                item["gain1"] = item.get("pet1") * 0.6
                item["gain2"] = item.get("pet2") * 0.6
                item["gain3"] = item.get("pet3") * 0.6
                item["gain4"] = item.get("pet4") * 0.6
            else:
                item["gain1"] = item.get("pet1")
                item["gain2"] = item.get("pet2")
                item["gain3"] = item.get("pet3")
                item["gain4"] = item.get("pet4")
        elif r[2] == "错":
            item["gain1"] = -int(item.get("pet1"))
            item["gain2"] = -int(item.get("pet2"))
            item["gain3"] = -int(item.get("pet3"))
            item["gain4"] = -int(item.get("pet4"))
        p = r[2]
        datas.append(item)
    sql = Sql()
    for d in datas:
        sql.update_fields(d)
    sql.close()


def update():
    try:
        # get_history()
        update_earn("big")
        update_earn("double")
    except:
        pass


if __name__ == '__main__':
    # try:
    #     get_history()
    # except Exception as e:
    #     print(e)
    # try:
    #     update_earn("big")
    # except:
    #     pass
    # try:
    #     update_earn("double")
    # except:
    #     pass
    while 1:
        try:
            get_now_big()
            get_now_double()
        except Exception as e:
            print(e)
            update()
            continue
        loger.error(datetime.datetime.now().strftime("%Y-%m-%d %X") + "next circle")
        time.sleep(20)