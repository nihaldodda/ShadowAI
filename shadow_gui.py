import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont


app = QApplication(sys.argv)
window = None


# =========================
# SIGNAL CONTROLLER
# =========================

class GuiController(QObject):

    show_signal = pyqtSignal()
    hide_signal = pyqtSignal()

    update_user_signal = pyqtSignal(str)
    update_quest_signal = pyqtSignal(str)
    update_command_signal = pyqtSignal(str)
    update_xp_signal = pyqtSignal(int)
    update_level_signal = pyqtSignal(int)
    update_rank_signal = pyqtSignal(str)


controller = GuiController()


# =========================
# MAIN HUD WINDOW
# =========================

class ShadowUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedSize(540, 420)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.status = "Idle"

        self.user = "Unknown"
        self.quest = "None"
        self.last_command = "-"

        self.xp = 0
        self.level = 1
        self.rank = "Initiate"

        self.pulse = 0

        # animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(40)

    # =========================

    def animate(self):
        self.pulse += 1
        self.update()

    # =========================

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # PANEL BACKGROUND
        painter.setBrush(QColor(10, 20, 30, 220))
        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawRoundedRect(
            0,
            0,
            self.width(),
            self.height(),
            20,
            20
        )

        # BORDER GLOW
        pen = QPen(QColor(0, 200, 255))
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawRoundedRect(
            1,
            1,
            self.width() - 2,
            self.height() - 2,
            20,
            20
        )

        center_x = self.width() // 2
        center_y = 180

        core_radius = 50
        pulse_radius = core_radius + (self.pulse % 20)

        # OUTER PULSE
        pen = QPen(QColor(0, 200, 255, 80))
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawEllipse(
            center_x - pulse_radius,
            center_y - pulse_radius,
            pulse_radius * 2,
            pulse_radius * 2
        )

        # CORE RING
        pen = QPen(QColor(0, 230, 255))
        pen.setWidth(4)
        painter.setPen(pen)

        painter.drawEllipse(
            center_x - core_radius,
            center_y - core_radius,
            core_radius * 2,
            core_radius * 2
        )

        # CENTER DOT
        painter.setBrush(QColor(0, 230, 255))
        painter.drawEllipse(center_x - 4, center_y - 4, 8, 8)

        # STATUS TEXT
        painter.setPen(QColor(200, 255, 255))
        painter.setFont(QFont("Consolas", 11))

        painter.drawText(
            0,
            center_y + core_radius + 30,
            self.width(),
            20,
            Qt.AlignmentFlag.AlignCenter,
            f"Shadow • {self.status}"
        )

        # LEFT PANEL
        painter.setFont(QFont("Consolas", 10))
        painter.setPen(QColor(0, 255, 200))

        painter.drawText(30, 60, f"User: {self.user}")
        painter.drawText(30, 85, f"Level: {self.level}")
        painter.drawText(30, 110, f"XP: {self.xp}")
        painter.drawText(30, 135, f"Rank: {self.rank}")

        # RIGHT PANEL
        right_x = self.width() - 220

        painter.drawText(right_x, 60, "Active Quest:")
        painter.drawText(right_x, 80, self.quest)

        painter.drawText(right_x, 120, "Last Command:")
        painter.drawText(right_x, 140, self.last_command)

        # VOICE WAVEFORM
        wave_y = self.height() - 50
        wave_x = 100

        pen = QPen(QColor(0, 200, 255))
        pen.setWidth(2)
        painter.setPen(pen)

        for i in range(12):

            height = ((self.pulse + i * 4) % 20)

            painter.drawLine(
                wave_x + i * 25,
                wave_y,
                wave_x + i * 25,
                wave_y - height
            )

    # =========================
    # UPDATE METHODS
    # =========================

    def update_user(self, name):
        self.user = name

    def update_quest(self, quest):
        self.quest = quest

    def update_command(self, cmd):
        self.last_command = cmd

    def update_xp(self, xp):
        self.xp = xp

    def update_level(self, level):
        self.level = level

    def update_rank(self, rank):
        self.rank = rank


# =========================
# WINDOW FUNCTIONS
# =========================

def _create_window():

    global window

    if window is None:
        window = ShadowUI()

    window.show()
    window.raise_()


def _hide_window():

    global window

    if window:
        window.hide()


controller.show_signal.connect(_create_window)
controller.hide_signal.connect(_hide_window)


# =========================
# DATA UPDATE SIGNALS
# =========================

def _update_user(name):
    if window:
        window.update_user(name)


def _update_quest(q):
    if window:
        window.update_quest(q)


def _update_command(cmd):
    if window:
        window.update_command(cmd)


def _update_xp(xp):
    if window:
        window.update_xp(xp)


def _update_level(level):
    if window:
        window.update_level(level)


def _update_rank(rank):
    if window:
        window.update_rank(rank)


controller.update_user_signal.connect(_update_user)
controller.update_quest_signal.connect(_update_quest)
controller.update_command_signal.connect(_update_command)
controller.update_xp_signal.connect(_update_xp)
controller.update_level_signal.connect(_update_level)
controller.update_rank_signal.connect(_update_rank)


# =========================
# PUBLIC API
# =========================

def show_shadow():
    controller.show_signal.emit()


def hide_shadow():
    controller.hide_signal.emit()


def update_user(name):
    controller.update_user_signal.emit(name)


def update_quest(q):
    controller.update_quest_signal.emit(q)


def update_last_command(cmd):
    controller.update_command_signal.emit(cmd)


def update_xp(xp):
    controller.update_xp_signal.emit(xp)


def update_level(level):
    controller.update_level_signal.emit(level)


def update_rank(rank):
    controller.update_rank_signal.emit(rank)