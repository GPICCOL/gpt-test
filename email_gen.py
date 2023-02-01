import os
import json
from mysql.connector import connect, Error

from dotenv import load_dotenv
load_dotenv()

host_url = os.getenv("DATABASE_URL")
user = os.getenv("USERNAME")
password = os.getenv("PWD")
db = "gpt-db"

def connect_db(query_arg, vals=[]):
  query_type = query_arg.upper().split(' ', 1)[0]
  # print(query_type)
  # print(query_arg)
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
            cursor.execute(select_query)
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

query = "SELECT * FROM test WHERE id = 9"
query_result = connect_db(query)
for item in query_result:
  print(item[1])
  print(item[2])

