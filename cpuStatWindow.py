from gi.repository import Gtk
from cpuStat import CpuInfo
from time import sleep
import threading
import app, utilities
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

overall_cpu =[]

interval = 5
stop = False
cpu_time = []
list_intr = []
list_ctxt = []
mem_list = []
prev_cpu_values = {}
prev_mem_values = {}

curr_cpu_values = {}
curr_mem_values = {}


class CPUWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="CPU Stats")
        self.set_border_width(20)
        self.set_default_size(500, 400)
        self.set_position(Gtk.WindowPosition.CENTER)


        # Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        histGrid = utilities.create_hist_sec(self)

        vbox.pack_start(histGrid, True, True, 0)
        cpuLabel = Gtk.Label("CPU Utilization:")
        vbox.pack_start(cpuLabel, True, True, 0)


        cpuBox = Gtk.Box()
        self.add(cpuBox)
        global cpu_time, list_intr, list_ctxt

        global mem_list

        # initialize prev values
        self.initialize()
        sleep(1)
        cpu_time, list_intr, list_ctxt, mem_list = self.cpu_stat_calculator()


        global overall_cpu

        self.cpu_time_list_store = Gtk.ListStore(str, str, str, str)
        for item in cpu_time:
            self.cpu_time_list_store.append(list(item))
            if 'cpu' in item:
                c = item[3].replace("%", "")
                overall_cpu.append(float(c))

        # Treeview
        self.cpu_time_treeview = Gtk.TreeView(self.cpu_time_list_store)

        for i, col_title in enumerate(["Core", "User Mode", "System Mode", "Overall"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            column.set_sort_column_id(i)
            self.cpu_time_treeview.append_column(column)

        cpuBox.pack_start(self.cpu_time_treeview, True, True, 0)
        vbox.pack_start(cpuBox, True, True, 0)

        graph_obj = GraphIt()
        self.graph_button = Gtk.Button(label="Graph it !")
        self.graph_button.connect("clicked", graph_obj.draw)
        vbox.pack_start(self.graph_button, True, True, 0)


        self.intr_list_store = Gtk.ListStore(str, int)
        for item in list_intr:
            self.intr_list_store.append(list(item))

        # Treeview
        self.intr_treeview = Gtk.TreeView(self.intr_list_store)

        for i, col_title in enumerate(["", ""]):
              renderer = Gtk.CellRendererText()
              column = Gtk.TreeViewColumn(col_title, renderer, text=i)
              column.set_sort_column_id(i)
              self.intr_treeview.append_column(column)

          # cpuBox.pack_start(self.intr_treeview, True, True, 0)
        vbox.pack_start(self.intr_treeview, True, True, 0)

        self.ctxt_list_store = Gtk.ListStore(str, int)
        for item in list_ctxt:
           self.ctxt_list_store.append(list(item))

        # Treeview
        self.ctxt_treeview = Gtk.TreeView(self.ctxt_list_store)

        for i, col_title in enumerate(["", ""]):
          renderer = Gtk.CellRendererText()
          column = Gtk.TreeViewColumn(col_title, renderer, text=i)
          column.set_sort_column_id(i)
          self.ctxt_treeview.append_column(column)

         # cpuBox.pack_start(self.ctxt_treeview, True, True, 0)
        vbox.pack_start(self.ctxt_treeview, True, True, 0)

        memUtilizationLabel = Gtk.Label("Memory Utilization")
        vbox.pack_start(memUtilizationLabel, True, True, 0)

        self.mem_list_list_store = Gtk.ListStore(str)
        for item in mem_list:
            self.mem_list_list_store.append(list(item))

        # Treeview
        self.mem_list_treeview = Gtk.TreeView(self.mem_list_list_store)

        for i, col_title in enumerate(["Utilization"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            self.mem_list_treeview.append_column(column)

        vbox.pack_start(self.mem_list_treeview, True, True, 0)

        self.back_button = Gtk.Button(label="Back")
        self.back_button.connect("clicked", self.home)
        vbox.pack_start(self.back_button, True, True, 0)

        self.update = threading.Thread(target=self.refresh_tree_view)
        self.update.setDaemon(True)
        self.update.start()


    def calculate_hist_stats(self, widget):
        print("Yet to implement")

    def initialize(self):
        global prev_cpu_values
        global prev_mem_values
        cpuObj = CpuInfo()
        prev_cpu_values = cpuObj.get_cpu_info()
        prev_mem_values = cpuObj.get_mem_info()

    def cpu_stat_calculator(self):

        global prev_cpu_values
        global prev_mem_values
        global curr_cpu_values
        global curr_mem_values
        global cpu_time, list_intr, list_ctxt
        global mem_list

        cpuObj = CpuInfo()

        curr_cpu_values = cpuObj.get_cpu_info()
        curr_mem_values = cpuObj.get_mem_info()

        cpu_time, list_intr, list_ctxt = cpuObj.calculate_cpu_metrics(prev_cpu_values, curr_cpu_values)
        mem_list = cpuObj.calculate_mem_metrics(prev_mem_values, curr_mem_values)
        print(mem_list)

        prev_cpu_values = cpuObj.swap_current_cache(curr_cpu_values)
        prev_mem_values = cpuObj.swap_current_cache(curr_mem_values)

        print(cpu_time)
        return cpu_time, list_intr, list_ctxt, mem_list

    def refresh_tree_view(self):
        global cpu_time, list_intr, list_ctxt, mem_list

        while not stop:
            sleep(2)
            self.cpu_time_list_store.clear()
            self.intr_list_store.clear()
            self.ctxt_list_store.clear()
            self.mem_list_list_store.clear()
            print("In refresh method")
            cpu_time, list_intr, list_ctxt, mem_list = self.cpu_stat_calculator()

            # self.cpu_time_list_store = Gtk.ListStore(str, str, str, str)
            for item in cpu_time:
                self.cpu_time_list_store.append(list(item))
                if 'cpu' in item:
                    c = item[3].replace("%", "")
                    overall_cpu.append(float(c))

            self.cpu_time_treeview.set_model(self.cpu_time_list_store)

            # self.intr_list_store = Gtk.ListStore(str, int)
            for item in list_intr:
                self.intr_list_store.append(list(item))
            self.intr_treeview.set_model(self.intr_list_store)

            # self.ctxt_list_store = Gtk.ListStore(str, int)
            for item in list_ctxt:
                self.ctxt_list_store.append(list(item))
            self.ctxt_treeview.set_model(self.ctxt_list_store)

            for item in mem_list:
                self.mem_list_list_store.append(list(item))
            self.mem_list_treeview.set_model(self.mem_list_list_store)

    def cpu_quit_window(self, widget, data):
        global stop
        global cpu_time, list_intr, list_ctxt
        stop = True

        cpu_time = []
        list_intr = []
        list_ctxt = []
        self.destroy()

        Gtk.main_quit()

    def home(self, widget):
        global stop
        global cpu_time, list_intr, list_ctxt
        stop = True

        cpu_time = []
        list_intr = []
        list_ctxt = []

        self.destroy()

        Gtk.main_quit()

        homeWindow = app.MainWindow()

        homeWindow.connect("delete-event", Gtk.main_quit)
        homeWindow.show_all()
        Gtk.main()


style.use('fivethirtyeight')


class GraphIt(object):

    def __init__(self):

        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(1,1,1)

    def animate(self,i):
        global overall_cpu
        xs = []
        ys = overall_cpu

        for i in range(0,len(overall_cpu)):
            xs.append(i)

        self.ax1.clear()
        self.ax1.plot(xs,ys)

    def draw(self, widget):
        print("Here")
        print(overall_cpu)
        ani = animation.FuncAnimation(self.fig, self.animate, interval=1000)
        plt.show()


if __name__ == '__main__':
    window = CPUWindow()
    window.connect("delete-event", window.cpu_quit_window)
    window.show_all()
    Gtk.main()
