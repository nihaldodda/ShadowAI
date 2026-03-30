from __future__ import annotations

from PySide6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    QObject,
    Qt,
    QTimer,
    QRect,
    Signal,
)
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QColor, QFont


class _SlidePopup(QWidget):
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(320)

        self._margin = 24
        self.setWindowOpacity(0.0)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(0)

        self._panel = QFrame()
        self._panel.setObjectName("ShadowToastPanel")
        panel_layout = QVBoxLayout(self._panel)
        panel_layout.setContentsMargins(18, 18, 18, 18)
        panel_layout.setSpacing(12)

        self.title_label = QLabel()
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.title_label.setStyleSheet(
            "color: #FFFFFF; letter-spacing: 1.5px; background: transparent; border: none;"
        )
        panel_layout.addWidget(self.title_label)

        self.body_label = QLabel()
        self.body_label.setWordWrap(True)
        self.body_label.setFont(QFont("Segoe UI", 10))
        self.body_label.setStyleSheet(
            "color: #D0D6FF; background: transparent; border: none;"
        )
        panel_layout.addWidget(self.body_label)

        self.footer_label = QLabel()
        self.footer_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self.footer_label.setStyleSheet(
            "color: #9FD4FF; background: transparent; border: none;"
        )
        panel_layout.addWidget(self.footer_label)

        self._panel.setStyleSheet(
            """
            #ShadowToastPanel {
                background-color: rgba(20, 20, 30, 230);
                border-radius: 14px;
                border: 2px solid rgba(120, 170, 255, 180);
            }
            """
        )

        shadow = QGraphicsDropShadowEffect(self._panel)
        shadow.setBlurRadius(38)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(10, 20, 45, 220))
        self._panel.setGraphicsEffect(shadow)

        outer.addWidget(self._panel)

        self._slide_anim: QPropertyAnimation | None = None
        self._fade_anim: QPropertyAnimation | None = None
        self._close_timer = QTimer(self)
        self._close_timer.setSingleShot(True)
        self._close_timer.timeout.connect(self._start_exit)

    def configure(self, title: str, body: str, footer: str, dwell_ms: int):
        self.title_label.setText(title)
        self.body_label.setText(body)
        self.footer_label.setText(footer)
        self._dwell_ms = dwell_ms
        self.adjustSize()

    def present(self, from_right: bool = True):
        screen = self.screen().availableGeometry() if self.screen() else QRect(0, 0, 1920, 1080)
        end_geo = QRect(
            screen.right() - self.width() - self._margin,
            screen.top() + self._margin + 40,
            self.width(),
            self.height(),
        )
        start_geo = QRect(end_geo)
        if from_right:
            start_geo.moveLeft(screen.right() + 40)
        else:
            start_geo.moveLeft(screen.left() - self.width() - 40)

        self.setGeometry(start_geo)
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()

        self._slide_anim = QPropertyAnimation(self, b"geometry", self)
        self._slide_anim.setDuration(380)
        self._slide_anim.setStartValue(start_geo)
        self._slide_anim.setEndValue(end_geo)
        self._slide_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._slide_anim.start()

        self._fade_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_anim.setDuration(300)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_anim.start()

        self._close_timer.start(self._dwell_ms)

    def _start_exit(self):
        end_geo = QRect(self.geometry())
        end_geo.moveLeft(self.screen().availableGeometry().right() + 80)

        self._slide_anim = QPropertyAnimation(self, b"geometry", self)
        self._slide_anim.setDuration(320)
        self._slide_anim.setStartValue(self.geometry())
        self._slide_anim.setEndValue(end_geo)
        self._slide_anim.setEasingCurve(QEasingCurve.Type.InCubic)

        self._fade_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_anim.setDuration(300)
        self._fade_anim.setStartValue(1.0)
        self._fade_anim.setEndValue(0.0)

        self._slide_anim.finished.connect(self._finish_close)
        self._slide_anim.start()
        self._fade_anim.start()

    def _finish_close(self):
        self.hide()
        self.setWindowOpacity(0.0)
        self.closed.emit()


class QuestPopupManager(QObject):
    """Owns short-lived toast popups; no backend logic."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_new: _SlidePopup | None = None
        self._active_done: _SlidePopup | None = None

    def show_new_quest(
        self,
        title: str,
        description: str,
        reward_xp: int,
        category: str | None = None,
        dwell_ms: int = 5200,
    ):
        self._dismiss(self._active_new)
        p = _SlidePopup()

        if category:
            if category.lower() == "btech":
                cat_display = "BTech"
            else:
                cat_display = category.replace("_", " ").title()
            cat_line = f"Category: {cat_display}"
        else:
            cat_line = ""
        task_line = f"Task: {title}" if title else ""
        extra_desc = (description or "").strip()

        body_parts = [x for x in [cat_line, task_line, extra_desc] if x]
        body = "\n\n".join(body_parts) if body_parts else f"{title}\n\n{description}"

        p.configure(
            "NEW QUEST",
            body,
            f"Reward: +{reward_xp} XP",
            dwell_ms,
        )
        p.closed.connect(lambda: self._forget("new", p))
        self._active_new = p
        p.present(from_right=True)

    def show_quest_completed(
        self,
        xp_gained: int,
        level: int,
        rank_code: str,
        rank_name: str,
        current_xp: int,
        xp_to_next: int,
        dwell_ms: int = 4800,
    ):
        self._dismiss(self._active_done)
        p = _SlidePopup()
        rank_line = f"{rank_code} — {rank_name}"
        body = (
            f"+{xp_gained} XP earned.\n"
            f"Level {level} · {current_xp} / {xp_to_next} XP this level."
        )
        p.configure("QUEST COMPLETED", body, rank_line, dwell_ms)
        p.closed.connect(lambda: self._forget("done", p))
        self._active_done = p
        p.present(from_right=True)

    def _forget(self, kind: str, ref: _SlidePopup):
        if kind == "new" and self._active_new is ref:
            self._active_new = None
        if kind == "done" and self._active_done is ref:
            self._active_done = None
        ref.deleteLater()

    def _dismiss(self, popup: _SlidePopup | None):
        if popup and popup.isVisible():
            popup._close_timer.stop()
            popup._start_exit()
