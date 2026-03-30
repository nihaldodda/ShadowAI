from __future__ import annotations

import math

from PySide6.QtCore import (
    QAbstractAnimation,
    QPoint,
    Property,
    QRectF,
    Qt,
    QTimer,
    QEasingCurve,
    QPropertyAnimation,
    Signal,
)
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget

from shadow.ui.animations import phase_sin


class AvatarOverlay(QWidget):
    """Circular floating avatar; click opens main UI unless dragged."""

    open_main_requested = Signal()

    def __init__(self, phase_fn, parent=None):
        super().__init__(parent)
        self._phase_fn = phase_fn
        self.setFixedSize(120, 120)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._drag_anchor: QPoint | None = None
        self._press_pos: QPoint | None = None
        self._moved = False

        self._tick = 0
        self._last_phase: str | None = None
        self._idle_breath = 0.45
        self._idle_anim = QPropertyAnimation(self, b"idleBreath")
        self._idle_anim.setDuration(2800)
        self._idle_anim.setStartValue(0.22)
        self._idle_anim.setEndValue(1.0)
        self._idle_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._idle_anim.setLoopCount(-1)

        self._thinking_rotation = 0.0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._timer.start(26)

    def get_idle_breath(self) -> float:
        return self._idle_breath

    def set_idle_breath(self, v: float):
        self._idle_breath = v
        self.update()

    idleBreath = Property(float, get_idle_breath, set_idle_breath)

    def _sync_idle_animation(self, phase: str):
        if phase == "idle":
            if self._idle_anim.state() != QAbstractAnimation.State.Running:
                self._idle_anim.start()
        else:
            self._idle_anim.pause()

    def _on_tick(self):
        phase = self._phase_fn() if self._phase_fn else "idle"
        if phase != self._last_phase:
            self._last_phase = phase
            self._sync_idle_animation(phase)
        self._tick += 1
        if phase == "thinking":
            self._thinking_rotation = (self._thinking_rotation + 0.55) % 360.0
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.position().toPoint()
            self._drag_anchor = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._moved = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_anchor is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = (event.position().toPoint() - self._press_pos).manhattanLength()
            if delta > 6:
                self._moved = True
            self.move(event.globalPosition().toPoint() - self._drag_anchor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._moved:
                self.open_main_requested.emit()
            self._drag_anchor = None
            self._press_pos = None
            self._moved = False
        super().mouseReleaseEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        ph = self._phase_fn() if self._phase_fn else "idle"
        self._sync_idle_animation(ph)

    def paintEvent(self, event):
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() / 2
        cy = self.height() / 2
        base_r = min(cx, cy) - 10

        phase = self._phase_fn() if self._phase_fn else "idle"
        t = self._tick * 26.0
        breath = self._idle_breath if phase == "idle" else 0.55

        # ---- Idle: soft layered glow ----
        if phase == "idle":
            g_outer = breath * 0.85 + 0.15 * phase_sin(t, 3200)
            halo = QRadialGradient(cx, cy, base_r + 22)
            halo.setColorAt(0.0, QColor(90, 150, 255, int(35 + 75 * g_outer)))
            halo.setColorAt(0.45, QColor(130, 100, 255, int(20 + 45 * g_outer)))
            halo.setColorAt(0.75, QColor(60, 120, 220, int(12 + 25 * breath)))
            halo.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo))
            painter.drawEllipse(self.rect().adjusted(-14, -14, 14, 14))
            ring_alpha = int(70 + 110 * breath)
        elif phase == "listening":
            pulse = 0.62 + 0.38 * phase_sin(t, 520)
            ring_alpha = int(100 + 130 * pulse)
            halo = QRadialGradient(cx, cy, base_r + 18)
            halo.setColorAt(0.0, QColor(0, 210, 200, int(40 + 80 * pulse)))
            halo.setColorAt(0.65, QColor(80, 140, 255, int(25 + 40 * pulse)))
            halo.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo))
            painter.drawEllipse(self.rect().adjusted(-12, -12, 12, 12))
        elif phase == "thinking":
            th = 0.68 + 0.32 * phase_sin(t, 2400)
            ring_alpha = int(110 + 95 * th)
            halo = QRadialGradient(cx, cy, base_r + 16)
            halo.setColorAt(0.0, QColor(160, 120, 255, int(35 + 55 * th)))
            halo.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo))
            painter.drawEllipse(self.rect().adjusted(-10, -10, 10, 10))
        else:
            sp = 0.58 + 0.42 * phase_sin(t, 340)
            ring_alpha = int(130 + 90 * sp)
            halo = QRadialGradient(cx, cy, base_r + 20)
            halo.setColorAt(0.0, QColor(120, 220, 255, int(45 + 70 * sp)))
            halo.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo))
            painter.drawEllipse(self.rect().adjusted(-12, -12, 12, 12))

        # Core orb
        core_grad = QRadialGradient(cx, cy - base_r * 0.25, base_r * 1.2)
        core_grad.setColorAt(0.0, QColor(30, 55, 95, 235))
        core_grad.setColorAt(1.0, QColor(10, 14, 26, 245))
        painter.setBrush(QBrush(core_grad))
        painter.setPen(QPen(QColor(140, 180, 255, ring_alpha), 2))
        painter.drawEllipse(QRectF(cx - base_r, cy - base_r, base_r * 2, base_r * 2))

        # State-specific ring / motion graphics
        if phase == "listening":
            self._paint_listening_pulse(painter, cx, cy, base_r, t)
        elif phase == "thinking":
            self._paint_thinking_ring(painter, cx, cy, base_r)
        elif phase == "speaking":
            self._paint_speaking_bars(painter, cx, cy, base_r, t)

        inner = QRadialGradient(cx, cy, base_r * 0.45)
        inner.setColorAt(0.0, QColor(210, 240, 255, 240))
        inner.setColorAt(1.0, QColor(90, 170, 255, 0))
        painter.setBrush(QBrush(inner))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(cx - base_r * 0.35, cy - base_r * 0.35, base_r * 0.7, base_r * 0.7))

    def _paint_listening_pulse(self, painter: QPainter, cx: float, cy: float, base_r: float, t: float):
        for i, mul in enumerate((0.0, 0.45, 0.88)):
            phase = (t / 480.0 + mul) % 1.0
            expand = 5 + 14 * phase
            alpha = int(200 * (1.0 - phase) ** 1.4)
            painter.setPen(QPen(QColor(0, 230, 210, alpha), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(
                QRectF(cx - base_r - expand, cy - base_r - expand, (base_r + expand) * 2, (base_r + expand) * 2)
            )

    def _paint_thinking_ring(self, painter: QPainter, cx: float, cy: float, base_r: float):
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self._thinking_rotation)
        pen = QPen(QColor(170, 130, 255, 215), 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        dash_len = max(6, int(base_r * 0.22))
        pen.setDashPattern([dash_len, dash_len * 0.65])
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        rect = QRectF(-base_r + 4, -base_r + 4, (base_r - 4) * 2, (base_r - 4) * 2)
        painter.drawEllipse(rect)
        painter.restore()

    def _paint_speaking_bars(self, painter: QPainter, cx: float, cy: float, base_r: float, t: float):
        n = 18
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(n):
            ang = (i / n) * math.tau
            amp = 5 + 9 * (0.5 + 0.5 * math.sin((t / 95.0) + i * 0.65))
            w = 3.2
            painter.save()
            ox = cx + math.cos(ang) * (base_r + 11)
            oy = cy + math.sin(ang) * (base_r + 11)
            painter.translate(ox, oy)
            painter.rotate(math.degrees(ang) + 90)
            gr = QRadialGradient(0, -amp * 0.5, amp * 1.2)
            gr.setColorAt(0.0, QColor(200, 245, 255, 235))
            gr.setColorAt(1.0, QColor(80, 170, 255, 120))
            painter.setBrush(QBrush(gr))
            painter.drawRoundedRect(QRectF(-w / 2, -amp - 1, w, amp + 1), 1.4, 1.4)
            painter.restore()
