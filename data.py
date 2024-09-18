import os
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.models import PreparedRequest

from common import logger

CITY_DATA = {
    'Bardo': {'id': 19, 'max': 774.0}, 'Boboszów': {'id': 10, 'max': 289.0},
    'Bystrzyca Kł.': {'id': 1, 'max': 360.0}, 'Darnków': {'id': 31, 'max': 897.0},
    'Duszniki-Zdrój': {'id': 14, 'max': 221.0}, 'Gorzuchów': {'id': 2, 'max': 289.0},
    'Kłodzko': {'id': 5, 'max': 657.0}, 'Krosnowice': {'id': 6, 'max': 489.0},
    'Kudowa-Zdrój': {'id': 16, 'max': 378.0}, 'Lądek-Zdrój': {'id': 4, 'max': 311.0},
    'Międzygórze': {'id': 11, 'max': 2654.0}, 'Międzylesie': {'id': 8, 'max': 339.0},
    'St. Bystrzyca': {'id': 36, 'max': 187.0}, 'Stronie Śląskie': {'id': 12, 'max': 320.0},
    'Szalejów Dolny': {'id': 3, 'max': 300.0}, 'Szczytna': {'id': 15, 'max': 396.0},
    'Ścinawka': {'id': 18, 'max': 450.0}, 'Tłumaczów': {'id': 17, 'max': 360.0},
    'Wilkanów': {'id': 9, 'max': 360.0}, 'Żelazno': {'id': 7, 'max': 429.0}
}


def _get_data(url, tries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0',
    }

    r = requests.get(url, headers=headers)
    logger.info(f'Getting data for {url}')
    if r.status_code != 200 and tries > 0:
        logger.info(f'[{tries}] Retrying to get data from {url}. {r.status_code} : {r.text}')
        time.sleep(15)
        return _get_data(url, tries - 1)
    return r.text


def get_data(url):
    return _get_data(url)


def get_cities(url):
    logger.info(f'Getting cities data from {url}...')
    html = get_data(url)
    soup = BeautifulSoup(html, 'html.parser')
    all_cities = soup.findAll('tr')[1:]

    city_data = {}

    for city in all_cities:

        try:
            href = city.find('a', href=True)['href']
            city_name = city.find('b').text
            state = int(city.select('td[class=td-stan]')[0].text)
            width = int(city.select('div[class*=woda-bar]')[0].attrs['style'].split(':')[1].split('%')[0])
            if '\n' not in city_name:
                city_data[city_name] = {
                    'id': int(href.split('/')[-2]),
                    'max': round(state / width * 100, 0),
                }
        except:
            pass
    return city_data


def download_data_for_city(city_name: str, okr: int = 36):
    params = {
        'stc': CITY_DATA[city_name]['id'],
        'dta': datetime.now().strftime('%Y-%m-%d'),
        'okr': okr,
        'typ': 1
    }
    export_url = 'http://lsop.powiat.klodzko.pl/php/export.php?'
    req = PreparedRequest()
    req.prepare_url(export_url, params)
    r = get_data(req.url)
    return r


def get_data_for_city(city_name: str):
    filename = f'data/{city_name}.csv'
    df = pd.read_csv(filename, sep=';')
    return df


def save_to_file(data, filename):
    with open(filename, 'w') as f:
        f.write(data)


def get_delta(filename):
    if os.path.exists(filename):
        modified_time = os.path.getmtime(filename)
        delta = datetime.now() - datetime.fromtimestamp(modified_time)
        return delta.total_seconds()
    return float('inf')


def refresh_data(city_data, ttl=int(os.getenv('DEFAULT_TTL', 15 * 60)), force=False):
    cities_to_update = []
    for city in city_data:
        filename = f'data/{city}.csv'

        should_download = False
        message = f'{filename} was downloaded {get_delta(filename)} seconds ago'
        if not os.path.exists(filename) or force:
            should_download = True
            message = 'File does not exist or force.'
        elif os.path.exists(filename) and get_delta(filename) > ttl:
            should_download = True
            message = 'Data outdated. Refreshing.'
        else:
            logger.info(message)

        if should_download:
            cities_to_update.append((city, filename, f'Downloading data for {city}. {message}'))

    logger.info(f'{len(cities_to_update)} cities needs update.')
    for city, filename, message in cities_to_update:
        logger.info(message)
        city_data = download_data_for_city(city)
        save_to_file(city_data, filename)
        # simple rate limiting
        time.sleep(2)


if __name__ == '__main__':
    refresh_data(CITY_DATA)
