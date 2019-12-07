from time import sleep
from cpuStat import CpuInfo
import os
import socket
import utilities

TCP_FILE = '/proc/net/tcp'
UDP_FILE = '/proc/net/udp'
ETC_PASSWD_FILE = '/etc/passwd'

tcp = {}


class NetworkStat(object):

    def readContent(self, file_name):
        tcp_content = utilities.readfile(file_name)
        # skip the header line
        tcp_content.pop(0)

        connections = []

        for line in tcp_content:
            content = line.strip().split()

            # Local IP address and port number
            local_ip_port = content[1]
            local_dec_ip, local_dec_port = self.hex_to_dec_ip(local_ip_port)
            #local_hostname = convert_dec_ip_to_hostname(local_dec_ip)

            # Remote IP address and port number
            remote_ip_port = content[2]
            remote_dec_ip, remote_dec_port = self.hex_to_dec_ip(remote_ip_port)
           # remote_hostname = convert_dec_ip_to_hostname(remote_dec_ip)

            # Username of program
            uid = content[7]
            user_name = self.get_username_from_uid(uid)

            # Process ID
            inode = content[9]
            pid = self.get_pid_from_inode(inode)

            program_name = self.get_program_name_from_pid(pid)

            if file_name == TCP_FILE:
                protocol = 'TCP'
            else:
                protocol = 'UDP'

            l_hstnm = self.convert_dec_ip_to_hostname(local_dec_ip)
            r_hstnm = self.convert_dec_ip_to_hostname(remote_dec_ip)

            connection_tuple = (str(l_hstnm), str(local_dec_port), str(r_hstnm), str(remote_dec_port),
                                user_name, str(pid), program_name, protocol)
           
            connections.append(connection_tuple)

        return connections

    def get_pid_from_inode(self, inode):

        # list of all files and dir in /proc
        proc_files = os.listdir("/proc/")

        for f in proc_files:
            try:
                integer = int(f)
                pid = str(integer)
                fds = os.listdir("/proc/%s/fd/" % pid)
                for fd in fds:
                    # save the pid for sockets matching our inode
                    try:
                        if ('socket:[%d]' % int(inode)) == os.readlink("/proc/%s/fd/%s" % (pid, fd)):
                            # print(("/proc/%s/fd/%s" % (pid, fd)))
                            return pid
                    except OSError:
                        pass
            except ValueError:
                pass

    def get_username_from_uid(self, uid):
        username = "doesnt exists"
        etc_passwd_content = utilities.readfile(ETC_PASSWD_FILE)
        for line in etc_passwd_content:
            user_data = line.strip().split(":")

            if user_data[2] == str(uid):
                username = user_data[0]
        return username

    def hex_to_dec_ip(self, ip):
        hex_ip,hex_port = ip.split(":")
        dec_ip = "%i.%i.%i.%i" % (int(hex_ip[6:8], 16), int(hex_ip[4:6], 16), int(hex_ip[2:4], 16), int(hex_ip[0:2], 16))
        dec_port = "%i" % (int(hex_port, 16))

        return dec_ip, dec_port

    def convert_dec_ip_to_hostname(self, dec_ip):

        try:
            if dec_ip == "0.0.0.0":
                hostname = dec_ip
            else:
                hostname = socket.gethostbyaddr(dec_ip)
                hostname = hostname[0]
            return hostname
        except socket.herror:
            return dec_ip

    def get_program_name_from_pid(self, pid):

        if not pid:
            return 'None'

        comm = utilities.readfile("/proc/" + str(pid) + "/comm")
        return comm[0].strip()

    def getNetStatInfo(self):
        list1 = self.readContent(TCP_FILE)
        list2 = self.readContent(UDP_FILE)
        list3 = list1 + list2
        return list3

