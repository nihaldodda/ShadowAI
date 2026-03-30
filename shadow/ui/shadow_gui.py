from __future__ import annotations

import sys

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from shadow.voice.speaker import is_speaking

from shadow.ui.quest_popup import QuestPopupManager


class GuiController(QObject):
    show_signal = Signal()
    hide_signal = Signal()
    update_user_signal = Signal(str)
    update_quest_signal = Signal(str)
    update_command_signal = Signal(str)
    update_xp_signal = Signal(int)
    update_level_signal = Signal(int)
    update_rank_signal = Signal(str)
    assistant_online_signal = Signal(bool)
    listen_sig = Signal(bool)
    think_sig = Signal(bool)


class UiRuntimeState:
    __slots__ = ("listening", "thinking")

    def __init__(self):
        self.listening = False
        self.thinking = False


runtime = UiRuntimeState()
controller = GuiController()
controller.listen_sig.connect(lambda v: setattr(runtime, "listening", bool(v)))
controller.think_sig.connect(lambda v: setattr(runtime, "thinking", bool(v)))
quest_pending = {"data": None}
quest_mgr = QuestPopupManager()
avatar: AvatarOverlay | None = None
main_win: MainDashboardWindow | None = None

app = QApplication(sys.argv)
app.setApplicationName("Shadow")
app.setStyle("Fusion")
pal = app.palette()
pal.setColor(QPalette.ColorRole.Window, QColor(11, 15, 24))
pal.setColor(QPalette.ColorRole.WindowText, QColor(220, 232, 255))
app.setPalette(pal)


def _resolve_avatar_phase() -> str:
    if is_speaking:
        return "speaking"
    if runtime.thinking:
        return "thinking"
    if runtime.listening:
        return "listening"
    return "idle"


def _quest_refresh():
    try:
        from shadow.core.commands import quests

        q = quests.active_quest
        if q:
            return {"active": (q.title, q.description, q.xp_reward)}
    except Exception:
        pass
    return {"active": None}


def _ensure_ui():
    global avatar, main_win
    if main_win is None:
        from shadow.ui.main_window import MainDashboardWindow

        main_win = MainDashboardWindow(controller, _quest_refresh)
    if avatar is None:
        from shadow.ui.avatar_overlay import AvatarOverlay

        avatar = AvatarOverlay(_resolve_avatar_phase)
        avatar.open_main_requested.connect(lambda: main_win.show_dashboard() if main_win else None)


def _place_avatar():
    if not avatar:
        return
    screen = avatar.screen().availableGeometry() if avatar.screen() else None
    if not screen:
        return
    x = screen.right() - avatar.width() - 36
    y = screen.center().y() - avatar.height() // 2
    avatar.move(max(screen.left() + 8, x), max(screen.top() + 8, y))


def _on_show():
    _ensure_ui()
    controller.assistant_online_signal.emit(True)
    if avatar:
        _place_avatar()
        avatar.show()
        avatar.raise_()


def _on_hide():
    controller.assistant_online_signal.emit(False)
    if avatar:
        avatar.hide()
    if main_win:
        main_win.hide()


def _handle_quest_title(_title: str):
    try:
        from shadow.core.commands import quests

        q = quests.active_quest
        if q:
            quest_mgr.show_new_quest(
                q.title,
                q.description,
                q.xp_reward,
                category=getattr(q, "category", None),
            )
            quest_pending["data"] = (q.title, q.description, q.xp_reward)
    except Exception as e:
        print("[Shadow UI] quest hook:", e)


def _poll_quest_completion():
    try:
        from shadow.core.commands import quests
    except Exception:
        return

    # If a quest is already active (e.g., after restart), prime the completion popup data.
    if quest_pending["data"] is None and quests.active_quest is not None:
        q = quests.active_quest
        if q and getattr(q, "xp_reward", 0) > 0:
            quest_pending["data"] = (q.title, q.description, q.xp_reward)

    data = quest_pending["data"]
    if not data or quests.active_quest is not None:
        return

    title, _desc, xp_reward = data
    if xp_reward <= 0:
        quest_pending["data"] = None
        return
    quest_pending["data"] = None

    def _finish():
        try:
            from shadow.core.commands import shadow

            xp_need = shadow.level * 100
            quest_mgr.show_quest_completed(
                xp_reward,
                shadow.level,
                shadow.rank,
                shadow.rank_name,
                shadow.xp,
                xp_need,
            )
            if main_win:
                main_win.record_quest_completed(title, xp_reward)
        except Exception as e:
            print("[Shadow UI] completion hook:", e)

    QTimer.singleShot(160, _finish)


controller.show_signal.connect(_on_show)
controller.hide_signal.connect(_on_hide)
controller.update_quest_signal.connect(_handle_quest_title)

_quest_poll = QTimer()
_quest_poll.timeout.connect(_poll_quest_completion)
_quest_poll.start(420)


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


def notify_listening(active: bool):
    controller.listen_sig.emit(bool(active))


def notify_processing(active: bool):
    controller.think_sig.emit(bool(active))
