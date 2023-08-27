###############################################################################
#
#   Demonstration script for deck and disk information.
#
###############################################################################
#
#   2023 - August - Henk-Johan
#           - first version of the demo script
#
###############################################################################

import sys                              # so that we know on what system we run
from SONY_MDS_E12 import MDS as mds     # import the class for the deck

# create instance of the deck and connect to a COM-port - Windows
if sys.platform == 'win32':
    deck = mds('COM4')

# not tested on OSX yet
# if sys.platform == 'darwin':
    # deck = mds('xxxxxx')

# not tested on linux yet
# sys.platform == 'linux':
    # deck = mds('xxxxxx')

# try to open the serial port
if not deck.serial_open():
    print('Could not open serial port:', deck.serialport)

# try to put the deck in remote mode
if not deck.remote_on() == 0:
    print('Could not set MD deck in remote mode.')

# ask the model name of the deck
print('Connected with', deck.model_name_req() )

# ask the status of the disc in the deck
print('Disc data request', deck.disc_data_req() )

# ask status information of the deck
print('Status request', deck.status_req() ) # TBD

# ask information of the current disk in the deck
print('Disc data request', deck.disc_data_req() )

# ask the name of the disc in the deck
print('Disc name request', '\t\t', deck.disc_name_req() )

# ask the TOC for the first and last track
toc_data = deck.toc_data_req()
print('TOC data request', toc_data)

# ask the name of all the tracks on the disc
for counter in range(toc_data.get('first_track'), toc_data.get('last_track')+1,1):
    print('Track name request', '\t\t'+str(counter), '\t' + str( deck.track_name_req(counter) ))

# ask the deck how many seconds are left for recording
print('REC remain request [sec]', deck.rec_remain_req() )

# disable the remote mode of the deck so that the front panel can be used
if not deck.remote_off() == 0:
    print('Could not disable remote mote of the deck')

# close the serial port
if deck.serial_close():
    print('Could not close serialport', deck.serialport)