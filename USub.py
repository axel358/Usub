#!/usr/bin/python

import sys
import gi
import Utils
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from youtube_transcript_api import YouTubeTranscriptApi as yt_api
from youtube_transcript_api.formatters import WebVTTFormatter


class USub(Gtk.Application):
    def __init__(self, *args, **kargs):
        super().__init__(*args, application_id='cu.axel.usub', **kargs)

        self.builder = Gtk.Builder.new_from_file('MainWindow.glade')
        self.window = None

        self.subs_list_box = self.builder.get_object('subs_list_box')
        self.url_entry = self.builder.get_object('url_entry')

        self.builder.connect_signals(self)

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        if not self.window:
            self.window = self.builder.get_object('main_window')
            self.window.set_application(self)

        self.window.show_all()

    def parse_url(self, button):
        video_id = Utils.get_video_id(self.url_entry.get_text())
        if video_id:
            try:
                sub_list = yt_api.list_transcripts(video_id)
                self.update_sub_list(sub_list)
            except Exception:
                dialog = Gtk.MessageDialog(
                    transient_for=self.window,
                    flags=0, message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text='Something went wrong')
                dialog.format_secondary_text('Can\'t get subtitles for this video')
                dialog.run()
                dialog.destroy()

    def download_sub(self, button, sub):
        sub_content = sub.fetch()
        self.save_sub(sub_content, 'subtitle_' + sub.language_code+'.srt')

    def translate_sub(self, button, sub):
        dialog = Gtk.Dialog(title='Language code')
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        dialog.get_content_area().pack_start(Gtk.Label(label='Enter the language code to translate to'), True, True,
                                             10)
        lang_code_entry = Gtk.Entry()
        dialog.get_content_area().pack_start(lang_code_entry, True, True, 10)
        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            if len(lang_code := lang_code_entry.get_text()) > 1:
                sub_content = sub.translate(lang_code).fetch()
                self.save_sub(sub_content, 'subtitle_' + lang_code + '.srt')

        dialog.destroy()

    def save_sub(self, sub_content, name):
        dialog = Gtk.FileChooserDialog(title="Save subtitle", parent=self.window, action=Gtk.FileChooserAction.SAVE)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,
            Gtk.ResponseType.OK,
        )
        dialog.set_current_name(name)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            formatter = WebVTTFormatter()
            sub = formatter.format_transcript(sub_content)
            with open(dialog.get_filename(), 'w') as file:
                file.write(sub)

        dialog.destroy()

    def update_sub_list(self, sub_list):
        for child in self.subs_list_box.get_children():
            self.subs_list_box.remove(child)

        for sub in sub_list:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            sub_lang_label = Gtk.Label(label=sub.language)
            sub_download_button = Gtk.Button(label='Download')
            sub_download_button.connect('clicked', self.download_sub, sub)
            sub_translate_button = Gtk.Button(label='Translate')
            sub_translate_button.connect('clicked', self.translate_sub, sub)
            hbox.pack_start(sub_lang_label, False, True, 5)
            hbox.pack_end(sub_download_button, False, True, 5)
            hbox.pack_end(sub_translate_button, False, True, 5)
            row.add(hbox)
            self.subs_list_box.add(row)

        self.subs_list_box.show_all()


if __name__ == "__main__":
    app = USub()
    app.run(sys.argv)
