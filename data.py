import functools
import time

import requests
from bs4 import BeautifulSoup
from requests.models import PreparedRequest

from common import cache_function_result

TTL = 15 * 60


def time_cache(max_age, maxsize=128, typed=False):
    """Least-recently-used cache decorator with time-based cache invalidation.

    Args:
        max_age: Time to live for cached results (in seconds).
        maxsize: Maximum cache size (see `functools.lru_cache`).
        typed: Cache on distinct input types (see `functools.lru_cache`).
    """

    def _decorator(fn):
        @functools.lru_cache(maxsize=maxsize, typed=typed)
        def _new(*args, __time_salt, **kwargs):
            return fn(*args, **kwargs)

        @functools.wraps(fn)
        def _wrapped(*args, **kwargs):
            return _new(*args, **kwargs, __time_salt=int(time.time() / max_age))

        return _wrapped

    return _decorator


def _get_data(url, tries=3):
    r = requests.get(url, allow_redirects=True)
    time.sleep(0.1)
    print(f'Getting data for {url}')
    if r.status_code != 200 and tries > 0:
        print(f'Retrying to get data from {url}. {r.status_code} : {r.text}')
        time.sleep(0.5)
        return _get_data(url, tries - 1)
    return r.text


@cache_function_result(TTL)
def get_data(url):
    return _get_data(url)


def get_cities(url):
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
        f.write(r)




if __name__ == '__main__':
    url = 'http://lsop.powiat.klodzko.pl/index.php/woda'

    city_data = get_cities(url)
    for city in city_data:
        # okr is period in hours
        params = {'stc': city_data[city]['id'], 'dta': '2024-09-14', 'okr': 36, 'typ': 1}
        get_city_data(city, params)
