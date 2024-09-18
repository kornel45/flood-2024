from datetime import datetime, timedelta

import altair as alt
import pandas as pd
from altair import Tooltip

from data import CITY_DATA

pd.options.mode.chained_assignment = None


def create_chart(df, title, hours):
    try:
        df['max'] = CITY_DATA[title]['max']
    except:
        title = title + '.'
        df['max'] = CITY_DATA[title]['max']

    offset_red = (df['max'].max() / df['Woda'].max())

    title = alt.TitleParams(
        title, anchor='middle',
        # color='#c70029' if (df['max'].max() / df['Woda'].iloc[-1]) < 1 else None,
        fontSize=20
    )

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
            x=alt.X('Czas pomiaru', title='Czas pomiaru', axis=alt.Axis(format='%H:%M')),
            y=alt.Y('Woda', title='Poziom wody'),
            tooltip=[Tooltip('Czas pomiaru', format='%a %H:%M'),
                     Tooltip('Woda', title='Poziom wody')],
            y2=alt.value(0)
        )

    )

    line = (alt.Chart(pd.DataFrame({'y': [df['max'].max()]}))
            .mark_rule(color='red', size=2)
            .encode(y='y'))
    line_text = (alt.Chart(pd.DataFrame({
        'y': [1.05 * df['max'].max()],
        'x': [df['Czas pomiaru'].iloc[len(df) // 5]]
    }))
                 .mark_text(text='Poziom maksymalny')
                 .encode(x='x', y='y'))
    return c + line + line_text
