#!/usr/bin/python

import bluetooth
import time

print ("National Zoo and Aquarium Gate Guard")

brendanTile = 'FF:04:19:C1:CF:2D'
danielleTile = 'FF:3A:60:93:DE:A1'
russellTile =  'C6:54:F4:99:E7:E7'
fourthTile = 'CF:C3:75:38:F2:ED'

#brendanlist = ["FF:04:19:C1:CF:2D", Brendan]


while True:
##Print date and time
        print("Checking " + time.strftime("%a %d %b %Y %H:%m:%S", time.gmtime()))

##Test MAC addresses
        result=bluetooth.lookup_name('FF:04:19:C1:CF:2D', timeout=5)
        name= "Brendan"
        if(result!=None):
                print ( name + ": IN")
        else:
                print ( name + ": OUT")

        result=bluetooth.lookup_name(danielleTile, timeout=5)
        name= "Danielle"
        if(result!=None):
                print ( name + ": IN")
        else:
                print ( name + ": OUT")

        result=bluetooth.lookup_name(russellTile, timeout=5)
        name = "Russell"
        if(result!=None):
                print ( name +": IN")
        else:
                print ( name +": OUT")

        result=bluetooth.lookup_name(fourthTile, timeout=5)
        name = "4th Tile"
        if(result!=None):
                print ( name +": IN")
        else:
                print ( name +": OUT")

        time.sleep(10)




#def emailer():
