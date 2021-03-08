import pymysql
import pandas as pd
import datetime


db = pymysql.connect("10.67.40.183","abrsdemo","K0DuRU))(($$","Abhibus_Operators_Analysis")
cur_red = db.cursor()
cur_abhi = db.cursor()

cur_red.execute("select * from redbus_operator_master_id")
red_data = cur_red.fetchall()
cur_abhi.execute("select * from abhibus_operator_master_id")
abhi_data = cur_abhi.fetchall()

count = 0
for each_red in red_data:
    red_opr_name = each_red[0].lower()
    red_opr_id = each_red[1]
    for each_abhi in abhi_data:
        abhi_opr_name_bk = each_abhi[0].lower()
        abhi_opr_name = each_abhi[0].lower()
        abhi_opr_id = each_abhi[1]
        if red_opr_name == abhi_opr_name:
            cur_abhi.execute("update abhibus_operator_master_id set id = %s where operator = '%s'" %(red_opr_id,abhi_opr_name_bk))
            print(abhi_opr_name,red_opr_id)
            count += 1
db.commit()
print(count)
