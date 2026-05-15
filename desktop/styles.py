APP_STYLE = """
* {
    font-family: 'Segoe UI', Arial, sans-serif;
    outline: none;
}
QMainWindow, QDialog {
    background: #0d0d16;
}
QWidget {
    background: #0d0d16;
    color: #e8e8f8;
}
QLabel {
    color: #e8e8f8;
    background: transparent;
    border: none;
}

/* ─── INPUTS ─── */
QLineEdit {
    background: #13132a;
    border: 1px solid #252545;
    border-radius: 10px;
    padding: 10px 14px;
    color: #e8e8f8;
    font-size: 13px;
    selection-background-color: #6d5fff;
    min-height: 22px;
}
QLineEdit:focus {
    border: 1.5px solid #6d5fff;
    background: #181830;
}
QLineEdit:disabled {
    color: #383858;
    background: #0f0f22;
    border-color: #1a1a38;
}

QTextEdit {
    background: #16162a;
    border: 1.5px solid #2a2a50;
    border-radius: 12px;
    padding: 10px 14px;
    color: #e8e8f8;
    font-size: 13px;
    selection-background-color: #6d5fff;
}
QTextEdit:focus {
    border-color: #6d5fff;
    background: #1a1a32;
}

/* ─── BUTTONS ─── */
QPushButton#primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #6d5fff, stop:1 #9d7fff);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-size: 13px;
    font-weight: 600;
    min-height: 20px;
}
QPushButton#primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #7d6fff, stop:1 #ad8fff);
}
QPushButton#primary:pressed {
    background: #5d4fdf;
}

QPushButton#secondary {
    background: #18182e;
    color: #9090c8;
    border: 1.5px solid #2a2a50;
    border-radius: 10px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton#secondary:hover {
    background: #20203a;
    color: #e8e8f8;
    border-color: #4040a0;
}

QPushButton#danger {
    background: transparent;
    color: #ff5566;
    border: 1.5px solid rgba(255, 85, 102, 0.35);
    border-radius: 10px;
    padding: 9px 20px;
    font-size: 12px;
}
QPushButton#danger:hover {
    background: rgba(255, 85, 102, 0.1);
}

QPushButton#send_btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6d5fff, stop:1 #9d7fff);
    color: white;
    border: none;
    border-radius: 14px;
    font-size: 22px;
    min-width: 62px;
    min-height: 48px;
    max-width: 62px;
    max-height: 48px;
    padding: 0;
    text-align: center;
}
QPushButton#send_btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7d6fff, stop:1 #ad8fff);
}
QPushButton#send_btn:pressed {
    background: #5545ef;
}

QPushButton#logout_btn {
    background: #1a1a2e;
    border: 1.5px solid #2a2a50;
    color: #6060a0;
    border-radius: 8px;
    font-size: 14px;
    padding: 0;
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
}
QPushButton#logout_btn:hover {
    color: #ff5566;
    background: rgba(255, 85, 102, 0.1);
    border-color: rgba(255, 85, 102, 0.3);
}

QPushButton#new_chat_btn {
    background: transparent;
    border: 1.5px dashed #2a2a50;
    color: #5050a0;
    padding: 8px 12px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton#new_chat_btn:hover {
    border-color: #6d5fff;
    color: #9d8fff;
    background: rgba(109, 95, 255, 0.06);
}

QPushButton#icon_plus_btn {
    background: #1e1e38;
    border: 1.5px solid #2a2a50;
    color: #9d8fff;
    border-radius: 8px;
    font-size: 18px;
    font-weight: bold;
    padding: 0;
    min-width: 30px;
    max-width: 30px;
    min-height: 30px;
    max-height: 30px;
}
QPushButton#icon_plus_btn:hover {
    background: rgba(109, 95, 255, 0.15);
    border-color: #6d5fff;
}

/* ─── AUTH TABS ─── */
QPushButton#auth_tab_active {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #6d5fff, stop:1 #9d7fff);
    color: white;
    border: none;
    border-radius: 9px;
    padding: 9px 20px;
    font-size: 13px;
    font-weight: 700;
}
QPushButton#auth_tab_inactive {
    background: transparent;
    color: #50508a;
    border: none;
    border-radius: 9px;
    padding: 9px 20px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton#auth_tab_inactive:hover {
    color: #9090c8;
    background: rgba(255,255,255,0.04);
}

/* ─── SCROLL ─── */
QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    background: transparent;
    width: 5px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #2a2a50;
    border-radius: 3px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #4040a0; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

/* ─── LABELS ─── */
#section_title {
    font-size: 22px;
    font-weight: 800;
    color: #e8e8f8;
    letter-spacing: -0.5px;
    background: transparent;
}
#section_sub {
    font-size: 12px;
    color: #50508a;
    background: transparent;
}
#field_label {
    font-size: 10px;
    font-weight: 700;
    color: #50508a;
    letter-spacing: 0.8px;
    background: transparent;
}
#err_label { color: #ff5566; font-size: 12px; background: transparent; }
#ok_label { color: #1dd8a0; font-size: 12px; background: transparent; }
#typing_label {
    color: #50508a;
    font-size: 13px;
    font-style: italic;
    padding: 8px 20px;
    background: transparent;
}
#chat_title_label {
    font-size: 14px;
    font-weight: 700;
    color: #e8e8f8;
    background: transparent;
}
#stat_val {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -1px;
    background: transparent;
}
#stat_label {
    font-size: 11px;
    color: #50508a;
    font-weight: 500;
    background: transparent;
}
#card_title {
    font-size: 14px;
    font-weight: 700;
    color: #c0c0e0;
    background: transparent;
}

/* ─── AUTH ─── */
#auth_logo {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -1px;
    background: transparent;
}
#auth_sub {
    font-size: 13px;
    color: #50508a;
    background: transparent;
}

/* ─── PROGRESS BAR ─── */
QProgressBar {
    background: #1a1a30;
    border: none;
    border-radius: 4px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6d5fff,stop:1 #1dd8a0);
    border-radius: 4px;
}

/* ─── SEARCH ─── */
#search_input {
    background: #16162a;
    border: 1.5px solid #1e1e38;
    border-radius: 9px;
    padding: 7px 12px;
    color: #9090c8;
    font-size: 12px;
}
#search_input:focus {
    border-color: #4040a0;
    color: #e8e8f8;
}

/* ─── CHAT BUBBLES ─── */
#bubble_user {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #6d5fff, stop:1 #9d7fff);
    border-radius: 18px;
    border-bottom-right-radius: 4px;
    border: none;
}
#bubble_ai {
    background: #181828;
    border: 1px solid #252545;
    border-radius: 18px;
    border-bottom-left-radius: 4px;
}
#bubble_text {
    color: #e8e8f8;
    font-size: 13px;
    background: transparent;
    border: none;
    line-height: 1.5;
}
#ai_avatar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #6d5fff, stop:1 #1dd8a0);
    border-radius: 11px;
    color: white;
    font-size: 10px;
    font-weight: 700;
    border: none;
}

/* ─── TOPICS CARD ─── */
#topics_card {
    background: #111119;
    border: 1px solid #1e1e30;
    border-radius: 12px;
}
"""
