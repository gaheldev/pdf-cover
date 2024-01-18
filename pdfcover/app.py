import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import os
from pypdf import PdfWriter

from .helpers import pdfopen



class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="pdf cover")
        self.set_border_width(10)

        self.cover = ''
        self.body = ''
        self.generated = ''

        ########################################################3
        # structure
        box_outer = Gtk.Box(spacing=6,
                      orientation=Gtk.Orientation.VERTICAL)
        self.add(box_outer)

        ########################################################3
        # cover picker
        listbox_cover = Gtk.ListBox()
        listbox_cover.set_selection_mode(Gtk.SelectionMode.NONE)
        box_outer.pack_start(listbox_cover, True, True, 0)

        # file picker
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        row.add(hbox)

        self.cover_label = Gtk.Label()
        hbox.pack_start(self.cover_label, True, True, 0)

        cover_button = Gtk.Button(label="Pick cover")
        cover_button.connect("clicked", self.on_pick_cover)
        hbox.pack_start(cover_button, False, True, 0)

        listbox_cover.add(row)

        # extract first page
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        box_outer.add(hbox)

        self.check_first_page = Gtk.CheckButton(label="Extract first page", active=True)
        hbox.pack_end(self.check_first_page, False, True, 0)

        ########################################################3
        # body picker
        listbox_body = Gtk.ListBox()
        listbox_body.set_selection_mode(Gtk.SelectionMode.NONE)
        box_outer.pack_start(listbox_body, True, True, 0)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        row.add(hbox)

        self.body_label = Gtk.Label()
        hbox.pack_start(self.body_label, True, True, 0)

        body_button = Gtk.Button(label="Pick body")
        body_button.connect("clicked", self.on_pick_body)
        hbox.pack_start(body_button, False, True, 0)

        listbox_body.add(row)
        box_outer.add(listbox_body)

        ########################################################3
        # export
        generate_button = Gtk.Button(label="Export")
        generate_button.connect("clicked", self.on_generate)
        box_outer.add(generate_button)


    @property
    def extract_first_page(self) -> bool:
        return self.check_first_page.get_active()


    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("pdf files")
        filter_text.add_mime_type("application/pdf")
        dialog.add_filter(filter_text)


    def pick_pdf(self, title: str):
        dialog = Gtk.FileChooserDialog(
            title=title, parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        self.add_filters(dialog)

        file = ''
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            file = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()
        return file


    def pick_export(self):
        dialog = Gtk.FileChooserDialog(
            title="Export pdf", parent=self, action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_APPLY,
            Gtk.ResponseType.APPLY,
        )

        self.add_filters(dialog)

        file = ''
        response = dialog.run()
        if response == Gtk.ResponseType.APPLY:
            print("Apply clicked")
            print("File selected: " + dialog.get_filename())
            file = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()
        return file


    def on_pick_cover(self, widget):
        self.cover = self.pick_pdf("Pick a cover")
        self.cover_label.set_label(os.path.basename(self.cover))


    def on_pick_body(self, widget):
        self.body = self.pick_pdf("Pick a body")
        self.body_label.set_label(os.path.basename(self.body))


    def on_generate(self, widget):
        self.generated = self.pick_export()
        if not self.generated.endswith('.pdf'):
            self.generated += '.pdf'

        if os.path.isfile(self.generated):
            print('file exists')
            return

        self.export()


    def export(self):
        if not self.cover or not self.body or not self.generated:
            print("Aborting export")
            return

        print(f'Exporting to {self.generated}...')

        merger = PdfWriter()

        if self.extract_first_page:
            merger.append(self.cover, [0])
        else:
            merger.append(self.cover)

        merger.append(self.body)

        merger.write(self.generated)
        merger.close()
        print('done')

        pdfopen(self.generated)



win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
