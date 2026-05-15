# SmartTutor Desktop — Главное окно
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from chat_widget import ChatWidget
from progress_widget import ProgressWidget
from profile_widget import ProfileWidget
from session import clear_session


class MainWindow(QMainWindow):
    def __init__(self, token=None, user=None):
        super().__init__()
        self.token = token
        self.user = user or {}
        self.is_logged = token is not None
        self.setWindowTitle("SmartTutor")
        self.setMinimumSize(1000, 660)
        self.resize(1200, 760)
        self.setWindowIcon(QIcon("SmartTutor.png"))
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── SIDEBAR ──
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background: #0d0d18; border-right: 1px solid #1e1e38;")
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(0, 0, 0, 0)
        sb.setSpacing(0)

        # Logo
        logo_area = QWidget()
        logo_area.setStyleSheet("QWidget { background: #0d0d18; border: none; border-bottom: 1px solid #1e1e38; }")
        logo_area.setFixedHeight(70)
        logo_l = QHBoxLayout(logo_area)
        logo_l.setContentsMargins(16, 0, 16, 0)
        logo_l.setSpacing(12)

        logo_icon = QLabel("🎓")
        logo_icon.setFixedSize(38, 38)
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_icon.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #6d5fff,stop:1 #9d7fff);
            border-radius: 11px;
            font-size: 20px;
            border: none;
        """)

        logo_info = QVBoxLayout()
        logo_info.setSpacing(3)
        logo_txt = QLabel("SmartTutor")
        logo_txt.setStyleSheet("""
            font-size: 16px; font-weight: 800; color: #ffffff;
            background: transparent; border: none; letter-spacing: -0.5px;
        """)
        logo_sub = QLabel("Учебный ассистент")
        logo_sub.setStyleSheet("""
            font-size: 11px; color: #40406a;
            background: transparent; border: none;
        """)
        logo_info.addWidget(logo_txt)
        logo_info.addWidget(logo_sub)
        logo_l.addWidget(logo_icon)
        logo_l.addLayout(logo_info)
        logo_l.addStretch()
        sb.addWidget(logo_area)

        # Nav buttons
        nav_area = QWidget()
        nav_area.setStyleSheet("background: transparent;")
        nav_l = QVBoxLayout(nav_area)
        nav_l.setContentsMargins(10, 14, 10, 14)
        nav_l.setSpacing(2)

        self.nav_btns = {}
        for key, icon, label in [("chat","💬","Чат"),("progress","📊","Прогресс"),("profile","👤","Профиль")]:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setFixedHeight(42)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._style_nav(btn, key == "chat")
            btn.clicked.connect(lambda _, k=key: self.show_section(k))
            nav_l.addWidget(btn)
            self.nav_btns[key] = btn
        sb.addWidget(nav_area)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("color: #1e1e38; background: #1e1e38; max-height: 1px; border: none;")
        sb.addWidget(div)
        sb.addStretch()

        # User section
        user_sec = QWidget()
        user_sec.setStyleSheet("background: #0a0a16; border-top: 1px solid #1e1e38;")
        user_sec.setFixedHeight(72)
        user_l = QHBoxLayout(user_sec)
        user_l.setContentsMargins(14, 0, 14, 0)
        user_l.setSpacing(10)

        self.av_label = QLabel()
        self.av_label.setFixedSize(38, 38)
        self.av_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel()
        self.name_label.setStyleSheet("background: transparent; border: none;")
        self.plan_label = QLabel()
        self.plan_label.setStyleSheet("font-size: 10px; color: #404068; background: transparent; border: none;")

        user_info = QVBoxLayout()
        user_info.setSpacing(2)
        user_info.addWidget(self.name_label)
        user_info.addWidget(self.plan_label)

        self.action_btn = QPushButton()
        self.action_btn.setFixedSize(36, 36)
        self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        user_l.addWidget(self.av_label)
        user_l.addLayout(user_info)
        user_l.addStretch()
        user_l.addWidget(self.action_btn)
        sb.addWidget(user_sec)
        root.addWidget(sidebar)

        # Update user section based on login state
        self.update_user_section()

        # ── CONTENT STACK ──
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: #0a0a12;")

        if self.is_logged:
            self.init_pages()
        else:
            self.init_guest_pages()

        root.addWidget(self.stack)

    def update_user_section(self):
        if self.is_logged:
            name = self.user.get("full_name") or self.user.get("username") or "?"
            self.av_label.setText(name[0].upper())
            self.av_label.setStyleSheet("""
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #6d5fff,stop:1 #1dd8a0);
                border-radius: 11px; color: white; font-size: 16px; font-weight: 700; border: none;
            """)
            self.name_label.setText(name[:16] + ("…" if len(name)>16 else ""))
            self.name_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #c0c0e8; background: transparent; border: none;")
            self.plan_label.setText("Free план")
            self.action_btn.setText("⏻")
            self.action_btn.setToolTip("Выйти")
            self.action_btn.setStyleSheet("""
                QPushButton {background: #1a1a30; border: 1px solid #2a2a50;
                    color: #60609a; border-radius: 10px; font-size: 15px;}
                QPushButton:hover {color: #ff5566; background: rgba(255,85,102,0.1); border-color: rgba(255,85,102,0.3);}
            """)
            try: self.action_btn.clicked.disconnect()
            except: pass
            self.action_btn.clicked.connect(self.logout)
        else:
            self.av_label.setText("?")
            self.av_label.setStyleSheet("""
                background: #1e1e38; border-radius: 11px;
                color: #40406a; font-size: 16px; font-weight: 700; border: none;
            """)
            self.name_label.setText("Не авторизован")
            self.name_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #50508a; background: transparent; border: none;")
            self.plan_label.setText("Войдите в аккаунт")
            self.action_btn.setText("→")
            self.action_btn.setToolTip("Войти")
            self.action_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6d5fff,stop:1 #9d7fff);
                    border: none; color: white; border-radius: 10px; font-size: 16px; font-weight: bold;
                }
                QPushButton:hover {background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7d6fff,stop:1 #ad8fff);}
            """)
            try: self.action_btn.clicked.disconnect()
            except: pass
            self.action_btn.clicked.connect(self.open_login)

    def init_pages(self):
        self.chat_w = ChatWidget(self.token, self.user)
        self.progress_w = ProgressWidget(self.token, self.user)
        self.profile_w = ProfileWidget(self.token, self.user)
        self.stack.addWidget(self.chat_w)
        self.stack.addWidget(self.progress_w)
        self.stack.addWidget(self.profile_w)

    def init_guest_pages(self):
        # Show locked state for all sections
        for label in ["Чат", "Прогресс", "Профиль"]:
            w = self.make_locked_page(label)
            self.stack.addWidget(w)

    def make_locked_page(self, name):
        w = QWidget()
        w.setStyleSheet("background: #0a0a12;")
        l = QVBoxLayout(w)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.setSpacing(16)

        icon = QLabel("🔒")
        icon.setStyleSheet("font-size: 52px; background: transparent;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel(f"{name} недоступен")
        title.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #7070b0; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub = QLabel("Войдите в аккаунт чтобы получить доступ")
        sub.setStyleSheet("font-size: 13px; color: #404060; background: transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn = QPushButton("  →  Войти в аккаунт")
        btn.setFixedSize(220, 48)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #6d5fff, stop:1 #9d7fff);
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #7d6fff, stop:1 #ad8fff);
            }
            QPushButton:pressed { background: #5545ef; }
        """)
        btn.clicked.connect(self.open_login)

        l.addWidget(icon)
        l.addWidget(title)
        l.addWidget(sub)
        l.addSpacing(8)
        l.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        return w

    def open_login(self):
        from auth_window import LoginDialog
        dlg = LoginDialog(self)
        dlg.logged_in.connect(self.on_logged_in)
        dlg.exec()

    def on_logged_in(self, data):
        self.token = data["access_token"]
        self.user = data
        self.is_logged = True
        self.update_user_section()
        # Clear stack and re-init
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.deleteLater()
        self.init_pages()
        self.show_section("chat")

    def _style_nav(self, btn, active):
        if active:
            btn.setStyleSheet("""
                QPushButton {background: rgba(109,95,255,0.14); color: #a090ff;
                    border: none; border-radius: 10px; text-align: left;
                    padding: 0 16px; font-size: 13px; font-weight: 600;}
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {background: transparent; color: #55559a;
                    border: none; border-radius: 10px; text-align: left;
                    padding: 0 16px; font-size: 13px; font-weight: 500;}
                QPushButton:hover {background: #181830; color: #c0c0e8;}
            """)

    def show_section(self, name):
        idx = {"chat":0, "progress":1, "profile":2}
        self.stack.setCurrentIndex(idx[name])
        for k, btn in self.nav_btns.items():
            self._style_nav(btn, k == name)
        if name == "progress" and self.is_logged:
            self.progress_w.load_data()

    def logout(self):
        reply = QMessageBox.question(self, "Выход", "Выйти из аккаунта?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            clear_session()         # ← удаляем сохранённую сессию
            self.token = None
            self.user = {}
            self.is_logged = False
            self.update_user_section()
            while self.stack.count():
                w = self.stack.widget(0)
                self.stack.removeWidget(w)
                w.deleteLater()
            self.init_guest_pages()
            self.show_section("chat")
