import mysql.connector

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="mrranmoru98",
  database="CaseNumber"
)
mycursor = mydb.cursor()

def insertData(caseid, issuetype):
    sql = "INSERT INTO CaseID(caseid, issuetype) VALUES(%s, %s)"
    val = (caseid, issuetype)
    mycursor.execute(sql, val)
    mydb.commit()

def queryData(caseid, issuetype):
    mycursor.execute("SELECT caseid FROM CaseID WHERE caseid=" + caseid)
    myresult = mycursor.fetchall()
    if not len(myresult):
        print("Not in Database")
        insertData(caseid, issuetype)
        return true
    else:
        print("Already in Database")
        return false

