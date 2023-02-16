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

#Function definitions - DB Functions
#Function: Read from a MySQL DB instance
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
            cursor.execute(select_query, { 'field_name': vals})
            query_result = cursor.fetchall()
        else:
          query_result = "This function handles only SELECT queries"
  except Error as e:
    print(e)
  return query_result

#Function: Change status of reviews
def change_status(reservation_id, status):
  update_query = "UPDATE rez SET rev_status = %s WHERE idrez = %s"
  vals=[]
  for id in reservation_id:
    vals.append((status, id))
  try:
    with connect(
        host=host_url,
        user=user,
        password=password_db,
        database=db
    ) as connection:
      with connection.cursor() as cursor:
        cursor.executemany(update_query, vals)
        # cursor.execute(write_query, vals)
        connection.commit()
        query_result = "UPDATE query executed, updates rows: " + str(cursor.rowcount)
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
    conf_message = "Message sent to " + html_message['To']
    return conf_message

#Retrieve reservation id of reservations in status = Reviewed
query = "SELECT idrez FROM rez WHERE rev_status = %(field_name)s"
current_status = "Reviewed"
reviewed_rezids = read_db(query, current_status)
rez_id = []
for id in reviewed_rezids:
  for items in id:
    rez_id.append(items)

#Retrieve email data and reviews
query = "SELECT reviews.idreviews, reviews.title, reviews.content, guest.firstName, guest.email, rez.date, staff.name, staff.title FROM guest INNER JOIN rez ON guest.idguest=rez.guest_idguest INNER JOIN reviews ON rez.idrez=reviews.rez_idrez INNER JOIN staff ON staff.idstaff=rez.staff_idstaff WHERE rez_idrez = %(field_name)s"

for id in rez_id:
  result = read_db(query, id)
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
#Collapse retrieved reviews and titles    
  res = [i + j for i, j in zip(titles, reviews)]
  content = "".join(res)
#Prepare body of the message
  intro = "<html><body><p>Dear " + fname +",<p>We hope you will take a few minutes to help us spread the word about our restaurant.  " + manager_name+ ", our " + manager_title + " told us you had a nice time at M&G Fusion Cuisine last " + day + ". </p><p> We would love your help to let everyone know about your experience. Based on your discussion with " + manager_name + " we drafted three possible reviews for you. Would you be so kind to copy and post the one you prefer to <a href='https://www.yelp.com/writeareview/biz/n-HwtvIHbogu2iCsOc5MQA?return_url=%2Fbiz%2Fn-HwtvIHbogu2iCsOc5MQA&review_origin=biz-details-war-button'>Yelp</a>, <a href='https://www.tripadvisor.com/UserReviewEdit-g40024-d7359790-City_Pork_Jefferson-Baton_Rouge_Louisiana.html'>Tripadvisor</a>, <a href='https://goo.gl/maps/rDbvTLUDbQe45Sdh6'>Google</a>, or your favorite online review site? </p><p> You can of course edit the review as you see fit. <i>Anything you can do to help would be great and we thank you for it!</i></p>"
  closing = "<p>Your friends at M&G Fusion Cuisine!</p></body></html>"
  body = intro + content + closing
#Send emails
  sending_status = send_email(sender_name, subject, body, sender, recipients, password_email)
  sending_status

update_status = change_status(rez_id, status = "Sent")
update_status

