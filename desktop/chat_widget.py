# SmartTutor Desktop — Виджет чата
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from api import ApiWorker


# ── Кастомный элемент списка чатов с кнопкой удаления при наведении ──────────
class ChatItem(QWidget):
    clicked      = pyqtSignal()
    delete_requested = pyqtSignal()

    def __init__(self, title, is_active=False, parent=None):
        super().__init__(parent)
        self.is_active = is_active
        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 4, 0)
        lay.setSpacing(0)

        self.main_btn = QPushButton(f"💬  {title}")
        self.main_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.main_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.main_btn.clicked.connect(self.clicked)

        self.del_btn = QPushButton("🗑")
        self.del_btn.setFixedSize(26, 26)
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.setVisible(False)
        self.del_btn.clicked.connect(self.delete_requested)

        lay.addWidget(self.main_btn)
        lay.addWidget(self.del_btn)

        self._apply_style(False)

    # ── стиль ──────────────────────────────────────────────────────────
    def _apply_style(self, hovered: bool):
        if self.is_active:
            bg, color = "#1e1e2e", "#e0e0f0"
        elif hovered:
            bg, color = "#1a1a28", "#c0c0e8"
        else:
            bg, color = "transparent", "#6060a0"

        self.main_btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                border: none;
                color: {color};
                text-align: left;
                padding: 0 8px 0 12px;
                border-radius: 8px;
                font-size: 12px;
            }}
        """)
        self.del_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #ff5566;
                font-size: 13px;
                border-radius: 5px;
                padding: 0;
            }
            QPushButton:hover { background: rgba(255,85,102,0.18); }
        """)

    # ── hover ───────────────────────────────────────────────────────────
    def enterEvent(self, e):
        self.del_btn.setVisible(True)
        self._apply_style(True)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.del_btn.setVisible(False)
        self._apply_style(False)
        super().leaveEvent(e)

BUBBLE_USER_STYLE = """
    QFrame {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 #6d5fff, stop:1 #9d7fff);
        border-radius: 18px;
        border-bottom-right-radius: 4px;
        border: none;
    }
    QLabel {
        background: transparent;
        border: none;
        color: #ffffff;
        font-size: 13px;
    }
"""

BUBBLE_AI_STYLE = """
    QFrame {
        background: #1c1c2e;
        border: 1px solid #2a2a50;
        border-radius: 18px;
        border-bottom-left-radius: 4px;
    }
    QLabel {
        background: transparent;
        border: none;
        color: #e8e8f8;
        font-size: 13px;
    }
"""


class MessageBubble(QWidget):
    def __init__(self, text, is_user=False, is_typing=False):
        super().__init__()
        # Maximum вертикально — пузырь не растягивается выше своего контента
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 4, 16, 4)
        outer.setSpacing(10)

        if is_typing:
            lbl = QLabel("⏳  SmartTutor печатает...")
            lbl.setObjectName("typing_label")
            outer.addWidget(lbl)
            outer.addStretch()
            return

        # Форматируем текст заранее, чтобы измерить ширину
        formatted = self.format_text(text)

        # Вычисляем точную ширину пузыря через QTextDocument
        # Это решает проблему "узкого столбика" — QLabel узнаёт ширину ДО рендера
        MAX_CONTENT = 520   # максимальная ширина содержимого
        PAD_H = 28          # горизонтальные отступы frame (14px * 2)
        PAD_V = 20          # вертикальные отступы frame (10px * 2)
        doc = QTextDocument()
        doc.setDefaultFont(QFont("Segoe UI", 10))
        doc.setHtml(formatted)
        doc.setTextWidth(MAX_CONTENT)
        # idealWidth — ширина, при которой текст идёт горизонтально (1 строка)
        ideal_content = min(MAX_CONTENT, max(40, int(doc.idealWidth())))
        bubble_w = ideal_content + PAD_H
        # Считаем высоту: text height + padding
        doc.setTextWidth(ideal_content)
        bubble_h = int(doc.size().height()) + PAD_V

        # QFrame — только он рисует border-radius + фон правильно
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.NoFrame)
        frame.setFixedWidth(bubble_w)    # точная ширина
        frame.setFixedHeight(bubble_h)   # точная высота — не растягивается
        frame.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        frame.setStyleSheet(BUBBLE_USER_STYLE if is_user else BUBBLE_AI_STYLE)

        frame_l = QVBoxLayout(frame)
        frame_l.setContentsMargins(14, 10, 14, 10)
        frame_l.setSpacing(0)

        label = QLabel()
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setText(formatted)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        frame_l.addWidget(label)

        if is_user:
            outer.addStretch()
            outer.addWidget(frame)
        else:
            av = QLabel("AI")
            av.setFixedSize(32, 32)
            av.setAlignment(Qt.AlignmentFlag.AlignCenter)
            av.setStyleSheet("""
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #6d5fff,stop:1 #1dd8a0);
                border-radius: 11px; color:white;
                font-size:10px; font-weight:700; border:none;
            """)
            outer.addWidget(av)
            outer.addWidget(frame)
            outer.addStretch()

    def format_text(self, text):
        import re
        t = text
        # Блоки кода
        t = re.sub(
            r'```(\w*)\n?([\s\S]*?)```',
            r'<pre style="background:#0a0a18;border:1px solid #2a2a45;border-radius:6px;'
            r'padding:10px;margin:6px 0;font-family:Consolas,monospace;font-size:12px;'
            r'white-space:pre-wrap;color:#c0e0ff">\2</pre>', t)
        # Инлайн-код
        t = re.sub(
            r'`([^`\n]+)`',
            r'<code style="background:rgba(109,95,255,0.2);padding:1px 5px;border-radius:4px;'
            r'font-family:Consolas,monospace;font-size:12px;color:#c0d0ff">\1</code>', t)
        # Заголовки
        t = re.sub(r'^## (.+)$',
            r'<div style="font-size:15px;font-weight:700;margin:10px 0 5px;color:#ffffff">\1</div>',
            t, flags=re.MULTILINE)
        t = re.sub(r'^### (.+)$',
            r'<div style="font-size:13px;font-weight:600;margin:8px 0 4px;color:#a0a0e0">\1</div>',
            t, flags=re.MULTILINE)
        # Жирный
        t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
        # Маркеры прогресса
        t = t.replace('✅ ШАГ ЗАСЧИТАН',
            '<span style="color:#1dd8a0;font-weight:bold">✅ Шаг засчитан!</span>')
        t = t.replace('🎉 ТЕМА ЗАВЕРШЕНА',
            '<div style="color:#1dd8a0;font-weight:bold;font-size:14px">🎉 Тема завершена!</div>')
        # Списки
        t = re.sub(r'^[-•]\s+(.+)$',
            r'<div style="padding:2px 0 2px 12px">• \1</div>', t, flags=re.MULTILINE)
        # Переносы строк
        t = t.replace('\n', '<br>')
        return t


class ChatWidget(QWidget):
    def __init__(self, token, user):
        super().__init__()
        self.token = token
        self.user = user
        self.sessions = []
        self.cur_sid = None
        self._workers = []
        self._pending_text = None
        self._sidebar_visible = True
        self._sidebar_anim = None        # держим ссылку чтобы не умерла
        self.setup_ui()
        self.load_sessions()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── ЛЕВАЯ ПАНЕЛЬ ──
        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(220)
        self.left_panel.setObjectName("sidebar")
        left_l = QVBoxLayout(self.left_panel)
        left_l.setContentsMargins(0, 12, 0, 12)
        left_l.setSpacing(4)

        chats_lbl = QLabel("ЧАТЫ")
        chats_lbl.setStyleSheet(
            "font-size:10px;color:#404060;font-weight:bold;"
            "letter-spacing:1px;padding:0 16px 4px;")
        left_l.addWidget(chats_lbl)

        self.search = QLineEdit()
        self.search.setObjectName("search_input")
        self.search.setPlaceholderText("🔍  Поиск чатов...")
        self.search.setFixedHeight(32)
        self.search.setStyleSheet("margin:0 8px;border-radius:8px;")
        self.search.textChanged.connect(self.filter_chats)
        left_l.addWidget(self.search)
        left_l.addSpacing(4)

        self.new_btn = QPushButton("＋  Новый чат")
        self.new_btn.setObjectName("new_chat_btn")
        self.new_btn.setFixedHeight(34)
        self.new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_btn.clicked.connect(self.new_chat)
        left_l.addWidget(self.new_btn)

        chat_scroll = QScrollArea()
        chat_scroll.setWidgetResizable(True)
        chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        chat_scroll.setStyleSheet("background:transparent;border:none;")
        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background:transparent;")
        self.chat_list_layout = QVBoxLayout(self.chat_container)
        self.chat_list_layout.setContentsMargins(8, 4, 8, 4)
        self.chat_list_layout.setSpacing(2)
        self.chat_list_layout.addStretch()
        chat_scroll.setWidget(self.chat_container)
        left_l.addWidget(chat_scroll)
        layout.addWidget(self.left_panel)

        self.sidebar_div = QFrame()
        self.sidebar_div.setFrameShape(QFrame.Shape.VLine)
        self.sidebar_div.setStyleSheet("color:#1e1e30;")
        layout.addWidget(self.sidebar_div)

        # ── ПРАВАЯ ЧАСТЬ ──
        right = QWidget()
        right_l = QVBoxLayout(right)
        right_l.setContentsMargins(0, 0, 0, 0)
        right_l.setSpacing(0)

        self.topbar = QWidget()
        self.topbar.setStyleSheet("background:#0d0d18;border-bottom:1.5px solid #1e1e3a;")
        self.topbar.setFixedHeight(54)
        tb_l = QHBoxLayout(self.topbar)
        tb_l.setContentsMargins(12, 0, 20, 0)
        tb_l.setSpacing(10)

        # Кнопка скрыть/раскрыть боковую панель
        self.toggle_btn = QPushButton("‹")
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setToolTip("Скрыть список чатов")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: #1a1a30;
                border: 1px solid #2a2a50;
                color: #6060a0;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(109,95,255,0.15);
                color: #a090ff;
                border-color: #6d5fff;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        tb_l.addWidget(self.toggle_btn)

        self.chat_title = QLabel("Выбери чат или создай новый")
        self.chat_title.setObjectName("chat_title_label")
        tb_l.addWidget(self.chat_title)
        tb_l.addStretch()
        right_l.addWidget(self.topbar)

        # Область сообщений — БЕЗ addStretch()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background:#0a0a12;border:none;")
        self.msg_container = QWidget()
        self.msg_container.setStyleSheet("background:#0a0a12;")
        self.msg_layout = QVBoxLayout(self.msg_container)
        self.msg_layout.setContentsMargins(0, 16, 0, 16)
        self.msg_layout.setSpacing(6)

        self.empty_label = QLabel("✨  Чем могу помочь?\n\nНапиши тему которую хочешь изучить")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.empty_label.setStyleSheet(
            "font-size:16px;color:#303050;padding:40px;background:transparent;")
        self.msg_layout.addWidget(self.empty_label)

        self.scroll.setWidget(self.msg_container)
        right_l.addWidget(self.scroll)

        input_wrap = QWidget()
        input_wrap.setStyleSheet("background:#0d0d18;border-top:1.5px solid #1e1e3a;")
        input_wrap.setFixedHeight(76)
        input_l = QHBoxLayout(input_wrap)
        input_l.setContentsMargins(16, 14, 16, 14)
        input_l.setSpacing(10)

        self.input = QTextEdit()
        self.input.setPlaceholderText("Задай вопрос или напиши тему для изучения...")
        self.input.setFixedHeight(48)
        self.input.installEventFilter(self)
        self.input.setStyleSheet("""
            QTextEdit {
                background:#13132a;border:1px solid #252545;
                border-radius:12px;padding:10px 14px;
                color:#e8e8f8;font-size:13px;
            }
            QTextEdit:focus { border:1.5px solid #6d5fff;background:#181830; }
        """)

        send = QPushButton("➤")
        send.setObjectName("send_btn")
        send.setFixedSize(62, 48)
        send.setCursor(Qt.CursorShape.PointingHandCursor)
        send.clicked.connect(self.send_message)
        input_l.addWidget(self.input)
        input_l.addWidget(send)
        right_l.addWidget(input_wrap)
        layout.addWidget(right)

    def eventFilter(self, obj, event):
        if obj == self.input and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not (
                    event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    # ── СПИСОК ЧАТОВ ──────────────────────────────────────────
    def load_sessions(self):
        w = ApiWorker("GET", "/chat/sessions", self.token)
        w.success.connect(self.on_sessions)
        self._workers.append(w)
        w.start()

    def on_sessions(self, data):
        self.sessions = [s for s in data if not s.get("is_deleted")]
        self.render_chat_list()

    def render_chat_list(self, filter_text=""):
        while self.chat_list_layout.count() > 1:
            item = self.chat_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for s in self.sessions:
            title = s.get("title") or "Новый чат"
            if filter_text and filter_text.lower() not in title.lower():
                continue

            is_active = s["id"] == self.cur_sid
            sid = s["id"]

            item = ChatItem(title, is_active=is_active)
            item.clicked.connect(
                lambda s_id=sid, s_title=title: self.open_chat(s_id, s_title))
            item.delete_requested.connect(
                lambda s_id=sid: self.delete_chat(s_id))
            # Правый клик — переименовать
            item.main_btn.setContextMenuPolicy(
                Qt.ContextMenuPolicy.CustomContextMenu)
            item.main_btn.customContextMenuRequested.connect(
                lambda pos, s_id=sid, s_title=title, b=item.main_btn:
                    self.chat_context_menu(pos, s_id, s_title, b))

            self.chat_list_layout.insertWidget(
                self.chat_list_layout.count() - 1, item)

    def filter_chats(self, text):
        self.render_chat_list(text)

    # ── СКРЫТЬ / РАСКРЫТЬ БОКОВУЮ ПАНЕЛЬ ─────────────────────
    def toggle_sidebar(self):
        if self._sidebar_visible:
            # Скрываем: анимируем ширину от 220 → 0
            self._sidebar_anim = QPropertyAnimation(self.left_panel, b"maximumWidth")
            self._sidebar_anim.setDuration(220)
            self._sidebar_anim.setStartValue(220)
            self._sidebar_anim.setEndValue(0)
            self._sidebar_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self._sidebar_anim.finished.connect(self._on_sidebar_hidden)
            self._sidebar_anim.start(QAbstractAnimation.DeletionPolicy.KeepWhenStopped)
            self._sidebar_visible = False
            self.toggle_btn.setText("›")
            self.toggle_btn.setToolTip("Раскрыть список чатов")
        else:
            # Раскрываем: показываем и анимируем от 0 → 220
            self.left_panel.setVisible(True)
            self.sidebar_div.setVisible(True)
            self.left_panel.setMaximumWidth(0)
            self._sidebar_anim = QPropertyAnimation(self.left_panel, b"maximumWidth")
            self._sidebar_anim.setDuration(220)
            self._sidebar_anim.setStartValue(0)
            self._sidebar_anim.setEndValue(220)
            self._sidebar_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self._sidebar_anim.finished.connect(self._on_sidebar_shown)
            self._sidebar_anim.start(QAbstractAnimation.DeletionPolicy.KeepWhenStopped)
            self._sidebar_visible = True
            self.toggle_btn.setText("‹")
            self.toggle_btn.setToolTip("Скрыть список чатов")

    def _on_sidebar_hidden(self):
        self.left_panel.setVisible(False)
        self.sidebar_div.setVisible(False)

    def _on_sidebar_shown(self):
        # Снимаем ограничение максимальной ширины после анимации
        self.left_panel.setMaximumWidth(220)
        self.left_panel.setFixedWidth(220)

    # ── КОНТЕКСТНОЕ МЕНЮ ──────────────────────────────────────
    def chat_context_menu(self, pos, sid, title, btn):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background:#1a1a2e;border:1px solid #2a2a50;
                border-radius:8px;padding:4px;
                color:#e8e8f8;font-size:12px;
            }
            QMenu::item { padding:8px 18px;border-radius:6px; }
            QMenu::item:selected { background:#2a2a45; }
        """)
        rename_act = menu.addAction("✏️  Переименовать")
        delete_act = menu.addAction("🗑️  Удалить")
        action = menu.exec(btn.mapToGlobal(pos))
        if action == rename_act:
            self.rename_chat(sid, title)
        elif action == delete_act:
            self.delete_chat(sid)

    def rename_chat(self, sid, current_title):
        text, ok = QInputDialog.getText(
            self, "Переименовать чат", "Новое название:",
            QLineEdit.EchoMode.Normal, current_title)
        if ok and text.strip():
            w = ApiWorker("PATCH", f"/chat/sessions/{sid}",
                          self.token, {"title": text.strip()})
            w.success.connect(lambda _: self.load_sessions())
            self._workers.append(w)
            w.start()
            if sid == self.cur_sid:
                self.chat_title.setText(text.strip())

    def delete_chat(self, sid):
        reply = QMessageBox.question(
            self, "Удалить чат", "Удалить этот чат? Действие необратимо.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            w = ApiWorker("PATCH", f"/chat/sessions/{sid}",
                          self.token, {"is_deleted": True})
            w.success.connect(lambda _: self.on_chat_deleted(sid))
            self._workers.append(w)
            w.start()

    def on_chat_deleted(self, sid):
        self.sessions = [s for s in self.sessions if s["id"] != sid]
        if self.cur_sid == sid:
            self.cur_sid = None
            self.chat_title.setText("Выбери чат или создай новый")
            self.clear_messages()
        self.render_chat_list()

    # ── НОВЫЙ ЧАТ ─────────────────────────────────────────────
    def new_chat(self):
        w = ApiWorker("POST", "/chat/sessions", self.token)
        w.success.connect(self.on_new_chat)
        self._workers.append(w)
        w.start()

    def on_new_chat(self, data):
        self.sessions.insert(0, data)
        self.open_chat(data["id"], "Новый чат")
        if self._pending_text:
            text = self._pending_text
            self._pending_text = None
            QTimer.singleShot(100, lambda: self._send(text))

    # ── ОТКРЫТИЕ ЧАТА ─────────────────────────────────────────
    def open_chat(self, sid, title):
        self.cur_sid = sid
        self.chat_title.setText(title)
        self.clear_messages()
        self.render_chat_list()
        w = ApiWorker("GET", f"/chat/sessions/{sid}/messages", self.token)
        w.success.connect(self.on_messages)
        self._workers.append(w)
        w.start()

    def on_messages(self, data):
        # Убираем empty_label из layout
        idx = self.msg_layout.indexOf(self.empty_label)
        if idx >= 0:
            self.msg_layout.takeAt(idx)
        self.empty_label.hide()

        if not data:
            # Показываем заглушку ТОЛЬКО если нет уже добавленных пузырей
            # (защита от гонки: _send уже добавил пузырь до on_messages)
            if self.msg_layout.count() == 0:
                self.msg_layout.addWidget(self.empty_label)
                self.empty_label.show()
            return

        for msg in data:
            self.add_bubble(msg["content"], msg["role"] == "user")
        self.scroll_bottom()

    # ── ОТПРАВКА ──────────────────────────────────────────────
    def send_message(self):
        text = self.input.toPlainText().strip()
        if not text:
            return
        if not self.cur_sid:
            self._pending_text = text
            self.input.clear()
            self.new_chat()
            return
        self._send(text)

    def _send(self, text):
        if not self.cur_sid:
            return
        self.input.clear()

        # Скрыть заглушку и убрать из layout
        idx = self.msg_layout.indexOf(self.empty_label)
        if idx >= 0:
            self.msg_layout.takeAt(idx)
        self.empty_label.hide()

        self.add_bubble(text, True)

        typing = MessageBubble("", is_typing=True)
        self.msg_layout.addWidget(typing)
        self.scroll_bottom()

        w = ApiWorker("POST", "/chat/send", self.token,
                      {"content": text, "session_id": self.cur_sid})
        w.success.connect(lambda d: self.on_response(d, typing))
        w.failure.connect(lambda e: self.on_error(e, typing))
        self._workers.append(w)
        w.start()

    def on_response(self, data, typing):
        try:
            typing.deleteLater()
        except RuntimeError:
            pass
        self.add_bubble(data.get("answer", ""), False)
        self.scroll_bottom()
        self.load_sessions()

    def on_error(self, err, typing):
        try:
            typing.deleteLater()
        except RuntimeError:
            pass
        self.add_bubble(f"Ошибка: {err}", False)

    # ── ВСПОМОГАТЕЛЬНЫЕ ───────────────────────────────────────
    def add_bubble(self, text, is_user):
        bubble = MessageBubble(text, is_user)
        self.msg_layout.addWidget(bubble)

    def clear_messages(self):
        while self.msg_layout.count() > 0:
            item = self.msg_layout.takeAt(0)
            w = item.widget()
            if w and w is not self.empty_label:
                w.deleteLater()
        self.msg_layout.addWidget(self.empty_label)
        self.empty_label.show()

    def scroll_bottom(self):
        def _do():
            self.scroll.verticalScrollBar().setValue(
                self.scroll.verticalScrollBar().maximum())
        QTimer.singleShot(60, _do)
        QTimer.singleShot(280, _do)
