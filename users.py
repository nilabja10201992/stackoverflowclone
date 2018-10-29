import mysql.connector
import json
import time

def checkuserexist(email):
    database = mysql.connector.connect(host="localhost",user="root",passwd="helloWORLD@123")
    cursor = database.cursor()
    cursor.execute("SELECT userid FROM stackoverflow.users where useremail= %s", (email,))
    data = cursor.fetchone()
    number_of_rows=cursor.rowcount
    if number_of_rows > 0 :
        return True
    else:
        return False

def addusers(username, alias, usermail, upasswd):
    database = mysql.connector.connect(host="localhost",user="root",passwd="helloWORLD@123")
    cursor = database.cursor()
    sql = "INSERT INTO stackoverflow.users (username, alias, useremail, userpass, userrating) VALUES (%s, %s, %s, %s, %s)"
    val = (username, alias , usermail, upasswd, 0)
    if checkuserexist(usermail):
        return -1
    else:
        cursor.execute(sql,val)
        database.commit()
        return 1

def getPassword(alias):
    database = mysql.connector.connect(host="localhost",user="root",passwd="helloWORLD@123")
    cursor = database.cursor()
    cursor.execute("SELECT userpass FROM stackoverflow.users where alias= %s", (alias,))
    data = cursor.fetchone()
    print (data[0])
    number_of_rows=cursor.rowcount
    if number_of_rows > 0 :
        return data[0]
    else:
        return None

def email_confirmation(email):
    database = mysql.connector.connect(host="localhost",user="root",passwd="helloWORLD@123")
    cursor = database.cursor()
    cursor.execute("UPDATE stackoverflow.users SET email_verified = 1 where useremail = %s", (email,))
    database.commit()
   
