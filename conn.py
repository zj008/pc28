import pymysql
import logging
from configparser import ConfigParser

cf = ConfigParser()
cf.read("conf/base_conf")

class Sql():
    def __init__(self):
        self.db = pymysql.Connect(
            host=cf.get("mysql", "host"),
            port=int(cf.get("mysql", "port")),
            user=cf.get("mysql", "user"),
            password=cf.get("mysql", "pass"),
            database=cf.get("mysql", "db")
        )
        self.cursor = self.db.cursor()

    def save(self, item):
        table = item.pop("table")
        keys = ', '.join(item.keys())
        values = ', '.join(['%s'] * len(item))
        sql = 'insert into %s(%s) values(%s)' % (table, keys, values)
        try:
            self.cursor.execute(sql, tuple(item.values()))
            self.db.commit()
        except Exception as e:
            logging.error("save error: error info : " + e.__str__())
            self.db.rollback()
        logging.info("save success")
        return

    def update(self, item, field):
        sql = "update %s set %s = %s where id = %s "%(item.get("table"), field, item.get(field), item.get("id"))
        print(sql)
        self.cursor.execute(sql)
        self.db.commit()
        print("update success")
        return

    def is_exists(self, item, field="id"):
        table = item.get("table")
        sql = "select %s from %s where %s = '%s'" % (field, table, field, item.get(field))

        self.cursor.execute(sql)
        ret = self.cursor.fetchone()
        if ret:
            print("ret", ret)
            logging.error(field + ": " + str(item.get(field)) + field + " exists in " + table)
            return 1
        return 0

    def update_fields(self, data):
        table = data.pop("table")
        id = data.pop("id")
        l = []
        try:
            for k, v in data.items():
                sql = "update %s set %s = '%s' where id = %s" % (table, k, v, id)
                self.cursor.execute(sql)
                logging.info("update success")
            self.db.commit()
        except Exception as e:
            logging.error(f"error when update {table}, error is {e.__str__()}")

    def close(self):
        self.cursor.close()
        self.db.close()