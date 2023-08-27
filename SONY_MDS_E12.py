###############################################################################
#
#   Interface module for the Sony MDS-E12 MiniDisc Recorder
#   probably also works with other studio decks
#
###############################################################################
#
#   2023 - August - Henk-Johan
#           - first version of interface module
#
###############################################################################
#
#   The MDS-E12 can communicate via the RS232 interface.
#   The communication is strictly in bytes. The cable is standard cross.
#   The RS232 settings are fixed at 9600 / 8bit / no parity / 1 bit
#
#   The deck communicates in packets
#   1 header            PC->MDS 0x7E    MDS->PC 0x6F
#   2 packet length     max 32 bytes
#   3 format type       fixed at 0x05
#   4 category          fixed at 0x47
#   5 data
#   6 terminator        fixed at 0xFF
#
#   Before commands can be used the deck must be put in remote mode.
#   At the end the deck needs to be taken out of remote mode so that the panel
#   buttons can be used again. They are blocked while in remote mode!
#
###############################################################################


import time                         # for sleeping
import serial                       # for RS232 connection


class MDS:

    def __init__(self, serialport):
        '''Init of the MDS. We need to parse the serialport location that we are going to use.'''
        self.serialport = serialport

    def serial_open(self):
        '''Open the serialport that we parsed at the init.'''
        self.ser = serial.Serial(
            port        = self.serialport,
            baudrate    = 9600,
            parity      = serial.PARITY_NONE,
            stopbits    = serial.STOPBITS_ONE,
            bytesize    = serial.EIGHTBITS,
            timeout     = 2
            )
        return self.ser.is_open

    def serial_close(self):
        '''Close the serialport that we parsed at the init.'''
        self.ser.close()
        return self.ser.is_open

    def process_command(self, b5, b6, data, debug = False, sleep=0.5):
        """Handle byte commands with the MDS. This method will only do a basic inspection of the data that comes back."""
        # add the terminator at the end
        data.append(0xFF)
        # add byte 6, then 5, then category, then format type at the front
        data.insert(0,b6)
        data.insert(0,b5)
        data.insert(0,0x47)
        data.insert(0,0x05)
        # now insert the amount of bytes in the packet at the front
        data.insert(0,len(data)+2)
        # add the header at the front
        data.insert(0,0x7E)
        # transform the list into a byte array so we can push it out of the RS232 port
        transmit = bytearray(data)
        # write to the RS232 port
        if debug:
            print('Transmitting:', list(transmit))
        trbytes = self.ser.write(transmit)
        if trbytes != len(transmit):
            return [-1]
        # small delay to give the MDS time to respond. keep in mind, it is slow.
        time.sleep(sleep)
        # check how many bytes are in the buffer    
        exp =  int(self.ser.in_waiting )
        if exp == 0:
            return [-2]
        if debug:
            print('received bytes: ', exp)
        # prepare a receive array with length of exp, the amount of bytes in the buffer
        receive = bytearray( exp )
        # read the bytes into the buffer and return
        self.ser.readinto(receive)
        return list(receive)

    def remote_on(self): # 6.2 / 7.2
        """Enable the remote mode of the MDS"""
        receive = self.process_command(0x10, 0x03, [])
        # we can expect a status message ?? --> to be double checked
        # print('remote_on', receive)
        if len(receive) == 0:
            return -1
        if receive[0] != 0x6F:      # check header
            return -1
        if receive[-1] != 0xFF:     # check terminator
            return -1
        if receive[-3] != 0x10:
            print('remote_on -2', receive)
            return -2
        if receive[-2] != 0x03:      # remote on accepted check
            print('remote_on -3', receive)
            return -3
        return 0

    def remote_off(self): # 6.2
        """Enable the remote mode of the MDS"""
        receive = self.process_command(0x10, 0x04, [])
        # print('remote_off', receive)
        if len(receive) == 0:
            return -1
        if receive[0] != 0x6F:      # check header
            return -1
        if receive[-1] != 0xFF:     # check terminator
            return -1
        if receive[4] != 0x10:
            print('remote_off -2', receive)
            return -2
        if receive[5] != 0x04:      # remote off accpted check
            print('remote_off -3', receive)
            return -3
        return 0

    def model_request(self): # 6.29
        """Verify the model data against a fixed response. This is probably fixed for the E12."""
        receive = self.process_command(0x20, 0x10)
        # print('model_request', receive)
        if len(receive) == 0:
            return -1
        if receive[0] != 0x6F:      # check header
            return -1
        if receive[-1] != 0xFF:     # check terminator
            return -2
        if receive[4] != 0x20:
            return -3
        if receive[5] != 0x10:
            return -4
        if receive[6] != 0x01:
            return -5
        if receive[7] != 0x03:
            return -6
        return 0

    def model_name_req(self): # 6.32
        """Ask the MDS for the model name."""
        name = ''
        receive = self.process_command(0x20, 0x22, [])
        # print('model_name_req', receive)
        if len(receive) == 0:
            return -1
        if receive[0] != 0x6F:      # check the header
            return -1
        if receive[-1] != 0xFF:     # check the terminator
            return -1
        if receive[4] != 0x20:
            return -2
        if receive[5] != 0x22:
            return -3
        if len(receive) > 5:
            for counter in range(6,len(receive)-1,1):
                if receive[counter] != 0:
                    name += chr(receive[counter])
            return name
        else:
            return -4

    def operation_play(self): # 6.4
        """Set operation mode : play"""
        receive = self.process_command(0x02, 0x01, [])
        # print('operation_play', receive)
        if len(receive) == 0:
            return -1
        if receive[0] != 0x6F:
            return -1
        if receive[-1] != 0xFF:
            return -1
        if receive[-3] != 0x02:
            return -2
        if receive[-2] != 0x01:
            return -3
        return 0

    def operation_stop(self): # 6.5 / 7.5
        """Set operation mode : stop"""
        receive = self.process_command(0x02, 0x02, [])
        # print('operation_stop:', receive)
        # when the deck is already in stop, then there will be no response ???
        # needs to be further checked at some point.
        if receive[0] == -2: # -2 means, no data received
            return 0
        if len(receive) == 0:
            return -1
        if receive[0] != 0x6F:
            return -1
        if receive[-1] != 0xFF:
            return -1
        if receive[-3] != 0x02:
            return -2
        if receive[-2] != 0x02:
            return -3
        return 0    

    def operation_rec(self): # 6.13
        """Set operation mode : rec"""
        receive = self.process_command(0x02, 0x21, [])
        # print('operation_rec', receive)
        if len(receive) == 0:
            return -1
        if receive[0] != 0x6F:
            return -1
        if receive[-1] != 0xFF:
            return -1
        if receive[-3] != 0x02:
            return -2
        if receive[-2] != 0x21:
            return -3    
        return 0

    def operation_eject(self): # 6.15
        """Set operation mode : eject"""
        receive = self.process_command(0x02, 0x40)
        print('operation_eject', receive)
        if len(receive) == 0:
            return -1
        if receive[0] != 0x6F:
            return -1
        if receive[-1] != 0xFF:
            return -1
        if receive[-3] != 0x02:
            return -2
        if receive[-2] != 0x40:
            return -3    
        return 0

    def status_req(self, debug = False): # 6.30 / 7.11
        """Ask the MDS for status information"""
        return_dict = dict()
        receive = self.process_command(0x20, 0x20, [])
        if debug:
            print('status_req', receive)
        if len(receive) == 0:
            return_dict['return'] = -1
            return return_dict
        if receive[0] != 0x6F:
            return_dict['return'] = -1
            return return_dict
        if receive[-1] != 0xFF:
            return_dict['return'] = -1
            return return_dict
        if receive[4] != 0x20:
            return_dict['return'] = -2
            return return_dict
        if receive[5] != 0x20:
            return_dict['return'] = -3
            return return_dict
        if receive[9] != 0x01:
            return_dict['return'] = -4
            return return_dict
        data1 = '{0:08b}'.format(receive[6])
        data2 = '{0:08b}'.format(receive[7])
        data3 = '{0:08b}'.format(receive[8])
        #-----------------------------------
        # print(data1, data2, data3)
        #-----------------------------------
        return_dict['return'] = 0
        #-----------------------------------
        # disc info
        if data1[2:3] == '1':
            return_dict['disc'] = 'no disc'
            if debug:
                print('\t', 'No disc')
        else:
            return_dict['disc'] = 'disc loaded'
            if debug:
                print('\t', 'Disc exist')
        #-----------------------------------
        # operation mode info
        if data1[4:8] == '0000':
            return_dict['mode'] = 'STOP'
            if debug:
                print('\t', 'STOP')
        if data1[4:8] == '0001':
            return_dict['mode'] = 'PLAY'
            if debug:
                print('\t', 'PLAY')
        if data1[4:8] == '0010':
            return_dict['mode'] = 'PAUSE'
            if debug:
                print('\t', 'PAUSE')
        if data1[4:8] == '0011':
            return_dict['mode'] = 'EJECT'
            if debug:
                print('\t', 'EJECT')
        if data1[4:8] == '0100':
            return_dict['mode'] = 'REC PLAY'
            if debug:
                print('\t', 'REC PLAY')
        if data1[4:8] == '0101':
            return_dict['mode'] = 'REC PAUSE'
            if debug:
                print('\t', 'REC PAUSE')
        if data1[4:8] == '0110':
            return_dict['mode'] = 'rehearsal'
            if debug:
                print('\t', 'rehearsal')
        if data1[4:8] == '1111':
            return_dict['mode'] = 'not available to play'
            if debug:
                print('\t', 'not available to play')
        #-----------------------------------
        # TOC info
        if data2[0:1] == '1':
            return_dict['TOC'] = 'read done'
            if debug:
                print('\t', 'TOC read done')
        else:
            return_dict['TOC'] = 'not yet read'
            if debug:
                print('\t', 'TOC read not yet')
        #-----------------------------------
        # REC info
        if data2[2:3] == '1':
            return_dict['REC'] = 'possible'
            if debug:
                print('\t', 'REC possible')
        else:
            return_dict['REC'] = 'impossible'
            if debug:
                print('\t', 'REC impossible')
        #-----------------------------------
        # Channels
        if data3[0:1] == '1':
            return_dict['channels'] = 'MONO'
            if debug:
                print('\t', 'MONO')
        else:
            return_dict['channels'] = 'STEREO'
            if debug:
                print('\t', 'STEREO')
        #-----------------------------------
        # copy info
        if data3[1:2] == '1':
            return_dict['COPY'] = 'impossible'
            if debug:
                print('\t', 'COPY impossible')
        else:
            return_dict['COPY'] = 'possible'
            if debug:
                print('\t', 'COPY possible')
        #-----------------------------------
        # DIN info
        if data3[2:3] == '1':
            return_dict['DIN'] = 'unlock'
            if debug:
                print('\t', 'DIN unlock')
        else:
            return_dict['DIN'] = 'lock'
            if debug:
                print('\t', 'DIN lock')
        #-----------------------------------
        # input info
        if data3[5:8] == '001':
            return_dict['input'] = 'analog'
            if debug:
                print('\t', 'Analog')
        if data3[5:8] == '011':
            return_dict['input'] = 'optical'
            if debug:
                print('\t', 'Optical')
        if data3[5:8] == '101':
            return_dict['input'] = 'coaxial'
            if debug:
                print('\t', 'Coaxial')
        #-----------------------------------
        return return_dict

    def toc_data_req(self): # 6.34 / 7.21
        """Ask the MDS for toc data"""
        return_dict = dict()
        receive = self.process_command(0x20, 0x44, [0x01])
        # print('toc_data_req', receive)
        if len(receive) == 0:
            return_dict['return'] = -1
            return return_dict
        if receive[0] != 0x6F:
            return_dict['return'] = -1
            return return_dict
        if receive[-1] != 0xFF:
            return_dict['return'] = -2
            return return_dict
        if receive[4] != 0x20:
            return_dict['return'] = -3
            return return_dict
        if receive[5] != 0x60:
            return_dict['return'] = -4
            return return_dict
        if receive[6] != 0x01:
            return_dict['return'] = -5
            return return_dict
        if receive[11] != 0x00:
            return_dict['return'] = -6
            return return_dict
        #-----------------------------------
        return_dict['return'] = 0
        #-----------------------------------
        return_dict['first_track'] = receive[ 7]
        return_dict['last_track']  = receive[ 8]
        return_dict['total_min']   = receive[ 9]
        return_dict['total_sec']   = receive[10]
        return return_dict

    def disc_data_req(self): # 6.31 / 7.12
        """Ask the MDS for disc data"""
        return_dict = dict()
        receive = self.process_command(0x20, 0x21, [])
        # print('disc_data_req', receive)
        if len(receive) == 0:
            return_dict['return'] = -1
            return return_dict
        if receive[0] != 0x6F:
            return_dict['return'] = -1
            return return_dict
        if receive[-1] != 0xFF:
            return_dict['return'] = -2
            return return_dict
        if receive[4] != 0x20:
            return_dict['return'] = -3
            return return_dict
        if receive[5] != 0x21:
            return_dict['return'] = -4
            return return_dict
        if receive[6] != 0x00:
            return_dict['return'] = -5
            return return_dict
        if receive[8] != 0x00:
            return_dict['return'] = -6
            return return_dict
        if receive[9] != 0x00:
            return_dict['return'] = -7
            return return_dict
        if receive[10] != 0x00:
            return_dict['return'] = -8
            return return_dict
        #-----------------------------------
        return_dict['return'] = 0
        #-----------------------------------
        data = '{0:08b}'.format(receive[7])
        #-----------------------------------
        if data[6:8] == '00':
            return_dict['disc'] = 'reserved'
        if data[6:8] == '01':
            return_dict['disc'] = 'recordable'
        if data[6:8] == '10':
            return_dict['disc'] = 'pre master'
        if data[6:8] == '11':
            return_dict['disc'] = 'reserved'
        #-----------------------------------
        if data[5:6] == '0':
            return_dict['protection'] = 'no protect'
        if data[5:6] == '1':
            return_dict['protection'] = 'protected'
        #-----------------------------------
        if data[4:5] == '0':
            return_dict['error'] = 'no error'
        if data[4:5] == '1':
            return_dict['error'] = 'disc error'
        #-----------------------------------
        return return_dict

    def disc_name_req(self) -> str: # 6.36 / 7.15
        """Ask the MDS for the disc name"""
        receive = self.process_command(0x20, 0x48, [0x01], sleep=0.7)
        # print('disc_name_req', receive)
        if len(receive) == 0:
            return '-1'
        if receive[0] != 0x6F:
            return '-1'
        if receive[-1] != 0xFF:
            return '-2'
        if receive[4] != 0x20:
            return '-3'
        if receive[5] == 0x85:
            disc_name = 'no disk name set'
            return disc_name
        if receive[5] == 0x48:
            disc_name = ''
            header      = 0
            terminator  = 0
            while terminator < len(receive):
                header      = receive.index(111,header)
                terminator  = receive.index(255,terminator)
                # get part of the message, then move to the next part
                part = receive[header+7:terminator]
                for item in part:
                    if (item != 0x00) and (item != 0xFF):
                        disc_name += chr(item)
                # move the new header 
                header      = terminator
                terminator  += 1
            return disc_name
        return 0

    def rec_remain_req(self) -> int: # 6.40
        """Ask the MDS for rec remain time"""
        receive = self.process_command(0x20, 0x54, [0x01])
        # print('rec_remain_req', receive)
        if len(receive) == 0:
            return -1
        if receive[0] != 0x6F:
            return -1
        if receive[-1] != 0xFF:
            return -2
        if receive[4] != 0x20:
            return -3
        if receive[5] != 0x54:
            return -4
        if receive[6] != 0x01:
            return -5
        minutes = receive[7]
        seconds = receive[8]
        return minutes*60 + seconds

    def track_name_req(self, tracknr) -> str: # 6.37 / 7.16 / 7.26
        """Ask the MDS for a track name"""
        receive = self.process_command(0x20, 0x4A, [tracknr], sleep=3)
        # print('track_name_req', receive)
        if len(receive) == 0:
            return '-1'
        if receive[0] != 0x6F:
            return '-1'
        if receive[-1] != 0xFF:
            return '-2'
        if receive[4] != 0x20:
            return '-3'
        if receive[5] == 0x86: # -> no track name message
            return 'no track name set'
        if receive[5] == 0x4A:
            track_name = ''
            header      = 0
            terminator  = 0
            while terminator < len(receive):
                header      = receive.index(111,header)
                terminator  = receive.index(255,terminator)
                # get part of the message, then move to the next part
                part = receive[header+7:terminator]
                for item in part:
                    if (item != 0x00) and (item != 0xFF):
                        track_name += chr(item)
                    # as soon as we see the 0x00 it is the end of the name
                    if item == 0x00:
                        break
                # move the new header 
                header      = terminator
                terminator  += 1
            return track_name
        return 0

    def track_name_write(self, tracknr, name) -> int: # 6.43
        """Ask the MDS to write a name to a track"""
        # name part needs to end with 0x00 to indicate to the MDS
        # that no further name data is to be expected
        name += chr(0x00)
        packet = 1
        namecounter = 0
        while namecounter < len(name):
            namepart = name[namecounter:namecounter+16]
            # print(namepart, len(namepart))
            data = []
            # only the first is sending track number
            if packet == 1:
                data.append(tracknr)
            else: # after that we continue with packet numbers
                data.append(packet)
            # byte all the letters
            for letter in namepart:
                data.append( ord(letter) )
            # different command if first or second
            if packet == 1:
                receive = self.process_command(0x20, 0x72, data)
            else:
                receive = self.process_command(0x20, 0x73, data)
            # handle the responses
            # print('track_name_write', receive)
            if receive[0] != 0x6F:
                return -1
            if receive[-1] != 0xFF:
                return -1
            if receive[4] != 0x20:
                return -2
            if receive[5] != 0x87:
                return -2
            # up the counters
            packet += 1
            namecounter += 16
        return 0