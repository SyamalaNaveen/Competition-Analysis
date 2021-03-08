import pymysql

host     = "127.0.0.1"
username = "root"
password = "Naveen"
database = "final"

top_routes = ['Hyderabad-Vijayawada','Hyderabad-Bangalore','Bangalore-Hyderabad','Pune-Shirdi','Chennai-Coimbatore','Hyderabad-Visakhapatnam','Bangalore-Vijayawada',
'Hyderabad-Chennai','Delhi-Manali','Mumbai-Bangalore','Chennai-Bangalore','Bangalore-Chennai','Indore-Bhopal','Pune-Mumbai','Ahmedabad-Mumbai']

def db_connection():
    db = pymysql.connect(host,username,password,database,autocommit=True)
    cur = db.cursor()
    return db,cur
