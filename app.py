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

# Filtrando apenas ações Americanas
siglas = df['name'].str.split('.').str[0].tolist()

# Selecionando o periodo
data = yf.download(siglas[0], start="2023-01-01", end="2024-01-01", interval="1wk")

data