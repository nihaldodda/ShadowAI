from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from shadow.ui.widgets.xp_progress_bar import XpProgressBar


class MainDashboardWindow(QMainWindow):
    """Main Shadow hub: sidebar navigation and stacked feature pages."""

    def __init__(self, controller, refresh_quest_state_fn, parent=None):
        super().__init__(parent)
        self._controller = controller
        self._refresh_quest_state = refresh_quest_state_fn

        self.setWindowTitle("Shadow")
        self.resize(980, 620)
        self.setMinimumSize(860, 520)

        root = QFrame()
        root.setObjectName("Root")
        self.setCentralWidget(root)
        main_layout = QHBoxLayout(root)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._sidebar = QFrame()
        self._sidebar.setObjectName("Sidebar")
        self._sidebar.setFixedWidth(220)
        side_lay = QVBoxLayout(self._sidebar)
        side_lay.setContentsMargins(16, 22, 16, 22)
        side_lay.setSpacing(8)

        brand = QLabel("SHADOW")
        brand.setObjectName("Brand")
        side_lay.addWidget(brand)
        side_lay.addSpacing(12)

        self._nav_buttons: list[QPushButton] = []
        for key, label in [
            ("dash", "Dashboard"),
            ("quests", "Quests"),
            ("profile", "Profile"),
            ("history", "Command History"),
        ]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("navKey", key)
            btn.setObjectName("NavButton")
            btn.clicked.connect(lambda checked=False, k=key: self._select_nav(k))
            side_lay.addWidget(btn)
            self._nav_buttons.append(btn)

        side_lay.addStretch(1)

        self._stack = QStackedWidget()
        self._stack.setObjectName("Stack")

        self._page_dashboard = self._build_dashboard_page()
        self._page_quests = self._build_quests_page()
        self._page_profile = self._build_profile_page()
        self._page_history = self._build_history_page()

        self._stack.addWidget(self._page_dashboard)
        self._stack.addWidget(self._page_quests)
        self._stack.addWidget(self._page_profile)
        self._stack.addWidget(self._page_history)

        main_layout.addWidget(self._sidebar)
        main_layout.addWidget(self._stack, 1)

        self._apply_theme()

        # state mirrored from backend signals (no logic, display only)
        self._user = "Unknown"
        self._level = 1
        self._xp = 0
        self._rank = "E - Initiate of Shadows"
        self._quest_title = "None"
        self._recent_commands: list[str] = []
        self._history: list[str] = []
        self._completed_quests: list[tuple[str, int]] = []

        self._connect_controller()
        self._hydrate_from_backend()
        self._select_nav("dash")

        self._quest_timer = QTimer(self)
        self._quest_timer.timeout.connect(self._sync_quest_panel)
        self._quest_timer.start(700)

    def _apply_theme(self):
        self.setStyleSheet(
            """
            QMainWindow, #Root {
                background-color: #0b0f18;
            }
            #Sidebar {
                background-color: #10162a;
                border-right: 1px solid rgba(120, 160, 255, 80);
            }
            #Brand {
                color: #dbe8ff;
                font-size: 18px;
                font-weight: 700;
                letter-spacing: 4px;
            }
            #NavButton {
                text-align: left;
                padding: 10px 14px;
                border-radius: 10px;
                color: #c7d6ef;
                background: transparent;
                border: 1px solid transparent;
                font-size: 13px;
            }
            #NavButton:hover {
                background: rgba(120, 160, 255, 35);
                border: 1px solid rgba(120, 160, 255, 90);
            }
            #NavButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(99, 140, 255, 95), stop:1 rgba(160, 99, 255, 85));
                color: #0b0f18;
                font-weight: 600;
                border: 1px solid rgba(180, 210, 255, 160);
            }
            #Stack {
                background: #0b0f18;
            }
            QFrame#Panel {
                background: rgba(16, 22, 38, 220);
                border-radius: 16px;
                border: 1px solid rgba(120, 160, 255, 95);
            }
            QLabel#Title {
                color: #dbe8ff;
                font-size: 15px;
                font-weight: 700;
            }
            QLabel#Muted {
                color: #8fa3bf;
                font-size: 12px;
            }
            QLabel#Hero {
                color: #e6f0ff;
                font-size: 26px;
                font-weight: 800;
            }
            QListWidget {
                background: rgba(10, 14, 24, 180);
                border: 1px solid rgba(120, 160, 255, 60);
                border-radius: 12px;
                color: #d3e2ff;
                padding: 8px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background: rgba(120, 160, 255, 120);
            }
            """
        )

    def _wrap_scroll(self, inner: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(inner)
        return scroll

    def _build_dashboard_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 26, 28, 26)
        lay.setSpacing(16)

        hero = QLabel("Command Center")
        hero.setObjectName("Hero")
        lay.addWidget(hero)

        row = QHBoxLayout()
        row.setSpacing(16)

        status_panel = QFrame()
        status_panel.setObjectName("Panel")
        sp = QVBoxLayout(status_panel)
        t = QLabel("Assistant status")
        t.setObjectName("Title")
        sp.addWidget(t)
        self.lbl_status = QLabel("Standby — wake Shadow to initialize.")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setObjectName("Muted")
        sp.addWidget(self.lbl_status)

        snap = QFrame()
        snap.setObjectName("Panel")
        sn = QVBoxLayout(snap)
        tx = QLabel("Progress snapshot")
        tx.setObjectName("Title")
        sn.addWidget(tx)
        self.lbl_snapshot = QLabel()
        self.lbl_snapshot.setObjectName("Muted")
        self.lbl_snapshot.setWordWrap(True)
        sn.addWidget(self.lbl_snapshot)
        self._xp_bar_dashboard = XpProgressBar()
        self._xp_bar_dashboard.setMinimumHeight(20)
        self._xp_bar_dashboard.setMaximumHeight(22)
        sn.addWidget(self._xp_bar_dashboard)
        self.lbl_snapshot_xp = QLabel()
        self.lbl_snapshot_xp.setObjectName("Muted")
        sn.addWidget(self.lbl_snapshot_xp)

        row.addWidget(status_panel, 1)
        row.addWidget(snap, 1)
        lay.addLayout(row)

        recent_title = QLabel("Last commands")
        recent_title.setObjectName("Title")
        lay.addWidget(recent_title)
        self.list_recent = QListWidget()
        self.list_recent.setMaximumHeight(220)
        lay.addWidget(self.list_recent, 1)
        return self._wrap_scroll(page)

    def _build_quests_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 26, 28, 26)
        lay.setSpacing(16)

        title = QLabel("Quest board")
        title.setObjectName("Hero")
        lay.addWidget(title)

        active_panel = QFrame()
        active_panel.setObjectName("Panel")
        ap = QVBoxLayout(active_panel)
        at = QLabel("Active quest")
        at.setObjectName("Title")
        ap.addWidget(at)
        self.lbl_active_quest = QLabel("No active quest.")
        self.lbl_active_quest.setWordWrap(True)
        self.lbl_active_quest.setObjectName("Muted")
        ap.addWidget(self.lbl_active_quest)

        done_panel = QFrame()
        done_panel.setObjectName("Panel")
        dp = QVBoxLayout(done_panel)
        dt = QLabel("Completed (this session)")
        dt.setObjectName("Title")
        dp.addWidget(dt)
        self.list_done_quests = QListWidget()
        dp.addWidget(self.list_done_quests, 1)

        lay.addWidget(active_panel)
        lay.addWidget(done_panel, 1)
        return self._wrap_scroll(page)

    def _build_profile_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 26, 28, 26)
        lay.setSpacing(18)

        title = QLabel("Profile")
        title.setObjectName("Hero")
        lay.addWidget(title)

        card = QFrame()
        card.setObjectName("Panel")
        c = QVBoxLayout(card)
        self.lbl_profile_user = QLabel()
        self.lbl_profile_user.setObjectName("Title")
        self.lbl_profile_level = QLabel()
        self.lbl_profile_level.setObjectName("Muted")
        self.lbl_profile_rank = QLabel()
        self.lbl_profile_rank.setObjectName("Title")
        self.lbl_profile_rank_name = QLabel()
        self.lbl_profile_rank_name.setObjectName("Muted")
        self.lbl_profile_xp = QLabel()
        self.lbl_profile_xp.setObjectName("Muted")
        c.addWidget(self.lbl_profile_user)
        c.addWidget(self.lbl_profile_level)
        c.addWidget(self.lbl_profile_rank)
        c.addWidget(self.lbl_profile_rank_name)
        c.addWidget(self.lbl_profile_xp)
        self._xp_bar_profile = XpProgressBar()
        xp_row = QHBoxLayout()
        xp_row.setSpacing(12)
        xp_row.addWidget(self._xp_bar_profile, 1)
        self.lbl_profile_xp_bar = QLabel()
        self.lbl_profile_xp_bar.setObjectName("Muted")
        self.lbl_profile_xp_bar.setMinimumWidth(120)
        self.lbl_profile_xp_bar.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        xp_row.addWidget(self.lbl_profile_xp_bar)
        c.addLayout(xp_row)
        lay.addWidget(card)
        lay.addStretch(1)
        return self._wrap_scroll(page)

    def _build_history_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 26, 28, 26)
        lay.setSpacing(12)
        title = QLabel("Command history")
        title.setObjectName("Hero")
        lay.addWidget(title)
        self.list_history = QListWidget()
        lay.addWidget(self.list_history, 1)
        return self._wrap_scroll(page)

    def _hydrate_from_backend(self):
        """Sync display from saved memory and live state (read-only); repairs missed signals at import time."""
        try:
            from shadow.core.memory_manager import get_name, load_memory

            n = get_name()
            if n:
                self._user = n

            mem = load_memory()
            self._level = int(mem.get("level", self._level))
            self._xp = int(mem.get("xp", self._xp))
            rc, rn = mem.get("rank"), mem.get("rank_name")
            if rc and rn:
                self._rank = f"{rc} - {rn}"
        except Exception:
            pass
        try:
            from shadow.core.commands import shadow

            self._level = shadow.level
            self._xp = shadow.xp
            self._rank = f"{shadow.rank} - {shadow.rank_name}"
        except Exception:
            pass
        try:
            from shadow.core.commands import quests

            q = quests.active_quest
            if q:
                self._quest_title = q.title
        except Exception:
            pass
        self._refresh_snapshot()
        self._refresh_profile()
        self._sync_quest_panel()
        if self._user != "Unknown":
            self.lbl_profile_user.setText(f"Operator: {self._user}")

    def _connect_controller(self):
        c = self._controller
        c.update_user_signal.connect(self._on_user)
        c.update_quest_signal.connect(self._on_quest)
        c.update_command_signal.connect(self._on_command)
        c.update_xp_signal.connect(self._on_xp)
        c.update_level_signal.connect(self._on_level)
        c.update_rank_signal.connect(self._on_rank)
        c.assistant_online_signal.connect(self._on_online_changed)

    def _on_online_changed(self, online: bool):
        if online:
            self.lbl_status.setText("Online — awaiting voice commands.")
        else:
            self.lbl_status.setText("Standby — wake Shadow to initialize.")

    def _on_user(self, name: str):
        self._user = name
        self._refresh_profile()

    def _on_quest(self, title: str):
        self._quest_title = title
        self._sync_quest_panel()

    def _on_command(self, cmd: str):
        self._history.append(cmd)
        self.list_history.addItem(QListWidgetItem(cmd))
        self.list_history.scrollToBottom()

        self._recent_commands.append(cmd)
        if len(self._recent_commands) > 12:
            self._recent_commands = self._recent_commands[-12:]
        self.list_recent.clear()
        for line in reversed(self._recent_commands):
            self.list_recent.addItem(QListWidgetItem(line))

    def _on_xp(self, xp: int):
        self._xp = xp
        self._refresh_snapshot()
        self._refresh_profile()

    def _on_level(self, level: int):
        self._level = level
        self._refresh_snapshot()
        self._refresh_profile()

    def _on_rank(self, rank: str):
        self._rank = rank
        self._refresh_snapshot()
        self._refresh_profile()

    def _xp_to_next(self) -> int:
        return self._level * 100

    def _rank_code_and_name(self) -> tuple[str, str]:
        parts = self._rank.split(" - ", 1)
        code = parts[0].strip() if parts else "?"
        name = parts[1].strip() if len(parts) > 1 else ""
        return code, name

    def _xp_fraction(self) -> float:
        need = self._xp_to_next()
        if need <= 0:
            return 0.0
        return max(0.0, min(1.0, self._xp / need))

    def _refresh_snapshot(self):
        need = self._xp_to_next()
        code, rname = self._rank_code_and_name()
        rline = f"Rank: {code}" + (f" — {rname}" if rname else "")
        self.lbl_snapshot.setText(
            f"Level {self._level}\n"
            f"{rline}\n"
            f"XP: {self._xp} / {need}"
        )
        self._xp_bar_dashboard.set_fraction(self._xp_fraction())
        self.lbl_snapshot_xp.setText(f"{self._xp} / {need} XP")

    def _refresh_profile(self):
        self.lbl_profile_user.setText(f"Operator: {self._user}")
        self.lbl_profile_level.setText(f"Level {self._level}")
        code, rname = self._rank_code_and_name()
        self.lbl_profile_rank.setText(f"Rank: {code}")
        self.lbl_profile_rank_name.setText(rname if rname else " ")
        need = self._xp_to_next()
        self.lbl_profile_xp.setText(f"XP: {self._xp} / {need}")
        self._xp_bar_profile.set_fraction(self._xp_fraction())
        self.lbl_profile_xp_bar.setText(f"{self._xp} / {need} XP")

    def _sync_quest_panel(self):
        data = self._refresh_quest_state()
        active = data.get("active")
        if active:
            title, desc, xp = active
            self.lbl_active_quest.setText(f"{title}\n{desc}\nReward: {xp} XP")
        else:
            self.lbl_active_quest.setText("No active quest.")

    def record_quest_completed(self, title: str, xp: int):
        self._completed_quests.insert(0, (title, xp))
        if len(self._completed_quests) > 40:
            self._completed_quests = self._completed_quests[:40]
        self.list_done_quests.clear()
        for t, x in self._completed_quests:
            self.list_done_quests.addItem(QListWidgetItem(f"{t}  ·  +{x} XP"))

    def _select_nav(self, key: str):
        mapping = {"dash": 0, "quests": 1, "profile": 2, "history": 3}
        idx = mapping.get(key, 0)
        self._stack.setCurrentIndex(idx)
        for b in self._nav_buttons:
            b.setChecked(b.property("navKey") == key)

    def show_dashboard(self):
        self.show()
        self.raise_()
        self.activateWindow()
