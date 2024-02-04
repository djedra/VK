import requests
import time
import configparser
from tqdm import tqdm
from datetime import datetime
import os


config = configparser.ConfigParser()  # объекта парсера
config.read('settings.ini')

VKtoken = config["VK"]["token"]
YAtoken = config["Yandex"]["token"]
VK_id = config["VK"]["id_vk"]

class VkUser:

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }
    def get_photo(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'user_id': VK_id,
            'access_token': VKtoken,
            'v': '5.131',
            'extended': '1',
            'album_id': 'wall',
            'photo_sizes': '1',
            'sort': '1',
            'offset': '0',
            'count': '20'
        }
        req = requests.get(url, params=params).json()

        dict_photo = {}
        for dict_ in (req['response']['items']):
            for i in dict_['sizes']:
                if i['type'] == 'z':
                    j = dict_['likes']
                    p = j['count']

                    if dict_photo.keys() == p:
                        dict_photo[p + current_datetime] = i['url']
                    else:
                        dict_photo[p] = i['url']
        return dict_photo

    def get_file(self):
        url = vk.get_photo().values()
        r = requests.get(url)
        with open('VK_photo/' + vk.get_photo().values() + '.jpg', 'wb') as f:
            f.write(r.content)

current_datetime = datetime.now().now().strftime('%Y-%m-%d_%H-%M-%S')

vk = VkUser(VKtoken, '5.131')

path1 = 'VK_photo/'
if path1 in os.getcwd():
    for i, j in vk.get_photo().items():
        r = requests.get(j)
        with open(path1 + str(i) + '.jpg', 'wb') as f:
            f.write(r.content)
if not os.path.isdir('VK_photo'):
    os.mkdir('VK_photo')
    for i, j in vk.get_photo().items():
        r = requests.get(j)
        with open(path1 + str(i) + '.jpg', 'wb') as f:
            f.write(r.content)




class YandexDisk:

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def _get_path(self, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        response = requests.put(f'{upload_url}?path={disk_file_path}', headers=headers)
        if response.status_code == 201:
            print('Sucsess')

    def _get_upload_link(self, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, disk_file_path, filename):
        href = self._get_upload_link(disk_file_path=disk_file_path).get("href", "")
        response = requests.put(href, data=open(filename, 'rb'))
        response.raise_for_status()



ya = YandexDisk(token=YAtoken)

path = 'backUP_photo_VK_'

ya._get_path(path)
ya._get_upload_link(path)

for i in os.walk('VK_photo/'):
    for j in tqdm(i[2]):
        time.sleep(0.5)
        ya.upload_file_to_disk('backUP_photo_VK_/' + str(j), 'VK_photo/' + str(j))


