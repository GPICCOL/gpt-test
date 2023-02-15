import os
import json
import datetime
import calendar
import smtplib

from email.mime.text import MIMEText
from mysql.connector import connect, Error

from dotenv import load_dotenv
load_dotenv()

#Database specifications
host_url = os.getenv("DATABASE_URL")
user = os.getenv("USERNAME")
password_db = os.getenv("PWD")
db = "gpt-db"

#Static email specifications
sender_name = "M&G Fusion Cuisine Restaturant"
sender = os.getenv("EMAIL")
password_email = os.getenv("EMAIL_PWD")
subject = "Help us share your experience at M&G Fusion Cuisine!"
body = "This is the body of the text message"
recipients = ["lele.piccoli@gmail.com"]

#Current reservation
rez_id = 2

#Functions definition
#Database connections
def read_db(query_arg, vals=[]):
  query_type = query_arg.upper().split(' ', 1)[0]
  try:
    with connect(
        host=host_url,
        user=user,
        password=password_db,
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

#Function for sending emails
def send_email(name, subject, body, sender, recipients, password_email):
    html_message = MIMEText(body, 'html')
    html_message['Subject'] = subject
    html_message['From'] = name
    html_message['To'] = ', '.join(recipients)
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender, password_email)
    server.sendmail(sender, recipients + [sender], html_message.as_string())
    server.quit()

#Retrieve titles and reviews and for a specifica reservation id
query = "SELECT reviews.idreviews, reviews.title, reviews.content, guest.firstName, guest.email, rez.date, staff.name, staff.title FROM guest INNER JOIN rez ON guest.idguest=rez.guest_idguest INNER JOIN reviews ON rez.idrez=reviews.rez_idrez INNER JOIN staff ON staff.idstaff=rez.staff_idstaff WHERE rez_idrez = %(rez_idrez)s"
result = read_db(query, rez_id)

fname = result[0][3]
recipients = [result[0][4]]
manager_name = result[0][6]
manager_title = result[0][7]
d = result[0][5]
day = calendar.day_name[d.weekday()]
titles = []
reviews = []
for item in result:
  titles.append("<p><b>" + item[1] + "</b></p>")
  reviews.append("<p>" + item[2] + "</p>")
  
res = [i + j for i, j in zip(titles, reviews)]
content = "".join(res)

intro = "<html><body><p>Dear " + fname +",<p>We hope you will take a few minutes to help us spread the word about our restaurant.  " + manager_name+ ", our " + manager_title + " told us you had a nice time at M&G Fusion Cuisine last " + day + ". </p><p> We would love your help to let everyone know about your experience. Based on your discussion with " + manager_name + " we drafted three possible reviews for you. Would you be so kind to copy and post the one you prefer to <a href='https://www.yelp.com/writeareview/biz/n-HwtvIHbogu2iCsOc5MQA?return_url=%2Fbiz%2Fn-HwtvIHbogu2iCsOc5MQA&review_origin=biz-details-war-button'>Yelp</a>, <a href='https://www.tripadvisor.com/UserReviewEdit-g40024-d7359790-City_Pork_Jefferson-Baton_Rouge_Louisiana.html'>Tripadvisor</a>, <a href='https://goo.gl/maps/rDbvTLUDbQe45Sdh6'>Google</a>, or your favorite online review site? </p><p> You can of course edit the review as you see fit. <i>Anything you can do to help would be great and we thank you for it!</i></p>"

closing = "<p>Your friends at M&G Fusion Cuisine!</p></body></html>"

body = intro + content + closing

send_email(sender_name, subject, body, sender, recipients, password_email)


