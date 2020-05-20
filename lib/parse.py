from lxml import etree
from lib.error import IdChangeError
import logging

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
                history[id]["res" + str(index) ] = "对" if res[0] == "中" else "错"
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








