import os
# import sqlalchemy.pool as pool
# from sqlalchemy import create_engine, text
# from tenacity import retry, wait_exponential, stop_after_attempt
import psycopg2
import sqlalchemy.pool as pool
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
params = {
    'user': os.environ['DB_USERNAME'],
    'password': os.environ['DB_PASSWORD'],
    'port': os.environ['DB_PORT'],
    'database': os.environ['DB_NAME'],
    'host': os.environ['DB_HOST']
}
#
# Returns a new connection to the database
def getconn():
    return psycopg2.connect(user=params['user'],
                          password=params['password'],
                          port=params['port'],
                          database=params['database'],
                          host=params['host'])

postgres_pool = pool.NullPool(getconn)
postgres_engine = create_engine("postgresql://", pool=postgres_pool)

def get_db_data(query):  
    with postgres_engine.connect() as connection:
        data = pd.read_sql(query, connection)
        return data
# postgres_pool = pool.NullPool(getconn)
# postgres_engine = create_engine("postgresql://", pool=postgres_pool)

# @retry(wait=wait_exponential(multiplier=2, min=1, max=10), stop=stop_after_attempt(5))
# def try_connection():
#     try:
#         with postgres_engine.connect() as connection:
#             stmt = text("SELECT 1")
#             connection.execute(stmt)
#         print("Connection to database successful.")

#     except Exception as e:
#         print("Connection to database failed, retrying. If connecting to the Plotly-hosted sample database, "
#               "then this database instance can take a few minutes to wake from its sleep-state.")
#         raise Exception

# try_connection()