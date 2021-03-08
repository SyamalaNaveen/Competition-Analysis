import time,re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.options import Options
import pandas as pd
from collections import Counter
import pymysql
from os import close, remove
import datetime
import time
import config_file
import requests
from fake_useragent import UserAgent
import urllib3

#open redbus and abhibus sites and inserts date 
def routes(src,dest,date_selected):
    db,cur = config_file.db_connection()
    print("Route Started")
    pause_time = 0.5
    month = {"01":"Jan","02":"Feb","03":"Mar","04":"Apr","05":"May","06":"Jun","07":"Jul","08":"Aug","09":"Sep","10":"Oct","11":"Nov","12":"Dec"}
    headers = ['route','operator','pick_time','drop_time','site','date','id']
    date_selected = date_selected.replace("/","-")
    route = src + "-" +dest
    options = Options()
    ua = UserAgent()
    userAgent = ua.random
    print(userAgent)
    #options.add_argument(f'user-agent={userAgent}')
    #options.add_argument(f'--proxy-server={None}')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)
#    driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)
    print("test1")

    driver.get('https://www.redbus.in/')
    print("test2")
    #print(driver.current_url)
    #driver.find_element_by_xpath('/html/body/div/div/div[1]').click()
    time.sleep(5)
    red_source = driver.find_element_by_xpath('//*[@id="src"]')
    red_source.send_keys(src)

    time.sleep(1)
    red_source.send_keys(Keys.TAB)
    red_desti = driver.find_element_by_xpath('//*[@id="dest"]')
    red_desti.send_keys(dest)
    time.sleep(1)
    red_desti.send_keys(Keys.TAB)
    print(driver.current_url)
    #driver.find_element_by_xpath('//*[@id="rb-calendar_onward_cal"]/table/tbody/tr[1]/td[3]').click()
    driver.find_element_by_xpath('//*[@id="rb-calendar_onward_cal"]/table/tbody/tr[6]/td[1]').click()

    driver.find_element_by_xpath('//*[@id="search_btn"]').click()
    current_link_1 = driver.current_url
    time.sleep(1)
    current_link_date = re.search('&onward=(.*)&opId',current_link_1).group(1)
    cur_link_month = current_link_date.split("-")[1]
    cur_link_date = current_link_date.split("-")[0]
    cur_link_year = current_link_date.split("-")[2]
    date_selected_month = date_selected.split("-")[1]
    user_month = month[date_selected_month]
    user_date = date_selected.split("-")[0]
    user_year = date_selected.split("-")[2]
    user_selected_date = user_date + "-"+user_month + "-" + user_year
    new_current_link = current_link_1.replace(current_link_date,user_selected_date)
    print(new_current_link)
    driver.get(new_current_link)
    time.sleep(3)
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    red_operator = driver.find_elements_by_xpath('//div[@class="travels lh-24 f-bold d-color"]')
    red_origin = driver.find_elements_by_xpath('//div[@class="dp-time f-19 d-color f-bold"]')
    red_destination = driver.find_elements_by_xpath('//div[@class="bp-time f-19 d-color disp-Inline"]')
    #red_fare = driver.find_elements_by_class('f-19 f-bold')

    redbus_oper = []

    red_site_details = {}

    for each in headers:
        red_site_details[each]=[]

#sql = "UPDATE abhibus_operator_master_id SET id = %s WHERE operator = %s"
#cur_abhi.execute(sql,(red_opr_id,abhi_opr_name_bk))

    def get_id(opr,site):
        if site == "red":
            sql = "Select id FROM redbus_operator_master_id WHERE LOWER(operator) = %s"
            cur.execute(sql,opr.lower())
#            cur.execute("Select id FROM redbus_operator_master_id WHERE LOWER(operator) = '%s'" %opr.lower())
            data = cur.fetchall()
            found = False
            if len(data) > 0:
                # Select stmt to get ids in ascedning order and take the last value. Add one to that value.Assign to a variable.
                # Id = variable
                #cur.execute("Select * From redbus_operator_master_id ORDER BY id where LAST(id) As LAST_value From redbus_operator_master_id")
                Id = data[0][0]

            else:
                sql = "INSERT INTO redbus_operator_master_id(operator) VALUES(%s)"
                cur.execute(sql,(opr))
                db.commit()
                sql = "Select id FROM redbus_operator_master_id WHERE LOWER(operator) = %s"
                cur.execute(sql,(opr.lower()))
#                cur.execute("Select id FROM redbus_operator_master_id WHERE LOWER(operator) = '%s'" % (opr.lower()))
                data2 = cur.fetchall()
                if len(data2) > 0:
                    Id = data2[0][0]
            return Id
        elif site == "abhi":
            sql = "Select id FROM abhibus_operator_master_id WHERE LOWER(operator) =%s"
            cur.execute(sql,(opr.lower()))

            data = cur.fetchall()
            found = False
            Id = 0
            print(data)
            if len(data) > 0:
                Id = int(data[0][0])
                #print(Id)
            else:
                sql = "INSERT INTO abhibus_operator_master_id(operator,id) VALUES(%s,%s)"
                cur.execute(sql,(opr,0))

                db.commit()
            return Id

    for op1,pi1,drp1 in zip(red_operator,red_origin,red_destination):
        opr = op1.text.strip()

        id = get_id(opr,"red")

        red_site_details['operator'].append(opr)
        red_site_details['drop_time'].append(drp1.text.strip())
        red_site_details['pick_time'].append(pi1.text.strip())
        red_site_details['date'].append(date_selected)
        red_site_details['site'].append("Redbus")
        red_site_details['route'].append(route)
        red_site_details['id'].append(id)

    update_ids()
    print("update_ids is over")
    url = 'https://www.abhibus.com/'
    driver.get(url)
    driver.maximize_window()
    time.sleep(3)
    print(driver.current_url)
    print("abhi opened")
    driver.find_element_by_xpath('//*[@id="myModal"]/div/div/div[1]/button/span').click()
    source = driver.find_element_by_xpath('//input[@id = "source"]')
    source.send_keys(src)
    time.sleep(5)
    source.send_keys(Keys.TAB)
    destination = driver.find_element_by_xpath('//input[@id = "destination"]')
    destination.send_keys(dest)
    sleep(2)
    destination.send_keys(Keys.TAB)
    driver.find_element_by_xpath('//*[@id="datepicker1"]').click()
    driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div[2]/table/tbody/tr[3]/td[4]/a').click()
    sleep(2)
    driver.find_element_by_xpath('//*[@id="frmFinal"]/div/div[6]/a').click()
    sleep(4)
    current_link = driver.current_url
    print(current_link)
    dt = current_link.split('/')[-2]
    new_current_url = current_link.replace(dt,date_selected)
    driver.get(new_current_url)
    print(new_current_url)
    sleep(4)
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    operator = driver.find_elements_by_xpath('//h2[@class="TravelAgntNm ng-binding"]')
    price = driver.find_elements_by_xpath('//strong[@class="TickRate ng-binding"]')
    drop_time = driver.find_elements_by_xpath('//span[@class="ArvTm tooltipsteredDropping ng-binding tooltipstered"]')
    pick_time = driver.find_elements_by_xpath('//span[@class="StrtTm tooltipsteredBoarding ng-binding tooltipstered"]')

    abhi_site_details = {}
    for each in headers:
        abhi_site_details[each] = []
    operators_list = []

    for op,pr,pi,drp in zip(operator,price,pick_time,drop_time):
        opr = op.text
        if opr != "":
            id = get_id(opr,'abhi')
            abhi_site_details['operator'].append(opr)
            abhi_site_details['drop_time'].append(drp.text.strip())
            abhi_site_details['pick_time'].append(pi.text.strip())
            abhi_site_details['date'].append(date_selected)
            abhi_site_details['site'].append("Abhibus")
            abhi_site_details['route'].append(route)
            abhi_site_details['id'].append(id)

    df_abhi_oprs = pd.DataFrame(abhi_site_details)

    df_red_oprs = pd.DataFrame(red_site_details)

    for index,row in df_red_oprs['operator'].iteritems():
        sql = "INSERT INTO redbus_operators_data_datewise(operator,pick_time,date,site,rid,route) VALUES (%s,%s,%s,%s,%s,%s)"
        cur.execute(sql,(df_red_oprs['operator'][index],df_red_oprs['pick_time'][index],
        df_red_oprs['date'][index],df_red_oprs['site'][index],int(df_red_oprs['id'][index]),route))


    for index,row in df_abhi_oprs['operator'].iteritems():
        id = df_abhi_oprs['id'][index].item()

        sql = "INSERT INTO abhibus_operators_data_datewise(operator,pick_time,date,site,rid,route) VALUES(%s,%s,%s,%s,%s,%s)"
        cur.execute(sql,(df_abhi_oprs['operator'][index],df_abhi_oprs['pick_time'][index],df_abhi_oprs['date'][index],df_abhi_oprs['site'][index],
        id,route))

    db.commit()
    print("Scraping Finished and Data Pushed to DB")

def get_data(date_selected,route):
    db,cur = config_file.db_connection()
    sql = "SELECT * FROM both_operators WHERE id<>0 and date = %s AND route = %s" # and
    cur.execute(sql,(date_selected,route))
    op_data = cur.fetchall()
    operator, a_services,r_services,schedule_period_abhi,schedule_period_red,status,description,serial_no,scraped_time = [],[],[],[],[],[],[],[],[]
    date_db,route_db = [],[]
    disp ={}
    abhi_service_timings,red_service_timings = [],[]
    disp_header=['operator','opid','abhibus_services','redbus_services','missing_services']
    missing_services = []
    dummy,ids = [],[]
    print(op_data)
    print(len(op_data))
    for each in op_data:
        id = each[2]
        print(each[0],id)
        if id not in dummy:
            ids.append(id)
            operator.append(each[0])
            sql = "SELECT * FROM both_operators WHERE site = %s AND id = %s AND date = %s AND route = %s"
            cur.execute(sql,('Abhibus',id,date_selected,route))
            samp_ab_data = cur.fetchall()
            if len(samp_ab_data) > 0:
                for e in samp_ab_data:
                    timings = e[-1]
                    timings = timings.split(",")
                    running_time = timings[0] + " - " + timings[-1]
                    schedule_period_abhi.append(running_time)
                    a_services.append(e[1])
                    abhi_service_timings.append(timings)
            else:
                a_services.append(0)
                schedule_period_abhi.append("NA")
                abhi_service_timings.append("NA")
            sql = "SELECT * FROM both_operators WHERE site = %s ANd id = %s AND date = %s AND route = %s"
            cur.execute(sql,('Redbus',id,date_selected,route))
            samp_red_data = cur.fetchall()
            if len(samp_red_data) > 0:
                for e1 in samp_red_data:
                    timings1 = e1[-1]
                    timings1 = timings1.split(",")
                    running_time1 = timings1[0] + " - " + timings1[-1]
                    schedule_period_red.append(running_time1)
                    r_services.append(e1[1])
                    red_service_timings.append(timings1)
            else:
                r_services.append(0)
                schedule_period_red.append("NA")
                red_service_timings.append("NA")
            dummy.append(id)

    sql = "Select * FROM both_operators where id = %s and site=%s and date = %s and route = %s"
    cur.execute(sql,(0,'Abhibus',date_selected,route))

    abhi_zeros = cur.fetchall()
    for each_zero in abhi_zeros:
        ids.append(each_zero[2])
        operator.append(each_zero[0])
        a_services.append(each_zero[1])
        r_services.append(0)
        timings2 = each_zero[-1]
        print(timings2)
        if "NA" not in timings2:
            timings2 = timings2.split(",")
            running_time2 = timings2[0] + " - " + timings2[-1]
            abhi_service_timings.append(timings2)
        else:
            abhi_service_timings.append("NA")
        red_service_timings.append("NA")
        schedule_period_abhi.append(running_time2)
        schedule_period_red.append("NA")

    i = 1
    scraped_datetime = datetime.datetime.now()
    for a,b in zip(a_services,r_services):
        missing_serv = a-b
        missing_services.append(missing_serv)
        serial_no.append(i)
        scraped_time.append(scraped_datetime)
        i += 1
        date_db.append(date_selected)
        route_db.append(route)

    for ab,rd in zip(abhi_service_timings,red_service_timings):
        print("Abhibus ",ab)
        print("Redbus ",rd)
        if "NA" in ab:
            status_code = "Missing"
            content = "No services in Abhibus"
        elif "NA" not in rd:
            missing_pickTime = list(set(rd)-set(ab))
            extra_picktime = list(set(ab)-set(rd))
            content = ""
            sts = 0
            if len(missing_pickTime) >0:
                sts = 1
                content = content + ",".join(missing_pickTime)
                content = content + " are missing services in Abhibus."
            if len(extra_picktime) > 0:
                sts = 2
                content = content + ",".join(extra_picktime)
                content = content + " are extra services in Abhibus."
            if sts == 0:
                status_code = "Exact"
            else:
                status_code = "Excess"
        else:
            status_code = "Excess"
            content = "Services are only avialable in Abhibus"
        status.append(status_code)
        description.append(content)

    print("Operator",len(operator))
    opr = pd.DataFrame(operator)
    opr.columns = ["Operator"]

    print("a_services",len(a_services))
    abh_serv = pd.DataFrame(a_services)
    abh_serv.columns = ["Abhibus Inventory"]

    print("r_services",len(r_services))
    red_serv = pd.DataFrame(r_services)
    red_serv.columns = ["Redbus Inventory"]

    print("missing_services",len(missing_services))
    missing_serv = pd.DataFrame(missing_services)
    missing_serv.columns = ["Difference"]

    print("schedule_period_abhi",len(schedule_period_abhi))
    schedule_period_abhi_df = pd.DataFrame(schedule_period_abhi)
    schedule_period_abhi_df.columns = ["Abhibus Operation Time"]

    print("schedule_period_red",len(schedule_period_red))
    schedule_period_red_df = pd.DataFrame(schedule_period_red)
    schedule_period_red_df.columns = ["Redbus Operation Time"]

    print("status",len(status))
    status_df = pd.DataFrame(status)
    status_df.columns = ["Status"]

    print("serial_no",len(serial_no))
    serial_num_df = pd.DataFrame(serial_no)
    serial_num_df.columns = ['S.No']

    print("description",len(description))
    description_df = pd.DataFrame(description)
    description_df.columns = ['Comments']

    print("date",len(date_db))
    date_db_df = pd.DataFrame(date_db)
    date_db_df.columns = ['date']

    print("route",len(route_db))
    route_db_df = pd.DataFrame(route_db)
    route_db_df.columns = ['route']

    print("scrape_time",len(scraped_time))
    scraped_time_df = pd.DataFrame(scraped_time)
    scraped_time_df.columns = ['scrape_time']


#    op_ids = pd.DataFrame(ids)

    df = pd.concat([serial_num_df,opr,abh_serv,red_serv,missing_serv,schedule_period_abhi_df,schedule_period_red_df,status_df,description_df,date_db_df,route_db_df,scraped_time_df],axis = 1)

    for indx,row in df.iterrows():
        sno = int(df['S.No'][indx])
        opr = df['Operator'][indx]
        abhi_inv = int(df['Abhibus Inventory'][indx])
        red_inv = int(df['Redbus Inventory'][indx])
        diff = int(df['Difference'][indx])
        abhi_opr_time = df['Abhibus Operation Time'][indx]
        red_opr_time = df['Redbus Operation Time'][indx]
        status = df['Status'][indx]
        cmts = df['Comments'][indx]
        dte = df['date'][indx]
        rte = df['route'][indx]
        scr_time = str(df['scrape_time'][indx])
        #print(scr_time,type(scr_time))
        #print(sno,opr,abhi_inv,red_inv,diff,abhi_opr_time,red_opr_time,status,cmts,dte,rte,scr_time)
        sql = "INSERT INTO display_data(sno,operator,abhibus_inventory,redbus_inventory,difference,abhibus_operation_time,redbus_operation_time,status,comment,date,route,scraped_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cur.execute(sql,(sno,opr,abhi_inv,red_inv,diff,abhi_opr_time,red_opr_time,status,cmts,dte,rte,scr_time))

    opr_count = int(df.shape[0])

    l1 = list(df['Abhibus Inventory'])
    l2 = list(df['Redbus Inventory'])
    bus_sum = 0
    for n,m in zip(l1,l2):
        if n == m:
            bus_sum += n
        else:
            if n>m :
                bus_sum += n
            else :
                bus_sum += m
    bus_count = int(bus_sum)

    sql = "INSERT INTO bus_opr_count values(%s,%s,%s,%s)"
    cur.execute(sql,(date_selected,route,bus_count,opr_count))
    return df

def compare_both_sites(date_selected,route):
    db,cur = config_file.db_connection()
    db.commit()

    sql = "SELECT operator,Count(operator),rid,site,date,route,GROUP_CONCAT(pick_time) AS service_time from redbus_operators_data_datewise  where date =%s and route =%s  group by operator"
    cur.execute(sql,(date_selected,route))
    red_full_list = []
    opr_data = cur.fetchall()
    for each_opr in opr_data:
        try:
            sql = "insert into both_operators values(%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sql,(each_opr[0],each_opr[1],each_opr[2],'Redbus',date_selected,route,each_opr[6]))
            db.commit()
        except:
            print("Except Red: ",each_opr)
            pass

    sql = "SELECT operator,Count(operator),rid,site,date,route,GROUP_CONCAT(pick_time) AS service_time from abhibus_operators_data_datewise where date =%s and route =%s group by operator"
    cur.execute(sql,(date_selected,route))
    opr_data1 = cur.fetchall()
    for each_opr1 in opr_data1:
        try:
            sql = "INSERT INTO both_operators VALUES(%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sql,(each_opr1[0],each_opr1[1],each_opr1[2],'Abhibus',date_selected,route,each_opr1[6]))
            db.commit()
        except:
            print("Except Abhi: ",each_opr)
            pass
    db.commit()
    print("Comparing Both Sides is Completed")

def update_ids():
    red_db,cur_red = config_file.db_connection()
    abhi_db,cur_abhi = config_file.db_connection()

    cur_red.execute("select * from redbus_operator_master_id")
    red_data = cur_red.fetchall()
    sql = "UPDATE abhibus_operator_master_id SET id = %s where map_status <>1"
    cur_abhi.execute(sql,(0))
    abhi_db.commit()
    print("Check db")

    cur_abhi.execute("select * from abhibus_operator_master_id")
    abhi_data = cur_abhi.fetchall()
    count = 0
    for each_red in red_data:
        red_opr_name = each_red[0].lower()
        red_opr_id = each_red[1]
        for each_abhi in abhi_data:
            abhi_opr_name_bk = each_abhi[0]
            abhi_opr_name = each_abhi[0].lower()
            if red_opr_name == abhi_opr_name:

                sql = "UPDATE abhibus_operator_master_id SET id = %s WHERE operator = %s"
                cur_abhi.execute(sql,(red_opr_id,abhi_opr_name_bk))
                count += 1
                abhi_db.commit()
                break
    abhi_db.commit()
    print(count)

def get_ids_for_operators(date_selected,route):
    db,cur_red  = config_file.db_connection()
    db1,cur_abhi = config_file.db_connection()
    cur_red.execute("select operator from redbus_operators_data_datewise")
    red_data = cur_red.fetchall()
    for each_rd_opr in red_data:
        red_opr = each_rd_opr[0]
        cur_red.execute("Select id from redbus_operator_master_id where lower(operator) = '%s'" % red_opr.lower())
        red_data1 = cur_red.fetchall()

        if len(red_data1) > 0:
            Id = red_data1[0]
            Id = Id[0]
            if Id is not None:
                cur_red.execute("update redbus_operators_data_datewise set rid = %s where operator = '%s'" %(Id,red_opr))
                db.commit()
            else:
                try:
                    cur_red.execute("update redbus_operators_data_datewise set rid = %s where operator = '%s'" %(Id,red_opr))
                    db.commit()
                except:
                    pass
            db.commit()
        else:
            cur_red.execute("insert into redbus_operator_master_id(operator) values('%s')"%(red_opr))
            db.commit()
    update_ids()
    print("Abhibus Ids updated")
    cur_abhi.execute("select operator from abhibus_operators_data_datewise")
    abhi_data = cur_abhi.fetchall()
    for each_ab_opr in abhi_data:
        abhi_opr = each_ab_opr[0]

        cur_abhi.execute("Select id from abhibus_operator_master_id where lower(operator) = '%s'" % abhi_opr.lower())
        abhi_data1 = cur_abhi.fetchall()
        if len(abhi_data1) > 0:
            Id1 = abhi_data1[0]
            Id1 = Id1[0]
            if Id1 is not None:
                cur_abhi.execute("update abhibus_operators_data_datewise set rid = %s where operator = '%s'" %(Id1,abhi_opr))
                db1.commit()
            else:
                try:
                    cur_abhi.execute("update abhibus_operators_data_datewise set rid = %s where operator = '%s'" %(Id1,abhi_opr))
                    db1.commit()
                except:
                    pass
        else:
            cur_abhi.execute("insert into abhibus_operator_master_id(operator) values('%s')"%(abhi_opr))
            db1.commit()


    db1.commit()
    db.commit()
    print("Commited")
