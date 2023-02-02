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
rez_id = 2

#Function definitions
#Read and write from a MySQL DB instance function
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

#GPT response extraction function
def response_extract(gpt_text):
  responses = gpt_text.strip()
  responses = ''.join(responses.splitlines())
  responses = list(responses.split(sep="**separator**"))
  prompt_elements = []
  for res in responses:
    prompt_elements.append(res.split(sep=":")[1])
  prompt_elements = "; ".join(prompt_elements)
  return prompt_elements


#retrieve observations for a specifica reservation id
query = "SELECT type, content FROM observations WHERE rez_idrez = %(rez_idrez)s"
result = connect_db(query, rez_id)

#extract and format the observations from the tuple returned
prompt_items = []
for row in result:
    prompt_items.append(": ".join(map(str, row)))
prompt_text = "; ".join(prompt_items)

#Create the prompt for the review using a base and the observations
prompt_base = "Write 3 positive restaurant reviews in the syle of Yelp. Vary the degree of emphasis, making one review positive, one very positive and one over the top positive and excited. Keep each review under 100 words and return them as one string of text separating the reviews with this string: **separator**. Do not use any semicolons (;) in the reviews. Use only the following information to write each review: "

prompt_text = prompt_base + prompt_text

#Contact GPT3 to create the review and extract the text of the response
response = openai.Completion.create(
  model="text-davinci-003",
  prompt=prompt_text,
  max_tokens=300,
  temperature=0.7
)

prompt_text = response_extract(response["choices"][0]["text"])


# reviews = response["choices"][0]["text"]
# reviews = list(reviews.split(sep="**separator**"))
# reviews = reviews[1:]
# prompt_reviews = []
# for review in reviews:
#   prompt_reviews.append(review.split(sep=": ")[1])
# 
# prompt_text = "; ".join(prompt_reviews)

#Create the prompt for the title using a base and the  review text
prompt_title = "Write a title of less than 10 words for each of the following 3 restaurant reviews. Use a numbered list with a colon (:) as the separator between the number and the title: " + prompt_text
prompt_title

#Contact GPT3 to create the review and extract the text of the response (the title)
response = openai.Completion.create(
  model="text-davinci-003",
  prompt=prompt_title,
  max_tokens=120,
  temperature=0.7
)

# titles = response["choices"][0]["text"]
# titles = list(titles.split(sep="\n\n"))
# titles = titles[1:]

titles = response_extract(response["choices"][0]["text"])

#Loop through the reviews and titles to create the records value
#Write the titles and responses in the review table using the correct foreign key value
query = "INSERT INTO reviews (title, content, rez_idrez) VALUES (%s, %s, %s)"
# for item in items:
#   # TODO: write code...
records = [
  (title, review, rez_id),
  # ("title4", "content4", rez_id),
  ]
connect_db(query, records)



