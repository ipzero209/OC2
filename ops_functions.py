import xml.etree.ElementTree as et
import requests
import pfw


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
