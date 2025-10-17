import os
import sys
from PyQt6.QtCore import QTimer, Qt, QLockFile
from PyQt6.QtGui import QIcon, QAction, QGuiApplication
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSystemTrayIcon, QMenu, QSlider, QLineEdit,\
    QPushButton, QMessageBox
import ctypes


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.duration = 0
        self.create_window()
        self.create_tray()

    def create_window(self) -> None:
        self.setWindowTitle('Спокойной ночи')
        self.setWindowIcon(ICON)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

        self.line = QLineEdit('Время в минутах')
        self.line.textChanged.connect(self.line_change)
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setGeometry(50, 50, 200, 50)
        self.slider.setMinimum(1)
        self.slider.setMaximum(180)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(15)
        self.slider.valueChanged.connect(self.slider_change)
        self.button = QPushButton('Запустить')
        self.button.pressed.connect(self.set_timer)

        layout = QVBoxLayout(self)
        layout.addWidget(self.line)
        layout.addWidget(self.slider)
        layout.addWidget(self.button)

        x = QGuiApplication.primaryScreen().availableGeometry().right()
        y = QGuiApplication.primaryScreen().availableGeometry().bottom()
        self.move(x - 500, y - 500)
        self.resize(200, 100)
        self.show()

    def create_tray(self) -> None:
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(ICON)
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

    def show_window(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()

    def slider_change(self) -> None:
        self.line.setText(str(self.slider.value()))
        self.slider.setTickInterval(15)

    def line_change(self) -> None:
        try:
            self.slider.setValue(int(self.line.text()))
        except ValueError:
            self.line.setText('0')

    def set_timer(self) -> None:
        try:
            self.duration = int(self.line.text())
            self.info.setText(f'Минут до отключения: {self.duration}')
            self.stop.setDisabled(False)
            self.hide()
            self.timer.start(60001)  # 1 минута в милисекундах
        except ValueError:
            pass

    def stop_timer(self) -> None:
        self.timer.stop()
        self.info.setText('Таймер не запущен')
        self.stop.setDisabled(True)

    def last_warning(self) -> None:
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Предупреждение")
        dlg.setText(f"Компьютер выключится через {self.duration} минут")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        button_y = dlg.button(QMessageBox.StandardButton.Yes)
        button_y.setText('Ладно')
        button_n = dlg.button(QMessageBox.StandardButton.No)
        button_n.setText('Сбросить таймер')
        button_n.clicked.connect(self.stop_timer)
        dlg.setIcon(QMessageBox.Icon.Question)
        dlg.open()

    def update(self) -> None:
        self.duration -= 1
        self.info.setText(f'Минут до отключения: {self.duration}')
        self.slider.setValue(self.duration)

        if self.duration == 5:
            self.last_warning()

        if self.duration < 1:
            shutdown()

    # На кнопку закрытия приложение не должно выключаться, а только сворачиваться
    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()


def shutdown():
    app.quit()
    os.system('shutdown /s /t 10')


# Получаем файлы необходимые для запуска
def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


FILE_ATTRIBUTE_HIDDEN = 0x02


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ICON = QIcon(resource_path('icon.png'))
    app.setStyle("Fusion")

    app.setApplicationName("Sleeper")
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Sleeper')

    # Проверяем, чтобы это приложение не было запущено 2 раза
    lock = QLockFile('lock')
    if lock.tryLock(timeout=0):
        ctypes.windll.kernel32.SetFileAttributesW('lock', FILE_ATTRIBUTE_HIDDEN)  # Скрываем lock файл от пользователя
        window = MainWindow()
        app.exec()
        del lock

    else:
        lock_error = QMessageBox()
        lock_error.setIcon(QMessageBox.Icon.Information)
        lock_error.setText('Приложение уже запущено')
        lock_error.setWindowTitle('Ошибка')
        lock_error.setWindowIcon(ICON)  # Установите иконку окна
        lock_error.exec()
