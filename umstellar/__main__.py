import logging
import sys
from contextlib import suppress

import gi
from gi.repository import Adw, Gdk, Gtk

from . import apps
from .apps import category_descriptions

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")


CATEGORY_DESCRIPTION = "Select the components you want to also include in your system"


app_list: dict[str, apps.App] = {}


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        kwargs["resizable"] = False
        kwargs["title"] = "Set up your system"
        super().__init__(*args, **kwargs)
        self.set_default_size(800, 600)
        # Things will go here
        self.header_bar = Adw.HeaderBar()
        logging.debug(self.header_bar.get_decoration_layout())
        # do not show window controls
        self.header_bar.set_title_widget(Adw.WindowTitle(title="Install More Apps"))
        self.header_bar.set_show_end_title_buttons(False)
        # don't add controls to headerbar
        # self.header_bar.set_show_close_button(False)
        self.install_button = Gtk.Button(
            label="Install Selections",
            css_classes=["suggested-action"],
            sensitive=False,
        )
        self.install_button.connect("clicked", self.install)

        skip_button = Gtk.Button(label="Skip")
        # skip_button.add_css_class("destructive-action")

        skip_button.connect("clicked", self.skip)

        self.header_bar.pack_start(skip_button)
        # add button to headerbar (on the end)
        self.header_bar.pack_end(self.install_button)

        self.set_titlebar(self.header_bar)

        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_size_request(800, 200)
        # force max box size to be 800x600

        # self.sidebar = Gtk.StackSidebar()
        # self.sidebar.get_stack()

        self.sidebar = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        for cat in sorted(set(x.category or "Utilities" for x in apps.apps.values())):
            logging.info(f"Found category {cat}")
            row = Gtk.ListBoxRow(name=cat)
            # set icon for the row too

            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

            # Get icon name from apps.py:category_icons dict
            # if not found, use "applications-other"
            icon_name = apps.category_icons.get(cat, "applications-other")
            icon = Gtk.Image.new_from_icon_name(icon_name)

            row_box.append(icon)

            title_label = Gtk.Label(
                label=cat.title(),
                margin_top=10,
                margin_bottom=10,
                margin_start=25,
                margin_end=25,
            )

            row_box.append(title_label)

            row.set_child(row_box)
            # make row text align to the left
            row.get_child().set_halign(Gtk.Align.START)
            self.sidebar.append(row)
        self.sidebar.connect("row-selected", self.on_sidebar_click)
        self.sidebar.add_css_class("navigation-sidebar")

        # left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # left.set_size_request(200, -1)
        # left.append(self.sidebar)

        self.box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, vexpand=False, hexpand=True
        )

        # force size of box1 to be 800x600

        self.box.set_margin_start(25)
        self.box.set_margin_end(25)
        self.box.set_margin_top(25)
        self.box.set_margin_bottom(25)

        # split into 2 boxes

        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_bottom=25)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_string(".text-center { text-align: center; }")
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        # FIXME: how can I center align this
        self.cta_label = Gtk.Label(css_classes=["h4", "text-center"])
        self.cta_label.set_xalign(0.5)
        self.cta_label.set_markup(CATEGORY_DESCRIPTION)

        header_box.append(self.cta_label)

        self.box.append(header_box)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # GtkListBox of AdwActionRows

        self.listbox = Gtk.ListBox(
            selection_mode=Gtk.SelectionMode.NONE, css_classes=["boxed-list"]
        )

        # self.listbox.add_css_class("navigation-sidebar")

        default_cat = self.sidebar.get_first_child()
        if default_cat:
            default_cat = default_cat.get_name()
        else:
            default_cat = "Utilities"

        for id, app in apps.apps.items():
            if default_cat != app.category:
                continue
            row = apps.AppEntry(app, id)

            # connect row's suffix's tickbox to an action
            # where it adds the app to the list of apps to install

            row.tickbox.connect("toggled", self.on_app_toggled(row))

            # some doesn't have option_toggle
            with suppress(AttributeError):
                row.option_toggle.connect("toggled", self.on_rowoption_toggled(row))

            self.listbox.append(row)

        content_box.append(self.listbox)

        self.box.append(content_box)

        # note: this is the main view

        # self.big_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.big_box = Adw.NavigationSplitView()
        self.big_box.set_size_request(800, 600)
        # set size limit to 800x600

        self.set_child(self.big_box)
        # todo: port to Adw.NavigationSplitView
        sidebar_page = Adw.NavigationPage()
        sidebar_page.set_child(self.sidebar)
        self.big_box.set_sidebar(sidebar_page)

        self.list_page = Adw.NavigationPage()
        self.scrolled.set_child(self.box)
        self.list_page.set_child(self.scrolled)
        self.big_box.set_content(self.list_page)

        # self.scrolled.set_child(self.big_box)

    def on_sidebar_click(self, _: Gtk.ListBox, row: Gtk.ListBoxRow):
        logging.debug("Sidebar moment")
        cat = row.get_name()

        if desc := category_descriptions.get(cat, None):
            self.cta_label.set_markup(CATEGORY_DESCRIPTION + "\n" + desc)
        else:
            self.cta_label.set_markup(CATEGORY_DESCRIPTION)

        # clear the listbox
        while child := self.listbox.get_first_child():
            self.listbox.remove(child)

        # TOOD: refactor
        for id, app in apps.apps.items():
            if cat == "Utilities":
                if app.category:
                    continue
            elif app.category != cat:
                continue
            row = apps.AppEntry(app, id)

            # check app_list if the app is already in the list
            # if it is, set the tickbox to active, same for the option_toggle
            app_entry = app_list.get(id, None)
            if app_entry:
                row.tickbox.set_active(True)
                with suppress(AttributeError):
                    row.option_toggle.set_active(app_entry.option.option)

            # connect row's suffix's tickbox to an action
            # where it adds the app to the list of apps to install
            row.tickbox.connect("toggled", self.on_app_toggled(row))

            # some doesn't have option_toggle
            with suppress(AttributeError):
                row.option_toggle.connect("toggled", self.on_rowoption_toggled(row))

            self.listbox.append(row)

    def on_app_toggled(self, appentry: apps.AppEntry):
        def inner(checkbtn):
            logging.debug("toggled")

            if checkbtn.get_active():
                # set key of id in app_list to app
                app_list.update({appentry.appid: appentry.app})
                with suppress(AttributeError):
                    appentry.desc_label.set_visible(True)
                    appentry.optionbox.set_visible(True)
                    appentry.option_toggle.set_visible(True)
            else:
                # remove key from app_list
                app_list.pop(appentry.appid, None)
                with suppress(AttributeError):
                    appentry.optionbox.set_visible(False)

            logging.debug(app_list)
            self.install_button.set_sensitive(bool(app_list))

        return inner

    def close_window(self):
        self.close()
        return

    def install(self, _):
        self.close_window()
        logging.debug(app_list)
        self.destroy()

    def skip(self, _):
        # exit
        logging.debug("exiting")
        exit(0)

    def on_rowoption_toggled(self, parent):
        def inner(checkbtn):
            act = checkbtn.get_active()

            if opt := app_list.get(parent.appid, None).option:
                opt.set(act)
                if parent.appid in app_list:
                    opt.set(act)

            logging.debug(app_list)

        return inner


class App(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


def main():
    app = App()
    app.run(sys.argv)
    app.activate()

    # logging.debug(app_list)


if __name__ == "__main__":
    main()
