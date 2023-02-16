import sys
import os
import json
import openai
assert ('openai' in sys.modules), "The OpenaAI module did not import correclty"

from mysql.connector import connect, Error

#read environment and import environment variables
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
host_url = os.getenv("DATABASE_URL")
user = os.getenv("USERNAME")
password = os.getenv("PWD")
db = "gpt-db"

#Function definitions - DB Functions
#Function: Read from a MySQL DB instance
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
            cursor.execute(select_query, { 'field_name': vals})
            query_result = cursor.fetchall()
        else:
          query_result = "This function handles only SELECT queries"
  except Error as e:
    print(e)
  return query_result

#Function: Write to a MySQL DB instance 
def write_db(query_arg, vals=[]):
  query_type = query_arg.upper().split(' ', 1)[0]
  try:
    with connect(
        host=host_url,
        user=user,
        password=password,
        database=db
    ) as connection:
        if query_type == "INSERT":
          write_query = query_arg
          with connection.cursor() as cursor:
            cursor.executemany(write_query, vals)
            # cursor.execute(write_query, vals)
            connection.commit()
            query_result = "INSERT query executed"
        else:
          query_result = "This function handles only INSERT queries"
  except Error as e:
    print(e)
  return query_result

#Function: Change status of reviews
def change_status(reservation_id, status):
  update_query = "UPDATE rez SET rev_status = %(field_name)s WHERE idrez = %(field_name)s"
  vals=[]
  try:
    with connect(
        host=host_url,
        user=user,
        password=password,
        database=db
    ) as connection:
      with connection.cursor() as cursor:
        cursor.executemany(update_query, vals)
        # cursor.execute(write_query, vals)
        connection.commit()
        query_result = "UPDATE query executed"
  except Error as e:
    print(e)
  return query_result

#Function definitions - GPT Functions
#Function: Connect to GPT and pass the prompt, max_tokens and temperature
def invoke_gpt(text = "tell me something", tokens = 300, temp = 0.7):
  try:
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=text,
      max_tokens=tokens,
      temperature=temp
      )
  except Error as e:
    print(e)
  return response

#Function: GPT response extraction function - 
def response_extract(gpt_text):
  response = gpt_text.strip()
  response = ''.join(response.splitlines())
  return response

#Function: Make Reviews
def make_reviews(reservation_number, style = "Yelp", level = "positive"):
  #retrieve observations for a specifica reservation id
  query = "SELECT type, content FROM observations WHERE rez_idrez = %(field_name)s"
  result = read_db(query, reservation_number)
  assert len(result) > 0, f"You need at least one observation to proceed, you have {result}."
  #extract and format the observations from the tuple returned
  prompt_items = []
  for row in result:
    prompt_items.append(": ".join(map(str, row)))
  prompt_text = "; ".join(prompt_items)
  #Create the prompt for the review using a base and the observations
  prompt_base = "Write a " + level + " restaurant reviews in the syle of " + style + ". Keep the review under 120 words. Use only the following information to write the review: "
  prompt_text = prompt_base + prompt_text
  #Contact GPT3 to create the review and extract the text of the response
  #This is where I can loop and repeat if I have errors
  response = invoke_gpt(prompt_text, 300)
  review = response_extract(response["choices"][0]["text"])
  return review

#Function: Make titles
def make_titles(review_text):
  #Create the prompt for the title using a base and the  review text
  prompt_title = "Write a title of less than 10 words for the following restaurant reviews. The review is: " + review_text
  #Contact GPT3 to create the review and extract the text of the response (the title)
  response = invoke_gpt(prompt_title, 120)
  title = response_extract(response["choices"][0]["text"])
  return title

#Function: Exctract title and reviews, write to DB
def write_reviews(reservation_id, style = "Yelp", level = ["positive", "very positive", "over the top positive and excited"]):
  records = []
  for i in range(0, len(level)):
    review = make_reviews(reservation_id, level[i])
    title = make_titles(review)
    records.append((title, review, reservation_id))
  #Write the titles and responses in the review table using the correct foreign key value
  query = "INSERT INTO reviews (title, content, rez_idrez) VALUES (%s, %s, %s)"
  write_db(query, records)
  return records

##Main program
#retrieve reservation ID of rez with observations
query = "SELECT idrez FROM rez WHERE rev_status = %(field_name)s"
status = "Observed"
observed_rezids = read_db(query, status)
rez_id = []
for id in observed_rezids:
  for items in id:
    rez_id.append(items)
    
#loop above is the same as list compression syntax (which i need to understand): 
#rez_id = [item for id in observed_rezids for item in id]

level = ["positive", "very positive", "over the top positive and excited"]
rez_id =  [x for x in rez_id if x < 3]
for id in rez_id:
  written_records = write_reviews(id, level)
  #written_status = change_status(id, status = "Reviewed")
