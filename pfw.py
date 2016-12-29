 class Device:
    """Devices are managed from Panorama and have the following attributes:

    ser_num: Serial number of the manaaged device.
    hostname: Host name of the managed device.
    model: Model numer of the managed device.
    family: Model family of the managed device.
    os_ver: Version of PAN-OS running on the managed device.
    mgmt_ip: Management IP of the managed device.
    """


    def __init__(self, ser_num, hostname, model, family, os_ver, mgmt_ip, is_ha=None, ha_peer=None, ha_state=None):
        """Return a device object"""
        self.ser_num = ser_num
        self.hostname = hostname
        self.model = model
        self.family = family
        self.mgmt_ip = mgmt_ip
        if is_ha == None:
            is_ha = 'no'
            ha_peer = 'No Peer'
            ha_state = 'Device not in HA'

    def devInfo(self):
        print "Serial number: " + str(self.ser_num)
        print "Hostname: " + self.hostname
        print "Model: " + str(self.model)
        print "PAN-OS version: " + str(self.os_ver)
        print "Management Address: " + str(self.ip_addr)
        print "Device in HA? " + self.is_ha
        print "HA peer IP address: " + str(self.ha_peer)
        print "HA state: " + self.ha_state
