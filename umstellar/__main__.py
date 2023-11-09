import gi
from . import apps

gi.require_version("Gtk", "4.0")
# libadwaita
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Things will go here
        self.set_titlebar(Adw.HeaderBar())
        self.set_title("Set up your system")
        self.set_default_size(800, 600)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.box)
        # force size of box1 to be 800x600
        self.box.set_size_request(800, 600)
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

        # test action rows

        # row1 = Adw.ActionRow()
        # row1.set_title("NVIDIA Drivers")
        # row1.set_subtitle("Install NVIDIA drivers")

        # row2 = Adw.ActionRow()
        # row2.set_title("Steam")
        # row2.set_subtitle("The Steam gaming platform")

        # listbox.append(row1)

        # listbox.append(row2)

        self.app_list = []

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

    def on_app_toggled(self, checkbtn, **kwargs):
        print("toggled")
        act = checkbtn.get_active()

        parent = checkbtn.get_parent().get_parent().get_parent()
        print(parent)
        if act:
            # set key of id in app_list to app
            self.app_list.append({parent.appid: parent.app})
        else:
            # remove key from app_list
            self.app_list.remove({parent.appid: parent.app})

        print(self.app_list)

    def on_option_toggled(self, checkbtn, **kwargs):
        print("toggled")
        act = checkbtn.get_active()

        parent = checkbtn.get_parent().get_parent().get_parent()
        print(parent)
        if act:
            # set key of id in app_list to app
            self.app_list.append({parent.appid: parent.app})
            parent.optionbox.show()
        else:
            # remove key from app_list
            self.app_list.remove({parent.appid: parent.app})

        print(self.app_list)
        # update option toggle sensitivity, or something

        parent.optionbox.hide()


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


if __name__ == "__main__":
    main()
