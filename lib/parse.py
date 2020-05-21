from lxml import etree
from lib.error import IdChangeError
import logging
import datetime


class Parser():
    def __init__(self, text):
        self.html = etree.HTML(text)

    def parse_fenxi(self, history, index):
        trs = self.html.xpath("//tbody/tr")
        for tr in trs[1:]:
            try:
                id = tr.xpath("./td[1]/text()")[0]
                pub_time = tr.xpath("./td[2]/text()")
                result = tr.xpath("./td[3]/text()")
                pre = tr.xpath("./td[4]/span/text()")
                res = tr.xpath("./td[5]/span/text()")
                if not history.get(id):
                    history[id] = dict()
                    history[id]["pub_time"] = pub_time[0]
                    history[id]["result"] = result[0]
                history[id]["alg" + str(index)] = pre[0]
                history[id]["res" + str(index)] = "对" if res[0] == "中" else "错"
            except Exception as e:
                logging.error(e)
                continue

    def parse_fenxi_now(self, history, index, t):
        trs = self.html.xpath("//tbody/tr")
        tr = trs[0]
        tr_l = trs[1]
        try:
            if not history.get("now"):
                history["now"] = dict()
                history["last"] = dict()
                id = tr.xpath("./td[1]/text()")[0]
                history.get("now")["id"] = id

                id_last = tr_l.xpath("./td[1]/text()")[0]
                history.get("last")["id"] = id_last
                history.get("last")["pub_time"] = tr_l.xpath("./td[2]/text()")[0]
                history.get("last")["result"] = tr_l.xpath("./td[3]/text()")[0]
            else:
                if history.get("now").get("id") != tr.xpath("./td[1]/text()")[0]:
                    raise IdChangeError
            history.get("now")["alg" + str(index)] = tr.xpath("./td[4]/span/text()")[0]
            history.get("last")["alg" + str(index)] = tr_l.xpath("./td[4]/span/text()")[0]
            history.get("last")["res" + str(index)] = "对" if tr_l.xpath("./td[5]/span/text()")[0] == "中" else "错"
        except Exception as e:
            logging.error(e)

    def parse_pt_zuhe(self, item, no):
        trs = self.html.xpath("//tbody//tr")
        now = trs[0]
        id = now[0].xpath("./text()")[0]
        pre1 = now[3].xpath("./span[1]/text()")[0]
        pre2 = now[3].xpath("./span[2]/text()")[0]
        item["now"]["id"] = id
        item["now"]["alg" + str(no)] = pre1 + pre2

        last = trs[1]
        item["last"]["id"] = last[0].xpath("./text()")[0]
        pre1 = last[3].xpath("./span[1]/text()")[0]
        pre2 = last[3].xpath("./span[2]/text()")[0]
        item["last"]["pub_time"] = datetime.datetime.now().strftime("%Y:%m:%d") + last[1].xpath("./text()")[0]
        item["last"]["result"] = last[2].xpath("./text()")[0]
        item["last"]["alg" + str(no)] = pre1 + pre2
        item["last"]["res" + str(no)] = last[4].xpath(".//text()")[0]

    def parse_pt_big(self, item, no):
        trs = self.html.xpath("//tbody//tr")
        now = trs[0]
        id = now[0].xpath("./text()")[0]
        pre = now[3].xpath("./span/text()")[0]
        item["now"]["id"] = id
        item["now"]["alg" + str(no)] = pre

        last = trs[1]
        item["last"]["id"] = last[0].xpath("./text()")[0]
        pre = last[3].xpath("./span/text()")[0]
        item["last"]["pub_time"] = datetime.datetime.now().strftime("%Y:%m:%d") + last[1].xpath("./text()")[0]
        item["last"]["result"] = last[2].xpath("./text()")[0]
        item["last"]["alg" + str(no)] = pre
        item["last"]["res" + str(no)] = last[4].xpath(".//text()")[0]

    @classmethod
    def pt_pre(cls, item):
        item["now"]["alg0"] = cls.get_alg0(item.get("now"))
        item["last"]["alg0"] = cls.get_alg0(item.get("last"))
        cls.get_res0(item.get("last"))

    @staticmethod
    def get_alg0(item):
        sort = dict()
        for i in range(1, 9):
            d = item.get("alg" + str(i))
            if not sort.get(d):
                sort[d] = 1
            else:
                sort[d] += 1
        ret = sorted(sort, key=lambda x: sort.get(x), reverse=True)
        if ret:
            return ret[0]

    @staticmethod
    def get_res0(item):
        for i in range(1, 9):
            if item.get("alg" + str(i)) == item.get("alg0"):
                item["res0"] = item["res" + str(i)]
                return

    @staticmethod
    def parse_earn(last, ret):
        if not ret or ret[0][0] is None:
            # pet1, pet2, pet3, pet4 =100, 100, 100, 100
            last["pet1"] = 100
            last["pet2"] = 100
            last["pet3"] = 100
            last["pet4"] = 100
        else:
            print(ret)
            res0, pet1, pet2, pet3, pet4 = ret[0]
            if res0 == "对":
                last["pet1"] = 100
                last["pet2"] = 100
                last["pet3"] = 100
                last["pet4"] = 100
            elif res0 == "错":
                last["pet1"] = 2 * pet1 if pet1 < 800 else 0
                last["pet2"] = 2 * pet2 if pet2 < 1600 else 0
                last["pet3"] = 2 * pet3 if pet3 < 3200 else 0
                last["pet4"] = 2 * pet4 if pet4 < 6400 else 0

        if last.get("res0") == "对":
            if last.get("result").endswith("13") or last.get("result").endswith("14"):
                last["gain1"] = int(last["pet1"] * 0.6)
                last["gain2"] = int(last["pet2"] * 0.6)
                last["gain3"] = int(last["pet3"] * 0.6)
                last["gain4"] = int(last["pet4"] * 0.6)
            else:
                last["gain1"] = last["pet1"]
                last["gain2"] = last["pet2"]
                last["gain3"] = last["pet3"]
                last["gain4"] = last["pet4"]
        if last.get("res0") == "错":
            last["gain1"] = -int(last["pet1"])
            last["gain2"] = -int(last["pet2"])
            last["gain3"] = -int(last["pet3"])
            last["gain4"] = -int(last["pet4"])
