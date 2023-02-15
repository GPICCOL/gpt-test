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
# rez_id = 1

#Function definitions
#Function: Connect to GPT and pass the prompt, max_tokens and temperature
def invoke_gpt(text = "tell me something", tokens = 300, temp = 0.7):
  response = openai.Completion.create(
    model="text-davinci-003",
    prompt=text,
    max_tokens=tokens,
    temperature=temp
    )
    # assert not response, f"The GPT function is returning an empty string"
  return response

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
            cursor.execute(select_query, { 'rez_idrez': vals})
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
            query_result = "Write query executed"
        else:
          query_result = "This function handles only INSERT queries"
  except Error as e:
    print(e)
  return query_result

#Function: GPT response extraction function - 
#ERRORS: when the response is messy and we dont have the normal structure it breaks need to do a check, if there are not three elements, kick out and inquire again with GPT and catch any other error gracefully
def response_extract(gpt_text):
  responses = gpt_text.strip()
  responses = ''.join(responses.splitlines())
  responses = list(responses.split(sep="**separator**"))
  # print(len(responses))
  prompt_elements = []
  for res in responses:
    print(res)
    prompt_elements.append(res.split(sep=":")[1])
  prompt_elements = "; ".join(prompt_elements)
  print(prompt_elements)
  return prompt_elements

#Function: Make Reviews
def make_reviews(reservation_number):
  rez_id = reservation_number
  #retrieve observations for a specifica reservation id
  query = "SELECT type, content FROM observations WHERE rez_idrez = %(rez_idrez)s"
  result = read_db(query, rez_id)
  assert len(result) > 0, f"You need at least one observation to proceed, you have {result}."

  #extract and format the observations from the tuple returned
  prompt_items = []
  for row in result:
    prompt_items.append(": ".join(map(str, row)))
  prompt_text = "; ".join(prompt_items)

  #Create the prompt for the review using a base and the observations
  prompt_base = "Write 3 positive restaurant reviews in the syle of Yelp. Vary the degree of emphasis, making one review positive, one very positive and one over the top positive and excited. Keep each review under 100 words. Mark the beginning of each review with a sequential number followed by a colon (:). Use the text **separator** between reviews. Do not use any semicolons (;) in the reviews. Use only the following information to write each review: "
  
  prompt_text = prompt_base + prompt_text
  
  #Contact GPT3 to create the review and extract the text of the response
  #This is where I can loop and repeat if I have errors
  response = invoke_gpt(prompt_text, 300)
  reviews = response_extract(response["choices"][0]["text"])
  return reviews

#Function: Make titles
def make_titles(review_text):
  print(type(review_text))
  #Create the prompt for the title using a base and the  review text
  prompt_title = "Write a title of less than 10 words for each of the following 3 restaurant reviews. Mark the beginning of each title with a sequential number followed by a colon (:). Use the text **separator** between titles. The reviews are: " + review_text
  
  #Contact GPT3 to create the review and extract the text of the response (the title)
  response = invoke_gpt(prompt_title, 120)
  
  titles = response_extract(response["choices"][0]["text"])
  return titles

#Function: Exctract title and reviews, write to DB
def write_reviews(title_list, review_list):
  #Format titles and reviews for INSERT query
  titles = list(title_list.split(";"))
  reviews = list(review_list.split(";"))
  records = []
  for i in range(0, len(titles)):
    title = titles[i].strip()
    review = reviews[i].strip()
    records.append((title, review, rez_id))
  
  #Write the titles and responses in the review table using the correct foreign key value
  query = "INSERT INTO reviews (title, content, rez_idrez) VALUES (%s, %s, %s)"
  write_db(query, records)


##Main program
rez_id = 1

reviews = make_reviews(rez_id)
titles = make_titles(reviews)
write_reviews(titles, reviews)




