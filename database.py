import mysql.connector

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="",
  database="CaseNumber"
)
mycursor = mydb.cursor()

def insertData(caseid, issuetype):
    sql = "INSERT INTO CaseID(caseid, issuetype) VALUES(%s, %s)"
    val = (caseid, issuetype)
    mycursor.execute(sql, val)
    mydb.commit()

def queryData(caseid):
    mycursor.execute("SELECT caseid FROM CaseID WHERE caseid=" + caseid)
    myresult = mycursor.fetchall()
    if not myresult:
        print("Not in Database")
        return False
    else:
        print("Already in Database")
        return True

