import os
import json
import openai

from mysql.connector import connect, Error

#read environment and import environment variables
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
host_url = os.getenv("DATABASE_URL")
user = os.getenv("USERNAME")
password = os.getenv("PWD")
db = "gpt-db"

#function definitions
#read and write from a MySQL DB instance
def connect_db(query_arg, vals=[]):
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
        elif query_type == "INSERT":
          write_query = query_arg
          with connection.cursor() as cursor:
            cursor.executemany(write_query, vals)
            # cursor.execute(write_query, vals)
            connection.commit()
            query_result = "Insert query, no results to show"
        else:
          query_result = "This function handles only SELECT and INSERT queries"
  except Error as e:
    print(e)
  return query_result

#retrieve observations for a specifica reservation
rez_id = 2
query = "SELECT type, content FROM observations WHERE rez_idrez = %(rez_idrez)s"
result = connect_db(query, rez_id)

prompt_items = []
for row in result:
    prompt_items.append(": ".join(map(str, row)))
prompt_text = "; ".join(prompt_items)

# prompt_base = "Write a positive restaurant review in the syle of Yelp. Vary the degree of emphsis, making one review positive, one very positive and one over the top positive and excited. Keep each one under 100 words. Use only the following elements: "
prompt_base = "Write a positive restaurant review in the syle of Yelp. Keep it under 100 words. Use only the following elements: "

prompt_text = prompt_base + prompt_text

response = openai.Completion.create(
  model="text-davinci-003",
  prompt=prompt_text,
  max_tokens=300,
  temperature=0.7
)
prompt_text
response
review = response["choices"][0]["text"]
prompt_title = "Write a title of less than 10 words for the following restaurant review: " + review

response = openai.Completion.create(
  model="text-davinci-003",
  prompt=prompt_title,
  max_tokens=120,
  temperature=0.7
)
title = response["choices"][0]["text"]

query = "INSERT INTO reviews (title, content, rez_idrez) VALUES (%s, %s, %s)"
records = [
  (title, review, rez_id),
  # ("title4", "content4", rez_id),
  ]
connect_db(query, records)


