from gi.repository import Gtk, GObject
from cpuStat import CpuInfo
from time import sleep
import threading
import app, utilities
from networkStat import NetworkInfo
from netstat import NetworkStat

stop = False
tcp = []
udp = []
ip = []
con = []

prev_protocol_values = {}
prev_interface_value = {}
nwSpeed = {}
nw_util_list =[]


class NetworkWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Network Stats")
        self.set_border_width(20)
        self.set_default_size(500, 400)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        histGrid = utilities.create_hist_sec(self)

        vbox.pack_start(histGrid, True, True, 0)
        networkLabel = Gtk.Label("Network Statistics:")
        vbox.pack_start(networkLabel, True, True, 0)

        networkBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(networkBox)
        global tcp, udp, ip, con

        # initialize prev values
        self.initialize()
        sleep(1)
        tcp, udp, ip = self.protocol_stat_calculator()

        self.tcp_list_store = Gtk.ListStore(str, float, float, float, float)
        for item in tcp:
            self.tcp_list_store.append(list(item))

        # Treeview
        self.tcp_treeview = Gtk.TreeView(self.tcp_list_store)

        for i, col_title in enumerate(["Field", "ActiveOpens", "CurrEstab", "InSegs", "OutSegs"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            column.set_sort_column_id(i)
            self.tcp_treeview.append_column(column)

        networkBox.pack_start(self.tcp_treeview, True, True, 0)

        self.udp_list_store = Gtk.ListStore(str, float, float)
        for item in udp:
            self.udp_list_store.append(list(item))

        # Treeview
        self.udp_treeview = Gtk.TreeView(self.udp_list_store)

        for i, col_title in enumerate(["Field", "InDatagrams", "OutDatagrams"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            column.set_sort_column_id(i)
            self.udp_treeview.append_column(column)

        networkBox.pack_start(self.udp_treeview, True, True, 0)

        self.ip_list_store = Gtk.ListStore(str, float, float, float)
        for item in ip:
            self.ip_list_store.append(list(item))

        # Treeview
        self.ip_treeview = Gtk.TreeView(self.ip_list_store)

        for i, col_title in enumerate(["Field", "Forwarding", "InReceives", "OutRequests"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            column.set_sort_column_id(i)
            self.ip_treeview.append_column(column)

        networkBox.pack_start(self.ip_treeview, True, True, 0)
        vbox.pack_start(networkBox, True, True, 0)


        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_border_width(10)
        self.scrolled_window.set_policy(
            Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)




        connectionLabel = Gtk.Label("Connections:")
        vbox.pack_start(connectionLabel, True, True, 0)

        net_stat_obj = NetworkStat()
        con = net_stat_obj.getNetStatInfo()
        self.con_list_store = Gtk.ListStore(str, str, str, str, str, str, str, str)
        for item in con:
            self.con_list_store.append(list(item))

        # Treeview
        self.con_treeview = Gtk.TreeView(self.con_list_store)

        for i, col_title in enumerate(["Local Address", "Port", "Remote Address", "Port", "UserName", "PID",
                                       "ProgramName", "Protocol"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            column.set_sort_column_id(i)
            self.con_treeview.append_column(column)

        self.scrolled_window.add_with_viewport(self.con_treeview)
        self.scrolled_window.set_size_request(750, 500)
        vbox.add(self.scrolled_window)

        global nw_util_list
        nw_util_list = self.networkUtil_calculator()

        self.nw_list_store = Gtk.ListStore(str, float)
        for item in nw_util_list:
            self.nw_list_store.append(list(item))

        # Treeview
        self.nw_util_treeview = Gtk.TreeView(self.nw_list_store)

        for i, col_title in enumerate(["Interface", "Utilization"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            column.set_sort_column_id(i)
            self.nw_util_treeview.append_column(column)

        vbox.pack_start(self.nw_util_treeview, True, True, 0)

        self.back_button = Gtk.Button(label="Home")
        self.back_button.connect("clicked", self.home)
        vbox.pack_start(self.back_button, True, True, 0)

        GObject.timeout_add_seconds(1, self.refresh_tree_view)

    def calculate_hist_stats(self, widget):
        print("Yet to implement")

    def initialize(self):
        global prev_protocol_values
        global prev_interface_value, nwSpeed

        net_obj = NetworkInfo()
        prev_protocol_values = net_obj.snmp_info()
        prev_interface_value, nwSpeed = net_obj.nwUtilization_info()

    def protocol_stat_calculator(self):

        global prev_protocol_values
        global tcp, udp, ip
        net_obj = NetworkInfo()
        curr_protocol_values = net_obj.snmp_info()
        tcp, udp, ip = net_obj.calculate_metrics(prev_protocol_values, curr_protocol_values)
        cpuObj = CpuInfo()
        prev_protocol_values = cpuObj.swap_current_cache(curr_protocol_values)
        print(tcp, udp, ip)
        return tcp, udp, ip

    def networkUtil_calculator(self):

        global prev_interface_value, nwSpeed, nw_util_list
        net_obj = NetworkInfo()

        curr, speed = net_obj.nwUtilization_info()
        nw_util_list = net_obj.calculate_network_utilization(prev_interface_value, curr, speed)
        return nw_util_list

    def refresh_tree_view(self):
        global tcp, udp, ip, con, nw_util_list

        if not stop:
            self.tcp_list_store.clear()
            self.udp_list_store.clear()
            self.ip_list_store.clear()
            # self.con_list_store.clear()

            print("In refresh method")
            tcp, udp, ip = self.protocol_stat_calculator()
            for item in tcp:
                self.tcp_list_store.append(list(item))
            self.tcp_treeview.set_model(self.tcp_list_store)

            for item in udp:
                self.udp_list_store.append(list(item))
            self.udp_treeview.set_model(self.udp_list_store)

            for item in ip:
                self.ip_list_store.append(list(item))
            self.ip_treeview.set_model(self.ip_list_store)

            net_stat_obj = NetworkStat()
            con = net_stat_obj.getNetStatInfo()
            self.con_list_store = Gtk.ListStore(str, str, str, str, str, str, str, str)
            print(con)
            for item in con:
                self.con_list_store.append(list(item))
            self.con_treeview.set_model(self.con_list_store)

            self.nw_list_store = Gtk.ListStore(str, float)
            nw_util_list = self.networkUtil_calculator()
            for item in nw_util_list:
                self.nw_list_store.append(list(item))
            self.nw_util_treeview.set_model(self.nw_list_store)

           
        return True

    def net_quit_window(self, widget, data):
        global stop
        global tcp, udp, ip
        stop = True

        tcp = []
        udp =[]
        ip = []
       
        self.destroy()

        Gtk.main_quit()

    def home(self, widget):
        global stop
        global tcp, udp, ip
        stop = True

        tcp = []
        udp = []
        ip = []

        self.destroy()

        Gtk.main_quit()

        homeWindow = app.MainWindow()

        homeWindow.connect("delete-event", Gtk.main_quit)
        homeWindow.show_all()
        Gtk.main()


if __name__ == '__main__':
    window = NetworkWindow()
    window.connect("delete-event", window.net_quit_window)
    window.show_all()
    Gtk.main()
