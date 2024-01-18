import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import os
from pypdf import PdfWriter

from .helpers import pdfopen



class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="pdfcover", resizable=False, default_width=320)
        self.set_border_width(10)

        self.cover = ''
        self.body = ''
        self.generated = ''

        ########################################################3
        # structure
        box_outer = Gtk.Box(spacing=25,
                            orientation=Gtk.Orientation.VERTICAL)
        self.add(box_outer)

        ########################################################3
        # cover picker
        vbox = Gtk.Box(spacing=10,
                       orientation=Gtk.Orientation.VERTICAL)
        box_outer.pack_start(vbox, False, True, 0)

        # file picker
        frame = Gtk.Frame()
        vbox.add(frame)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        frame.add(hbox)

        self.cover_label = Gtk.Label(label='...')
        hbox.pack_start(self.cover_label, True, True, 15)

        cover_button = Gtk.Button(label="Pick cover")
        cover_button.connect("clicked", self.on_pick_cover)
        hbox.pack_start(cover_button, False, True, 0)

        # extract first page
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        vbox.add(hbox)

        self.check_first_page = Gtk.CheckButton(label="Extract first page", active=True)
        hbox.pack_end(self.check_first_page, False, True, 0)

        ########################################################3
        # body picker
        frame = Gtk.Frame()
        box_outer.pack_start(frame, False, True, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        frame.add(hbox)

        self.body_label = Gtk.Label(label='...')
        hbox.pack_start(self.body_label, True, True, 15)

        body_button = Gtk.Button(label="Pick body")
        body_button.connect("clicked", self.on_pick_body)
        hbox.pack_start(body_button, False, True, 0)

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
            file = dialog.get_filename()

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
            file = dialog.get_filename()

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
            dialog = Gtk.MessageDialog(
                text='File already exists, override?', secondary_text=f"{self.generated}", parent=self, buttons=Gtk.ButtonsType.OK_CANCEL
            )

            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.CANCEL:
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
