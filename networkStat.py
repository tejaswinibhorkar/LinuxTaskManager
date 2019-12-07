from time import sleep
import utilities
import os, re
import utilities


class NetworkInfo(object):
    def __init__(self):
        self.SNMP_FILE = '/proc/net/snmp'
        self.dev_file = '/proc/net/dev'

    def snmp_info(self):
        snmp_values = {}
        field_headers = []

        snmp_content = utilities.readfile(self.SNMP_FILE)
        line_count = 0
        for line in snmp_content:
            field_type, field_values = line.split(":", 1)
            field_values = field_values.split()
            if (field_type == 'Ip' or field_type == 'Tcp' or field_type == 'Udp')and line_count == 0:
                field_headers = field_values
                line_count = 1
            elif (field_type == 'Ip' or field_type == 'Tcp' or field_type == 'Udp') and line_count == 1:
                snmp_values[field_type] = dict(zip(field_headers, field_values))
                line_count = 0

        return snmp_values

    def nwUtilization_info(self):
        interface_content = utilities.readfile(self.dev_file)
        interface_transmitted = {}
        interface_speed = {}

        for i in range(2, len(interface_content)):
            line_data = interface_content[i].split()
            if line_data[0] == "lo:":
                break;
            else:
                interface = line_data[0].split(":")[0]
                interface_transmitted[interface] = line_data[9]
                cmd = "ethtool " + interface + " | grep Speed"
                output = os.popen(cmd).read()
                if not output:
                    speed = 0
                else:
                    speed = str(output).split(":")[1]
                    # print(speed)
                    speed = re.findall('\d+', speed)
                    speed = speed[0]

                interface_speed[interface] = speed

        return interface_transmitted, interface_speed

    def calculate_network_utilization(self, prev_data, curr_data, speed_data):
        metric = {}
        list_util = []

        for interface in curr_data:
            delta = float(curr_data[interface]) - float(prev_data[interface])

            if speed_data[interface] == 0:
                metric[interface] = delta
            else:
                metric[interface] = (delta/float(speed_data[interface]))*1000000 # bytes/second

            tup1 = (interface,metric[interface] )
            list_util.append(tup1)

        print(metric)
        print(list_util)
        return list_util



    def calculate_metrics(self, prev_snmp_values, curr_snmp_values):
        metric_values = {}
        for field_type in curr_snmp_values:

            delta_list = {}
            for key in curr_snmp_values[field_type]:

                prev_val = float(prev_snmp_values[field_type][key])
                curr_val = float(curr_snmp_values[field_type][key])

                if key == "ActiveOpens" or key == "CurrEstab":
                    delta_val = (curr_val + prev_val)/2
                else:
                    delta_val = (curr_val - prev_val)
                delta_list[key] = delta_val
            metric_values[field_type] = delta_list


        tcp_list = [("Tcp", metric_values['Tcp']['ActiveOpens'], metric_values['Tcp']['CurrEstab'], metric_values['Tcp']['InSegs'], metric_values['Tcp']['OutSegs'] )]
        udp_list = [("Udp", metric_values['Udp']['InDatagrams'], metric_values['Udp']['OutDatagrams'])]
        ip_list = [("Ip", metric_values['Ip']['Forwarding'], metric_values['Ip']['InReceives'], metric_values['Ip']['OutRequests'])]

        print(ip_list)
        print(tcp_list)
        print(udp_list)
        return tcp_list, udp_list, ip_list

