from PyQt5 import QtCore, QtGui, QtWidgets
import sys


class QToaster(QtWidgets.QFrame):
    closed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QToaster, self).__init__(*args, **kwargs)
        QtWidgets.QHBoxLayout(self)

        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                           QtWidgets.QSizePolicy.Maximum)

        self.setStyleSheet('''
            QToaster {
                border: 1px solid gray;
                border-radius: 5px;
                background: palette(window);
            }
        ''')

        self.timer = QtCore.QTimer(singleShot=True, timeout=self.hide)

        self.opacityEffect = QtWidgets.QGraphicsOpacityEffect(opacity=0)
        self.setGraphicsEffect(self.opacityEffect)
        self.opacityAni = QtCore.QPropertyAnimation(self.opacityEffect, b'opacity')
        self.parent().installEventFilter(self)
        self.opacityAni.setStartValue(0.)
        self.opacityAni.setEndValue(1.)
        self.opacityAni.setDuration(100)
        self.opacityAni.finished.connect(self.checkClosed)
        self.margin = 10

    def checkClosed(self):
        if self.opacityAni.direction() == self.opacityAni.Backward:
            self.close()

    def restore(self):
        self.timer.stop()
        self.opacityAni.stop()
        if self.parent():
            self.opacityEffect.setOpacity(1)
        else:
            self.setWindowOpacity(1)

    def hide(self):
        self.opacityAni.setDirection(self.opacityAni.Backward)
        self.opacityAni.setDuration(500)
        self.opacityAni.start()

    def eventFilter(self, source, event):
        if source == self.parent() and event.type() == QtCore.QEvent.Resize:
            self.opacityAni.stop()
            parentRect = self.parent().rect()
            geo = self.geometry()
            geo.moveCenter(parentRect.center())
            geo.moveBottom(parentRect.bottom() - self.margin)
            self.setGeometry(geo)
            self.restore()
            self.timer.start()
        return super(QToaster, self).eventFilter(source, event)

    def enterEvent(self, event):
        self.restore()

    def leaveEvent(self, event):
        self.timer.start()

    def closeEvent(self, event):
        self.deleteLater()

    def resizeEvent(self, event):
        super(QToaster, self).resizeEvent(event)
        self.clearMask()

    @staticmethod
    def showMessage(parent, message,
                    icon=QtWidgets.QStyle.SP_MessageBoxInformation,
                    margin=10, closable=True,
                    timeout=5000):

        parent = parent.window()

        self = QToaster(parent)
        parentRect = parent.rect()

        self.timer.setInterval(timeout)

        if isinstance(icon, QtWidgets.QStyle.StandardPixmap):
            labelIcon = QtWidgets.QLabel()
            self.layout().addWidget(labelIcon)
            icon = self.style().standardIcon(icon)
            size = self.style().pixelMetric(QtWidgets.QStyle.PM_SmallIconSize)
            labelIcon.setPixmap(icon.pixmap(size))

        self.label = QtWidgets.QLabel(message)
        self.layout().addWidget(self.label)
        self.layout().setContentsMargins(10, 3, 10, 3)

        if closable:
            self.closeButton = QtWidgets.QToolButton()
            self.layout().addWidget(self.closeButton)
            closeIcon = self.style().standardIcon(
                QtWidgets.QStyle.SP_TitleBarCloseButton)
            self.closeButton.setIcon(closeIcon)
            self.closeButton.setAutoRaise(True)
            self.closeButton.clicked.connect(self.close)

        self.timer.start()
        self.raise_()
        self.adjustSize()
        self.margin = margin

        geo = self.geometry()
        geo.moveCenter(parentRect.center())
        geo.moveBottom(parentRect.bottom() - margin)

        self.setGeometry(geo)
        self.show()
        self.opacityAni.start()
