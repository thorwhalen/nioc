import os

import bs4
import numpy as np
import pandas as pd
import requests

from ut.util.time import utc_ms_to_utc_datetime

root_url = 'http://api.bitcoincharts.com/v1/csv/'

save_folder = os.path.expanduser('~/nioc/saves')
os.makedirs(save_folder, exist_ok=True)


def csv_html_list(url=root_url):
    r = requests.get(url)
    return r.content


def list_of_csv_files_from_html(html):
    b = bs4.BeautifulSoup(html)
    return list(filter(lambda x: x.endswith('gz'),
                       (bb.attrs['href'] for bb in b.findAll(name='a'))))


def download_gz(name, save_folder=save_folder, root_url=root_url):
    response = requests.get(root_url + name, stream=True)

    # Throw an error for bad status codes
    response.raise_for_status()

    with open(os.path.join(save_folder, name), 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)


def download_and_save_all_files_in_list(filenames=None, save_folder=save_folder, root_url=root_url):
    if filenames is None:
        filenames = list_of_csv_files_from_html(csv_html_list(url=root_url))

    for i, x in enumerate(filenames):
        print("{}: {}".format(i, x))
        try:
            download_gz(x, save_folder=save_folder, root_url=root_url)
        except Exception as e:
            print("!!! {}".format(e))

DFLT_FOLDER = save_folder

def df_of_csv_file(filepath='localbtcUSD.csv.gz', folder=DFLT_FOLDER):
    if not os.path.isfile(filepath):
        filepath = os.path.join(folder, filepath)
    df = pd.read_csv(filepath, compression='gzip', header=None, sep=',', quotechar='"')
    df.columns = ['ts', 'price', 'vol']

    df['ts'] = list(map(lambda x: utc_ms_to_utc_datetime(x * 1000), df['ts']))
    df.set_index('ts', inplace=True)
    return df


def delete_extreme_prices(df, p=99.9):
    price_cutoff = np.percentile(df['price'], p)
    lidx = df['price'] > price_cutoff
    print("{} pts with price > {} are being removed".format(sum(lidx), price_cutoff))
    return df.loc[~lidx]


def daily_price_mean(df):
    df = df.copy()
    df['avg_price'] = df['price'] * df['vol']
    df['day'] = list(map(lambda x: x.astype('datetime64[D]'), df.index.values))
    dg = df[['avg_price', 'day', 'vol']].groupby('day').sum()
    df['avg_price'] = df['avg_price'] / df['vol']
    return df
