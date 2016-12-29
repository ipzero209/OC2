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
        dev = raw_input('Which device would you like to download to (enter hostname)? ')
        downloadPANOS(ip, dev_host, dev_list, dl_version, api_key)






# Set up logging
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("ops_center.log")
formatter = logging.Formater('%(asctime)s %(name)s\t\t%(levelname)s:\t\t\t\t%(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)



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









