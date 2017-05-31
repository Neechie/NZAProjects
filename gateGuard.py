#!/usr/bin/python

import bluetooth
import bluetooth._bluetooth as bluez
import time
import os
import subprocess
import sys

import logging 

# choose between DEBUG (log every information) or CRITICAL (only error)
logLevel=logging.DEBUG
#logLevel=logging.CRITICAL

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



###################################################################################################################################
print ("National Zoo and Aquarium Gate Guard")

brendanTile = 'ff:04:19:c1:cf:2d'
danielleTile = 'FF:3A:60:93:DE:A1'
russellTile =  'C6:54:F4:99:E7:E7'
fourthTile = 'CF:C3:75:38:F2:ED'
brendanPhone = 'E8:B4:C8:72:52:0D'
#:brendanlist = ["FF:04:19:C1:CF:2D", Brendan]


while True:
##Print date and time
        print("Checking " + time.strftime("%a %d %b %Y %H:%m:%S", time.gmtime()))

##Test MAC addresses
        result=bluetooth.lookup_name(brendanPhone, timeout=5)
        name= "BrendanP"
        if(result!=None):
                print ( name + ": IN")
        else:
                print ( name + ": OUT")

        result=bluetooth.lookup_name(brendanTile, timeout=1)
        name= "DanielleT"
        if(result!=None):
                print ( name + ": IN")
        else:
                print ( name + ": OUT")

        result=bluetooth.lookup_name(russellTile, timeout=1)
        name = "Russell"
        if(result!=None):
                print ( name +": IN")
        else:
                print ( name +": OUT")

        result=bluetooth.lookup_name(fourthTile, timeout=1)
        name = "4th Tile"
        if(result!=None):
                print ( name +": IN")
        else:
                print ( name +": OUT")

        time.sleep(10)




#def emailer():
