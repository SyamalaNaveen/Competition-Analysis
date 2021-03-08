
from flask import *
import compare
import pymysql
import datetime
import pandas as pd
from flask import json
import config_file

from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
#Opens route_search
@app.route('/route_search',methods=['POST','GET'])
def home():
    db,cur = config_file.db_connection()
    cur.execute("SELECT citynames FROM location")
    locs = cur.fetchall()
    loc_list = []
    for each_loc in locs:
        loc_list.append(each_loc[0])

    loc_list = json.dumps(loc_list)
    return render_template("route_search.html", locations = loc_list)
//select Dates
@app.route("/operator_details",methods=['POST','GET'])
def compare_operators_src_dest():
    db,cur = config_file.db_connection()
    source = request.form['source']
    dest  = request.form['dest']
    route = source + "-" + dest
    date_selected  = request.form['datepicker1']
    date_selected_2  = request.form['datepicker2']
    if date_selected_2 != "":
        date_selected_split2 = date_selected_2.split('/')
        date_selected_2 = date_selected_split2[1]+'-'+date_selected_split2[0]+'-'+date_selected_split2[2]
        date_selected_split = date_selected.split('/')
        date_selected = date_selected_split[1]+'-'+date_selected_split[0]+'-'+date_selected_split[2]
        day2 = datetime.datetime.strptime(date_selected_2,"%d-%m-%Y")
        day1 = datetime.datetime.strptime(date_selected,"%d-%m-%Y")
        diff_in_days = (day2-day1).days
        total_bus_lst,total_oprs_lst = [],[]
        total_df,lst_of_dates = [],[]
        for each_date in range(diff_in_days+1):
            today_plus_1 = day1+datetime.timedelta(each_date)
            date_selected = today_plus_1.strftime('%d-%m-%Y')
            sql = "DELETE FROM abhibus_operators_data_datewise WHERE date = %s AND route = %s"
            cur.execute(sql,(date_selected,route))
            db.commit()
            sql1 = "DELETE FROM redbus_operators_data_datewise WHERE date = %s AND route = %s"
            cur.execute(sql1,(date_selected,route))
            db.commit()
            sql2 = "DELETE FROM both_operators WHERE date = %s AND route = %s"
            cur.execute(sql2,(date_selected,route))
            db.commit()
            sql3 = "DELETE FROM display_data WHERE date = %s AND route = %s"
            cur.execute(sql3,(date_selected,route))
            db.commit()
            print(date_selected)
            compare.routes(source,dest,date_selected)
            print("Route Over")
            #compare.get_ids_for_operators(date_selected,route)
            compare.compare_both_sites(date_selected,route)
            df = compare.get_data(date_selected,route)
            opr_count = df.shape[0]
            ab_bus_count = df['Abhibus Inventory'].sum()
            rd_bus_count = df['Redbus Inventory'].sum()
            if ab_bus_count >= rd_bus_count:
                bus_count = rd_bus_count
            else:
                bus_count = ab_bus_count
            total_oprs_lst.append(opr_count)
            total_df.append(df)
            lst_of_dates.append(date_selected)
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
            total_bus_lst.append(bus_sum)
            print(total_df)
            print(datetime.datetime.now())
        print(total_bus_lst)
        print(total_oprs_lst)
        return render_template('route_search_multi_details.html', src = source, dest=dest,total_df = total_df,lst_of_dates = lst_of_dates,
        total_bus_lst= total_bus_lst ,total_oprs_lst= total_oprs_lst)
    else:
        date_selected_split = date_selected.split('/')
        date_selected = date_selected_split[1]+'-'+date_selected_split[0]+'-'+date_selected_split[2]
        date_selected = datetime.datetime.strptime(date_selected,"%d-%m-%Y")
        date_selected = date_selected.strftime('%d-%m-%Y')
        sql = "DELETE FROM abhibus_operators_data_datewise WHERE date = %s AND route = %s"
        cur.execute(sql,(date_selected,route))
        db.commit()
        sql1 = "DELETE FROM redbus_operators_data_datewise WHERE date = %s AND route = %s"
        cur.execute(sql1,(date_selected,route))
        db.commit()
        sql2 = "DELETE FROM both_operators WHERE date = %s AND route = %s"
        cur.execute(sql2,(date_selected,route))
        db.commit()
        sql3 = "DELETE FROM display_data WHERE date = %s AND route = %s"
        cur.execute(sql3,(date_selected,route))
        db.commit()
        print(date_selected)
        compare.routes(source,dest,date_selected)
        print("Route Over")
        #compare.get_ids_for_operators(date_selected,route)
        compare.compare_both_sites(date_selected,route)
        df = compare.get_data(date_selected,route)
        opr_count = df.shape[0]
        ab_bus_count = df['Abhibus Inventory'].sum()
        rd_bus_count = df['Redbus Inventory'].sum()
        if ab_bus_count >= rd_bus_count:
            bus_count = rd_bus_count
        else:
            bus_count = ab_bus_count

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
        total_bus_lst = bus_sum

        print(df)
        print(datetime.datetime.now())
        return render_template('route_search_details.html',data = df, date=date_selected,src = source, dest=dest,
        total_bus_lst= bus_sum ,total_oprs_lst= opr_count)

#    return render_template('route_search.html',operator_info=[df.to_html(classes='data', header="true",index=False)],date=date_selected,src=source,dest= dest)
#Toproutes
@app.route("/top_routes",methods=['POST','GET'])
def top_routes():
    print(datetime.datetime.now())
    db,cur = config_file.db_connection()
    #src_dest = {'Hyderabad - Adilabad':['Hyderabad','Adilabad'],'Adilabad - Hyderabad':['Adilabad','Hyderabad']}
    src_dest = {'Hyderabad - Bangalore':['Hyderabad','Bangalore'],'Bangalore - Hyderabad':['Bangalore','Hyderabad'],'Pune - Shirdi':['Pune','Shirdi'],'Chennai - Coimbatore':['Chennai','Coimbatore'],
    'Hyderabad - Visakhapatnam':['Hyderabad','Visakhapatnam'],'Bangalore - Vijayawada':['Bangalore','Vijayawada'],'Hyderabad - Chennai':['Hyderabad','Chennai'],'Delhi - Manali':['Delhi','Manali'],'Mumbai - Bangalore':['Mumbai','Bangalore'],
    'Chennai - Bangalore':['Chennai','Bangalore'],'Indore - Bhopal':['Indore','Bhopal'],'Bangalore-Chennai':['Bangalore','Chennai'],'Pune - Mumbai':['Pune','Mumbai']
    ,'Ahmedabad - Mumbai':['Ahmedabad','Mumbai']}

    route_total_df = {}
    for route1,val in src_dest.items():
        source = val[0]
        dest = val[1]
        print(route1,source,dest)
        nt = datetime.datetime.now()
        list_of_days = []
        for each_day in range(2):
            today_plus_1 = nt+datetime.timedelta(each_day)
            today_plus_1 = datetime.datetime.strftime(today_plus_1,"%d-%m-%Y")
            list_of_days.append(today_plus_1)
        print(list_of_days)
        total_bus_lst,total_oprs_lst = [],[]
        total_df,lst_of_dates = [],[]
        route = source + "-" + dest
        for each_date in list_of_days:
            print(each_date)
            #today_plus_1 = day1+datetime.timedelta(each_date)
            #date_selected = today_plus_1.strftime('%d-%m-%Y')
            date_selected = each_date
            sql = "DELETE FROM abhibus_operators_data_datewise WHERE date = %s AND route = %s"
            cur.execute(sql,(date_selected,route))
            db.commit()
            sql1 = "DELETE FROM redbus_operators_data_datewise WHERE date = %s AND route = %s"
            cur.execute(sql1,(date_selected,route))
            db.commit()
            sql2 = "DELETE FROM both_operators WHERE date = %s AND route = %s"
            cur.execute(sql2,(date_selected,route))
            db.commit()
            sql3 = "DELETE FROM display_data WHERE date = %s AND route = %s"
            cur.execute(sql3,(date_selected,route))
            db.commit()
            sql3 = "DELETE FROM display_data WHERE date = %s AND route = %s"
            cur.execute(sql3,(date_selected,route))
            db.commit()
            compare.routes(source,dest,date_selected)
            #compare.get_ids_for_operators(date_selected,route)
            compare.compare_both_sites(date_selected,route)
            df = compare.get_data(date_selected,route)
            opr_count = df.shape[0]
            ab_bus_count = df['Abhibus Inventory'].sum()
            rd_bus_count = df['Redbus Inventory'].sum()
            if ab_bus_count >= rd_bus_count:
                bus_count = rd_bus_count
            else:
                bus_count = ab_bus_count
            total_oprs_lst.append(opr_count)
            total_df.append(df)
            lst_of_dates.append(date_selected)
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
            total_bus_lst.append(bus_sum)
            print(total_df)
            print(datetime.datetime.now())
        src = source
        dest=dest
        route_total_df[route] = []
        route_total_df[route].extend([src,dest,lst_of_dates,total_df,total_bus_lst,total_oprs_lst])
    # return render_template('route_search_multi.html', src = source, dest=dest,total_df = total_df,lst_of_dates = lst_of_dates,
    # total_bus_lst= total_bus_lst ,total_oprs_lst= total_oprs_lst)
    print(route_total_df)
    print(type(route_total_df))
    return render_template('route_search_multi_details.html',route_total_df=route_total_df)
#used append in db
@app.route("/top_route_data")
def top_route_display():
    db,cur = config_file.db_connection()
    cur.execute("SELECT route FROM display_data GROUP BY route")
    all_routes = []
    tp_routes = config_file.top_routes
    today_date = datetime.datetime.today().strftime('%d-%m-%Y')
    today_date = datetime.datetime.strptime(today_date,"%d-%m-%Y")
    for each_route in tp_routes:
        cur.execute("SELECT distinct(date) from display_data where route ='%s' "%(each_route))
        route_data = {}
        days_lst = []
        lst_of_scrapped = {}
        for each_date in cur.fetchall():
            each_dt1 = each_date[0]
            each_dt = datetime.datetime.strptime(each_dt1,"%d-%m-%Y")
            if each_dt >= today_date:
                each_dt = datetime.datetime.strftime(each_dt,'%d-%m-%Y')
                cur.execute("select * FROM display_data where route = '%s' and date = '%s'" %(each_route,each_dt))
                full_date_data = {}
                headers = ['sno','opr','abhi_inv','red_inv','diff','abhi_op_time','red_op_time','status','cmnts','each_dt','each_rt']
                for each in headers :
                    full_date_data[each] =[]

                lst_of_days = {}
                for each_rt_dte in cur.fetchall():
                    full_date_data['sno'].append(each_rt_dte[0])
                    full_date_data['opr'].append(each_rt_dte[1])
                    full_date_data['abhi_inv'].append(each_rt_dte[2])
                    full_date_data['red_inv'].append(each_rt_dte[3])
                    full_date_data['diff'].append(each_rt_dte[4])
                    full_date_data['abhi_op_time'].append(each_rt_dte[5])
                    full_date_data['red_op_time'].append(each_rt_dte[6])
                    full_date_data['status'].append(each_rt_dte[7])
                    full_date_data['cmnts'].append(each_rt_dte[8])
                    full_date_data['each_dt'].append(each_dt)
                    full_date_data['each_rt'].append(each_route)
                    scraped_time = each_rt_dte[11]
                    #scraped_time = datetime.datetime.now()
                df = pd.DataFrame(full_date_data)
                lst_of_days[each_dt] = df
                print(df)
                if scraped_time != None:
                    de = str(scraped_time).split(".")[0]
                    got_date = de.split(" ")[0]

                    got_date_new = got_date.split("-")[2]+"-"+got_date.split("-")[1]+"-"+got_date.split("-")[0]
                    scraped_time = got_date_new + " " + de.split(" ")[1]

                lst_of_scrapped[each_dt] = scraped_time
                days_lst.append(lst_of_days)
        route_data['days'] = days_lst
        route_data['scrapped'] = lst_of_scrapped
        route_data['name'] = each_route
        all_routes.append(route_data)
    return render_template('top_routes.html',route_total_df=all_routes)
#routes which are not in  top_routes
@app.route("/rest_of_top_routes")
def rest_of_top_routes():
    db,cur = config_file.db_connection()
    cur.execute("SELECT route FROM display_data GROUP BY route")
    routes_in_db = []
    for each in cur.fetchall():
        routes_in_db.append(each[0])
    all_routes = []
    tp_routes = config_file.top_routes

    rest_of_rtes = list(set(routes_in_db) - set(tp_routes))
    today_date = datetime.datetime.today().strftime('%d-%m-%Y')
    today_date = datetime.datetime.strptime(today_date,"%d-%m-%Y")

    for each_route in rest_of_rtes:
        cur.execute("SELECT distinct(date) from display_data where route ='%s' "%(each_route))
        route_data = {}
        days_lst = []
        lst_of_scrapped = {}
        for each_date in cur.fetchall():
            each_dt1 = each_date[0]
            each_dt = datetime.datetime.strptime(each_dt1,"%d-%m-%Y")
            if each_dt >= today_date:
                each_dt = datetime.datetime.strftime(each_dt,'%d-%m-%Y')
                cur.execute("select * FROM display_data where route = '%s' and date = '%s'" %(each_route,each_dt))
                full_date_data = {}
                headers = ['sno','opr','abhi_inv','red_inv','diff','abhi_op_time','red_op_time','status','cmnts','each_dt','each_rt']
                for each in headers :
                    full_date_data[each] =[]

                lst_of_days = {}
                for each_rt_dte in cur.fetchall():
                    full_date_data['sno'].append(each_rt_dte[0])
                    full_date_data['opr'].append(each_rt_dte[1])
                    full_date_data['abhi_inv'].append(each_rt_dte[2])
                    full_date_data['red_inv'].append(each_rt_dte[3])
                    full_date_data['diff'].append(each_rt_dte[4])
                    full_date_data['abhi_op_time'].append(each_rt_dte[5])
                    full_date_data['red_op_time'].append(each_rt_dte[6])
                    full_date_data['status'].append(each_rt_dte[7])
                    full_date_data['cmnts'].append(each_rt_dte[8])
                    full_date_data['each_dt'].append(each_dt)
                    full_date_data['each_rt'].append(each_route)
                    scraped_time = each_rt_dte[11]

                df = pd.DataFrame(full_date_data)
                lst_of_days[each_dt] = df
                if scraped_time != None:
                    de = str(scraped_time).split(".")[0]
                    got_date = de.split(" ")[0]

                    got_date_new = got_date.split("-")[2]+"-"+got_date.split("-")[1]+"-"+got_date.split("-")[0]
                    scraped_time = got_date_new + " " + de.split(" ")[1]


                lst_of_scrapped[each_dt] = scraped_time
                days_lst.append(lst_of_days)

        route_data['days'] = days_lst
        route_data['name'] = each_route
        route_data['scrapped'] = lst_of_scrapped
        all_routes.append(route_data)

    return render_template('rest_of_top_routes.html',route_total_df=all_routes)

@app.route("/all_routes",methods=['POST','GET'])
def all_routes():
    db,cur = config_file.db_connection()
    sql = "SELECT distinct(route) FROM display_data"
    cur.execute(sql)
    data = cur.fetchall()
    unique_routes =[]
    for each_rt in data:
        unique_routes.append(each_rt[0])
    data = pd.DataFrame(unique_routes)
    if request.method == 'POST':
        rt_selected = request.form.get("route")#['route_sel']
        sql = "SELECT distinct(date) from display_data where route =%s"
        cur.execute(sql,rt_selected)
        route_data = {}
        days_lst = []
        today = datetime.datetime.now()
        for each_date in cur.fetchall():
            each_dt = each_date[0]
            print(each_dt,type(each_dt))
            each_dt = datetime.datetime.strftime(each_dt
            ,"%d-%m-%Y")
            print(each_dt)#,type(each_dt))

            cur.execute("select * FROM display_data where route = '%s' and date = '%s'" %(rt_selected,each_dt))
            full_date_data = {}
            headers = ['sno','opr','abhi_inv','red_inv','diff','abhi_op_time','red_op_time','status','cmnts','each_dt','each_rt']
            for each in headers :
                full_date_data[each] =[]

            lst_of_days = {}
            for each_rt_dte in cur.fetchall():
                full_date_data['sno'].append(each_rt_dte[0])
                full_date_data['opr'].append(each_rt_dte[1])
                full_date_data['abhi_inv'].append(each_rt_dte[2])
                full_date_data['red_inv'].append(each_rt_dte[3])
                full_date_data['diff'].append(each_rt_dte[4])
                full_date_data['abhi_op_time'].append(each_rt_dte[5])
                full_date_data['red_op_time'].append(each_rt_dte[6])
                full_date_data['status'].append(each_rt_dte[7])
                full_date_data['cmnts'].append(each_rt_dte[8])
                full_date_data['each_dt'].append(each_dt)
                full_date_data['each_rt'].append(rt_selected)

            df = pd.DataFrame(full_date_data)
            lst_of_days[each_dt] = df
            days_lst.append(lst_of_days)
        route_data['days'] = days_lst
        route_data['name'] = rt_selected

        return render_template("all_routes.html", routes_data= route_data,routes=unique_routes)
    return render_template("all_routes.html",routes=unique_routes,route_data={},data=data)


@app.route("/",methods=['POST','GET'])
def dashboard():
    try:
        db,cur = config_file.db_connection()
        today_date = datetime.datetime.today().strftime('%d-%m-%Y')
        today_date = datetime.datetime.strptime(today_date,"%d-%m-%Y")
        sql = "SELECT route,DATE,SUM(abhibus_inventory),SUM(redbus_inventory) FROM display_data GROUP BY route,DATE"
        cur.execute(sql)
        result = {}
        headers = ['route','date','abhi_inv','red_inv','diff','percent']
        for each_header in headers :
            result[each_header] = []
        for each_row in cur.fetchall():
            each_dt1 = each_row[1]
            each_dt = datetime.datetime.strptime(each_dt1,"%d-%m-%Y")
            if each_dt >= today_date:
                result['route'].append(each_row[0])
                result['date'].append(each_row[1])
                result['abhi_inv'].append(each_row[2])
                result['red_inv'].append(each_row[3])
                result['diff'].append(int(each_row[3])-int(each_row[2]))
                dif = int(each_row[3])-int(each_row[2])
                red = int(each_row[3])
                res = int((dif/red)*100)
                result['percent'].append(res)
        df = pd.DataFrame(result)
        return render_template('dashboard.html',data=df)
    except:
        return render_template("error_page.html")

@app.route("/route_info",methods=['POST','GET'])
def route_info():
    print("hi Praveen")
    route = request.form['route']
    date_selected  = request.form['date']
    print(route,date_selected)
    df = compare.get_data(date_selected,route)
    opr_count = df.shape[0]
    ab_bus_count = df['Abhibus Inventory'].sum()
    rd_bus_count = df['Redbus Inventory'].sum()
    if ab_bus_count >= rd_bus_count:
        bus_count = rd_bus_count
    else:
        bus_count = ab_bus_count

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
    total_bus_lst = bus_sum

    source = route.split("-")[0]
    dest = route.split("-")[1]

    print(df)
    print(datetime.datetime.now())
    return render_template('route_search_details.html',data = df, date=date_selected,src = source, dest=dest,
    total_bus_lst= bus_sum ,total_oprs_lst= opr_count)

    #return render_template('route_search.html')
#select id
@app.route("/map_operators")
def map_operator():
    db,cur = config_file.db_connection()
    cur.execute("SELECT operator,id from redbus_operator_master_id")
    red_list = cur.fetchall()
    red_op_list = []
    for each_red in red_list:
        red_op_list.append(each_red[0])

    #print(len(red_op_list))

    cur.execute("SELECT operator,id from abhibus_operator_master_id")
    abhi_list = cur.fetchall()
    abhi_op_list = []
    for each_abhi in abhi_list:
        abhi_op_list.append(each_abhi[0])
    #print(len(abhi_op_list))

    red_op_list = json.dumps(red_op_list)
    abhi_op_list = json.dumps(abhi_op_list)

    return render_template("map_operators.html", red = red_op_list, abhi = abhi_op_list)
#abhibus update status
@app.route("/abhibus_update",methods=['POST','GET'])
def abhi_update():
    abhi_opr = request.form['abhibus']
    abhi_opr1  = request.form['abhibus1']

    print(abhi_opr,abhi_opr1)
    db,cur = config_file.db_connection()
    cur.execute("SELECT id from abhibus_operator_master_id where operator = '%s'"%abhi_opr)

    for each_id in cur.fetchall():
        id = each_id[0]
    status = "Already Mapped"
    if id != 0:
        cur.execute("UPDATE abhibus_operator_master_id SET id = %s WHERE operator ='%s'"%(id,abhi_opr1))
        db.commit()
        status = "Mapped"

    cur.execute("SELECT operator,id from redbus_operator_master_id")
    red_list = cur.fetchall()
    red_op_list = []
    for each_red in red_list:
        red_op_list.append(each_red[0])
    print(len(red_op_list))
    cur.execute("SELECT operator,id from abhibus_operator_master_id")
    abhi_list = cur.fetchall()
    abhi_op_list = []
    for each_abhi in abhi_list:
        abhi_op_list.append(each_abhi[0])
    print(len(abhi_op_list))

    red_op_list = json.dumps(red_op_list)
    abhi_op_list = json.dumps(abhi_op_list)
    return render_template("map_operators.html",status= status,red = red_op_list,abhi =abhi_op_list)

#redbus update status
@app.route("/redbus_update",methods=['POST','GET'])
def red_update():
    red_opr = request.form['redbus']
    red_opr1  = request.form['redbus1']


    db,cur = config_file.db_connection()
    cur.execute("SELECT id from redbus_operator_master_id where operator = '%s'"%red_opr)

    for each_id in cur.fetchall():
        id = each_id[0]
    status = "Already Mapped"
    if id != 0:
        cur.execute("UPDATE redbus_operator_master_id SET id = %s WHERE operator ='%s'"%(id,red_opr1))
        db.commit()
        status = "Mapped"

    cur.execute("SELECT operator,id from redbus_operator_master_id")
    red_list = cur.fetchall()
    red_op_list = []
    for each_red in red_list:
        red_op_list.append(each_red[0])
    print(len(red_op_list))
    cur.execute("SELECT operator,id from abhibus_operator_master_id")
    abhi_list = cur.fetchall()
    abhi_op_list = []
    for each_abhi in abhi_list:
        abhi_op_list.append(each_abhi[0])
    print(len(abhi_op_list))


    red_op_list = json.dumps(red_op_list)
    abhi_op_list = json.dumps(abhi_op_list)
    return render_template("map_operators.html",status=status,red = red_op_list,abhi =abhi_op_list)
# used to update operator
@app.route("/update_operators")
def update_opr1():
    db,cur = config_file.db_connection()
    cur.execute("SELECT operator,id from redbus_operator_master_id")
    red_list = cur.fetchall()
    red_op_list = []
    for each_red in red_list:
        red_op_list.append(each_red[0])

    #print(len(red_op_list))

    cur.execute("SELECT operator,id from abhibus_operator_master_id")
    abhi_list = cur.fetchall()
    abhi_op_list = []
    for each_abhi in abhi_list:
        abhi_op_list.append(each_abhi[0])
    #print(len(abhi_op_list))


    red_op_list = json.dumps(red_op_list)
    abhi_op_list = json.dumps(abhi_op_list)

    sql = "SELECT operator,id from abhibus_operator_master_id where map_status = 1"
    cur.execute(sql)
    opr = cur.fetchall()

    dict = {'abhi_opr':[],'red_opr':[],'status':[]}

    for each in opr:
        abhi_id = each[1]
        opr_abhi = each[0]
        sql = 'SELECT operator,id from redbus_operator_master_id where id = "%s"'
        cur.execute(sql,abhi_id)
        red_oprs = cur.fetchall()
        for each_red in red_oprs:
            opr_red = each_red[0]
            red_id = each_red[1]
            dict['abhi_opr'].append(opr_abhi)
            dict['red_opr'].append(opr_red)
            dict['status'].append("Mapped")

    df = pd.DataFrame(dict)

    return render_template("update_operators.html", red = red_op_list, abhi = abhi_op_list, df = df)

@app.route("/update",methods=['POST','GET'])
def update():
    abhi_opr = request.form['abhibus']
    red_opr  = request.form['redbus']

    print(abhi_opr,red_opr)
    db,cur = config_file.db_connection()
    sql = "SELECT id from redbus_operator_master_id where lower(operator) = %s"
    cur.execute(sql,(red_opr.lower()))
    for each_id in cur.fetchall():
        id = each_id[0]
        print("id is ",id)
    sql = "UPDATE abhibus_operator_master_id SET id = %s, map_status = %s WHERE lower(operator) = %s"
    cur.execute(sql,(id,1,abhi_opr.lower()))
    db.commit()
    sql = "SELECT operator,id from redbus_operator_master_id"
    cur.execute(sql)
    red_list = cur.fetchall()
    red_op_list = []
    for each_red in red_list:
        red_op_list.append(each_red[0])

    #print(len(red_op_list))

    sql = "SELECT operator,id from abhibus_operator_master_id"
    cur.execute(sql)
    abhi_list = cur.fetchall()
    abhi_op_list = []
    for each_abhi in abhi_list:
        abhi_op_list.append(each_abhi[0])
    #print(len(abhi_op_list))

    abhi_selected  = request
    red_op_list = json.dumps(red_op_list)
    abhi_op_list = json.dumps(abhi_op_list)


    sql = "SELECT operator,id from abhibus_operator_master_id where map_status = 1"
    cur.execute(sql)
    opr = cur.fetchall()

    dict = {'abhi_opr':[],'red_opr':[],'status':[]}

    for each in opr:
        abhi_id = each[1]
        opr_abhi = each[0]
        sql = 'SELECT operator,id from redbus_operator_master_id where id = "%s"'
        cur.execute(sql,abhi_id)
        red_oprs = cur.fetchall()
        for each_red in red_oprs:
            opr_red = each_red[0]
            red_id = each_red[1]
            dict['abhi_opr'].append(opr_abhi)
            dict['red_opr'].append(opr_red)
            dict['status'].append("Mapped")

    df = pd.DataFrame(dict)

    return render_template("update_operators.html",status="Mapped",red = red_op_list,abhi =abhi_op_list,df =df)

#used to map operator
@app.route('/mapped_operators',methods=['POST','GET'])
def already_mapped_operator():
    print("hello")
    db,cur = config_file.db_connection()
    sql = "SELECT operator,id from abhibus_operator_master_id where map_status = 1"
    cur.execute(sql)
    opr = cur.fetchall()
    opr_list = []

    dict = {'abhi_opr':[],'red_opr':[],'status':[]}

    for each in opr:
        abhi_id = each[1]
        opr_abhi = each[0]
        opr_list.append(each[0])
        sql = "SELECT operator,id from redbus_operator_master_id where id = %s"
        cur.execute(sql,abhi_id)
        red_oprs = cur.fetchall()
        for each_red in red_oprs:
            opr_red = each_red[0]
            red_id = each_red[1]
            dict['abhi_opr'].append(opr_abhi)
            dict['red_opr'].append(opr_red)
            dict['status'].append("Mapped")
    print(dict)
    return None

def testing():
    db,cur = config_file.db_connection()
    sql = "INSERT INTO test VALUES(10)"
    #print("hi")
    cur.execute(sql)
    #db.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(func=testing, trigger="interval", seconds=5)
# scheduler.start()

if __name__ == '__main__':
#    app.run(host='192.10.113.22',debug=True)
    #app.run(host= '0.0.0.0',debug=True)
    app.run(debug = True)
