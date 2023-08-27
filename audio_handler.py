###############################################################################
#
#   simple audio handler module to play a music file and return metadata
#
###############################################################################
#
#   2023 - August - Henk-Johan
#           - initial version
#
###############################################################################


# for the file information
import mutagen                      # for metadata
from mutagen.id3 import ID3         # for metadata
from mutagen.mp3 import MP3         # for metadata
from mutagen.flac import FLAC       # for metadata
from unidecode import unidecode     # to change title or artist text to unicode

import os                           # miniaudio only works with absolute paths
import time                         # because the audio player is not blocking we need a timer
import miniaudio                    # for audio file playback



class AudioHandler:
    def __init__(self):
        self.filename = ''

    def play_file(self,filename,sleeptime):
        '''Will play a file and use a timer to make it blocking. Not blocking function, have to pause via timer...'''
        abs_filename = os.path.join(os.getcwd(), filename ) 
        stream = miniaudio.stream_file(abs_filename)
        with miniaudio.PlaybackDevice() as device:
            device.start(stream)
            time.sleep(sleeptime)
        return 0

    def get_title(self, filename):
        '''Get the title of the song via mutagen.'''
        abs_file = os.path.join(os.getcwd(), filename ) 
        title = 'title'
        if '.mp3' in filename.lower():
            file_info = ID3(abs_file)
            title = str(file_info.get('TIT2'))
        if '.flac' in filename.lower():
            file_info = mutagen.File(abs_file)
            title = file_info.tags['title'][0]
        return unidecode(title)

    def get_artist(self, filename):
        '''Get the artist of the song via mutagen.'''
        abs_file = os.path.join(os.getcwd(), filename ) 
        artist = 'artist'
        if '.mp3' in filename.lower():
            file_info = ID3(abs_file)
            artist = str(file_info.get('TPE1'))
        if '.flac' in filename.lower():
            file_info = mutagen.File(abs_file)
            artist = file_info.tags['artist'][0]
        return unidecode(artist)

    def get_track_length(self, filename):
        '''Get the length of the song via mutagen. This is needed as our player function is not blocking.'''
        abs_file = os.path.join(os.getcwd(), filename ) 
        file_length = 0
        if '.mp3' in filename.lower():
            file_info = MP3(abs_file)
            file_length = file_info.info.length
        if '.flac' in filename.lower():
            file_info = FLAC(abs_file)    
            file_length = file_info.info.length
        return file_length