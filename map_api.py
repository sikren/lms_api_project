# часть проекта, отвечающая за работу с Yandex.Maps Static API
import requests


# работает только с координатами
def return_map(lon, lat, z, map_type, tags, img_scale):
    static_api = ' https://static-maps.yandex.ru/1.x/?'

    params = {
        "ll": f'{lon},{lat}',
        "z": z,
        "size": f'{img_scale[0]},{img_scale[1]}',
        "l": map_type,
        "pt": '~'.join(tags)
    }

    response = requests.get(static_api, params=params)

    if not response:
        return None
    else:
        return response.content


# если вместо координат топоним, то используется Geocoder
# потом используется return_map
def toponym_to_ll(name):
    geocoder = 'http://geocode-maps.yandex.ru/1.x/?'

    params = {
        "apikey": '40d1649f-0493-4b70-98ba-98533de7710b',
        "geocode": name,
        "format": 'json'
    }

    response = requests.get(geocoder, params=params)
    try:
        json_response = response.json()
        # Получаем первый топоним из ответа геокодера.
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        # Координаты центра топонима:
        return map(float, toponym["Point"]["pos"].split())
    except Exception:
        return False

