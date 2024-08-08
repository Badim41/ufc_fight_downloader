Код, позволяющий скачивать видео с сайта https://ufcfightpass.com
(Необходима подписка на учётной записи)

## Зависимости
```bash
pip install requests tqdm
```
+ ffmpeg

# Использование
```python
# ключ из заголовка: 'authorization: Mixed <AUTH_KEY>' в запросе https://dce-frontoffice.imggaming.com/api/v1/init
ufc_api = UFC_API("AUTH_KEY") 
video_url = # "https://ufcfightpass.com/video/..."
video_path = ufc_api.download_video(video_url)

print("Downloaded:", video_path)
```
