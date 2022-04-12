#!/usr/bin/python3

import sys
from youtube_transcript_api import YouTubeTranscriptApi as yt_api
from youtube_transcript_api.formatters import WebVTTFormatter
import PyQt5.QtWidgets as Qt
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5 import QtCore
import utils
from toast import QToaster
import resources


class MainWindow(Qt.QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        '''palette = self.palette()
        palette.setColor(QPalette.Highlight, QColor('red'))
        palette.setColor(QPalette.HighlightedText, QColor('red'))
        self.setPalette(palette)'''

        centerWidget = Qt.QWidget()
        vbox = Qt.QVBoxLayout()
        centerWidget.setLayout(vbox)
        self.setCentralWidget(centerWidget)

        self.urlEntry = Qt.QLineEdit()
        self.urlEntry.setPlaceholderText('Enter video url')
        goButton = Qt.QPushButton('GO')
        goButton.clicked.connect(self.parse_url)

        self.subsLv = Qt.QListWidget()
        self.subsLv.setSelectionMode(Qt.QAbstractItemView.NoSelection)
        self.subsLv.setSpacing(5)
        vbox.addWidget(self.subsLv)

        exitAct = Qt.QAction(QIcon.fromTheme('help-about', QIcon(':/icons/help-about.svg')), 'About', self)
        exitAct.triggered.connect(self.showAboutDialog)

        goAction = Qt.QAction(QIcon.fromTheme('edit-find', QIcon(':/icons/edit-find.svg')), 'GO', self)
        goAction.triggered.connect(self.parse_url)

        toolbar = self.addToolBar('main')
        toolbar.addWidget(self.urlEntry)
        toolbar.addAction(goAction)
        toolbar.addAction(exitAct)

        self.setGeometry(300, 300, 600, 450)
        self.setWindowTitle('USub')
        self.setWindowIcon(QIcon.fromTheme('usub', QIcon(':/icons/usub.svg')))
        self.show()

    def parse_url(self, button):
        video_id = utils.get_video_id(self.urlEntry.text())
        if video_id:
            try:
                sub_list = yt_api.list_transcripts(video_id)
                self.update_sub_list(sub_list)
            except Exception as e:
                Qt.QMessageBox.critical(self, 'Cannot get subs for the current video', str(e))
        else:
            QToaster.showMessage(self, 'Please enter a valid link', margin=15)

    def update_sub_list(self, subs):
        self.subsLv.clear()

        for sub in subs:
            item = Qt.QListWidgetItem(sub.language)
            item.setIcon(QIcon.fromTheme('add-subtitle', QIcon(':/icons/subtitle.svg')))
            actionsBox = Qt.QHBoxLayout()
            actionsWidget = Qt.QWidget()
            actionsWidget.setLayout(actionsBox)
            translateButton = Qt.QPushButton()
            translateButton.setIcon(QIcon.fromTheme('crow-translate-tray', QIcon(':/icons/translate.svg')))
            translateButton.clicked.connect(lambda: self.translateSub(sub))
            downloadButton = Qt.QPushButton()
            downloadButton.setIcon(QIcon.fromTheme('download', QIcon(':/icons/download.svg')))
            actionsBox.addStretch()
            actionsBox.setContentsMargins(0, 0, 0, 0)
            actionsBox.addWidget(translateButton)
            actionsBox.addWidget(downloadButton)
            downloadButton.clicked.connect(lambda state, s=sub: self.downloadSub(s))
            self.subsLv.addItem(item)
            self.subsLv.setItemWidget(item, actionsWidget)

    def downloadSub(self, sub):
        subContent = sub.fetch()
        self.saveSub('subtitle_' + sub.language_code+'.srt', subContent)

    def translateSub(self, sub):
        dialog = Qt.QDialog(self)
        dialog.setWindowTitle('Translate subtitle')
        buttonBox = Qt.QDialogButtonBox(Qt.QDialogButtonBox.Ok | Qt.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)
        vbox = Qt.QVBoxLayout()
        languageEntry = Qt.QLineEdit()
        languageEntry.setPlaceholderText('en')
        vbox.addWidget(Qt.QLabel('Enter the language code to transtale to'))
        vbox.addWidget(languageEntry)
        vbox.addWidget(buttonBox)
        dialog.setLayout(vbox)

        if dialog.exec_():
            if len(lang_code := languageEntry.text()) > 1:
                sub_content = sub.translate(lang_code).fetch()
                self.saveSub('subtitle_' + lang_code + '.srt', sub_content)

    def saveSub(self, name, subContent):
        files = Qt.QFileDialog.getSaveFileName(self, directory=name)
        if files[0]:
            formatter = WebVTTFormatter()
            sub = formatter.format_transcript(subContent)
            with open(files[0], 'w') as file:
                file.write(sub)

            QToaster.showMessage(self, 'Subtitle saved', margin=15)

    def showAboutDialog(self):
        Qt.QMessageBox.about(self, 'About USub', 'USub \nYouTube videos subtitle downloader \nAxel358 2022 \nv1.0 GPLv3.0')


if __name__ == '__main__':

    app = Qt.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
