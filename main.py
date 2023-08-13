import os
from PyQt6.QtGui import QIcon, QAction, QGuiApplication
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSystemTrayIcon, QMenu, QSlider, QLineEdit, QPushButton
from PyQt6.QtCore import QTimer, Qt


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.duration = 1000
        self.create_ui()

    def create_ui(self):
        self.create_window()
        self.create_tray()

    def create_window(self):
        self.setWindowTitle('Спокойной ночи')
        self.icon = QIcon('icon.png')
        self.setWindowIcon(self.icon)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

        self.line = QLineEdit('Время в минутах')
        self.line.textChanged.connect(self.line_change)
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setGeometry(50,50, 200, 50)
        self.slider.setMinimum(1)
        self.slider.setMaximum(180)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(15)
        self.slider.valueChanged.connect(self.slider_change)
        self.button = QPushButton('Запустить')
        self.button.pressed.connect(self.set_timer)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.line)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.button)

        x = QGuiApplication.primaryScreen().availableGeometry().right()
        y = QGuiApplication.primaryScreen().availableGeometry().bottom()
        self.move(x - 500, y - 500)
        self.resize(200, 100)
        self.show()

    def create_tray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon)
        self.tray.setVisible(True)
        self.tray.activated.connect(self.show_window)
        self.menu = QMenu()
        self.quit = QAction("Выключить программу")
        self.stop = QAction("Выключить таймер")
        self.info = QAction('Таймер не запущен')
        self.stop.setDisabled(True)
        self.info.setDisabled(True)
        self.quit.triggered.connect(app.quit)
        self.stop.triggered.connect(self.stop_timer)
        self.menu.addAction(self.info)
        self.menu.addAction(self.stop)
        self.menu.addAction(self.quit)
        self.tray.setContextMenu(self.menu)

    def show_window(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()

    def slider_change(self):
        self.line.setText(str(self.slider.value()))
        self.slider.setTickInterval(15)

    def line_change(self):
        try:
            self.slider.setValue(int(self.line.text()))
        except ValueError:
            self.line.setText('0')

    def set_timer(self):
        try:
            self.duration = int(self.line.text())
            self.info.setText(f'Минут до отключения: {self.duration}')
            self.stop.setDisabled(False)
            self.hide()
            self.timer.start(60000)
        except ValueError:
            pass

    def stop_timer(self):
        self.timer.stop()
        self.info.setText('Таймер не запущен')
        self.stop.setDisabled(True)

    def update(self):
        self.duration -= 1
        self.info.setText(f'Минут до отключения: {self.duration}')
        self.slider.setValue(self.duration)
        if self.duration < 1:
            self.shutdown()

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