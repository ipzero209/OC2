import xml.etree.ElementTree as et
import requests
import pfw
import shelve
import os
import getpass


def clearSubScreen():
    """Used to clear the screen."""
    os.system('cls' if os.name = 'nt' else 'clear')


def getAPIKey(ip):
    user = raw_input('Username: ')
    passwd = getpass.getpass('Password: ')
    key_req = "https://" + ip + "/api/?type=keygen&user=" + user + "&password=" + passwd
    key_resp = requests.get(key_req, verify=False)
    key_respXML = et.fromstring(key_resp.content)
    key = key_respXML.find('./result/key').text
    return key

def genInventory(ip, key):
    """Generates a list of panfw devices based on Panorama's connected devices."""
    op_cmd = "https://" + ip + "/api/?type=op&cmd=<show><devices><connected></connected></devices></show>&key=" + key
    dev_list = []
    resp = requests.get(op_cmd, verify=False)
    respXML = et.fromstring(resp.content)
    devices = respXML.find('./result/devices/*')
    for device in devices:
        sn_node = device.find('serial')
        host_node = device.find('hostname')
        model_node = device.find('model')
        fam_node = device.find('family')
        version_node = device.find('sw-version')
        addr_node = device.find('ip-address')
        dev_instance = pfw.Device(sn_node.text, host_node.text, model_node.text, fam_node.text, version_node.text, addr_node.text)
        dev_list.append(dev_instance)
    for device in dev_list:
        this_dev = device.ser_num
        ha_cmd = "https://" + ip + "/api/?type=op&cmd=<show><high-availability><state></state></high-availability></show>&target=" + this_dev + "&key=" + str(api_key)
        ha_resp = requests.get(ha_cmd, verify=False)
        ha_respXML = et.fromstring(ha_resp.content)
        device.is_ha = ha_respXML.find('./result/enabled').text
        if device.is_ha == 'yes':
            device.ha_peer = ha_respXML.find('./result/group/peer-info/mgmt-ip').text
            device.ha_state = ha_respXML.find('./result/group/local-info/state').text
        else:
            device.ha_state = "Device not in HA."
    d = shelve.open(ip + '-' + 'data.db')
    d['inventory'] = dev_list
    print "New inventory generated and loaded"
    return dev_list

def loadInventory(ip):
    print "Loading inventory..."
    d = shelve.open(ip + '-' + 'data.db')
    dev_inv = d['inventory']
    print "Inventory loaded."
    clearSubScreen()
    return dev_inv

