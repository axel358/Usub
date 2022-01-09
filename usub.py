#!/usr/bin/python3

import sys
import gi
import utils
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, Gdk
from youtube_transcript_api import YouTubeTranscriptApi as yt_api
from youtube_transcript_api.formatters import WebVTTFormatter


class USub(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='cu.axel.usub')

        self.builder = Gtk.Builder.new_from_file('window.ui')
        self.window = None

        self.subs_list_box = self.builder.get_object('subs_list_box')
        self.url_entry = self.builder.get_object('url_entry')

        self.builder.connect_signals(self)

    def do_activate(self):
        if not self.window:
            self.window = self.builder.get_object('main_window')
            self.window.set_application(self)

        self.window.show_all()

    def parse_url(self, button):
        video_id = utils.get_video_id(self.url_entry.get_text())
        if video_id:
            try:
                sub_list = yt_api.list_transcripts(video_id)
                self.update_sub_list(sub_list)
            except Exception as e:
                print(e)
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
        dialog = Gtk.Dialog(title='Language code', use_header_bar=True)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        dialog.get_content_area().pack_start(Gtk.Label(label='Enter the language code to translate to'), False, False,
                                             10)
        lang_code_entry = Gtk.Entry()
        lang_code_entry.set_margin_start(5)
        lang_code_entry.set_margin_end(5)
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

    def show_options(self, widget, data, option1, option2):
        option1.set_opacity(1)
        option2.set_opacity(1)
        option1.set_sensitive(True)
        option2.set_sensitive(True)

    def hide_options(self, widget, data,  option1, option2):
        option1.set_opacity(0)
        option2.set_opacity(0)
        option1.set_sensitive(False)
        option2.set_sensitive(False)

    def update_sub_list(self, sub_list):
        for child in self.subs_list_box.get_children():
            self.subs_list_box.remove(child)

        for sub in sub_list:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            sub_lang_label = Gtk.Label(label=sub.language)
            sub_download_button = Gtk.Button(label='Download')
            sub_download_button.get_style_context().add_class('suggested-action')
            sub_download_button.connect('clicked', self.download_sub, sub)
            sub_translate_button = Gtk.Button(label='Translate')
            sub_translate_button.connect('clicked', self.translate_sub, sub)
            hbox.pack_start(sub_lang_label, False, True, 5)
            hbox.pack_end(sub_download_button, False, True, 5)
            hbox.pack_end(sub_translate_button, False, True, 5)

            self.hide_options(None, None, sub_download_button, sub_translate_button)
            event_box = Gtk.EventBox()
            event_box.connect('enter-notify-event', self.show_options, sub_download_button, sub_translate_button)
            event_box.connect('leave-notify-event', self.hide_options, sub_download_button, sub_translate_button)
            event_box.add(hbox)
            row.add(event_box)
            self.subs_list_box.add(row)

        self.subs_list_box.show_all()

    def show_about_dialog(self, button):
        dialog = Gtk.AboutDialog()
        dialog.props.program_name = 'USub'
        dialog.props.version = "0.1.0"
        dialog.props.authors = ['Axel358']
        dialog.props.copyright = '(C) 2021 Axel358'
        dialog.props.logo_icon_name = 'usub'
        dialog.set_transient_for(self.window)
        dialog.show()


if __name__ == "__main__":
    app = USub()
    app.run(sys.argv)
