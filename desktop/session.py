# SmartTutor Desktop — Сохранение и загрузка сессии
import json
import os

SESSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session.json")


def save_session(data: dict):
    """Сохраняет токен и данные пользователя в файл"""
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "token": data.get("access_token", ""),
                "user": {
                    "user_id":   data.get("user_id"),
                    "username":  data.get("username"),
                    "email":     data.get("email"),
                    "full_name": data.get("full_name"),
                    "access_token": data.get("access_token", ""),
                }
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[session] Не удалось сохранить сессию: {e}")


def load_session() -> dict | None:
    """Загружает сохранённую сессию. Возвращает None если файла нет."""
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[session] Не удалось загрузить сессию: {e}")
    return None


def clear_session():
    """Удаляет файл сессии (выход из аккаунта)"""
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    except Exception as e:
        print(f"[session] Не удалось удалить сессию: {e}")
