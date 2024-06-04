import socket
import requests
import grequests
from random import randint


headers = {'Content-type': 'application/json'}


def find_free_port(port=5005):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', port)) == 0:
            return find_free_port(port=port + randint(0, 995))
        else:
            return port


def get_request(url, params=None):
    try:
        response = requests.get(url, params=params, headers=headers)
        return response
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        return e


def post_request(url, json_dict=None):
    try:
        response = requests.post(url, json=json_dict, headers=headers)
        return response
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        return e


def put_request(url, json_dict=None):
    try:
        response = requests.put(url, json=json_dict, headers=headers)
        return response
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        return e


def patch_request(url, json_dict=None):
    try:
        response = requests.patch(url, json=json_dict, headers=headers)
        return response
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        return e


def delete_request(url, json_dict=None):
    try:
        response = requests.delete(url, json=json_dict, headers=headers)
        return response
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        return e


def get_local_ip():
    return socket.gethostbyname(socket.gethostname())


def async_requests(url: str, json_dicts: list, method='get'):
    if hasattr(grequests, method):
        req_method = getattr(grequests, method)
    else:
        return []

    req_list = []
    for json_dict in json_dicts:

        if method == 'get':
            req_list.append(req_method(url=url, params=json_dict, headers=headers))
        else:
            req_list.append(req_method(url=url, json=json_dict, headers=headers))

    response_list = grequests.map(req_list)
    return response_list


if __name__ == '__main__':
    result = async_requests('http://localhost:5000/api/users/', [{'username': 'user_1'}])
    for response in result:
        print(response.status_code)
