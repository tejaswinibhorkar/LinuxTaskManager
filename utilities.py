import platform
from gi.repository import Gtk


def readfile(path):
    try:
        with open(path, 'r') as file:
            data = file.readlines()
            return data
    except IOError as e:
        print('Error Reading File: {}'.format(e))


def swap_current_cache(self, curr_cpu_values):
    prev_cpu_values_swap = curr_cpu_values
    return prev_cpu_values_swap


def calculate_percent(value):
    return value * 100


def convert_jiffy_seconds(value):
    return value * 0.01


def convert_kbToMb_or_bytesToKb(value):
    return value * 0.001


def virtual_mem():
    uname_result = platform.uname()
    if "x86_64" in uname_result[5]:
        virtual_memory = 2 ** 64
    else:
        virtual_memory = 2 ** 32

    return virtual_memory/1024

def create_hist_sec(self):

    histGrid = Gtk.Grid()
    self.add(histGrid)

    # histBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    startLabel = Gtk.Label("Start date-time:")
    endLabel = Gtk.Label("End date-time:")

    # Start date for hist data
    self.start_date_time = Gtk.Entry()
    # End date for hist data
    self.end_date_time = Gtk.Entry()

    histGrid.add(startLabel)
    histGrid.attach_next_to(self.start_date_time, startLabel, Gtk.PositionType.RIGHT, 1, 1)
    histGrid.attach_next_to(endLabel, startLabel, Gtk.PositionType.BOTTOM, 1, 1)
    histGrid.attach_next_to(self.end_date_time, endLabel, Gtk.PositionType.RIGHT, 1, 1)

    self.calculate_button = Gtk.Button(label="Calculate")
    self.calculate_button.connect("clicked", self.calculate_hist_stats)
    histGrid.attach_next_to(self.calculate_button, self.start_date_time, Gtk.PositionType.RIGHT, 1, 1)

    return histGrid

# v = virtual_mem()
# print(v)

print(round(0.028464795395645778,2))
