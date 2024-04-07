import yfinance as yf
import psycopg2
from sqlalchemy import create_engine
import pandas as pd

# banco de dados
dbname = 'annderoli'
user = 'postgres'
password = '123'
host = 'localhost'
port = '5432'

engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{dbname}')

conn = engine.connect()

query = "SELECT * FROM ativos;"

df = pd.read_sql(query, conn)

pd.set_option('display.max_rows', None, 'display.max_columns', None, 'display.max_colwidth', None)

ativo = df['name'].tolist()

# Selecionando o periodo
data = yf.download(ativo, start="2023-01-01", end="2024-01-01", interval="1wk")

data