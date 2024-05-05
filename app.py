import yfinance as yf
import psycopg2
from sqlalchemy import create_engine
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np
from pandas_datareader import data as pdr

# Configurações
yf.pdr_override()

# banco de dados
dbname = 'scrap_db'
user = 'postgres'
password = '123'
host = 'localhost'
port = '5432'

engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}')

conn = engine.connect()

query = "SELECT * FROM ativos;"

df_db = pd.read_sql(query, conn)

pd.set_option('display.max_rows', None, 'display.max_columns', None, 'display.max_colwidth', None)

# Acessando os Ativos do DB
ativos = df_db['name'].tolist()

data = yf.download(ativos, start="2024-01-01", end=None, interval="1wk")
data = data['Close'].dropna(axis=1)
data = data.reset_index()

# Regra
dfs = []

for ativo in data.columns:

    X = np.arange(len(data)).reshape(-1, 1)
    y = data[ativo].values.astype(float).reshape(-1, 1)
    reg = LinearRegression().fit(X, y)
    y_pred = reg.predict(X)

    # Premissa
    desvio_pad = np.std(y_pred)
    sup = y_pred + desvio_pad * 15
    inf = y_pred - desvio_pad * 15

    # Posição
    regra = np.where(y < inf, 'compra', np.where(y > sup, 'venda', ''))

    position = np.where((regra != np.roll(regra, 1)) & (regra == 'compra'), 'compra',
                np.where((regra != np.roll(regra, 1)) & (regra == 'venda'), 'venda', ''))

    position[0] = regra[0]

    df_ativo = pd.DataFrame({
        'Ativo': ativo,
        'Date': data['Date'],
        'Close': data[ativo],
        'Predicted_Close': y_pred.flatten(),
        'Position': position.flatten()
    })

    dfs.append(df_ativo)

df = pd.concat(dfs, ignore_index=True)
filtro = df.groupby('Ativo').tail(1)
lista = filtro[filtro['Position'] == 'compra']

lista