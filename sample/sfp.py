import re


class perform_sw():
    def __init__(self):
        self.slot_bit = False
        self.port_info = {}

    def get_online_port(self):
        with open('swshow.txt') as f:
            ret = f.read()
        with open('switch_2.txt') as f:
            ret = f.read()
        if 'Slot' in ret :
            self.slot_bit = True

        line_set = ret.splitlines()
        for i in range(len(line_set)):
            line = line_set[i]

            if 'Online' in  line:
                line_sp = line.split()

                if 'FC' in line:
                    if self.slot_bit:
                        portindex = int(line_sp[0])
                        slot       = int(line_sp [1])
                        portnum   = int(line_sp [2])
                        print {'portindex': portindex, 'slot': slot, 'portnum': portnum}
                        self.port_info[portindex] = {'portindex': portindex, 'slot': slot, 'portnum': portnum}
                    else:
                        portindex = int(line_sp[0])
                        slot = 0
                        portnum = int(line_sp[1])
                        self.port_info[portindex] = {'portindex': portindex, 'slot': slot, 'portnum': portnum}



    def is_online(self,portindex):
        online_port=self.port_info.keys()
        if portindex in online_port:
            return True
        else:
            return False


    def get_portindex(self,s_slot,s_portnum):
        online_port = self.port_info.keys()
        re_port_index = None
        for port_index in online_port:
            slot = self.port_info[port_index]['slot']
            portnum =self.port_info[port_index]['portnum']
            if slot == s_slot and s_portnum == portnum:
                re_port_index = port_index
        return re_port_index


    def get_sfp(self):

        with open('sfpshow.txt') as f:
            ret = f.read()
        with open('sfpshow2.txt') as f:
            ret = f.read()
        portindex = None
        online_bit = False
        line_set = ret.splitlines()
        for i in range(len(line_set)):
            line = line_set[i]

            if self.slot_bit:
                if re.match('^Slot',line):
                    line_sp = line.split('/')
                    slot = line_sp[0]
                    slot = slot.replace('Slot','')
                    port = line_sp[1]
                    port = port.replace(':','')
                    port = port.replace("Port",'')
                    portindex = self.get_portindex(int(slot),int(port))
                if not portindex == None:
                    if self.is_online(int(portindex)):
                        if re.match('^RX', line):
                            rx =  line.split('(')[1]
                            rx = rx.replace(')','')
                            rx = rx.replace('uW', '')
                            self.port_info[int(portindex)]['rx'] = rx
                        if re.match('^TX', line):
                            tx = line.split('(')[1]
                            tx = rx.replace(')', '')
                            tx = rx.replace('uW', '')
                            self.port_info[int(portindex)]['tx'] = tx
            else:
                if re.match('^Port', line):
                    portindex = line.split()[-1]
                    portindex = portindex.replace(':','')
                    online_bit = self.is_online(int(portindex))
                if online_bit:
                    if re.match('^RX', line):
                        rx=line.split(')')[0]
                        rx = rx.split('(')[1]
                        rx = rx.replace('uW','')
                        self.port_info[int(portindex)]['rx'] = rx

                    if re.match('^TX', line):
                        tx = line.split(')')[0]
                        tx = tx.split('(')[1]
                        tx = tx.replace('uW', '')
                        print tx
                        self.port_info[int(portindex)]['tx'] = tx

    def get_porterr(self):
        with open('porterrshow.txt') as f:
            ret = f.read()
        with open('porterrshow2.txt') as f:
            ret = f.read()
        line_set = ret.splitlines()
        for i in range(len(line_set)):
            line = line_set[i]
            if ':' in line:
                line_sp= line.split()
                enc = line_sp [3]
                crc = line_sp [4]
                portindex = line_sp[0]
                portindex = portindex.replace(':','')
                print portindex
                if self.is_online(int(portindex)):
                    self.port_info[int(portindex)]['crcerr'] = crc


    def get_througput(self):
        with open('througput.txt') as f:
            ret= f.read()
        with open('througput2.txt') as f:
            ret= f.read()
        line_set = ret.splitlines()
        port_list,value_list = [],[]
        if self.slot_bit:
            port_th_list=[]
            for i in range(len(line_set)):
                line=line_set[i]
                num= i%4
                if num == 0:
                    port_list=line.split()
                if num == 2:
                    line_sp = line.split()
                    slot = line_sp[1]
                    value_list =line_sp[2:]

                    for i in range(len(port_list)):
                        port = port_list[i]
                        val = value_list[i]
                        if not port == 'Total':
                            print 'slot,port ',slot,port
                            portindex = self.get_portindex(int(slot),int(port))
                            port_th_list.append([portindex,val])
            for th in port_th_list:
                try:
                    self.port_info[int(th[0])]['throughput'] = th[-1]
                except:
                    pass


        else:
            for i in range(len(line_set)):
                line=line_set[i]
                num= i%4
                if num == 0:
                    port_list=port_list+line.split()
                if num == 2:
                    value_list =value_list + line.split()

            print port_list
            print value_list
            for i in range(len(port_list)):
                portnum = port_list[i]
                value = value_list[i]
                if not portnum == 'Total':
                    if self.is_online(int(portnum)):
                        print portnum, value
                        self.port_info[int(portnum)]['throughput'] = value




    def main(self):
        self.get_online_port()
        print 'online port :',self.port_info.keys()
        self.get_sfp()
        self.get_througput()
        self.get_porterr()
        print self.port_info

if __name__ == '__main__':
    perform_sw().main()

