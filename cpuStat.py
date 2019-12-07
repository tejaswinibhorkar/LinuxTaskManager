from collections import OrderedDict
import re
import utilities

SECONDS = 0.01
PERCENT = 100

class CpuInfo(object):

    def __init__(self):

        self.STAT_FILE = '/proc/stat'
        self.MEM_INFO_FILE = '/proc/meminfo'
        self.cpu_count = 0

    def get_cpu_info(self):
        stat_content = utilities.readfile(self.STAT_FILE)
        values = OrderedDict()
        for line in stat_content:
            fields = line.split()
            is_cpu = re.findall('^cpu', fields[0])
            is_intr = re.findall('^intr', fields[0])
            is_ctxt = re.findall('^ctxt', fields[0])
            if is_cpu:
                self.cpu_count += 1
                field_values = [fields[1], fields[3], fields[4]]
                values[fields[0]] = field_values
            if is_intr:
                values[fields[0]] = fields[1]
            if is_ctxt:
                values[fields[0]] = fields[1]

        return values

    def get_mem_info(self):
        mem_content = utilities.readfile(self.MEM_INFO_FILE)
        values = OrderedDict()
        for line in mem_content:
            fields = line.split()
            is_totalMem = re.findall('^MemTotal', fields[0])
            is_freeMem = re.findall('^MemFree', fields[0])
            if is_totalMem:
                values[fields[0]] = fields[1]
            if is_freeMem:
                values[fields[0]] = fields[1]
        return values

    def calculate_cpu_metrics(self, prev_cpu_values, curr_cpu_values):

        listCpu = []
        list_intr =[]
        list_ctxt = []
        rate_intr_count =0
        rate_ctxt_count = 0

        for field in curr_cpu_values:
            if 'cpu' in field:
                # USER TIME
                prev_cpu_user_time = int(prev_cpu_values[field][0])
                cur_cpu_user_time = int(curr_cpu_values[field][0])
                delta_cpu_user_time = (cur_cpu_user_time - prev_cpu_user_time) * SECONDS

                # SYSTEM TIME
                prev_cpu_system_time = int(prev_cpu_values[field][1])
                cur_cpu_system_time = int(curr_cpu_values[field][1])
                delta_cpu_system_time = (cur_cpu_system_time - prev_cpu_system_time) * SECONDS

                # IDLE TIME
                prev_cpu_idle_time = int(prev_cpu_values[field][2])
                cur_cpu_idle_time = int(curr_cpu_values[field][2])
                delta_cpu_idle_time = (cur_cpu_idle_time - prev_cpu_idle_time) * SECONDS

                # CPU UTILIZATION
                total_cpu_used = delta_cpu_user_time + delta_cpu_system_time
                total_cpu_time = total_cpu_used + delta_cpu_idle_time
                overall_cpu_utilization = str(round(((total_cpu_used/total_cpu_time) * PERCENT), 2)) + "%"
                user_mode_utilization = str(round(((delta_cpu_user_time/total_cpu_time) * PERCENT), 2)) + "%"
                system_mode_utilization = str(round(((delta_cpu_system_time/total_cpu_time) * PERCENT), 2)) + "%"
               
		tup1 = (field, user_mode_utilization, system_mode_utilization,overall_cpu_utilization)
                listCpu.append(tup1)

            if 'intr' in field:
                prev_intr_count = int(prev_cpu_values[field])
                cur_intr_count = int(curr_cpu_values[field])
                rate_intr_count = (cur_intr_count - prev_intr_count)
                
                tup2 = ('Interrupt Count   ', rate_intr_count)
                list_intr.append(tup2)

            if 'ctxt' in field:
                prev_ctxt_count = int(prev_cpu_values[field])
                cur_ctxt_count = int(curr_cpu_values[field])
                rate_ctxt_count = (cur_ctxt_count - prev_ctxt_count)
                
                tup3 = ('Context Switches ', rate_ctxt_count)
                list_ctxt.append(tup3)

        return listCpu, list_intr, list_ctxt

    def swap_current_cache(self, curr_cpu_values):
        prev_cpu_values_swap = curr_cpu_values
        return prev_cpu_values_swap

    def calculate_mem_metrics(self, prev_mem, curr_mem):
        avg_mem = {}
        for field in curr_mem:
            prev_mem_value = float(prev_mem[field])
            cur_mem_value = float(curr_mem[field])
            avg_mem_value = ((prev_mem_value + cur_mem_value)/2) / 1024
            avg_mem[field] = avg_mem_value

        for memory in avg_mem:
            if 'MemFree' in memory:
                avg_free_mem = avg_mem[memory]

            if 'MemTotal' in memory:
                avg_total_mem = avg_mem[memory]

        total_mem_utilization = round((((avg_total_mem - avg_free_mem) / avg_total_mem) * PERCENT), 2)
        print("Total memory Utilization = {}%".format(total_mem_utilization))
        total_mem_utilization = str(total_mem_utilization) + "%"
        mem_list = []
        mem_list.append([total_mem_utilization])
        return mem_list
