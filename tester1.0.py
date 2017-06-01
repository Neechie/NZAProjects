

#!/usr/bin/python
#   File : tester1.0.py
#   Author: Neechie
#   Date: 31/05/2017
#   Description : Gate guard function to eb run on raspberrypi
#   URL : 
#   Version : 1.0
#


#Tag Data array
TAG_DATA = [  
           "Brendan","ff:04:19:c1:cf:2d",
            "Danielle","ff:3a:60:93:de:a1",
            "Russell","c6:54:f4:99:e7:e7",
            "Tile4","cf:c3:75:38:f2:ed"
           ]

#Tag data
brendanTile = 'ff:04:19:c1:cf:2d'
danielleTile = 'ff:3a:60:93:de:a1'
russellTile = 'c6:54:f4:99:e7:e7'
tile4 = 'cf:c3:75:38:f2:ed'

import logging

# choose between DEBUG (log every information) or CRITICAL (only error)
logLevel=logging.DEBUG
#logLevel=logging.CRITICAL

#logOutFilename='/var/log/test_beacon.log'       # output LOG : File or console (comment this line to console output)

########################################################################################################################################

##import libs
import os
import subprocess
import sys
import struct
import bluetooth._bluetooth as bluez
import time
import requests
import signal
import threading
import RPi.GPIO as GPIO

red = 7
green = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(red, GPIO.OUT)

#Emailer function and details
from pythonEmailer import send_email

###### INPUT EMAILER ACCOUNT CREDENTIALS BELOW ##########
user = 'NZARasPi@gmail.com'
pwd = 'Jamala123'
recipient = 'brendan_neech@hotmail.com'
subject = 'Gate Alert'
name = 'Name'
body = "There has been an alarm at the gate! " + 'Name' + " has been detected leaving the premises at  " + time.strftime("%T, %d/%m/%y") + 'Sent from NZARasPi'
 
LE_META_EVENT = 0x3e
OGF_LE_CTL=0x08
OCF_LE_SET_SCAN_ENABLE=0x000C
EVT_LE_CONN_COMPLETE=0x01
EVT_LE_ADVERTISING_REPORT=0x02

def print_packet(pkt):
    for c in pkt:
        sys.stdout.write("%02x " % struct.unpack("B",c)[0])

def packed_bdaddr_to_string(bdaddr_packed):
    return ':'.join('%02x'%i for i in struct.unpack("<BBBBBB", bdaddr_packed[::-1]))

def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x00)

def hci_toggle_le_scan(sock, enable):
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)

def handler(signum = None, frame = None):
    time.sleep(1)  #here check if process is done
    sys.exit(0)   
    
for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
    signal.signal(sig, handler)
            
FORMAT = '%(asctime)s - %(name)s -  %(message)s'
if globals().has_key('logOutFilename') :
    logging.basicConfig(format=FORMAT,filename=logOutFilename,level=logLevel)
else:
    logging.basicConfig(format=FORMAT,level=logLevel)

#Reset Bluetooth interface, hci0
os.system("sudo hciconfig hci0 down")
os.system("sudo hciconfig hci0 up")

#Make sure device is up
interface = subprocess.Popen(["sudo hciconfig"], stdout=subprocess.PIPE, shell=True)
(output, err) = interface.communicate()

if "RUNNING" in output: #Check return of hciconfig to make sure it's up
    logging.debug('Ok hci0 interface Up n running !')
else:
    logging.critical('Error : hci0 interface not Running. Do you have a BLE device connected to hci0 ? Check with hciconfig !')
    sys.exit(1)
    
devId = 0
try:
    sock = bluez.hci_open_dev(devId)
    logging.debug('Connect to bluetooth device %i',devId)
except:
    logging.critical('Unable to connect to bluetooth device...')
    sys.exit(1)

old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)
hci_toggle_le_scan(sock, 0x01)


while True:
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )
    
    pkt = sock.recv(255)
    ptype, event, plen = struct.unpack("BBB", pkt[:3])

    if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
            i =0
    elif event == bluez.EVT_NUM_COMP_PKTS:
            i =0 
    elif event == bluez.EVT_DISCONN_COMPLETE:
            i =0 
    elif event == LE_META_EVENT:
            subevent, = struct.unpack("B", pkt[3])
            pkt = pkt[4:]
            if subevent == EVT_LE_CONN_COMPLETE:
                le_handle_connection_complete(pkt)
            elif subevent == EVT_LE_ADVERTISING_REPORT:
                num_reports = struct.unpack("B", pkt[0])[0]
                report_pkt_offset = 0
                for i in range(0, num_reports):
                            result=packed_bdaddr_to_string(pkt[report_pkt_offset + 3:report_pkt_offset + 9])
                            found=0
                            GPIO.output(green,GPIO.LOW)
                            GPIO.output(red,GPIO.HIGH)
                            if (result == brendanTile):
                                name = "Brendan"
                                print name +": detected at gate"
                                send_email(user, pwd, recipient, subject, body, name)
                                GPIO.output(green,GPIO.HIGH)
                                time.sleep(5)                    
                            elif (result == tile4):
                                name = "Tile 4"
                                print name + ": detected at gate"
                                    
                            elif (result == russellTile):
                                name = "Russell"
                                print name +": detected at gate"
                                 
                            else:
                                print "No breach of the gate"
                            
                           











    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
GPIO.cleanup()

