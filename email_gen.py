import os
import json
import smtplib
import datetime
import calendar

from mysql.connector import connect, Error

from dotenv import load_dotenv
load_dotenv()

#Database specifications
host_url = os.getenv("DATABASE_URL")
user = os.getenv("USERNAME")
password = os.getenv("PWD")
db = "gpt-db"

#Static email specifications
SERVER = "localhost"
EMAIL_PWD = os.getenv("EMAIL_PWD")
PORT = 1025
FROM = "mng.fusion.cuisine@gmail.com"
SUBJECT = "We hope you can help us!"

#Current reservation
rez_id = 1

#Functions definition
#Database connections
def read_db(query_arg, vals=[]):
  query_type = query_arg.upper().split(' ', 1)[0]
  try:
    with connect(
        host=host_url,
        user=user,
        password=password,
        database=db
    ) as connection:
        if query_type == "SELECT":
          select_query = query_arg
          with connection.cursor() as cursor:
            cursor.execute(select_query, { 'rez_idrez': vals})
            query_result = cursor.fetchall()
        else:
          query_result = "This function handles only SELECT queries"
  except Error as e:
    print(e)
  return query_result

#Retrieve titles and reviews and for a specifica reservation id
query = "SELECT idreviews, title, content, firstName, email, date FROM guest INNER JOIN rez ON guest.idguest=rez.guest_idguest INNER JOIN reviews ON rez.idrez=reviews.rez_idrez WHERE rez_idrez = %(rez_idrez)s"
result = read_db(query, rez_id)

fname = result[0][3]
TO = [result[0][4]]
d = result[0][5]
day = calendar.day_name[d.weekday()]

intro = "Dear " + fname +",\n\n We hope you will take a few minutes to help us spread the word about our restaurant. Our restaurant manager told us you had a nice time at M&G Fusion Cuisine last " + day + ".\n\nWe would love to get your help to let everyone know about your experience. Based on your discussion with [restaurant managere name] we drafted three possible reviews. Would you be so kind to copy and post the one you prefer to your favorite online review site? You can of course edit the review as you see fit. Anything you can do to help would be great and we thank you for it!\n\n"

closing = "\n\nYour friends at M&G Fusion Cuisine!"

titles = []
reviews = []
for item in result:
  titles.append("\n\n" + item[1] + "\n")
  reviews.append(item[2] + "\n")
  
res = [i + j for i, j in zip(titles, reviews)]
content = "".join(res)

TEXT = intro + content + closing

message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ",".join(TO), SUBJECT, TEXT)

server = smtplib.SMTP(SERVER, PORT)
server.sendmail(FROM, TO, message)
server.quit()
