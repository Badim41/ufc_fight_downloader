Код, позволяющий скачивать видео с сайта https://ufcfightpass.com
(Необходима подписка на учётной записи)

## Зависимости
```bash
pip install requests tqdm
```
+ ffmpeg

# Использование
```python
ufc_api = UFC_API(login="ufc_login", password="ufc_password")
video_url = # "https://ufcfightpass.com/video/..."
video_path = ufc_api.download_video(video_url)

print("Downloaded:", video_path)
```
