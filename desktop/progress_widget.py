# SmartTutor Desktop — Виджет прогресса
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from api import ApiWorker


# ── Карточка статистики ───────────────────────────────────────
class StatCard(QWidget):
    def __init__(self, value, label, color):
        super().__init__()
        self.setMinimumHeight(100)
        self.setMinimumWidth(140)
        self.setStyleSheet(f"""
            QWidget {{
                background: #16162a;
                border: 1px solid #2a2a50;
                border-radius: 14px;
                border-top: 3px solid {color};
            }}
            QLabel {{ background: transparent; border: none; }}
        """)
        l = QVBoxLayout(self)
        l.setContentsMargins(20, 18, 20, 18)
        l.setSpacing(6)

        self.val = QLabel(str(value))
        self.val.setStyleSheet(
            f"font-size:30px;font-weight:800;color:{color};letter-spacing:-1px;")

        self.lbl = QLabel(label)
        self.lbl.setStyleSheet("font-size:12px;color:#6060a0;font-weight:500;")

        l.addWidget(self.val)
        l.addWidget(self.lbl)

    def set_value(self, v):
        self.val.setText(str(v))


# ── Строка темы с hover через enterEvent/leaveEvent ───────────
class TopicRow(QWidget):
    clicked = pyqtSignal(dict)   # передаём данные темы при клике

    def __init__(self, topic: dict, is_last: bool):
        super().__init__()
        self.topic = topic
        self.is_last = is_last
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hovered = False
        self._build()
        self._apply_style(False)

    def _build(self):
        row_l = QHBoxLayout(self)
        row_l.setContentsMargins(18, 14, 14, 14)
        row_l.setSpacing(14)

        status = self.topic.get("status", "active")
        icon = "✅" if status == "completed" else "🔄"

        # Название темы — жирный, красивый шрифт
        name = QLabel(f"{icon}  {self.topic.get('title', '—')}")
        name.setStyleSheet(
            "font-size:14px;font-weight:700;color:#d0d0f0;"
            "letter-spacing:0.2px;background:transparent;border:none;")

        total_steps = self.topic.get("total_steps") or 5
        current_step = self.topic.get("current_step") or 1
        steps_list = self.topic.get("steps", [])
        actual = len(steps_list) if steps_list else total_steps

        step_lbl = QLabel(f"Шаг {current_step} / {actual}")
        step_lbl.setStyleSheet(
            "font-size:12px;font-weight:600;color:#5050a0;"
            "background:transparent;border:none;min-width:70px;")

        progress = int(self.topic.get("progress", 0))
        prog_bar = QProgressBar()
        prog_bar.setValue(progress)
        prog_bar.setFixedWidth(100)
        prog_bar.setFixedHeight(6)
        prog_bar.setTextVisible(False)
        prog_bar.setStyleSheet("""
            QProgressBar { background:#1a1a38;border-radius:3px;border:none; }
            QProgressBar::chunk {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #6d5fff,stop:1 #1dd8a0);
                border-radius:3px;
            }
        """)

        prog_lbl = QLabel(f"{progress}%")
        prog_lbl.setStyleSheet(
            "font-size:12px;font-weight:600;color:#5050a0;"
            "background:transparent;border:none;min-width:36px;")

        # Иконка «открыть»
        arrow = QLabel("›")
        arrow.setStyleSheet(
            "font-size:20px;color:#404070;background:transparent;border:none;")

        row_l.addWidget(name, stretch=1)
        row_l.addWidget(step_lbl)
        row_l.addWidget(prog_bar)
        row_l.addWidget(prog_lbl)
        row_l.addWidget(arrow)

    def _apply_style(self, hovered: bool):
        sep = "none" if self.is_last else "1px solid #1e1e3a"
        bg = "rgba(109,95,255,0.09)" if hovered else "transparent"
        # Стиль только для самого виджета через objectName
        self.setObjectName("topic_row_hov" if hovered else "topic_row")
        self.setStyleSheet(f"""
            #topic_row, #topic_row_hov {{
                background: {bg};
                border-bottom: {sep};
            }}
        """)

    def enterEvent(self, e):
        self._apply_style(True)

    def leaveEvent(self, e):
        self._apply_style(False)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.topic)


# ── Диалог деталей темы (шаги + удалить/переименовать) ────────
class TopicDetailDialog(QDialog):
    topic_deleted = pyqtSignal(int)
    topic_renamed = pyqtSignal(int, str)

    def __init__(self, topic: dict, token: str, parent=None):
        super().__init__(parent)
        self.topic = topic
        self.token = token
        self._workers = []
        self._drag_pos = None
        self.setWindowTitle("Детали темы")
        self.setFixedWidth(500)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setFrameShape(QFrame.Shape.NoFrame)
        card.setStyleSheet("""
            QFrame {
                background: #12121f;
                border-radius: 20px;
                border: 1px solid #2a2a50;
            }
            QLabel { background: transparent; border: none; }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 18, 28, 24)
        layout.setSpacing(0)

        # Закрыть
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(26, 26)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton { background:#1e1e38;border:none;border-radius:8px;
                color:#505080;font-size:11px; }
            QPushButton:hover { background:#2a2a50;color:#e0e0ff; }
        """)
        close_btn.clicked.connect(self.reject)
        close_row.addWidget(close_btn)
        layout.addLayout(close_row)
        layout.addSpacing(6)

        # Заголовок + карандаш
        title_row = QHBoxLayout()
        self.title_lbl = QLabel(self.topic.get("title", "—"))
        self.title_lbl.setWordWrap(True)
        self.title_lbl.setStyleSheet(
            "font-size:18px;font-weight:800;color:#e8e8f8;letter-spacing:-0.3px;")
        title_row.addWidget(self.title_lbl, stretch=1)

        rename_btn = QPushButton("✏️")
        rename_btn.setFixedSize(32, 32)
        rename_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rename_btn.setToolTip("Переименовать тему")
        rename_btn.setStyleSheet("""
            QPushButton { background:#1e1e38;border:none;border-radius:9px;font-size:14px; }
            QPushButton:hover { background:#2a2a50; }
        """)
        rename_btn.clicked.connect(self.rename_topic)
        title_row.addWidget(rename_btn)
        layout.addLayout(title_row)
        layout.addSpacing(6)

        # Подпись — статус и прогресс
        status = self.topic.get("status", "active")
        progress = self.topic.get("progress", 0)
        sub = QLabel(
            f"{'✅ Завершено' if status=='completed' else '🔄 В процессе'}"
            f"  ·  {progress}% выполнено")
        sub.setStyleSheet("font-size:12px;color:#50508a;")
        layout.addWidget(sub)
        layout.addSpacing(22)

        # Заголовок шагов
        steps_hdr = QLabel("ШАГИ ОБУЧЕНИЯ")
        steps_hdr.setStyleSheet(
            "font-size:10px;font-weight:700;color:#404070;"
            "letter-spacing:1.5px;")
        layout.addWidget(steps_hdr)
        layout.addSpacing(10)

        # Область шагов
        steps_frame = QFrame()
        steps_frame.setFrameShape(QFrame.Shape.NoFrame)
        steps_frame.setStyleSheet("""
            QFrame { background:#0e0e1e;border:1px solid #1e1e38;border-radius:14px; }
            QLabel { background:transparent;border:none; }
        """)
        steps_vl = QVBoxLayout(steps_frame)
        steps_vl.setContentsMargins(0, 6, 0, 6)
        steps_vl.setSpacing(0)

        steps = self.topic.get("steps", [])
        if not steps:
            # Нет данных — показываем 5 пустых
            for i in range(1, 6):
                self._add_step(steps_vl, i, f"Шаг {i}", "pending", i < 5)
        else:
            for i, s in enumerate(steps):
                self._add_step(
                    steps_vl,
                    s.get("step_number", i + 1),
                    s.get("title", f"Шаг {i+1}"),
                    s.get("status", "pending"),
                    i < len(steps) - 1)

        layout.addWidget(steps_frame)
        layout.addSpacing(22)

        # Кнопка Удалить
        del_btn = QPushButton("🗑️  Удалить тему")
        del_btn.setFixedHeight(42)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet("""
            QPushButton {
                background:rgba(255,85,102,0.1);
                color:#ff5566;
                border:1.5px solid rgba(255,85,102,0.3);
                border-radius:11px;
                font-size:13px;font-weight:600;
            }
            QPushButton:hover { background:rgba(255,85,102,0.2); }
        """)
        del_btn.clicked.connect(self.delete_topic)
        layout.addWidget(del_btn)

        root.addWidget(card)

    def _add_step(self, layout, num, title, status, add_sep):
        row = QWidget()
        row.setStyleSheet(
            "QWidget{background:transparent;} QLabel{background:transparent;border:none;}")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(18, 12, 18, 12)
        rl.setSpacing(14)

        badge = QLabel(str(num))
        badge.setFixedSize(30, 30)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if status == "completed":
            badge.setText("✓")
            badge.setStyleSheet(
                "background:#1dd8a0;border-radius:15px;"
                "color:white;font-weight:800;font-size:14px;")
        elif status == "active":
            badge.setStyleSheet(
                "background:#6d5fff;border-radius:15px;"
                "color:white;font-weight:800;font-size:13px;")
        else:
            badge.setStyleSheet(
                "background:#1a1a30;border-radius:15px;"
                "color:#404060;font-weight:700;font-size:13px;")

        lbl = QLabel(title)
        if status == "completed":
            lbl.setStyleSheet(
                "font-size:13px;color:#505080;")
        elif status == "active":
            lbl.setStyleSheet(
                "font-size:13px;font-weight:700;color:#c0c0f0;")
        else:
            lbl.setStyleSheet(
                "font-size:13px;color:#404060;")

        rl.addWidget(badge)
        rl.addWidget(lbl, stretch=1)
        layout.addWidget(row)

        if add_sep:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("background:#1a1a30;max-height:1px;border:none;")
            layout.addWidget(sep)

    # ── Действия ─────────────────────────────────────────────
    def rename_topic(self):
        text, ok = QInputDialog.getText(
            self, "Переименовать", "Новое название:",
            QLineEdit.EchoMode.Normal, self.topic.get("title", ""))
        if ok and text.strip():
            w = ApiWorker("PATCH", f"/topics/{self.topic['id']}",
                          self.token, {"title": text.strip()})
            w.success.connect(lambda _: self._on_renamed(text.strip()))
            self._workers.append(w)
            w.start()

    def _on_renamed(self, new_title):
        self.topic["title"] = new_title
        self.title_lbl.setText(new_title)
        self.topic_renamed.emit(self.topic["id"], new_title)

    def delete_topic(self):
        reply = QMessageBox.question(
            self, "Удалить тему",
            "Удалить эту тему? Прогресс будет потерян.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            w = ApiWorker("DELETE", f"/topics/{self.topic['id']}", self.token)
            w.success.connect(lambda _: self._on_deleted())
            self._workers.append(w)
            w.start()

    def _on_deleted(self):
        self.topic_deleted.emit(self.topic["id"])
        self.accept()

    # Drag window
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None


# ── Главный виджет прогресса ──────────────────────────────────
class ProgressWidget(QWidget):
    def __init__(self, token, user):
        super().__init__()
        self.token = token
        self.user = user
        self._workers = []
        self._topic_data = []
        self.setup_ui()

    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        title = QLabel("Прогресс")
        title.setObjectName("section_title")
        sub = QLabel("Твоя учебная активность и изученные темы")
        sub.setObjectName("section_sub")
        layout.addWidget(title)
        layout.addWidget(sub)

        # Карточки
        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        self.card_q = StatCard("—", "Вопросов задано", "#7c6eff")
        self.card_t = StatCard("—", "Тем изучается",   "#1dd8a0")
        self.card_d = StatCard("—", "Дней активно",    "#ffaa44")
        for c in [self.card_q, self.card_t, self.card_d]:
            stats_row.addWidget(c)
        layout.addLayout(stats_row)

        # Заголовок + кнопка обновить
        hdr = QHBoxLayout()
        topics_lbl = QLabel("Учебные темы")
        topics_lbl.setStyleSheet(
            "font-size:15px;font-weight:700;color:#c0c0e0;background:transparent;")
        hdr.addWidget(topics_lbl)
        hdr.addStretch()

        refresh = QPushButton("🔄  Обновить")
        refresh.setFixedHeight(36)
        refresh.setFixedWidth(130)
        refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh.setStyleSheet("""
            QPushButton {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #6d5fff,stop:1 #9d7fff);
                color:white;border:none;border-radius:10px;
                font-size:12px;font-weight:600;
            }
            QPushButton:hover {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #7d6fff,stop:1 #ad8fff);
            }
            QPushButton:pressed { background:#5545ef; }
        """)
        refresh.clicked.connect(self.load_data)
        hdr.addWidget(refresh)
        layout.addLayout(hdr)

        # Область тем с рамкой
        self.topics_frame = QFrame()
        self.topics_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.topics_frame.setStyleSheet("""
            QFrame {
                background:#13132a;
                border:1px solid #2a2a55;
                border-radius:14px;
            }
        """)
        self.topics_layout = QVBoxLayout(self.topics_frame)
        self.topics_layout.setContentsMargins(0, 4, 0, 4)
        self.topics_layout.setSpacing(0)

        self.empty_topics = QLabel("Начни общаться с ИИ — темы появятся здесь")
        self.empty_topics.setStyleSheet(
            "color:#404060;font-size:13px;padding:32px;"
            "background:transparent;border:none;")
        self.empty_topics.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.topics_layout.addWidget(self.empty_topics)

        layout.addWidget(self.topics_frame)
        layout.addStretch()

        scroll.setWidget(container)
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.addWidget(scroll)

    # ── Загрузка данных ───────────────────────────────────────
    def load_data(self):
        w1 = ApiWorker("GET", "/profile/progress", self.token)
        w1.success.connect(self.on_progress)
        w1.failure.connect(lambda _: self.card_q.set_value("?"))
        self._workers.append(w1)
        w1.start()

        w2 = ApiWorker("GET", "/topics", self.token)
        w2.success.connect(self.on_topics)
        w2.failure.connect(lambda _: self.card_t.set_value("?"))
        self._workers.append(w2)
        w2.start()

        w3 = ApiWorker("GET", "/activity", self.token)
        w3.success.connect(self.on_activity)
        w3.failure.connect(lambda _: self.card_d.set_value("0"))
        self._workers.append(w3)
        w3.start()

    def on_progress(self, data):
        self.card_q.set_value(data.get("total_questions", 0))

    def on_activity(self, data):
        days = len(set(i.get("date", "") for i in data if i.get("date")))
        self.card_d.set_value(days)

    def on_topics(self, data):
        self._topic_data = data
        self.card_t.set_value(len(data))
        self._render_topics(data)

    def _render_topics(self, data):
        while self.topics_layout.count():
            item = self.topics_layout.takeAt(0)
            w = item.widget()
            if w and w is not self.empty_topics:
                w.deleteLater()

        if not data:
            self.topics_layout.addWidget(self.empty_topics)
            self.empty_topics.show()
            return

        self.empty_topics.hide()
        for i, t in enumerate(data):
            row = TopicRow(t, is_last=(i == len(data) - 1))
            row.clicked.connect(self.open_topic_detail)
            self.topics_layout.addWidget(row)

    def open_topic_detail(self, topic: dict):
        dlg = TopicDetailDialog(topic, self.token, self)
        dlg.topic_deleted.connect(self._on_topic_deleted)
        dlg.topic_renamed.connect(self._on_topic_renamed)
        dlg.exec()

    def _on_topic_deleted(self, topic_id: int):
        self._topic_data = [t for t in self._topic_data if t["id"] != topic_id]
        self.card_t.set_value(len(self._topic_data))
        self._render_topics(self._topic_data)

    def _on_topic_renamed(self, topic_id: int, new_title: str):
        for t in self._topic_data:
            if t["id"] == topic_id:
                t["title"] = new_title
        self._render_topics(self._topic_data)
