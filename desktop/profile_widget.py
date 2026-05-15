# SmartTutor Desktop — Виджет профиля
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from api import ApiWorker


class ProfileWidget(QWidget):
    def __init__(self, token, user):
        super().__init__()
        self.token = token
        self.user = user
        self._workers = []
        self.setup_ui()

    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        # Header
        title = QLabel("Профиль")
        title.setObjectName("section_title")
        layout.addWidget(title)

        # Hero card
        hero = QWidget()
        hero.setObjectName("card")
        hero.setStyleSheet("#card { background: #111119; border: 1px solid #1e1e30; border-radius: 14px; }")
        hero_l = QHBoxLayout(hero)
        hero_l.setContentsMargins(24, 24, 24, 24)
        hero_l.setSpacing(20)

        # Avatar
        av = QLabel()
        name = self.user.get("full_name") or self.user.get("username") or "?"
        av.setText(name[0].upper())
        av.setObjectName("profile_avatar")
        av.setFixedSize(72, 72)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #6d5fff,stop:1 #1dd8a0);
            border-radius: 20px; color: white; font-size: 28px; font-weight: 800;
        """)

        info = QVBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("font-size: 18px; font-weight: 800; color: #ffffff; background: transparent; letter-spacing: -0.5px;")
        email_lbl = QLabel(self.user.get("email") or "")
        email_lbl.setStyleSheet("font-size: 12px; color: #505080; background: transparent;")
        plan_lbl = QLabel("✦ Free план")
        plan_lbl.setStyleSheet("""
            background: rgba(109,95,255,0.12); color: #9d8fff;
            border: 1px solid rgba(109,95,255,0.25); border-radius: 99px;
            padding: 3px 12px; font-size: 11px; font-weight: 600;
        """)
        plan_lbl.setFixedWidth(90)

        info.addWidget(name_lbl)
        info.addWidget(email_lbl)
        info.addSpacing(6)
        info.addWidget(plan_lbl)
        hero_l.addWidget(av)
        hero_l.addLayout(info)
        hero_l.addStretch()
        layout.addWidget(hero)

        # Edit form card
        form_card = QWidget()
        form_card.setObjectName("card")
        form_card.setStyleSheet("#card { background: #111119; border: 1px solid #1e1e30; border-radius: 14px; }")
        form_l = QVBoxLayout(form_card)
        form_l.setContentsMargins(24, 20, 24, 20)
        form_l.setSpacing(12)

        card_title = QLabel("Основная информация")
        card_title.setObjectName("card_title")
        card_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #c0c0e0; background: transparent; padding-bottom: 12px; border-bottom: 1px solid #1e1e30;")
        form_l.addWidget(card_title)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setHorizontalSpacing(14)

        lbl_style = "font-size: 10px; font-weight: 600; color: #505080; background: transparent; letter-spacing: 0.5px;"

        name_lbl2 = QLabel("ПОЛНОЕ ИМЯ")
        name_lbl2.setStyleSheet(lbl_style)
        self.name_input = QLineEdit(self.user.get("full_name") or "")
        self.name_input.setPlaceholderText("Введите имя")
        self.name_input.setFixedHeight(38)

        user_lbl = QLabel("ИМЯ ПОЛЬЗОВАТЕЛЯ")
        user_lbl.setStyleSheet(lbl_style)
        self.user_input = QLineEdit(self.user.get("username") or "")
        self.user_input.setReadOnly(True)
        self.user_input.setFixedHeight(38)
        self.user_input.setStyleSheet("color: #505080; background: #0d0d14; border: 1px solid #1e1e30; border-radius: 8px; padding: 0 12px;")

        email_lbl2 = QLabel("EMAIL")
        email_lbl2.setStyleSheet(lbl_style)
        self.email_input = QLineEdit(self.user.get("email") or "")
        self.email_input.setReadOnly(True)
        self.email_input.setFixedHeight(38)
        self.email_input.setStyleSheet("color: #505080; background: #0d0d14; border: 1px solid #1e1e30; border-radius: 8px; padding: 0 12px;")

        grid.addWidget(name_lbl2, 0, 0)
        grid.addWidget(self.name_input, 1, 0)
        grid.addWidget(user_lbl, 0, 1)
        grid.addWidget(self.user_input, 1, 1)
        grid.addWidget(email_lbl2, 2, 0)
        grid.addWidget(self.email_input, 3, 0, 1, 2)
        form_l.addLayout(grid)

        save_row = QHBoxLayout()
        save_btn = QPushButton("Сохранить изменения")
        save_btn.setObjectName("primary")
        save_btn.setFixedHeight(40)
        save_btn.setFixedWidth(200)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save_profile)
        self.save_msg = QLabel("")
        self.save_msg.setStyleSheet("color: #1dd8a0; font-size: 12px; background: transparent;")
        save_row.addWidget(save_btn)
        save_row.addWidget(self.save_msg)
        save_row.addStretch()
        form_l.addLayout(save_row)
        layout.addWidget(form_card)

        # Password card
        pass_card = QWidget()
        pass_card.setObjectName("card")
        pass_card.setStyleSheet("#card { background: #111119; border: 1px solid #1e1e30; border-radius: 14px; }")
        pass_l = QVBoxLayout(pass_card)
        pass_l.setContentsMargins(24, 20, 24, 20)
        pass_l.setSpacing(12)

        pass_title = QLabel("Безопасность")
        pass_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #c0c0e0; background: transparent; padding-bottom: 12px; border-bottom: 1px solid #1e1e30;")
        pass_l.addWidget(pass_title)

        pass_grid = QGridLayout()
        pass_grid.setSpacing(10)
        pass_grid.setHorizontalSpacing(14)

        new_lbl = QLabel("НОВЫЙ ПАРОЛЬ")
        new_lbl.setStyleSheet(lbl_style)
        self.new_pass = QLineEdit()
        self.new_pass.setPlaceholderText("Минимум 6 символов")
        self.new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass.setFixedHeight(38)

        conf_lbl = QLabel("ПОДТВЕРДИТЬ")
        conf_lbl.setStyleSheet(lbl_style)
        self.conf_pass = QLineEdit()
        self.conf_pass.setPlaceholderText("Повторите пароль")
        self.conf_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.conf_pass.setFixedHeight(38)
        self.conf_pass.returnPressed.connect(self.change_password)

        pass_grid.addWidget(new_lbl, 0, 0)
        pass_grid.addWidget(self.new_pass, 1, 0)
        pass_grid.addWidget(conf_lbl, 0, 1)
        pass_grid.addWidget(self.conf_pass, 1, 1)
        pass_l.addLayout(pass_grid)

        pass_row = QHBoxLayout()
        pass_btn = QPushButton("Изменить пароль")
        pass_btn.setObjectName("secondary")
        pass_btn.setFixedHeight(40)
        pass_btn.setFixedWidth(180)
        pass_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pass_btn.clicked.connect(self.change_password)
        self.pass_msg = QLabel("")
        self.pass_msg.setStyleSheet("font-size: 12px; background: transparent;")
        pass_row.addWidget(pass_btn)
        pass_row.addWidget(self.pass_msg)
        pass_row.addStretch()
        pass_l.addLayout(pass_row)
        layout.addWidget(pass_card)
        layout.addStretch()

        scroll.setWidget(container)
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.addWidget(scroll)

    def save_profile(self):
        name = self.name_input.text().strip()
        w = ApiWorker("PUT", "/profile/me", self.token, {"full_name": name})
        w.success.connect(lambda _: self.show_msg(self.save_msg, "Сохранено! ✓", ok=True))
        w.failure.connect(lambda e: self.show_msg(self.save_msg, e, ok=False))
        self._workers.append(w)
        w.start()

    def change_password(self):
        np = self.new_pass.text()
        cp = self.conf_pass.text()
        if np != cp:
            self.show_msg(self.pass_msg, "Пароли не совпадают", ok=False)
            return
        if len(np) < 6:
            self.show_msg(self.pass_msg, "Минимум 6 символов", ok=False)
            return
        w = ApiWorker("PUT", "/profile/password", self.token, {"password": np})
        w.success.connect(lambda _: self.show_msg(self.pass_msg, "Пароль изменён! ✓", ok=True))
        w.failure.connect(lambda e: self.show_msg(self.pass_msg, e, ok=False))
        self._workers.append(w)
        w.start()

    def show_msg(self, lbl, text, ok=True):
        lbl.setText(text)
        lbl.setStyleSheet(f"color: {'#1dd8a0' if ok else '#ff5566'}; font-size: 12px; background: transparent;")
        QTimer.singleShot(3000, lambda: lbl.setText(""))
