###############################################################################
#
#   Demonstration script to get the deck out of remote mode.
#   When playing with the other scripts it is possible that you end up with
#   the deck in remote mode while the TOC has not been written yet. With this
#   small script you can then get the deck out of remote mode so that you can
#   still write the TOC info to the disc.
#
###############################################################################
#
#   2023 - August - Henk-Johan
#           - first version of the demo script
#
###############################################################################

import sys                                      # so that we know on what system we run
from SONY_MDS_E12 import MDS as mds             # import the class for the deck

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

# disable the remote mode of the deck so that the front panel can be used
if not deck.remote_off() == 0:
    print('Could not disable remote mote of the deck')

# close the serial port
if deck.serial_close():
    print('Could not close serialport', deck.serialport)