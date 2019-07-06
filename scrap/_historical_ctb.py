"""
THIS IS JUST A SLIGHTLY MODIFIED EXPORT OF A NOTEBOOK. NOT MEANT FOR USE. JUST COPY/PASTES.

# Resources
On https://stackoverflow.com/questions/16143266/get-bitcoin-historical-data:
found a great resource for bitcoin sales on many many exchanges: http://api.bitcoincharts.com/v1/csv/

Source for other coins: https://www.cryptodatasets.com/platforms/Bitfinex/
The bitcoincharts csvs (gz) don't have headers. The meaning of the three columns are:

     column 1) the trade's timestamp, column 2) the price, column 3) the volume of the trade

"""

import numpy as np
import os

from nioc.bitcoincharts import save_folder, download_gz, df_of_csv_file, delete_extreme_prices, daily_price_mean



# # Parsing the bitcoincharts data

import pandas as pd
import datetime

# In[7]:


df = df_of_csv_file('localbtcUSD.csv.gz', folder=save_folder)
df = delete_extreme_prices(df, p=99.9)

# In[9]:


df.tail()

# In[280]:


ddf = daily_price_mean(df)
print(ddf.head(3))
ddf.plot(figsize=(18, 8));

# In[ ]:

t = ddf.copy()
t['price_vol'] = t['price'] * t['vol']
tt = t.groupby('ts').sum()

ddf['avg_price'] = tt['price_vol'] / tt['vol']
tt = tt[['avg_price']]
w = tt[['avg_price']].reset_index(drop=False)
w.plot(x='ts', y='avg_price', figsize=(18, 8))

# In[279]:


ddf.plot(figsize=(18, 8));

# In[265]:


t = df.index.values[0]
t.astype('datetime64[D]')

# In[251]:


datetime.datetime.date(df.index.values[0])

# In[264]:


t.astype(datetime.datetime)

# In[260]:


daily_price_mean(df).head()

# In[282]:


t = df.copy()

# In[283]:


t['price_vol'] = t['price'] * t['vol']
tt = t.groupby('ts').sum()
print(tt.head())

tt['avg_price'] = tt['price_vol'] / tt['vol']
tt = tt[['avg_price']]
w = tt[['avg_price']].reset_index(drop=False)
w.plot(x='ts', y='avg_price', figsize=(18, 8))

# In[155]:


time_delta = datetime.timedelta(days=365)

# In[173]:


i = (w['ts'] + datetime.timedelta(days=365))[:5]
ww = w.set_index('ts')
www = ww.loc[i]

# In[193]:


ww = w.set_index('ts')

# In[203]:


www = (ww / ww.shift(365)).reset_index()
www.plot(x='ts', y='avg_price', logy=True, figsize=(18, 8))

# In[181]:


rng = pd.date_range('1/1/2011', periods=90, freq='M')
s = pd.DataFrame({'value': range(1, 91), 'date': rng})
s = s.set_index('date')
print(s.head())
s.shift(12)

# In[177]:


ww.shift(1, freq=time_delta)

# In[160]:


d = list()
for _, row in w.iterrows():
    t1 = row['avg_price']
row

# In[158]:


w['ts'].iloc[0] + time_delta

# In[149]:


w['ts'].iloc[1] - w['ts'].iloc[0]

# In[105]:


x = t.head().iloc[0]['ts']
x.date()

# In[97]:


t['ts'][:5]

# In[98]:


t = t.sort_values('ts')
t.head(10)

# In[99]:


# t['ts'] = pd.to_datetime(t['ts'])
t = t.set_index('ts')
t = t.resample("1d").sum().fillna(np.nan).rolling(window=3, min_periods=1).mean()

# t.plot(x='ts', y='btc_price', figsize=(18, 8));
t.head()

# In[94]:


len(df)

# In[91]:


len(np.unique(t.index.values)) == len(t)

# In[93]:


(52.21 + 40.00 + 70.3) / 3

# In[71]:


t = t[['btc_price']].reset_index(drop=False)

# In[74]:


d.plot(x='ts', y='btc_price', figsize=(18, 8));

# In[29]:


max_btc_price = 1e11
df['btc_price'] = df['price'] / df['vol']
lidx = df['btc_price'] > max_btc_price
print("{} pts with btc_price > {} are being removed".format(sum(lidx), max_btc_price))
df = df.loc[~lidx]
d = df[['ts', 'btc_price']]
d.plot(x='ts', y='btc_price', figsize=(18, 8));

# In[28]:


df.loc[lidx]

# # Other things to try

# ## Live data

# https://www.bitstamp.net/api/ticker/

# # Possible code for live data from bitcoincharts

# In[ ]:


# import pusherclient
# import time
# import logging
# import sys
# import datetime
# import signal
# import os
#
# logging.basicConfig()
# log_file_fd = None
#
#
# def sigint_and_sigterm_handler(signal, frame):
#     global log_file_fd
#     log_file_fd.close()
#     sys.exit(0)
#
#
# class BitstampLogger:
#
#     def __init__(self, log_file_path, log_file_reload_path, pusher_key, channel, event):
#         self.channel = channel
#         self.event = event
#         self.log_file_fd = open(log_file_path, "a")
#         self.log_file_reload_path = log_file_reload_path
#         self.pusher = pusherclient.Pusher(pusher_key)
#         self.pusher.connection.logger.setLevel(logging.WARNING)
#         self.pusher.connection.bind('pusher:connection_established', self.connect_handler)
#         self.pusher.connect()
#
#     def callback(self, data):
#         utc_timestamp = time.mktime(datetime.datetime.utcnow().timetuple())
#         line = str(utc_timestamp) + " " + data + "\n"
#         if os.path.exists(self.log_file_reload_path):
#             os.remove(self.log_file_reload_path)
#             self.log_file_fd.close()
#             self.log_file_fd = open(log_file_path, "a")
#         self.log_file_fd.write(line)
#
#     def connect_handler(self, data):
#         channel = self.pusher.subscribe(self.channel)
#         channel.bind(self.event, self.callback)
#
#
# def main(log_file_path, log_file_reload_path):
#     global log_file_fd
#     bitstamp_logger = BitstampLogger(
#         log_file_path,
#         log_file_reload_path,
#         "de504dc5763aeef9ff52",
#         "live_trades",
#         "trade")
#     log_file_fd = bitstamp_logger.log_file_fd
#     signal.signal(signal.SIGINT, sigint_and_sigterm_handler)
#     signal.signal(signal.SIGTERM, sigint_and_sigterm_handler)
#     while True:
#         time.sleep(1)


# if __name__ == '__main__':
#     log_file_path = sys.argv[1]
#     log_file_reload_path = sys.argv[2]
#     main(log_file_path, log_file_reload_path
