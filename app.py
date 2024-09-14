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
    if not os.path.isdir("data"):
        os.mkdir("data")
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

    data_container = st.container()
    dfs = load_dfs()
    n, m = 3, 7
    i = j = 0

    url = 'http://lsop.powiat.klodzko.pl/index.php/woda'
    city_data = get_cities(url)

    for city in city_data:
        # okr is period in hours
        params = {'stc': city_data[city]['id'], 'dta': '2024-09-14', 'okr': 36, 'typ': 1}
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

                offset_blue = (df['Woda'].max() / df['max'].max())
                offset_red = (df['max'].max() / df['Woda'].max())

                print(offset_red, offset_blue)

                with container:
                    title = alt.TitleParams(title, anchor='middle')

                    if offset_red < 1:
                        stops = [
                            alt.GradientStop(color='lightblue', offset=0),
                            alt.GradientStop(color='blue', offset=0.6 * offset_red),
                            alt.GradientStop(color='darkred', offset=0.7),
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
                                x1=1,
                                x2=1,
                                y1=1,
                                y2=0
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
