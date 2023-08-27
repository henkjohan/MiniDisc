###############################################################################
#
#   Demonstration script to record a track to the deck.
#
###############################################################################
#
#   2023 - August - Henk-Johan
#           - first version of the demo script
#
###############################################################################

import sys                                      # so that we know on what system we run
import time
from SONY_MDS_E12 import MDS as mds             # import the class for the deck
from audio_handler import AudioHandler as ahc   # wrapper for mutagen
ah = ahc()                                      # create instance of the class

# name of file to record to disc
filename = "SITHEA - Overthinking.flac"

print('#'*80)
print('Demo script to record a song to the MDS-E12')
print('#'*80)

# create instance of the deck and connect to a COM-port - Windows
if sys.platform == 'win32':
    deck = mds('COM4')

# if sys.platform == 'darwin':
#     deck = mds('xxxxxxx')

# if sys.platform == 'linux':
#     deck = mds('xxxxxxx')

# try to open the serial port
if not deck.serial_open():
    print('Could not open serial port:', deck.serialport)

# try to put the deck in remote mode
if deck.remote_on() != 0:
    print('Could not set MD deck in remote mode.')

# ask the model name of the deck
print('Connected with', deck.model_name_req() )

# ask how many seconds are left on the disc for recording
disc_remain_sec = deck.rec_remain_req()
print('REC remain request [sec]', '\t', disc_remain_sec)

# get some basic info from the song
title = ah.get_title(filename)
artist = ah.get_artist(filename)
track_name = artist + ' - ' + title
track_length = ah.get_track_length(filename)
print('Name   of track', '\t\t', track_name)
print('Length of track', '\t\t', track_length)

# check if there is space. else warn the user
if track_length > disc_remain_sec:
    print('Not enough space on Mini-disc left!')

# check what the next track number is going to be
toc_data = deck.toc_data_req()
print('Next tracknr', '\t\t\t', toc_data.get('last_track')+1)

# prepare deck for recording
print('Prepare for recording.')
deck.operation_rec()
time.sleep(5)
deck.operation_play()
print('Playback file from computer.')
ah.play_file(filename, track_length)    # sleep in the method...
print('Playback has ended.')
# stop the deck. recording complete
deck.operation_stop()
# give the deck time to finish up
time.sleep(2)

toc_data = deck.toc_data_req()
print('Track number', '\t\t\t', toc_data.get('last_track'))

deck.track_name_write(toc_data.get('last_track'), track_name)
print('Name on disc', '\t\t\t', deck.track_name_req(toc_data.get('last_track')) )

# disable the remote mode of the deck so that the front panel can be used
if not deck.remote_off() == 0:
    print('Could not disable remote mote of the deck')

# close the serial port
if deck.serial_close():
    print('Could not close serialport', deck.serialport)

print('#'*80)