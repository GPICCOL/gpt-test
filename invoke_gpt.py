import os
import openai

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

response = invoke_gpt()
response_extract(response["choices"][0]["text"])
