"""Glowing XP progress bar for Shadow UI (display only)."""
from __future__ import annotations

from PySide6.QtCore import Property, QRectF, Qt, QEasingCurve, QPropertyAnimation
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QWidget


class XpProgressBar(QWidget):
    """Rounded track with gradient fill; fraction 0..1."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(22)
        self.setMaximumHeight(26)
        self._fraction = 0.0
        self._pulse = 0.0
        self._pulse_anim = QPropertyAnimation(self, b"pulsePhase")
        self._pulse_anim.setDuration(2200)
        self._pulse_anim.setStartValue(0.0)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._pulse_anim.setLoopCount(-1)
        self._pulse_anim.start()

    def get_pulse_phase(self) -> float:
        return self._pulse

    def set_pulse_phase(self, v: float):
        self._pulse = v
        self.update()

    pulsePhase = Property(float, get_pulse_phase, set_pulse_phase)

    def set_fraction(self, value: float):
        self._fraction = max(0.0, min(1.0, float(value)))
        self.update()

    def paintEvent(self, event):
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        h = self.height()
        radius = h / 2 - 1
        track = QRectF(self.rect()).adjusted(1.5, 2, -1.5, -2)

        painter.setPen(QPen(QColor(80, 110, 160, 140), 1))
        painter.setBrush(QColor(12, 18, 34, 230))
        painter.drawRoundedRect(track, radius, radius)

        if self._fraction <= 0.001:
            return

        tw = track.width() - 4
        th = track.height() - 4
        fill_w = max(radius * 2, tw * self._fraction)
        inner = QRectF(track.left() + 2, track.top() + 2, fill_w, th)

        glow_boost = 0.12 + 0.08 * self._pulse
        g = QLinearGradient(inner.left(), inner.top(), inner.right(), inner.bottom())
        g.setColorAt(0.0, QColor(99, 170, 255, int(255 * (0.85 + glow_boost * 0.15))))
        g.setColorAt(0.5, QColor(140, 110, 255, int(255 * (0.9 + glow_boost * 0.1))))
        g.setColorAt(1.0, QColor(80, 200, 230, int(255 * (0.75 + glow_boost * 0.2))))

        painter.setPen(QPen(QColor(180, 210, 255, int(90 + 100 * self._pulse)), 1))
        painter.setBrush(g)
        painter.drawRoundedRect(inner, radius - 1, radius - 1)

        painter.setPen(Qt.PenStyle.NoPen)
        hi = QLinearGradient(inner.left(), inner.top(), inner.left(), inner.top() + inner.height() * 0.45)
        hi.setColorAt(0.0, QColor(255, 255, 255, 55))
        hi.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(hi)
        clip_r = QRectF(inner.left() + 1, inner.top() + 1, inner.width() - 2, inner.height() * 0.48)
        painter.drawRoundedRect(clip_r, radius - 2, radius - 2)
