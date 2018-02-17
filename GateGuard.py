

#!/usr/bin/python
#   File : GateGuard.py
#   Author: Neechie
#   Date: 31/05/2017
#   Description : Gate guard function to be run on raspberrypi
#   URL : 
#   Version : 1.0
#

import logging

logLevel=logging.DEBUG

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

#Counting marker for Tag Arrays
c=0

#Set GPIO pins for buttons and Leds
red = 7
green = 11
stopButton = 13
resetButton = 15
GPIO.setmode(GPIO.BOARD)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(red, GPIO.OUT)
GPIO.setup(stopButton, GPIO.IN)
GPIO.setup(resetButton, GPIO.IN)

marker = 0

GPIO.output(red,GPIO.LOW)
GPIO.output(green,GPIO.HIGH)

#Emailer function and details
from pythonEmailer import send_email

#Import tag data from TagData.py
from TagData import TAG, NAME


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

try:
            while marker == 0:
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
                                                for c in range(0,len(TAG)):

                                                            result=packed_bdaddr_to_string(pkt[report_pkt_offset + 3:report_pkt_offset + 9])
                                                            found=0
                                                            alarm = 0
                                                            if (result == TAG[c]):
                                                                        name = NAME[c]
                                                                        alarm = alarm + 1
                                                                        print name +": detected at gate"
                                                                        GPIO.output(red, GPIO.HIGH)
                                                                        GPIO.output(green, GPIO.LOW)
                                                                        if alarm == 1:
                                                                                    ###### INPUT EMAILER ACCOUNT CREDENTIALS BELOW ##########
                                                                                    user = "NZARasPi@gmail.com"
                                                                                    pwd = "Jamala123"
                                                                                    recipient = "brendan@nationalzoo.com.au"
                                                                                    subject = "Gate Alert: " + NAME[c]
                                                                                    name =  NAME[c]
                                                                                    body = ("There has been an alarm at the gate! \n" + name + " has been detected leaving the premises at  " +
                                                                                            time.strftime("%T, %d/%m/%y") + "\n\n Sent from NZA RasPi GateGuard")
 
                                                                                    send_email(user, pwd, recipient, subject, body, name)
                                                                                    time.sleep(3)
                                                                        if GPIO.input(resetButton) == 1:
                                                                                    alarm = 0
                                                                                    print "The alarm has been reset"
                                                                                    GPIO.output(red,GPIO.LOW)
                                                                                    GPIO.output(green,GPIO.HIGH)
                                                                                    time.sleep(5)
                                                                        elif GPIO.input(stopButton) == 1: 
                                                                                    marker = marker+1
                                                                        c = c+1
                                                                        
                                                            else:
                                                                        print "No breach of the gate"
                                                                        c = c+1


finally:
            print "Closing program"
            alarm = 0
            sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
            GPIO.cleanup()

