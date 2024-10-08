import os
import random
import re
import subprocess

import requests
from tqdm import tqdm

download_path = "downloaded"


class UFC_API:
    def __init__(self, login, password, create_new=False, proxies=None):
        self.login = login
        self.password = password
        self.proxies = proxies
        self.x_app_var = "6.7.1.4049534"
        self.x_api_key = self._get_api_key()

        self.auth_file = "~/.ufc_auth/ufc_auth.txt"
        if os.path.exists(self.auth_file) and not create_new:
            with open(self.auth_file, "r") as reader:
                self.mixed_auth_token = reader.read()
        else:
            self.mixed_auth_token = self._get_mixed_auth_token()
            # print("mixed_auth_token from login:", self.mixed_auth_token)
            os.makedirs(os.path.dirname(self.auth_file), exist_ok=True)
            with open(self.auth_file, "w") as writer:
                writer.write(self.mixed_auth_token)

        self.auth_key = self._get_auth_key(self.mixed_auth_token)
        # if not self.auth_key:
        #     print("No auth key!")
        # else:
        #     print(f"auth key: {self.auth_key}")

    def _get_mixed_auth_token(self):
        url = "https://dce-frontoffice.imggaming.com/api/v2/login"

        payload = {
            "id": self.login,
            "secret": self.password
        }

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru-RU",
            "authorization": f"Bearer {self._get_auth_key(None)}",
            "app": "dice",
            "content-type": "application/json",
            "origin": "https://ufcfightpass.com",
            "priority": "u=1, i",
            "realm": "dce.ufc",
            "referer": "https://ufcfightpass.com/",
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36",
            "x-api-key": self.x_api_key,
            "x-app-var": self.x_app_var
        }

        # print("headers", headers)

        response = requests.request("POST", url, json=payload, headers=headers, proxies=self.proxies)

        response_json = response.json()

        messages = response_json.get('messages')

        if messages:
            if messages[0] == "badLocation":
                raise Exception("Неверная локация для UFC! Используйте прокси")
            else:
                raise Exception(f"Неуспешная авторизация в UFC. Сообщения: {messages}")

        response.raise_for_status()

        return response.json()['authorisationToken']

    def _get_api_key(self):
        response = requests.request("GET", f"https://ufcfightpass.com/code/{self.x_app_var}/js/app.js", data="", proxies=self.proxies)

        # print(response.text)
        html_text = response.text  # '...{ENV_CONF:{env:"PROD", "otherKey": "value", "nestedKey": {"innerKey": "innerValue"}}}...'

        pattern = r'API_KEY:"(.*?)"'

        # Поиск совпадений
        match = re.search(pattern, html_text)

        if match:
            api_key = match.group(1)
            return api_key
        else:
            print('API_KEY не найден')

    def _get_auth_key(self, mixed_auth_token):
        url = "https://dce-frontoffice.imggaming.com/api/v2/realm-settings/domain/ufcfightpass.com"

        payload = ""
        headers = {
            "Realm": "dce.ufc",
            "Accept-Language": "ru-RU",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://ufcfightpass.com/",
            "app": "dice",
            "x-app-var": self.x_app_var,
            "x-api-key": self.x_api_key,

        }

        if mixed_auth_token:
            headers["Authorization"] = f"Bearer {mixed_auth_token}"

        response = requests.request("GET", url, data=payload, headers=headers, proxies=self.proxies)

        print(response.text)

        url = "https://dce-frontoffice.imggaming.com/api/v1/init"

        querystring = {"lk": "language",
                       "pk": ["subTitleLanguage", "audioLanguage", "autoAdvance", "pluginAccessTokens"],
                       "readLicences": "true", "countEvents": "LIVE", "menuTargetPlatform": "WEB"}

        payload = ""
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru",
            "app": "dice",
            "content-type": "application/json",
            "origin": "https://ufcfightpass.com",
            "priority": "u=1, i",
            "realm": "dce.ufc",
            "referer": "https://ufcfightpass.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.6.0.0 Safari/537.36",
            "x-api-key": self.x_api_key,
            "x-app-var": self.x_app_var
        }

        if mixed_auth_token:
            headers["Authorization"] = f"Mixed {mixed_auth_token}"

        response = requests.request("GET", url, data=payload, headers=headers, params=querystring, proxies=self.proxies)

        return response.json()['authentication']['authorisationToken']

    def _get_video_info(self, video_id):
        url = f"https://dce-frontoffice.imggaming.com/api/v4/vod/{video_id}"

        querystring = {"includePlaybackDetails": "URL"}

        payload = ""
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru-RU",
            "app": "dice",
            "authorization": f"Bearer {self.mixed_auth_token}",
            "content-type": "application/json",
            "origin": "https://ufcfightpass.com",
            "priority": "u=1, i",
            "realm": "dce.ufc",
            "referer": "https://ufcfightpass.com/",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.6.0.0 Safari/537.36",
            "x-api-key": self.x_api_key,
            "x-app-var": self.x_app_var
        }

        response = requests.request("GET", url, data=payload, headers=headers, params=querystring, proxies=self.proxies)

        return response.json()

    @staticmethod
    def _get_media_parts(url, original_url):
        response = requests.get(url)

        # print(url, response.text, response.status_code)

        parts_urls = [original_url + line for line in response.text.split("\n") if ".ts" in line or ".aac" in line]

        return parts_urls

    def _get_media_urls(self, video_info):
        player_url_callback = video_info['playerUrlCallback']
        response = requests.get(player_url_callback, proxies=self.proxies)
        media_master_url = response.json()['hls'][0]['url']
        original_url = media_master_url[:media_master_url.find("master")]

        response = requests.get(media_master_url, proxies=self.proxies)
        # print(response.text)

        video_pattern = re.compile(r'video/([^\s"]+)')
        audio_pattern = re.compile(r'audio/([^\s"]+)')

        # Поиск всех совпадений
        video_matches = video_pattern.findall(response.text)
        audio_matches = audio_pattern.findall(response.text)

        video_request_id = video_matches[1][video_matches[1].find("video/") + 1:video_matches[1].find("/index")]
        audio_request_id = audio_matches[0][audio_matches[0].find("audio/") + 1:audio_matches[0].find("/index")]

        # print("id:", video_request_id, audio_request_id)

        # Формирование полных URL
        video_urls = [original_url + "video/" + video_match for video_match in video_matches]
        audio_urls = [original_url + "audio/" + audio_match for audio_match in audio_matches]

        video_parts = self._get_media_parts(video_urls[1], original_url=f"{original_url}video/{video_request_id}/")
        audio_parts = self._get_media_parts(audio_urls[0], original_url=f"{original_url}audio/{audio_request_id}/")

        return audio_parts, video_parts

    @staticmethod
    def _download_content(url, output_file):
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(output_file, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # фильтруем пустые куски
                    file.write(chunk)

    @staticmethod
    def _combine_video_audio(video_id, rand_int, temp_video_file_names, temp_audio_file_names, output_file):
        # Соединяем все видео фрагменты в один файл без использования большого количества оперативной памяти
        combined_video_file = f"downloaded/{video_id}_{rand_int}_combined.ts"
        with open(combined_video_file, 'wb') as outfile:
            for video_file in temp_video_file_names:
                with open(video_file, 'rb') as infile:
                    outfile.write(infile.read())

        # Соединяем все аудиофрагменты в один файл аналогично
        combined_audio_file = f"downloaded/{video_id}_{rand_int}_combined.aac"
        with open(combined_audio_file, 'wb') as outfile:
            for audio_file in temp_audio_file_names:
                with open(audio_file, 'rb') as infile:
                    outfile.write(infile.read())

        # Объединяем видео и аудио в финальный MP4 файл
        subprocess.run([
            'ffmpeg', '-y',
            '-i', combined_video_file,
            '-i', combined_audio_file,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            output_file
        ], check=True)

        # Удаляем временные файлы
        os.remove(combined_video_file)
        os.remove(combined_audio_file)

    def download_video(self, url, output_path=None):
        if not os.path.exists(download_path):
            os.mkdir(download_path)

        if not "https://ufcfightpass.com/video/" in url:
            raise Exception("Ссылка должна быть в формате https://ufcfightpass.com/video/<ID>")

        video_id = url[url.rfind("/") + 1:]

        if not video_id.isdigit():
            raise Exception(f"\"{video_id}\" - должно быть числом")  # проверка на число

        print("video_id", video_id)

        video_info = self._get_video_info(video_id=video_id)

        print("video_info", video_info)

        audio_parts_url, video_parts_url = self._get_media_urls(video_info)

        temp_audio_file_names = []
        temp_video_file_names = []

        rand_int = random.randint(-99999, 99999)

        for i, video_part_url in enumerate(tqdm(video_parts_url, desc="Скачивание видеофрагментов:", unit="part")):
            video_path = f"{download_path}/{video_id}_{rand_int}_{i}.ts"
            self._download_content(url=video_part_url, output_file=video_path)
            temp_video_file_names.append(video_path)

        for i, audio_part_url in enumerate(tqdm(audio_parts_url, desc="Скачивание аудиофрагментов:", unit="part")):
            audio_path = f"{download_path}/{video_id}_{rand_int}_{i}.aac"
            self._download_content(url=audio_part_url, output_file=audio_path)
            temp_audio_file_names.append(audio_path)

        if not output_path:
            output_path = f"{video_id}.mp4"

        self._combine_video_audio(video_id=video_id, rand_int=rand_int, temp_video_file_names=temp_video_file_names,
                                  temp_audio_file_names=temp_audio_file_names, output_file=output_path)

        for file in temp_video_file_names + temp_audio_file_names:
            os.remove(file)

        return output_path

# пустой get auth
# из него ключ в login
# ключ из login в get video info
