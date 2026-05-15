# SmartTutor Desktop — Точка входа
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon
from main_window import MainWindow
from styles import APP_STYLE
from session import load_session


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    app.setFont(QFont("Segoe UI", 10))
    app.setWindowIcon(QIcon("SmartTutor.png"))

    # Пытаемся загрузить сохранённую сессию
    saved = load_session()
    if saved and saved.get("token"):
        win = MainWindow(token=saved["token"], user=saved.get("user", {}))
    else:
        win = MainWindow()

    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
