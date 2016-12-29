import xml.etree.ElementTree as et
import requests
import pfw
import shelve
import os
import getpass
from time import sleep


# Set up logging for ops functions
logger = logging.getLogger("funct")
logger.setLevel(logging.DEBUG)
f_fh = logging.FileHandler("ops_center.log")
formatter = logging.Formatter('%(asctime)s %(name)s\t\t%(levelname)s:\t\t\t\t%(message)s')
f_fh.setFormatter(formatter)
logger.addHandler(f_fh)






def clearScreen():
    """Used to clear the screen."""
    os.system('cls' if os.name = 'nt' else 'clear')

def separator(nl):
    nl_count = 0
    while nl <= nl_count:
        print "\n"
    print "============================================="


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

# =========================================================
# Op menu functions
# =========================================================

def listDevices(dev_list):
    for device in dev_list:
        print device.hostname + "\t\t" + device.os_ver
    pause = raw_input('Press any key to continue.')
    return





def exportInventory(dev_list, ip):
    outfile = open(ip + 'device_inv.text', 'w+', 0)
    print "Exporting inventory for Panorama %s to filename %s-device_inv.txt" %(ip, ip)
    for device in dev_list:
        outfile.write(device.ser_num + '\n')
        outfile.write(device.hostname + '\n')
        outfile.write(device.model + '\n')
        outfile.write(device.os_ver + '\n')
        outfile.write(device.mgmt_ip + '\n')
        outfile.write(device.is_ha + '\n')
        outfile.write(device.ha_peer + '\n')
        outfile.write(device.ha_state + '\n')
        separator(2)
    outfile.close()
    return

def printInventory(dev_list):
    for device in dev_list:
        device.devInfo()
        separator(2)
        pause = raw_input('Press any key to continue')
    return

def printDevInfo(this_dev, dev_list):
    for device in dev_list:
        if device.hostname == this_dev:
            device.devInfo()
    pause = raw_input('Press any key to continue')
    return

# TODO: Handle response after job checker is complete \/

def getPANOSVersion(ip, this_host, dev_list, version, key):
    target_devs = []
    for device in dev_list:
        if device.hostname == this_host:
            this_dev = device
            target_devs.append(this_dev)
    if this_dev.is_ha == 'yes':
        peer_IP = this_dev.ha_peer
        for device in dev_list:
            if device.mgmt_ip == peer_IP:
                peer_dev = device
                target_devs.append(peer_dev)
    fam = this_dev.family
    target_ver = "PanOS_" + fam + "-" + version
    sw_list_req = "https://" + ip + "/api/?type=op&cmd=<request><batch><software><info></info></software></batch></request>&key=" key
    sw_list_resp = requests.get(sw_list_req, verify=False)
    if target_ver not in sw_list_resp.content:
        check_req = "https://" + ip + "api/?type=op&cmd=<request><batch><software><check></check></software></batch></request>&key=" + key
        check_resp = requests.get(check_req, verify=False)
        if check_resp.status_code != 200:
            logging.error('Failed to update software table.')
            break
        dl_req = "https://" + ip + "/api/?type=op&cmd=<request><batch><software><download><file>" + target_ver + "</file></download></software></batch></request>&key=" + key
        dl_resp = requests.get(dl_req, verify=False)
        dl_respXML = et.fromstring(dl_resp.content)
        msg = dl_respXML.find('./result/msg/line').text
        if "jobid" in msg:
            jobID = dl_respXML.find('./result/job').text
        else:
            logging.error("Issue with downloading %s: %s:%s" %(target_ver, str(dl_resp.status_code), msg))
        job_result = jobChecker(ip, jobID, key)
    if job_result == 1:
        break
    for t_dev in target_devs:
        up_str = "https://" + ip + "/api/?type=op&cmd=<request><batch><software><upload><file>" + target_ver + "/file><devices>" + t_dev.ser_num + "</devices></upload></software></batch></request>&key=" + api_key"
        up_resp = requests.get(up_str, verify=Flase)
        up_respXML = et.fromstring(up_resp.content)
        msg = up_respXML.find('./result/msg/line').text
        if "jobid" in msg:
            jobID = up_respXML.find('./result/job').text
        else:
            logging.error('Issue uploading %s on %s: %s' % (version, this_host, msg))
        job_result = jobChecker(ip, jobID, key)
    if job_result == 1:
        break





def jobChecker(ip, id, key):
    """Checks the status of the specified job."""
    job_check_str = "https://" + ip + "api/?type=op&cmd=<show><jobs><id>" + id + "</id></jobs></show>&key=" + key
    job_check_resp = requests.get(job_check_str, verify=False)
    job_checkXML = et.fromstring(job_check_resp.content)
    if job_check_resp.status_code != 200:
        logging.error('Code %i, %s' %(job_check_resp.status_code, job_check_resp.content))
    status = job_checkXML.find('./result/job/status').text
    progress = job_checkXML.find('./result/job/progress').text
    logging.info('Job ID %s on %s is %s percent complete.' % (id, ip, progress))
    while status == "ACT":
        sleep(10)
        job_check_resp = requests.get(job_check_str, verify=False)
        job_checkXML = et.fromstring(job_check_resp.content)
        status = job_checkXML.find('./result/job/status').text
        progress = job_checkXML.find('./result/job/progress').text
        logging.info('Job ID %s on %s is %s percent complete.' % (id, ip, progress))
        if progress == "99":
            print "Waiting for daemons to complete."
            sleep (120)
    job_check_resp = requests.get(job_check_str, verify=False)
    job_checkXML = et.fromstring(job_check_resp)
    result = job_checkXML.find('./result/job/result').text
    if result == "OK":
        logging.info('Job ID %s is complete on %s' %(id, ip))
        return 0
    else:
        logging.error('There was an issue with job %s on %s status is %s' %(id, ip, result))
        return 1




