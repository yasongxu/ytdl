# -*- coding:utf-8 -*-
import re
import os
import time
import requests
import logging
import click
import youtube_dl

from api.to_html import BODY, PART
from api.api import ydl_api as get_all_video_by_channel_id

YOUTUBE_API_KEY = "AIzaSyB-LNfsvxdw3bxkCh63j4UsBBYtn6Kfix"
TIME_RE = "([0-1]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9]).([0-9][0-9][0-9])"
WORD_RE = "<c>(?!.[:]).*?</c>"
COLOR_RE = "<c.color.{6}>"
PUNCTUATE_URL = "http://bark.phon.ioc.ee/punctuator"
DEAD_TIME = 300

logger = logging.getLogger(__name__)


class VttToHtml(object):
    def __init__(self, folder):
        if not folder:
            folder = os.path.abspath('.')
        else:
            if folder[-1] == "/":
                folder = folder[:-1]
        self.folder = folder
        self.SUB_FOLDER = self.folder + "/subtitle_files/sub/"
        self.TXT_FOLDER = self.folder + "/subtitle_files/txt/"
        self.HTML_FOLDER = self.folder + "/subtitle_files/html/"
        self.PUNC_FOLDER = self.folder + "/subtitle_files/punctuate/"
        self.init_folder()

    def init_folder(self):
        if not os.path.exists(self.folder):
            raise Exception("folder not existed, please check!")
        else:
            for path in [self.SUB_FOLDER, self.TXT_FOLDER, self.HTML_FOLDER, self.PUNC_FOLDER]:
                if not os.path.exists(path):
                    os.makedirs(path)

    def get_source_sub(self):
        subs = os.listdir(self.SUB_FOLDER)
        return subs

    @staticmethod
    def convert_to_txt_from_vtt_content(text):
        words_list = []
        time_list = []
        for line in text:
            if '\n' in line:
                quote = line.rstrip('\n')
                if "-->" in quote or "<" not in quote:
                    continue
                else:
                    if quote:
                        if quote[0] != "<":
                            f_index = quote.index("<")
                            c_index = quote.index("<c>")
                            quote = quote[f_index:c_index + 3] + " " + quote[:f_index] + quote[
                                                                                         c_index + 3:]
                        quote = re.sub(COLOR_RE, "<c>", quote)
                        words_match = re.findall(WORD_RE, quote)
                        words_match = [re.sub(TIME_RE, "", word) for word in words_match]
                        timestamp_match = re.findall(TIME_RE, quote)
                        words = [
                            word.replace("<c>", "").replace("</c>", "").replace("<>", "").strip()
                            for word in
                            words_match]
                        timestamp = sorted(
                            [int(i[0]) * 3600 * 1000 + int(i[1]) * 60 * 1000 + int(
                                i[2]) * 1000 + int(i[3]) for i in
                             timestamp_match])
                        if len(words) == len(timestamp):
                            pass
                        elif len(words) - len(timestamp) == 1:
                            if len(words) > 1:
                                words[1] = words[0] + " " + words[1]
                                words.pop(0)
                            elif not timestamp:
                                timestamp = [time_list[-1]]
                        elif len(words) - len(timestamp) == -1:
                            origin_word = words[0].split(" ")
                            words[0] = origin_word[1]
                            words.insert(0, origin_word[0])
                        else:
                            raise Exception("convert_to_txt_from_vtt_content timestamp error")
                        if len(words) != len(timestamp):
                            raise Exception("convert_to_txt_from_vtt_content words error")
                        words_list.extend(words)
                        time_list.extend(timestamp)
        last_timestamp = 0
        text = ""
        for index, word in enumerate(words_list):
            current_timestamp = time_list[index]
            if last_timestamp == 0:
                add_quote = " "
            else:
                if current_timestamp - last_timestamp > 3800:
                    add_quote = " &"
                else:
                    add_quote = " "
            text += add_quote + word
            last_timestamp = time_list[index]
        return text

    @staticmethod
    def punctuate(text):
        a = requests.post(url=PUNCTUATE_URL, data={"text": text})
        return a.content

    @staticmethod
    def convert_to_html_from_punctuated(text, title):
        parts = [PART.format(part_content=part) for part in text.split("&")]
        all_part = " ".join(parts)
        return BODY.format(article_title=title, all_part=all_part)

    @staticmethod
    def save_file(f_name, text):
        with open(f_name, 'w') as f:
            f.write(text)

    def run(self):
        for source in self.get_source_sub():
            try:
                with open(self.SUB_FOLDER + source) as text:
                    article_name = source.split(".vtt")[0]
                    _text = self.convert_to_txt_from_vtt_content(text)
                    logger.info("convert_to_txt_from_vtt_content done")

                    # save txt：avoid punctuate failed
                    file_name = self.TXT_FOLDER + article_name + ".txt"
                    self.save_file(file_name, _text)
                    logger.info("save_file txt done")

                    _text = self.punctuate(_text)
                    logger.info("punctuate done")

                    # sleep 3s: limit the rate of visiting punctuate server
                    time.sleep(3)
                    file_name = self.PUNC_FOLDER + article_name + ".txt"
                    self.save_file(file_name, _text)
                    logger.info("punctuate save done")

                    # save html file
                    _text = self.convert_to_html_from_punctuated(_text, article_name)
                    file_name = self.HTML_FOLDER + article_name + ".html"
                    self.save_file(file_name, _text)
                    logger.info("html save done")
            except Exception as e:
                logger.error(e)
                continue


class YdlDownChannelVtt(object):
    def __init__(self, video_list, folder=None):
        if not folder:
            folder = os.path.abspath('.')
        else:
            if folder[-1] == "/":
                folder = folder[:-1]
        self.folder = folder
        self.video_list = video_list
        self.SUB_FOLDER = self.folder + "/subtitle_files/sub/"
        self.init_folder()

    def init_folder(self):
        if not os.path.exists(self.folder):
            raise Exception("folder not existed, please check!")
        else:
            for path in [self.SUB_FOLDER]:
                if not os.path.exists(path):
                    os.makedirs(path)

    def download(self, url_list):
        ydl_opts = {"writeautomaticsub": True, "skip_download": True, "subtitleslangs": ["en"],
                    "forcethumbnail": True,
                    'outtmpl': self.SUB_FOLDER + "%(title)s.%(ext)s"}

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url_list)

    def run(self):
        self.download(self.video_list)


@click.command()
@click.option('--folder', default="", help='the file folder you run the demo')
@click.option('--channel_id', default="", help='The channel_id you want to download')
@click.option('--video_id', default="AjFfsOA7AQI", help='The single video url you want to download')
def execute(folder="", channel_id="", video_id="AjFfsOA7AQI"):
    try:
        video_list = []
        if video_id:
            video_list = ["https://www.youtube.com/watch?v={0}".format(video_id)]
        if channel_id:
            video_list = get_all_video_by_channel_id(channel_id)

        # start download subtitle
        download = YdlDownChannelVtt(video_list, folder)
        download.run()

        # start convert to html file
        to_html = VttToHtml(folder)
        to_html.run()
    except Exception as e:
        logger.error("run failed , error is {0}".format(e))


if __name__ == '__main__':
    execute()
