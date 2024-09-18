from copy import deepcopy

from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="kornel45")

cities = [
    'Bardo',
    'Boboszów',
    'Bystrzyca Kł.',
    'Darnków',
    'Duszniki-Zdrój',
    'Gorzuchów',
    'Krosnowice',
    'Kudowa-Zdrój',
    'Kłodzko',
    'Lądek-Zdrój',
    'Międzygórze',
    'Międzylesie',
    'St. Bystrzyca',
    'Stronie Śląskie',
    'Szalejów Dolny',
    'Szczytna',
    'Tłumaczów',
    'Wilkanów',
    'Ścinawka',
    'Żelazno',
]

# data = {}
# for city in cities:
#     location = geolocator.geocode(city)
#     data[city] = [location.latitude, location.longitude]

city_positions = {
    'Bardo': [50.5007045, 16.6869162],  # manually fixed
    'Boboszów': [50.167257, 16.6956357],
    'Gorzuchów': [50.491291, 16.5952994],
    'Krosnowice': [50.3868379, 16.6314746],
    'Kłodzko': [50.438651, 16.6551878],
    'Lądek-Zdrój': [50.3458254, 16.7525948],
    'Międzylesie': [50.2180131, 16.6669348],
    'Szalejów Dolny': [50.4250496, 16.6040547],
    'Szczytna': [50.4169281, 16.5608185],
    'Tłumaczów': [50.55458, 16.5521101],
    'Wilkanów': [50.2908459, 16.6866414],
    'Żelazno': [50.371621, 16.6729932]
}


def normalize(x, min_val, max_val):
    return (x - min_val) / (max_val - min_val) * 800


def get_city_positions(data):
    data = deepcopy(data)
    min_lat, min_long = float('inf'), float('inf')
    max_lat, max_long = -float('inf'), -float('inf')
    for city in data:
        if data[city][0] < min_lat:
            min_lat = data[city][0]
        elif data[city][0] > max_lat:
            max_lat = data[city][0]
        if data[city][1] < min_long:
            min_long = data[city][1]
        elif data[city][0] > max_long:
            max_long = data[city][1]
    for city in data:
        data[city] = [normalize(data[city][0], min_lat, max_lat), normalize(data[city][1], min_long, max_long)]

    return data
