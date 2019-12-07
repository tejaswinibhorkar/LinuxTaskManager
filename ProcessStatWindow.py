from gi.repository import Gtk, GObject
from cpuStat import CpuInfo
from time import sleep
import app
from processStat import ProcessStat


stop = False
all_pids = []
all_procs = []
prev_cpu_values = {}
prev_proc_values = {}
prev_mem_values = {}


class ProcessWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Process Stats")
        self.set_border_width(20)
        self.set_size_request(950, 800)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # search entry
        self.entry = Gtk.Entry()
        self.entry.connect("changed", self.textchange)
        vbox.pack_start(self.entry, True, True, 0)

        self.search = ""

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_border_width(10)
        self.scrolled_window.set_policy(
            Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)

        topLabel = Gtk.Label("Top Output:")
        vbox.pack_start(topLabel, True, True, 0)

        global all_procs

        # initialize prev values
        self.initialize()
        sleep(1)
        all_procs = self.proc_stat_calculator()

        self.proc_list_store = Gtk.ListStore(str, str, str, int, int, float, float, float, float)
        for item in all_procs:
            if not self.search:
                self.proc_list_store.append(list(item))
            elif self.search in item:
                self.proc_list_store.append(list(item))
            else:
                for i in item:
                    if self.search in str(i):
                        self.proc_list_store.append(list(item))


        sorted_model = Gtk.TreeModelSort(model=self.proc_list_store)
        sorted_model.set_sort_column_id(5, Gtk.SortType.DESCENDING)
        self.proc_treeview = Gtk.TreeView(model=sorted_model)

        # Treeview
        for i, col_title in enumerate(["PID", "Username", "Program Name", "VmSize (kB)", "RSS (kB)",
                                       "%CPU", "%UM", "%SM",
                                       "%Mem"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            column.set_sort_column_id(i)
            if isinstance(i, float):
                column.set_cell_data_func(renderer, lambda col, cell, model, iter, unused: cell.set_property("text", "%g" % model.get(iter, 0)[0]))

            self.proc_treeview.append_column(column)

        self.scrolled_window.add_with_viewport(self.proc_treeview)
        self.scrolled_window.set_size_request(750, 500)
        vbox.add(self.scrolled_window)

        self.back_button = Gtk.Button(label="Back")
        self.back_button.connect("clicked", self.home)
        vbox.pack_start(self.back_button, True, True, 0)

        GObject.timeout_add_seconds(1, self.refresh_tree_view)

    def initialize(self):
        global all_pids, prev_cpu_values, prev_proc_values, prev_mem_values

        process_obj = ProcessStat()
        all_pids = process_obj.getAllPIDs()

        cpu_obj = CpuInfo()
        values = cpu_obj.get_cpu_info()
        prev_cpu_values = values['cpu']

        prev_proc_values = process_obj.read_process_info(all_pids)
        prev_mem_values = cpu_obj.get_mem_info()

    def proc_stat_calculator(self):

        global all_pids, prev_cpu_values, prev_proc_values, prev_mem_values, all_procs

        cpu_obj = CpuInfo()
        process_obj = ProcessStat()

        curr_cpu_values = cpu_obj.get_cpu_info()['cpu']
        curr_proc_values = process_obj.read_process_info(all_pids)


        all_process = process_obj.calculate_metrics(all_pids, prev_proc_values, curr_proc_values, prev_cpu_values, curr_cpu_values,
                                      prev_mem_values)

        prev_cpu_values = cpu_obj.swap_current_cache(curr_cpu_values)
        prev_proc_values = cpu_obj.swap_current_cache(curr_proc_values)

        print(all_procs)
        return all_process

    def refresh_tree_view(self):


        global all_procs
        all_procs = []

        self.proc_list_store.clear()

        print("In refresh method")
        all_procs = []
        all_procs = self.proc_stat_calculator()

        for item in all_procs:
            if not self.search:
                self.proc_list_store.append(list(item))
            elif self.search in item:
                self.proc_list_store.append(list(item))
            else:
                for i in item:
                    if self.search in str(i):
                        self.proc_list_store.append(list(item))

            self.proc_list_store.set_sort_column_id(5, Gtk.SortType.DESCENDING)
            self.proc_treeview.set_model(self.proc_list_store)
        return True

    def proc_quit_window(self, widget, data):
        global stop, all_procs, prev_cpu_values, prev_mem_values, prev_proc_values
        stop = True

        all_procs = []
        prev_proc_values = []
        prev_mem_values = []
        prev_cpu_values = []

        self.destroy()

        Gtk.main_quit()

    def home(self, widget):
        global stop, all_procs, prev_cpu_values, prev_mem_values, prev_proc_values
        stop = True

        all_procs = []
        prev_proc_values = []
        prev_mem_values = []
        prev_cpu_values = []

        self.destroy()

        Gtk.main_quit()

        homeWindow = app.MainWindow()

        homeWindow.connect("delete-event", Gtk.main_quit)
        homeWindow.show_all()
        Gtk.main()

    def textchange(self, widget):
        self.search = self.entry.get_text()
        print(self.search)


if __name__ == '__main__':
    window = ProcessWindow()
    window.connect("delete-event", window.proc_quit_window)
    window.show_all()
    Gtk.main()
