import gi
from . import apps
from gi.repository import Gtk, Adw, GObject, GLib

gi.require_version("Gtk", "4.0")
# libadwaita
gi.require_version("Adw", "1")

global app_list
app_list = {}


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Things will go here
        title = Adw.WindowTitle()
        title.set_title("Set up your system")
        self.header_bar = Adw.HeaderBar()
        print(self.header_bar.get_decoration_layout())
        # do not show window controls
        self.header_bar.set_title_widget(title)
        self.header_bar.set_show_end_title_buttons(False)
        # don't allow resizing
        self.set_resizable(False)
        # don't add controls to headerbar
        # self.header_bar.set_show_close_button(False)
        install_button = Gtk.Button(
            label="Install",
        )
        install_button.add_css_class("suggested-action")

        install_button.connect("clicked", self.install)

        skip_button = Gtk.Button(
            label="Skip",
        )
        skip_button.add_css_class("destructive-action")

        skip_button.connect("clicked", self.skip)

        self.header_bar.pack_start(
            skip_button,
        )

        # add button to headerbar (on the end)
        self.header_bar.pack_end(
            install_button,
        )

        self.set_titlebar(self.header_bar)
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_size_request(800, 600)
        self.set_title("Set up your system")
        self.set_default_size(800, 600)
        # force max box size to be 800x600

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # self.box.set_size_request(800, 600)
        self.box.set_vexpand(False)
        self.box.set_hexpand(False)
        self.set_child(self.scrolled)
        # force size of box1 to be 800x600
        # dont allow resizing
        self.set_resizable(False)

        # box padding of 25px

        self.box.set_margin_start(25)
        self.box.set_margin_end(25)
        self.box.set_margin_top(25)
        self.box.set_margin_bottom(25)

        # split into 2 boxes

        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        cta_label = Gtk.Label()
        cta_label.add_css_class("h4")

        cta_label = Gtk.Label()

        cta_label.set_markup("Select the apps you want to install")

        header_box.append(cta_label)

        # set headerbox margin

        header_box.set_margin_bottom(25)

        self.box.append(header_box)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # GtkListBox of AdwActionRows

        listbox = Gtk.ListBox()

        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox.add_css_class("boxed-list")

        for id, app in apps.apps.items():
            row = apps.AppEntry(app, id)

            # connect row's suffix's tickbox to an action
            # where it adds the app to the list of apps to install

            row.tickbox.connect("toggled", self.on_app_toggled)

            listbox.append(row)

        content_box.append(listbox)

        # Second list box for uhh feature flags for each app

        listbox2 = Gtk.ListBox()

        listbox2.set_selection_mode(Gtk.SelectionMode.NONE)

        listbox2.add_css_class("boxed-list")

        self.box.append(content_box)
        self.scrolled.set_child(self.box)

    def on_app_toggled(self, checkbtn, **kwargs):
        print("toggled")
        act = checkbtn.get_active()

        parent = checkbtn.get_parent().get_parent().get_parent()
        print(parent)
        if act:
            # set key of id in app_list to app
            app_list.update({parent.appid: parent.app})
        else:
            # remove key from app_list
            app_list.pop(parent.appid)

        print(app_list)

    def on_option_toggled(self, checkbtn, **kwargs):
        print("toggled")
        act = checkbtn.get_active()

        parent = checkbtn.get_parent().get_parent().get_parent()
        print(parent)
        if act:
            # set key of id in app_list to app
            app_list.append({parent.appid: parent.app})
            parent.optionbox.show()
        else:
            # remove key from app_list
            app_list.remove({parent.appid: parent.app})

        print(app_list)
        # update option toggle sensitivity, or something

        parent.optionbox.hide()

    def close_window(self):
        self.close()
        return

    def install(self, button):
        self.close_window()
        print(app_list)
        self.destroy()

    def skip(self, button):
        # exit
        print("exiting")
        print(button)
        exit(0)


class App(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


def main():
    app = App()
    app.run()

    for app in app_list.values():
        app.execute()


if __name__ == "__main__":
    main()
