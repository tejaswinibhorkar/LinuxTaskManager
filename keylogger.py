from gi.repository import Gtk, GObject
import threading, app
import time

class KeyLoggerWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Key Logger")
        self.set_border_width(20)
        self.set_default_size(500, 400)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Box
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.box)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_border_width(10)
        self.scrolled_window.set_policy(
            Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)

        logLabel = Gtk.Label("Key Logger")
        self.box.pack_start(logLabel, True, True, 0)

        log = open("/home/keylogs").read()

        self.textview = Gtk.TextView()
        self.textview.set_editable(True)
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text(log)

        self.scrolled_window.add_with_viewport(self.textview)
        self.scrolled_window.set_size_request(800, 700)
        self.box.add(self.scrolled_window)

        self.back_button = Gtk.Button(label="Home")
        self.back_button.connect("clicked", self.home)
        self.box.pack_start(self.back_button, True, True, 0)

        # 1. define the tread, updating your text
        self.update = threading.Thread(target=self.refresh)
        # 2. Deamonize the thread to make it stop with the GUI
        self.update.setDaemon(True)
        # 3. Start the thread
        self.update.start()

    def refresh(self):
        print("edit text ")
        while True:
            time.sleep(2)
            log = open("/home/keylogs").read()
            GObject.idle_add(
                self.textbuffer.set_text, log,
                priority=GObject.PRIORITY_DEFAULT
                )

    def quit_window(self, widget, data):
        self.destroy()
        Gtk.main_quit()

    def home(self, widget):

        self.destroy()

        Gtk.main_quit()

        homeWindow = app.MainWindow()

        homeWindow.connect("delete-event", Gtk.main_quit)
        homeWindow.show_all()
        Gtk.main()



if __name__ == '__main__':
    window = KeyLoggerWindow()
    GObject.threads_init()
    window.connect("delete-event", Gtk.main_quit)
    window.show_all()
    Gtk.main()
