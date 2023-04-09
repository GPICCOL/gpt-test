import os
import openai
import pandas as pd

# Read environment and import environment variables
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

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

# Function: GPT response extraction function - 
def response_extract(gpt_text):
  response = gpt_text.strip()
  response = ''.join(response.splitlines())
  return response

# Create the basic prompt
prompts = {"python": "Given the following question for a Python program, I need you to \
evaluate some code on a scale of 1 to 10 and breifly explain your evaluation. \
Here is the original question: ", "sql": "Our relational database has a schema with two tables called \
STUDENT(sID, sNAme, GPA, sizeHS with primary key sID and COLLEGE(cNAme, state, enrollment) with primary \
key cName. STUDENT and COLLEGE are in a many-to-many relationship called APPLY(sID, cName, major, decision) with sID and cName \
as the foreign keys. I need you to evaluate some code on a scale of 1 to 10 and breifly explain your evaluation. \
Here is the original question: "}

# Read the data, starting with the questions
df = pd.read_excel('coding_exam.xlsx', header=None, sheet_name='questions', usecols='A:F', skiprows=0)
questions = {}
keys = df.iloc[0].tolist()  # extract the first row as a list of keys
values = df.iloc[1].tolist()  # extract the second row as a list of values
questions = dict(zip(keys, values))  # create the dictionary using the zip function


# Read Python answers by each student
df = pd.read_excel('coding_exam.xlsx', sheet_name='answers', usecols='A:C', skiprows=0)
python_answers = {}
for index, row in df.iterrows():
  username = row[0]
  answers = (row[1], row[2])
  python_answers[username] = answers
  
# Read SQL answers by each student
df = pd.read_excel('coding_exam.xlsx', sheet_name='answers', usecols='A,D:G', skiprows=0)
sql_answers = {}
for index, row in df.iterrows():
  username = row[0]
  answers = (row[1], row[2], row[3], row[4])
  sql_answers[username] = answers
  
python_prompts = {}
for username in python_answers.keys():
    prompt_1 = prompts["python"] + questions["q1"] + "The answer is: \n" + python_answers[username][0]
    prompt_2 = prompts["python"] + questions["q2"] + "The answer is: \n" + python_answers[username][1]
    python_prompts[username] = (prompt_1, prompt_2)

sql_prompts = {}
for username in sql_answers.keys():
    prompt_1 = prompts["sql"] + questions["q3"] + "The answer is: \n" + sql_answers[username][0]
    prompt_2 = prompts["sql"] + questions["q4"] + "The answer is: \n" + sql_answers[username][1]
    prompt_3 = prompts["sql"] + questions["q5"] + "The answer is: \n" + sql_answers[username][2]
    prompt_4 = prompts["sql"] + questions["q6"] + "The answer is: \n" + sql_answers[username][3]
    sql_prompts[username] = (prompt_1, prompt_2, prompt_3, prompt_4)

python_evaluations = {}
for user in python_prompts.keys():
    python_evaluations[user] = []  # create an empty list to store evaluations for each user
    for prompt in python_prompts[user]:
        response = invoke_gpt(prompt)
        evaluation = response_extract(response["choices"][0]["text"])
        python_evaluations[user].append(evaluation)  # add the evaluation to the list for this user

sql_evaluations = {}
for user in sql_prompts.keys():
    sql_evaluations[user] = []  # create an empty list to store evaluations for each user
    for prompt in sql_prompts[user]:
        response = invoke_gpt(prompt)
        evaluation = response_extract(response["choices"][0]["text"])
        sql_evaluations[user].append(evaluation)  # add the evaluation to the list for this user

# write Python evaluations to CSV
dfp = pd.DataFrame.from_dict(python_evaluations, orient='index')
dfp.index.name = 'User'
dfp.to_csv('python_evaluations.csv')

# write SQL evaluations to CSV
dfs = pd.DataFrame.from_dict(sql_evaluations, orient='index')
dfs.index.name = 'User'
dfs.to_csv('sql_evaluations.csv')



