import time

import requests
from bs4 import BeautifulSoup
from cachetools.func import ttl_cache
from requests.models import PreparedRequest

from common import logger


def _get_data(url, tries=3):
    r = requests.get(url, allow_redirects=True)
    logger.info(f'Getting data for {url}')
    if r.status_code != 200 and tries > 0:
        logger.info(f'Retrying to get data from {url}. {r.status_code} : {r.text}')
        time.sleep(5)
        return _get_data(url, tries - 1)
    return r.text


@ttl_cache(maxsize=128, ttl=5 * 60)
def get_data(url):
    time.sleep(5)
    return _get_data(url)


@ttl_cache(maxsize=128, ttl=24 * 60 * 60)  # can be cached, as they are not building any more cities in near future
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


def get_city_data(city_name, params):
    export_url = 'http://lsop.powiat.klodzko.pl/php/export.php?'
    req = PreparedRequest()
    req.prepare_url(export_url, params)
    r = get_data(req.url)
    with open(f'data/{city_name}.csv', 'w') as f:
        logger.info(f'writing {len(r)} to {f.name}')
        f.write(r)

    return r


def refresh_data(city_data):
    for city in city_data:
        logger.info(f'refreshing data for {city}')
        # okr is period in hours
        params = {'stc': city_data[city]['id'], 'dta': '2024-09-14', 'okr': 36, 'typ': 1}
        get_city_data(city, params)


if __name__ == '__main__':
    url = 'http://lsop.powiat.klodzko.pl/index.php/woda'

    city_data = get_cities(url)
    for city in city_data:
        # okr is period in hours
        params = {'stc': city_data[city]['id'], 'dta': '2024-09-14', 'okr': 36, 'typ': 1}
        get_city_data(city, params)
