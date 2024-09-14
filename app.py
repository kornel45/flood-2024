import os
import threading
import time

import pandas as pd
import streamlit as st

from chart import create_chart
from common import logger
from data import refresh_data, CITY_DATA


def load_df(path):
    df = pd.read_csv(path, sep=';')
    df = df[['Czas pomiaru', 'Woda']]
    df['Woda'] = df['Woda'].str.replace(',', '.').astype(float)
    df['Czas pomiaru'] = df['Czas pomiaru'].apply(pd.to_datetime)
    return df


def load_dfs(cities_data):
    result = []
    if not os.path.isdir("data"):
        os.mkdir("data")

    files = os.listdir("data")
    if not files:
        refresh_data(cities_data)
        files = os.listdir("data")
    files_order = lambda x: 'aaaa' if 'kłodzko' in x.lower() else x.lower()
    for file in sorted(files, reverse=True, key=files_order):
        title = file.replace('.csv', '')
        try:
            df = load_df(f"data/{file}")
            result.append([title, df])
        except:
            os.remove(f"data/{file}")
    return result


def schedule_refresh(city_data):
    logger.info('running scheduled data refresh')
    while True:
        refresh_data(city_data)
        time.sleep(5 * 60)


def schedule():
    with open('schedule', 'w') as f:
        f.write('yes')


def is_scheduled():
    if not os.path.isfile('schedule'):
        return False
    with open('schedule', 'r') as f:
        return f.read().lower() == 'yes'


if __name__ == '__main__':
    logger.info('starting app')
    url = 'http://lsop.powiat.klodzko.pl/index.php/woda'
    # if not is_scheduled():
    #     t = threading.Thread(target=schedule_refresh, args=(CITY_DATA,))
    #     t.start()
    #     schedule()

    st.set_page_config(layout="wide")
    st.write("### Woda w powiecie kłodzkim")

    # data_container = st.container()
    dfs = load_dfs(CITY_DATA)
    logger.info(len(dfs))
    # n, m = 3, 7
    # i = j = 0
    # with data_container:
    #     containers = st.columns(n)
    #     while dfs:
    #         for container in containers:
    #             if not dfs:
    #                 break
    #             title, df = dfs.pop()
    #             with container:
    #                 chart = create_chart(df, title)
    #                 st.altair_chart(chart, use_container_width=True)
