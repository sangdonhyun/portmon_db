import glob
import os
import re

class data_parse():
    def __init__(self):
        self.port_info  = {}


    def sample_data(self):
        flist = glob.glob(os.path.join('sample','*.tmp'))
        print flist
        return flist


    def get_port_info(self,back_data):
        line_set =back_data.splitlines()
        if 'Slot' in back_data:
            slot_bit = True
        else:
            slot_bit = False

        for line in line_set:
            if 'Online' in  line and 'FC' in line:
                line_tmp=line.split()
                port_index = line_tmp[0].strip()
                # print 'slot_bit :',slot_bit
                if slot_bit:
                    slot = line_tmp[1].strip()
                    portnum = line_tmp[2].strip()

                    self.port_info[port_index] = {'slot' : str(slot), 'portnum':str(portnum)}
                else:
                    portnum = line_tmp[1].strip()
                    self.port_info[port_index] = {'slot': '0', 'portnum': str(portnum)}

    def get_port_crc(self,back_data):
        line_set =back_data.splitlines()
        oneline_port= self.port_info.keys()
        for line in line_set:
            line_tmp = line.split()
            if len(line_tmp) > 17:
                port_index = line_tmp[0]

                if ':' in port_index:
                    # print line, len(line_tmp) ,line_tmp[4]
                    port_index = port_index.replace(':','')

                crc_cnt = line_tmp[4].strip()
                cnc_cnt  = line_tmp[3].strip()
                if port_index in oneline_port:
                    self.port_info[port_index]['crcerr'] = crc_cnt

                    # self.port_info[port_index]['cnc_cnt'] = cnc_cnt


    def is_online_port(self,slot,portnum):
        # print self.port_info
        online_port_index = None
        online_bit = False
        onlines= self.port_info.keys()
        for port_index in onlines:
            # print port_index,self.port_info[port_index]
            # print slot,portnum,self.port_info[port_index]['slot'] ,self.port_info[port_index]['portnum']


            if self.port_info[port_index]['slot'] == slot.strip() :
                if  self.port_info[port_index]['portnum'].strip() == portnum.strip():
                    online_bit = True
                    break
        return port_index,online_bit

    def get_port_sfp(self,back_data):

        line_set = back_data.splitlines()
        online_bit = False
        oneline_port = self.port_info.keys()
        for line in line_set:

            if re.match('^Port', line):

                #                 print 'port_line:',line.strip()
                portindex = line.split()[-1]
                #                 print portindex,':' in portindex
                if ':' in portindex:
                    portindex = portindex.replace(':', '')

            if re.match('^Slot', line) and 'Port' in line:
                "Slot  1/Port  6:"
                slotline = line
                slotline = slotline.replace('Slot', '')
                slotline = slotline.replace('/Port', '')
                slotline = slotline.replace(':', '')
                stset = slotline.split()
                slot = str(stset[0])
                pnum = str(stset[1])

                port_index,online_bit = self.is_online_port(slot,pnum)
                print online_bit,port_index
                if online_bit:
                    print slot, pnum, line
                    print 'port_index :', port_index
                    print 'online bit :', online_bit
            if online_bit:
                if re.match('^RX Power', line):
                    for arg in line.split():
                        if '(' in arg:
                            rx = arg.replace('(', '')
                            rx = rx.replace(')', '')
                            rx = rx.replace('uW', '')
                            self.port_info[port_index]['rx'] = str(rx)
                if re.match('^TX Power',line):
                    for arg in line.split():
                        if '(' in arg:
                            tx=arg.replace('(','')
                            tx = tx.replace(')', '')
                            tx = tx.replace('uW', '')
                            self.port_info[port_index]['tx']=str(tx)


    def main(self):
        flist = glob.glob(os.path.join('sample','*.tmp'))


        for f in flist:
            print f
            with open(f) as f:
                lineset = f.read()

        data_list=lineset.split('###***')
        # print data_list
        for back_data in data_list:
            print back_data[:10]
            # port index setting
            if back_data[:10] == 'switchshow':
                self.get_port_info(back_data)
            print self.port_info.keys()
            print self.port_info
            #crc err or enc count
            if back_data[:10] == 'porterrsho':
                self.get_port_crc(back_data)
            print self.port_info
            if back_data[:10] == 'porterrsho':
                self.get_port_crc(back_data)
            if back_data[:10] == 'sfpshow -a':
                self.get_port_sfp(back_data)

        for i in self.port_info.keys():
            print self.port_info[i]

if __name__=='__main__':
    print 'data'
    data_parse().main()