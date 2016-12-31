#!/usr/bin/python

import requests
import os
import sys
import xml.etree.ElementTree as et
from time import sleep
import shelve
import pfw
import logging
import ops_functions as ops



# Set up logging
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("ops_center.log")
formatter = logging.Formater('%(asctime)s %(name)s\t\t%(levelname)s:\t\t\t\t%(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)






###################################################################################
##      Main Script Functions




def opsMenu(dev_list):
    ops_menu_option = True
    while ops_menu_option:
    print """
    1. List Devices
    2. Print Inventory
    3. Export Inventory
    4. Device Info
    5. Download PAN-OS Version to device
    6. Upgrade Device
    7. Exit Ops Menu"""
    menu_option = raw_input('What operation would you like to perform? ')
    if menu_option == "1":
        ops.clearScreen()
        ops.listDevices(dev_list)
        menu_option = True
        ops.clearScreen()
    elif menu_option == "2":
        ops.clearScreen()
        ops.printInventory(dev_list)
        menu_option = True
        ops.clearScreen()
    elif menu_option == "3":
        ops.exportInventory(dev_list, pano_IP)
        menu_option = True
        ops.clearScreen()
    elif menu_option == "4":
        ops.clearScreen()
        dev = raw_input("Enter the hostname of the firewall you would like to see: ")
        ops.printDevInfo(dev, dev_list)
        ops.clearScreen()
        menu_option = True
    elif menu_option == "5":
        dl_version = raw_input('What version of PAN-OS would you lime to Download (e.g. 7.1.4 or press I for more info): ')
        dev_host = raw_input('Which device would you like to download to (enter hostname)? ')
        ops.downloadPANOS(pano_IP, dev_host, dev_list, dl_version, api_key)
        print "%s downloaded on %s (and it's peer if in HA)" % (dl_version, dev)
        ops.clearScreen()
        menu_option = True
    elif menu_optio == "6":
        print "Please ensure that the device has the latest version of content installed."
        up_ver = raw_input('What version of PAN-OS would you like to install? Note that the script handles multiple versions (e.g. from 6.0.5 to 7.1.4):')
        dev_host = raw_input('Which device would you like to upgrade (enter hostname)? ')
        for device in dev_list:
            if device.hostname == dev_host:
                dev1 = device
                if dev1.is_ha == 'yes':
                    for device in dev_list:
                        if device.mgmt_ip == dev1.ha_peer:
                            dev2 = device
                    confirm = raw_input('%s is in HA with %s. Would you like to upgrade both? (Y/n) ' % (dev1.hostname, dev2.hostname))
                    if confirm == 'Y' or 'y' or '':
                        ops.haUpgrade(dev1, dev2, , version, pano_IP, api_key) # TODO - write ops ha upgrade function.
                    else:
                        conf_single = raw_input('Are you sure that you want to only upgrade one device in the HA pair? (y/N) ')
                        if conf_single == 'y' or 'Y':
                            ops.devUpgrade(dev1, version, pano_IP, api_key) # TODO - write ops single device upgrade function.
                        else:
                            print "Cancelling operation."
                            break
                else:
                    confirm = raw_input('This operation will upgrade %s to PAN-OS version %s. Do you want to contine? (Y/n) ')
                    if confirm == 'n' or 'N':
                        break
                    elif confirm == 'y' or 'Y' or '':
                        ops.devUpgrade(dev1, version, pano_IP, api_key)








# Get IP address of the Panorama that we want to work with
pano_IP = raw_input("Panorama IP address: ")


# Check to see if we have a data file for this Panorama yet.

data_file = pano_ip + '-' + 'data.db'
if os.path.isfile(data_file):
    logging.info('Data file found. Checking for API key.')
    d = shelve.open(data_file)
    try:
        api_key = d['api_key']
        logging.info('Existing API key loaded.')
        sleep(2)
    except Exception:
        print "No API key found. Please generate one."
        logging.error('No API key found. Please generate one.')
        sleep(2)
else:
    print "No data file found. Please generate an API key and inventory."
    logging.warning('No data file found. Please generate an API key and inventory.')



# Create main menu

menu_option = True
while menu_option:
    print """
    1. Create Inventory
    2. Load Inventory
    3. Generate API key
    4. Operations
    5. Quit
    """
    menu_option = raw_input("What are we doing today? ")
    if menu_option == "1":
        device_list = ops_functions.genInventory(pano_IP, api_key)
        menu_option = True
        clearMainScreen()
    elif menu_option == "2":
        clearMainScreen()
        device_list = loadInventory()
        menu_option = True
    elif menu_option == "3":
        api_key = ops_functions.getAPIKey(pano_IP)
        print "API key generated"
        menu_option = True
        clearMainScreen()
    elif menu_option == "4":
        clearScreen()
        opMenu(device_list)
        clearMainScreen()
        menu_option = True
    elif menu_option == "5":
        clearMainScreen()
        exit()
    else:
        menu_option = True
        clearMainScreen()









