import requests
import configparser
from tqdm import tqdm
from datetime import datetime
import os

config = configparser.ConfigParser()
config.read('settings.ini')

VKtoken = config["VK"]["token"]
YAtoken = config["Yandex"]["token"]
VK_id = config["VK"]["id_vk"]


class VkUser:
    def __init__(self, token, version):
        self.token = token
        self.version = version

    def get_photo(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'owner_id': VK_id,
            'access_token': self.token,
            'v': self.version,
            'extended': '1',
            'album_id': 'wall',
            'photo_sizes': '1',
            'sort': '1',
            'offset': '0',
            'count': '20'
        }
        req = requests.get(url, params=params).json()

        dict_photo = {}
        for item in (req['response']['items']):
            likes = item['likes']['count']
            for size in item['sizes']:
                if size['type'] == 'z':
                    dict_photo[likes] = size['url']
        return dict_photo

    def download_photo(self, likes, url):
        filename = f'VK_photo/{likes}_{current_datetime}.jpg'
        r = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(r.content)
        return filename


class YandexDisk:
    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def _create_folder(self, disk_folder_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        response = requests.put(f'{upload_url}?path={disk_folder_path}', headers=headers)
        if response.status_code == 201:
            print('Folder created successfully')

    def get_upload_link(self, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, disk_file_path, filename):
        href = self.get_upload_link(disk_file_path=disk_file_path).get("href", "")
        response = requests.put(href, data=open(filename, 'rb'))
        response.raise_for_status()


def download_and_save_photos(photo_dict):
    vk = VkUser(VKtoken, '5.131')
    global current_datetime
    current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    if not os.path.isdir('VK_photo'):
        os.mkdir('VK_photo')

    ya = YandexDisk(token=YAtoken)
    path = f'backUP_photo_VK_{current_datetime}'
    ya._create_folder(path)

    for likes, url in tqdm(photo_dict.items(), desc="Downloading photos"):
        filename = vk.download_photo(likes, url)
        ya.upload_file_to_disk(f"{path}/{os.path.basename(filename)}", filename)


def main():
    vk = VkUser(VKtoken, '5.131')
    photo_dict = vk.get_photo()
    download_and_save_photos(photo_dict)


if __name__ == "__main__":
    main()
