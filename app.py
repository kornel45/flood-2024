import os

import altair as alt
import pandas as pd
import streamlit as st

from data import get_cities, get_city_data


def load_df(path):
    df = pd.read_csv(path, sep=';')
    df = df[['Czas pomiaru', 'Woda']]
    df['Woda'] = df['Woda'].str.replace(',', '.').astype(float)
    df['Czas pomiaru'] = df['Czas pomiaru'].apply(pd.to_datetime)
    return df


def load_dfs():
    result = []
    files = os.listdir("data")
    files_order = lambda x: 'aaaa' if 'kłodzko' in x.lower() else x.lower()
    for file in sorted(files, reverse=True, key=files_order):
        title = file.replace('.csv', '')
        df = load_df(f"data/{file}")
        result.append([title, df])
    return result


if __name__ == '__main__':
    st.set_page_config(layout="wide")
    st.write("### Woda w powiecie kłodzkim")
    age = st.slider("Ile godzin danych?", 24, 60, step=12, value=36)

    data_container = st.container()
    dfs = load_dfs()
    n, m = 3, 7
    i = j = 0

    url = 'http://lsop.powiat.klodzko.pl/index.php/woda'
    city_data = get_cities(url)

    for city in city_data:
        # okr is period in hours
        params = {'stc': city_data[city]['id'], 'dta': '2024-09-14', 'okr': age, 'typ': 1}
        get_city_data(city, params)

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

                with container:
                    title = alt.TitleParams(title, anchor='middle')

                    line = alt.Chart(df).mark_rule(color='red').encode(y='max')

                    c = (
                            alt.Chart(df, title=title)
                            .mark_circle()
                            .encode(x='Czas pomiaru', y="Woda", tooltip=['Czas pomiaru', "Woda"])
                            + line
                    )

                    st.altair_chart(c, use_container_width = True)
