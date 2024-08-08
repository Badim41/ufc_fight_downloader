class ContentDownload:
    def __init__(self, data):
        self.permission = data['permission']
        self.period = data['period']

class SocialSharingDetail:
    def __init__(self, data):
        self.universal_link = data['universalLink']

class UFCVideo:
    def __init__(self, json_data):
        self.description = json_data['description']
        self.duration = json_data['duration']
        self.title = json_data['title']
        self.long_description = json_data['longDescription']
        self.offline_playback_languages = json_data['offlinePlaybackLanguages']
        self.max_height = json_data['maxHeight']
        self.categories = json_data['categories']
        self.content_download = ContentDownload(json_data['contentDownload'])
        self.favourite = json_data['favourite']
        self.thumbnail_url = json_data['thumbnailUrl']
        self.sub_events = json_data['subEvents']
        self.watched_at = json_data['watchedAt']
        self.watch_progress = json_data['watchProgress']
        self.id = json_data['id']
        self.access_level = json_data['accessLevel']
        self.player_url_callback = json_data['playerUrlCallback']
        self.thumbnails_preview = json_data['thumbnailsPreview']
        self.displayable_tags = json_data['displayableTags']
        self.plugins = json_data['plugins']
        self.social_sharing_detail = SocialSharingDetail(json_data['socialSharingDetail'])
        self.watch_status = json_data['watchStatus']
        self.watch_context = json_data['watchContext']
        self.computed_releases = json_data['computedReleases']
        self.online_playback = json_data['onlinePlayback']
        self.licences = json_data['licences']
        self.type = json_data['type']
