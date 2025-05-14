import requests
from tqdm import tqdm
import time


class YandexAPIClient:
    base_url = "https://dog.ceo/api/breed/"
    yandex_url = "https://cloud-api.yandex.net/v1/disk/resources"

    def __init__(self, token, breed):
        self.token = token
        self.breed = breed

    def get_breed(self):
        url = f"{self.base_url}{self.breed}/images"
        resp = requests.get(url, timeout=30)
        images_list = resp.json()
        return images_list["message"]

    def get_sub_breed(self):
        url = f"{self.base_url}{self.breed}/list"
        resp = requests.get(url, timeout=30)
        sub_breeds = resp.json()
        sub_breeds_dict = {}

        for sb in sub_breeds["message"]:
            url2 = f"{self.base_url}{self.breed}/{sb}/images"
            response = requests.get(url2, timeout=30)
            images = response.json()
            image_url = images["message"][0]
            sub_breeds_dict[sb] = image_url
        return sub_breeds_dict

    def get_headers(self):
        headers = {
            "Authorization": f"OAuth {self.token}"
        }
        return headers

    def create_folder(self):
        with tqdm(total=1, desc=f"Create folder '{self.breed}'") as pbar:
            try:
                param = {"path": self.breed}
                param_sub_breed = {"path": f"disk:/{self.breed}/Sub-breeds"}
                response = requests.put(self.yandex_url, headers=self.get_headers(), params=param, timeout=30)
                response.raise_for_status()
                time.sleep(3.0)
                pbar.update(1)
            except Exception as e:
                tqdm.write(f"Request failed: {e}")

            if len(self.get_sub_breed()) > 0:
                try:
                    response = requests.put(self.yandex_url, headers=self.get_headers(), params=param_sub_breed, timeout=30)
                    response.raise_for_status()
                except Exception as e:
                    tqdm.write(f"Request failed: {e}")

    def send_photo_breed(self):
        self.create_folder()
        url_download = f"{self.yandex_url}/upload"
        counter = 1
        max_counter = 19

        with tqdm(total=max_counter, unit="image", desc="Upload Breed's images") as pbar:
            for breed_image_url in self.get_breed():
                try:
                    param = {"url": breed_image_url, "path": f"disk:/{self.breed}/{str(counter)}.png"}
                    response = requests.post(url_download, headers=self.get_headers(), params=param, timeout=30)
                    time.sleep(0.5)
                    pbar.update(1)
                    if counter > max_counter:
                        break
                    counter += 1
                    response.raise_for_status()
                except Exception as e:
                    tqdm.write(f"Request failed: {e}")
                    continue

        self.send_photo_sub_breeds()

    def send_photo_sub_breeds(self):
        url_download = f"{self.yandex_url}/upload"
        counter = 1
        max_counter = len(self.get_sub_breed())

        with tqdm(total=max_counter, unit="image", desc="Upload Sub-breed's images") as pbar:
            for sub_breed_image in self.get_sub_breed():
                try:
                    param = {"url": self.get_sub_breed()[sub_breed_image], "path": f"disk:/{self.breed}/Sub-breeds/{sub_breed_image}.png"}
                    response = requests.post(url_download, headers=self.get_headers(), params=param, timeout=30)
                    time.sleep(0.5)
                    pbar.update(1)
                    if counter > max_counter + 1:
                        break
                    counter += 1
                    response.raise_for_status()
                except Exception as e:
                    tqdm.write(f"Request failed: {e}")
                    continue

me = YandexAPIClient(..., ...)
me.send_photo_breed()