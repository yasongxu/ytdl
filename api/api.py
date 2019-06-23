# -*- coding: utf-8 -*-

import time
import httplib2
import logging
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0"
logger = logging.getLogger(__name__)


class Youtube(object):
    def __init__(self):
        self.args = argparser.parse_args()
        self.service = self.get_authenticated_service()

    def get_authenticated_service(self):
        flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
                                       message=MISSING_CLIENT_SECRETS_MESSAGE)
        storage = Storage("youtube-api-snippets-oauth2.json")
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, self.args)
        return build(API_SERVICE_NAME, API_VERSION,
                     http=credentials.authorize(httplib2.Http()))

    @staticmethod
    def remove_empty_kwargs(**kwargs):
        good_kwargs = {}
        if kwargs is not None:
            for key, value in kwargs.iteritems():
                if value:
                    good_kwargs[key] = value
        return good_kwargs

    def get_playlist_id_by_channel_id(self, channel_id):
        results = self.service.channels().list(
            part='contentDetails',
            id=channel_id).execute()
        return results["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    def get_video_list_by_play_list_id(self, channel_id, l_next=""):
        if l_next:
            results = self.service.playlistItems().list(
                part='contentDetails',
                pageToken=l_next,
                maxResults=50,
                playlistId=channel_id).execute()
        else:
            results = self.service.playlistItems().list(
                part='contentDetails',
                maxResults=50,
                playlistId=channel_id).execute()
        return {"totalResults": results["pageInfo"]["totalResults"],
                "nextPageToken": results.get("nextPageToken", ""),
                "items": results["items"]}

    def get_all_video_by_channel_id(self, channel_id):
        try:
            all_videos = []
            play_list_id = self.get_playlist_id_by_channel_id(channel_id)
            result = self.get_video_list_by_play_list_id(play_list_id)
            total = result["totalResults"]
            l_next = ""
            page_size = 50
            while total > 0:
                time.sleep(3)
                result = self.get_video_list_by_play_list_id(play_list_id, l_next)
                items = result["items"]
                l_next = result["nextPageToken"]
                all_videos.extend(
                    ["https://www.youtube.com/watch?v=" + x["contentDetails"]["videoId"] for x in
                     items])
                total -= page_size
            logger.info("get video success ,channel id is {0}, videos is {1} ".format(channel_id,
                                                                                      all_videos))
            return all_videos

        except Exception as e:
            logger.error("get video error {0},channel id is {1}".format(e, channel_id))
            return []


def ydl_api(channel_id):
    ydl = Youtube()
    return ydl.get_all_video_by_channel_id(channel_id)
