import yfinance as yf
import psycopg2
from sqlalchemy import create_engine
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np
from pandas_datareader import data as pdr

# banco de dados
dbname = 'scrap_db'
user = 'postgres'
password = '123'
host = 'localhost'
port = '5432'

engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}')

conn = engine.connect()

query = "SELECT * FROM ativos;"

df = pd.read_sql(query, conn)

pd.set_option('display.max_rows', None, 'display.max_columns', None, 'display.max_colwidth', None)

ativo = df['name'].tolist()

# Selecionando o periodo
data = yf.download(ativo[5], start="2024-01-01", end="2024-03-30", interval="1wk")

yf.pdr_override()

df = pd.DataFrame(data)
df = df.reset_index()

# Regressão
p = -100
X = df.index[p:].values.reshape(-1, 1)
y = df['Close'][p:].values.reshape(-1, 1)

reg = LinearRegression().fit(X, y)

y_pred = reg.predict(X)

desvio_pad = np.std(y_pred)
sup = y_pred + desvio_pad*0.4
inf = y_pred - desvio_pad*0.4
sup2 = y_pred + desvio_pad*0.8
inf2 = y_pred - desvio_pad*0.8


def ma(values, n=200):
     
    return values.rolling(n).mean().dropna()

# Grafico
plt.style.use('dark_background')

fig, ax = plt.subplots()

ax.scatter(df.index[-150:], df['Close'][-150:], color='w')

ax.plot(ma(df['Close']), '-w')
ax.plot(X, y_pred, '--w')
ax.plot(X, sup, '--r')
ax.plot(X, inf, '--g')
ax.plot(X, sup2, '--r')
ax.plot(X, inf2, '--g')

# regra
df = df[p:]

df['y_pred'] = y_pred
df['inf'] = inf
df['inf2'] = inf2
df['sup'] = sup
df['sup2'] = sup2

# trade
pd.set_option('display.max_rows', None)

regra = np.where( y < inf, 'compra', 
        np.where( y > sup, 'venda',''))

position = np.where((regra != np.roll(regra, 1)) & 
                    (regra == 'compra'),'compra',
            np.where(
                (regra != np.roll(regra, 1)) & 
                (regra == 'venda'),'venda', ''))

position[0][0] = regra[0][0]

df['regra'] = regra
df['position'] = position

df[['Close', 'inf', 'sup', 'position']]
