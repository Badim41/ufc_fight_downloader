import os
import random
import re

import requests
from tqdm import tqdm
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

download_path = "downloaded"


class UFC_API:
    def __init__(self, mixed_auth_token):
        self.app_var = "6.7.1.1cf11b9"
        self.api_key = self._get_api_key()
        self.mixed_auth_token = mixed_auth_token
        self.auth_key = self._get_auth_key()

    def _get_api_key(self):
        response = requests.request("GET", f"https://ufcfightpass.com/code/{self.app_var}/js/app.js", data="")

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

    def _get_auth_key(self):

        url = "https://dce-frontoffice.imggaming.com/api/v1/init"

        querystring = {"lk": "language",
                       "pk": ["subTitleLanguage", "audioLanguage", "autoAdvance", "pluginAccessTokens"],
                       "readLicences": "true", "countEvents": "LIVE", "menuTargetPlatform": "WEB"}

        payload = ""
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru",
            "app": "dice",
            "authorization": f"Mixed {self.mixed_auth_token}",
            "content-type": "application/json",
            "origin": "https://ufcfightpass.com",
            "priority": "u=1, i",
            "realm": "dce.ufc",
            "referer": "https://ufcfightpass.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.6.0.0 Safari/537.36",
            "x-api-key": self.api_key,
            "x-app-var": self.app_var
        }

        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

        return response.json()['authentication']['authorisationToken']

    def _get_video_info(self, video_id):
        url = f"https://dce-frontoffice.imggaming.com/api/v4/vod/{video_id}"

        querystring = {"includePlaybackDetails": "URL"}

        payload = ""
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru-RU",
            "app": "dice",
            "authorization": f"Bearer {self.auth_key}",
            "content-type": "application/json",
            "origin": "https://ufcfightpass.com",
            "priority": "u=1, i",
            "realm": "dce.ufc",
            "referer": "https://ufcfightpass.com/",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.6.0.0 Safari/537.36",
            "x-api-key": self.api_key,
            "x-app-var": self.app_var
        }

        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

        return response.json()

    @staticmethod
    def _get_media_parts(url, original_url):
        response = requests.get(url)

        # print(url, response.text, response.status_code)

        parts_urls = [original_url + line for line in response.text.split("\n") if ".ts" in line or ".aac" in line]

        return parts_urls

    def _get_media_urls(self, video_info):
        player_url_callback = video_info['playerUrlCallback']
        response = requests.get(player_url_callback)
        media_master_url = response.json()['hls'][0]['url']
        original_url = media_master_url[:media_master_url.find("master")]

        response = requests.get(media_master_url)
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
    def _combine_video_audio(temp_video_file_names, temp_audio_file_names, output_file):
        # Соединение видеофрагментов
        video_clips = [VideoFileClip(video) for video in temp_video_file_names]
        final_video = concatenate_videoclips(video_clips)

        # Соединение аудиофрагментов
        audio_clips = [AudioFileClip(audio) for audio in temp_audio_file_names]
        final_audio = concatenate_videoclips(audio_clips)

        # Добавляем аудио к видео
        final_video = final_video.set_audio(final_audio)

        # Сохранение финального файла
        final_video.write_videofile(output_file, codec="libx264", audio_codec="aac")

        # Закрываем клипы, чтобы освободить память
        final_video.close()
        final_audio.close()

        # Удаляем временные файлы
        for file in temp_video_file_names + temp_audio_file_names:
            os.remove(file)

    def download_video(self, url, output_path=None):
        if not os.path.exists(download_path):
            os.mkdir(download_path)

        if not "https://ufcfightpass.com/video/" in url:
            raise Exception("Ссылка должна в формате https://ufcfightpass.com/video/<ID>")

        video_id = url[url.rfind("/") + 1:]
        print("video_id", video_id)

        video_info = self._get_video_info(video_id=video_id)

        audio_parts_url, video_parts_url = self._get_media_urls(video_info)

        temp_audio_file_names = []
        temp_video_file_names = []

        rand_int = random.randint(-99999, 99999)

        print("Скачивание видеофрагментов:")
        for i, video_part_url in enumerate(tqdm(video_parts_url, desc="Видео", unit="part")):
            video_path = f"{download_path}/{video_id}_{rand_int}_{i}.ts"
            self._download_content(url=video_part_url, output_file=video_path)
            temp_video_file_names.append(video_path)

        # Скачать аудиофрагменты с отображением прогресса
        print("Скачивание аудиофрагментов:")
        for i, audio_part_url in enumerate(tqdm(audio_parts_url, desc="Аудио", unit="part")):
            audio_path = f"{download_path}/{video_id}_{rand_int}_{i}.aac"
            self._download_content(url=audio_part_url, output_file=audio_path)
            temp_audio_file_names.append(audio_path)

        if not output_path:
            output_path = f"{video_id}.mp4"

        self._combine_video_audio(temp_video_file_names=temp_video_file_names,
                                  temp_audio_file_names=temp_audio_file_names, output_file=output_path)
        return output_path

if __name__ == '__main__':
    import secret
    ufc_api = UFC_API(secret.ufc_auth_key)

    print(ufc_api.download_video("https://ufcfightpass.com/video/..."))
