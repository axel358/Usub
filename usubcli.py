#!/bin/python3

from youtube_transcript_api import YouTubeTranscriptApi as yt_api
from youtube_transcript_api.formatters import WebVTTFormatter
import utils

while True:
    vid_url = input('Enter video url: ')
    vid_id = utils.get_video_id(vid_url)

    if vid_id is None:
        print('Please enter a valid YouTube link')
    else:
        break

sub_list = yt_api.list_transcripts(vid_id)

count = 0
lang_codes = []
for sub in sub_list:
    print(count, sub.language)
    count = count + 1
    lang_codes.append(sub.language_code)

while True:
    index = int(input('Enter the desired number: '))
    if index > len(lang_codes) - 1:
        print('Enter a number in range')
    else:
        break

sub = sub_list.find_transcript([lang_codes[index]])
lang_code = input(
    'Translate this subtitle? \nLanguage code to translate to (leave blank for no transalation): ')
if len(lang_code) > 1:
    sub = sub.translate(lang_code).fetch()
else:
    sub = sub.fetch()

formatter = WebVTTFormatter()
sub = formatter.format_transcript(sub)

name = input('Name for the subtitle (leave blank for default): ')

# TODO: Get subtitle name using a web request
if name is None or len(name) < 1:
    if len(lang_code) > 1:
        name = 'subtitle_' + lang_code
    else:
        name = 'subtitle_' + lang_codes[index]

name = name + '.srt'

with open(name, 'w') as file:
    file.write(sub)

print(name+' saved')

