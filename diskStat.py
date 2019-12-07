from time import sleep
import re
import utilities

class DiskInfo(object):
    def __init__(self):
        self.DISK_STAT_FILE = '/proc/diskstats'

    def get_all_disk_names(self, path):
        disk_content = utilities.readfile(path)
        disk_name_list = []
        for line in disk_content:
            fields = line.split()
            is_disk = re.findall('(^[hs]d[a-z]+)', fields[2])
            is_disk_part = re.findall('(^[hs]d[a-z]+)([\d]+)', fields[2])
            if is_disk_part or is_disk:
                disk_name_list.append(fields[2])
        return disk_name_list

    def get_disk_stats(self, path, disk_name_list):
        disk_content = utilities.readfile(path)
        disk_stats = {}
        for line in disk_content:
            fields = line.split()
            disk_name = fields[2]
            if any(disk_name in name for name in disk_name_list):
                disk_stats[(fields[2], 'diskReads')] = fields[3]
                disk_stats[(fields[2], 'diskWrites')] = fields[7]
                disk_stats[(fields[2], 'BlockReads')] = fields[5]
                disk_stats[(fields[2], 'BlockWrites')] = fields[9]
        return disk_stats

    def calculate_metrics(self, disk_name_list, device_stats_cache, device_stats_current):
        disk_stat_list = []
        for name in disk_name_list:
            # get disk reads
            cur_disk_read = int(device_stats_current[(name, 'diskReads')])
            prev_disk_read = int(device_stats_cache[(name, 'diskReads')])

            # delta disk reads
            delta_disk_reads = (cur_disk_read - prev_disk_read)

            # get disk writes
            cur_disk_write = int(device_stats_current[(name, 'diskWrites')])
            prev_disk_write = int(device_stats_cache[(name, 'diskWrites')])

            # delta disk writes
            delta_disk_writes = (cur_disk_write - prev_disk_write)

            # get Block reads
            cur_block_reads = int(device_stats_current[(name, 'BlockReads')])
            prev_block_reads = int(device_stats_cache[(name, 'BlockReads')])

            # delta Block Reads
            delta_block_reads = (cur_block_reads - prev_block_reads)

            # get block writes
            cur_block_write = int(device_stats_current[(name, 'BlockWrites')])
            prev_block_write = int(device_stats_cache[(name, 'BlockWrites')])

            # delta Block writes
            delta_block_writes = (cur_block_write - prev_block_write)

            tup = (name, delta_disk_reads, delta_disk_writes, delta_block_reads, delta_block_writes)

            disk_stat_list.append(tup)

        return disk_stat_list

