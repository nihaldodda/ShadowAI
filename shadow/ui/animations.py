"""
Lightweight animation helpers for Qt property animations and easing.
"""
from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation


def slide_fade_in(widget, prop_name: str, start: float, end: float, duration_ms: int = 350):
    anim = QPropertyAnimation(widget, prop_name.encode(), widget)
    anim.setDuration(duration_ms)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    return anim


def phase_sin(t_ms: float, period_ms: float) -> float:
    """0..1 smooth oscillation for glow intensity."""
    import math

    return 0.5 + 0.5 * math.sin((t_ms / period_ms) * 2.0 * math.pi)


def phase_linear(t_ms: float, period_ms: float) -> float:
    return (t_ms % period_ms) / period_ms
