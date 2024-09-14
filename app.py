import os
import threading
import time

import altair as alt
import pandas as pd
import schedule
import streamlit as st

from common import logger
from data import get_cities, refresh_data


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
    schedule.every(15).minutes.do(refresh_data, city_data=city_data)
    while True:
        schedule.run_pending()
        time.sleep(5)


if __name__ == '__main__':
    url = 'http://lsop.powiat.klodzko.pl/index.php/woda'

    city_data = get_cities(url)
    t = threading.Thread(target=schedule_refresh, args=(city_data,))
    t.start()

    st.set_page_config(layout="wide")
    st.write("### Woda w powiecie kłodzkim")

    data_container = st.container()
    dfs = load_dfs(city_data)
    n, m = 3, 7
    i = j = 0
    with data_container:
        containers = st.columns(n)
        while dfs:
            for container in containers:
                if not dfs:
                    break
                title, df = dfs.pop()

                try:
                    df['max'] = city_data[title]['max']
                except:
                    title = title + '.'
                    df['max'] = city_data[title]['max']

                offset_blue = (df['Woda'].max() / df['max'].max())
                offset_red = (df['max'].max() / df['Woda'].max())

                with container:
                    title = alt.TitleParams(title, anchor='middle')

                    if offset_red < 1:
                        stops = [
                            alt.GradientStop(color='lightblue', offset=0),
                            alt.GradientStop(color='blue', offset=0.8 * offset_red),
                            alt.GradientStop(color='darkred', offset=0.9 * offset_red),
                            alt.GradientStop(color='black', offset=1),
                        ]
                    else:
                        stops = [
                            alt.GradientStop(color='lightblue', offset=0),
                            alt.GradientStop(color='blue', offset=1),
                        ]

                    c = (
                        alt.Chart(df, title=title)
                        .mark_area(
                            line={'color': 'darkblue'},
                            color=alt.Gradient(
                                gradient='linear',
                                stops=stops,
                                x1=1, x2=1, y1=1, y2=0
                            )
                        )
                        .encode(
                            x=alt.X('Czas pomiaru', title='Czas pomiaru'),
                            y=alt.Y('Woda', title='Poziom wody'),
                            tooltip=['Czas pomiaru', "Woda"], y2=alt.value(0)
                        )

                    )

                    line = (alt.Chart(pd.DataFrame({'y': [df['max'].max()]}))
                            .mark_rule(color='red', size=2)
                            .encode(y='y'))
                    line_text = (alt.Chart(pd.DataFrame({
                        'y': [1.05 * df['max'].max()],
                        'x': [df['Czas pomiaru'].iloc[20]]
                    }))
                                 .mark_text(text='Poziom maksymalny')
                                 .encode(x='x', y='y'))
                    st.altair_chart(c + line + line_text, use_container_width=True)
