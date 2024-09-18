import requests
import streamlit as st
from streamlit_flow import streamlit_flow, StreamlitFlowNode, StreamlitFlowEdge

from city_position import city_positions, get_city_positions
from data import CITY_DATA

st.set_page_config(
    page_title="Schemat przepływu rzek - Kotlina Kłodzka",
    layout="wide"
)


data = get_city_positions(city_positions)
hydro_data = requests.get('https://danepubliczne.imgw.pl/api/data/hydro2')
hydro_data = hydro_data.json()
keys = ['lon', 'lat', 'stan', 'stan_data']
hydro_data = {d['nazwa_stacji'].title(): {key: val for key, val in d.items() if key in keys} for d in hydro_data}

hydro_dict = {}
for city in city_positions:
    if city in hydro_data:
        hydro_dict[city] = hydro_data[city]
nodes = []
for i, (city, (lat, lon)) in enumerate(data.items()):
    percentage = round(int(hydro_dict.get(city).get('stan')) / CITY_DATA.get(city).get('max') * 100)
    if percentage > 85:
        color = 'progress_color=FF0000'
    elif percentage > 60:
        color = 'progress_color=fcba03'
    else:
        color = 'progress_color=00ff00'
    nodes.append(
        StreamlitFlowNode(
            id=city,
            pos=(lon, -lat),
            data={
                'content': f"""{city}<br>![{percentage}%](https://progress-bar.xyz/{percentage}?{color})"""
            },
            node_type='default',
            source_position='left' if city != 'Kłodzko' else 'top',
            target_position='left' if city != 'Kłodzko' else 'bottom'
        )
    )

edges = []
edges_raw = [
    ('Boboszów', 'Międzylesie'),
    ('Międzygórze', 'Wilkanów'),
    ('Kłodzko', 'Bardo'),
    ('Żelazno', 'Kłodzko'),
    ('Lądek-Zdrój', 'Żelazno'),
    ('Międzylesie', 'Kłodzko'),
    ('Wilkanów', 'Żelazno'),
    ('Krosnowice', 'Kłodzko'),
    ('Szczytna', 'Szalejów Dolny'),
    ('Szalejów Dolny', 'Kłodzko'),
    ('Tłumaczów', 'Gorzuchów'),
    ('Gorzuchów', 'Kłodzko'),
    ('St. Bystrzyca', 'Bystrzyca Kł.'),
]


for c1, c2 in edges_raw:
    edges.append(
        StreamlitFlowEdge(f'{c1}-{c2}', c1, c2, animated=True, edge_type='straight')
    )

selected_id = streamlit_flow('ret_val_flow', nodes, edges, height=1000, fit_view=True)
