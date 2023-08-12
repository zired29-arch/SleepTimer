import os

from PyQt6.QtGui import QIcon, QAction, QGuiApplication
from PyQt6.QtWidgets import QApplication, QWidget,  QVBoxLayout, QComboBox, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QTimer


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.duration = 1000

        self.setWindowTitle('Спокойной ночи')
        self.icon = QIcon('icon.png')
        self.setWindowIcon(self.icon)
        self.choice = QComboBox()
        self.choice.setEditable(True)
        self.choice.addItems(('5', '10', '20', '30', '45', '60', '90', '120', '180'))

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.choice.setCurrentText('Выбери время в минутах')

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.choice)

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon)
        self.tray.setVisible(True)
        self.menu = QMenu()
        self.quit = QAction("Выход")
        self.open = QAction('Показать')
        self.quit.triggered.connect(app.quit)
        self.open.triggered.connect(self.show)
        self.menu.addAction(self.open)
        self.menu.addAction(self.quit)
        self.tray.setContextMenu(self.menu)
        self.choice.currentIndexChanged.connect(self.set_timer)

        self.make_window()

    def set_timer(self):
        self.duration = int(self.choice.currentText())
        self.hide()
        self.timer.start(60000)

    def update(self):
        self.duration -= 1
        self.choice.setCurrentText(str(self.duration))
        if self.duration < 1:
            self.shutdown()

    def make_window(self):
        x = QGuiApplication.primaryScreen().availableGeometry().right()
        y = QGuiApplication.primaryScreen().availableGeometry().bottom()
        self.move(x - 200, y - 100)
        self.resize(200, 100)
        self.show()

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()

    @staticmethod
    def shutdown():
        os.system('shutdown /s /t 0')


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec()
