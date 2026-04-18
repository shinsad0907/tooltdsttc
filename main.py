"""
MMO Tool Pro v3.1 — Facebook Manager
Tích hợp: get_page.py, đa luồng login, proxy per-account, avatar, cookie, token, pages
Format nhập: uid|pass|2fa
"""

import sys, random, string, json, os, time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QTreeWidget, QTreeWidgetItem, QCheckBox, QComboBox, QTextEdit,
    QGroupBox, QSplitter, QMenu, QAction, QHeaderView, QFrame,
    QScrollArea, QStackedWidget, QSizePolicy, QAbstractItemView, QSpacerItem,
    QDialog, QFormLayout, QProgressBar, QProgressDialog, QMessageBox, QInputDialog,
    QTabWidget, QPlainTextEdit, QFileDialog, QListWidget, QListWidgetItem, QRadioButton
)

from PyQt5.QtCore import Qt, QTimer, QDateTime, QThread, pyqtSignal, QObject, QRectF, QRect
from PyQt5.QtGui import QFont, QColor, QIcon, QPalette, QCursor, QPixmap, QPainter, QBrush, QLinearGradient
from source.regpage_worker import RegisterWorker, RegisterBatchManager

# ─────────────────────────────────────────────
#  SPINBOX STYLE (mũi tên ▲▼ rõ ràng)
# ─────────────────────────────────────────────
SPINBOX_STYLE = """
QSpinBox, QDoubleSpinBox {
    background-color: #111827;
    border: 1px solid #2e4570;
    border-radius: 7px;
    padding: 5px 32px 5px 10px;
    color: #c9d6ea;
    font-size: 13px;
    font-weight: 700;
    font-family: 'Consolas', monospace;
    min-height: 32px;
    selection-background-color: #0d1e38;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: rgba(45,111,255,0.7);
    background-color: #0d1629;
}
QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #4d78cc;
}
QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 26px;
    height: 16px;
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #1c2d4a,stop:1 #162038);
    border-left: 1px solid #2e4570;
    border-bottom: 1px solid #2e4570;
    border-top-right-radius: 7px;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #2d6fff,stop:1 #1a4fd6);
}
QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed {
    background: #0d1629;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: url(ARROW_UP_NORMAL);
    width: 10px;
    height: 6px;
}
QSpinBox::up-arrow:hover, QDoubleSpinBox::up-arrow:hover {
    image: url(ARROW_UP_HOVER);
}
QSpinBox::up-arrow:disabled, QDoubleSpinBox::up-arrow:disabled {
    image: url(ARROW_UP_DIM);
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 26px;
    height: 16px;
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #162038,stop:1 #0f1724);
    border-left: 1px solid #2e4570;
    border-top: 1px solid #2e4570;
    border-bottom-right-radius: 7px;
}
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #1a4fd6,stop:1 #2d6fff);
}
QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed {
    background: #0d1629;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: url(ARROW_DOWN_NORMAL);
    width: 10px;
    height: 6px;
}
QSpinBox::down-arrow:hover, QDoubleSpinBox::down-arrow:hover {
    image: url(ARROW_DOWN_HOVER);
}
QSpinBox::down-arrow:disabled, QDoubleSpinBox::down-arrow:disabled {
    image: url(ARROW_DOWN_DIM);
}
"""

# ─────────────────────────────────────────────
#  STYLESHEET
# ─────────────────────────────────────────────
STYLE = """
QMainWindow, QWidget {
    background-color: #0b0f14;
    color: #dde4ef;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}
#Sidebar { background-color: #080c10; border-right: 1px solid #1a2336; min-width: 210px; max-width: 210px; }
#LogoFrame { background-color: #080c10; border-bottom: 1px solid #1a2336; min-height: 58px; max-height: 58px; }
#LogoTitle { color: #4d8fff; font-size: 15px; font-weight: 800; font-family: 'Consolas', monospace; letter-spacing: 2px; }
#LogoSub   { color: #2e3f5c; font-size: 10px; }
#NavSection { color: #2e3f5c; font-size: 9px; font-family: 'Consolas', monospace; letter-spacing: 2.5px; font-weight: 700; padding: 14px 14px 4px 14px; }
#NavBtn { background: transparent; border: none; color: #5a7099; font-size: 13px; font-weight: 500; text-align: left; padding: 8px 14px; border-radius: 8px; margin: 1px 6px; min-height: 34px; }
#NavBtn:hover { background-color: #111827; color: #c9d6ea; }
#NavBtnActive { background-color: #0d1e38; border: none; color: #ffffff; font-size: 13px; font-weight: 600; text-align: left; padding: 8px 14px; border-radius: 8px; margin: 1px 6px; min-height: 34px; border-left: 3px solid #2d6fff; }
#SubNavBtn { background: transparent; border: none; color: #344a6b; font-size: 12px; text-align: left; padding: 6px 14px 6px 42px; border-radius: 6px; margin: 1px 6px; min-height: 28px; }
#SubNavBtn:hover { background-color: #111827; color: #8098bf; }
#SubNavBtnActive { background: transparent; border: none; color: #00d4aa; font-size: 12px; font-weight: 600; text-align: left; padding: 6px 14px 6px 42px; border-radius: 6px; margin: 1px 6px; min-height: 28px; }
#SidebarFooter { border-top: 1px solid #1a2336; padding: 10px 14px; background: #080c10; }
#StatusLabel { color: #10b981; font-size: 11px; font-family: 'Consolas', monospace; }
#Topbar { background-color: #0b0f14; border-bottom: 1px solid #1a2336; min-height: 50px; max-height: 50px; }
#Breadcrumb { color: #3d5278; font-size: 12px; font-family: 'Consolas', monospace; }
#BreadcrumbCurrent { color: #c9d6ea; font-size: 12px; font-family: 'Consolas', monospace; font-weight: 700; }
#ClockLabel { color: #f59e0b; font-size: 13px; font-family: 'Consolas', monospace; font-weight: 700; background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.2); border-radius: 6px; padding: 3px 10px; }
#BadgeBlue  { color: #4d8fff; font-size: 10px; font-family: 'Consolas', monospace; font-weight: 700; background: rgba(45,111,255,0.08); border: 1px solid rgba(45,111,255,0.25); border-radius: 12px; padding: 3px 9px; }
#BadgeGreen { color: #00d4aa; font-size: 10px; font-family: 'Consolas', monospace; font-weight: 700; background: rgba(0,212,170,0.08); border: 1px solid rgba(0,212,170,0.25); border-radius: 12px; padding: 3px 9px; }
#StatCard { background-color: #111827; border: 1px solid #1a2336; border-radius: 10px; min-height: 72px; max-height: 72px; }
#StatLabel { color: #2e3f5c; font-size: 9px; font-family: 'Consolas', monospace; letter-spacing: 2px; text-transform: uppercase; font-weight: 700; background: transparent; }
#StatValueBlue   { color: #6ba3ff; font-size: 24px; font-weight: 800; font-family: 'Consolas', monospace; background: transparent; }
#StatValueGreen  { color: #00d4aa; font-size: 24px; font-weight: 800; font-family: 'Consolas', monospace; background: transparent; }
#StatValueRed    { color: #ff6b6b; font-size: 24px; font-weight: 800; font-family: 'Consolas', monospace; background: transparent; }
#StatValueYellow { color: #f59e0b; font-size: 24px; font-weight: 800; font-family: 'Consolas', monospace; background: transparent; }
#PageTitle { color: #e8edf5; font-size: 20px; font-weight: 800; background: transparent; }
#PageSub   { color: #3d5278; font-size: 12px; background: transparent; }
#PageIconFb { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #1877f2,stop:1 #4298ff); border-radius: 12px; color: white; font-size: 20px; font-weight: 800; min-width: 46px; max-width: 46px; min-height: 46px; max-height: 46px; }
#SectionLabel { color: #2e4570; font-size: 9px; font-family: 'Consolas', monospace; letter-spacing: 2px; font-weight: 700; text-transform: uppercase; background: transparent; padding: 4px 0; }

QPushButton {
    background-color: #1c2d4a; color: #a8c0e0;
    border: 1px solid #2e4570; padding: 6px 14px;
    border-radius: 7px; font-weight: 600; font-size: 12px; min-height: 30px;
}
QPushButton:hover { background-color: #243a5e; color: #e8edf5; border-color: #4d78cc; }
QPushButton:pressed { background-color: #111d30; }
QPushButton#btnPrimary { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1a4fd6,stop:1 #3d7aff); color: white; border: 1px solid #5588ff; font-weight: 700; }
QPushButton#btnPrimary:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #2d62f0,stop:1 #5a90ff); border-color: #7aaaff; }
QPushButton#btnSuccess { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0a7a55,stop:1 #00b890); color: white; border: 1px solid #00d4aa; font-weight: 700; }
QPushButton#btnSuccess:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #00b890,stop:1 #00e8c0); border-color: #00f5c4; }
QPushButton#btnDanger { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #9b1f1f,stop:1 #d63030); color: white; border: 1px solid #ef4444; font-weight: 700; }
QPushButton#btnDanger:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #d63030,stop:1 #ff5555); border-color: #ff7070; }
QPushButton#btnWarn { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #8a3e00,stop:1 #cc7a00); color: #fff8e0; border: 1px solid #f59e0b; font-weight: 700; }
QPushButton#btnWarn:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #cc7a00,stop:1 #f5a800); }
QPushButton#btnGetPage { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #4a1d96,stop:1 #7c3aed); color: white; border: 1px solid #8b5cf6; font-weight: 700; }
QPushButton#btnGetPage:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7c3aed,stop:1 #9d6eff); border-color: #a78bfa; }
QPushButton#btnLogin { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0a7a55,stop:1 #00b890); color: white; border: 1px solid #00d4aa; font-weight: 700; }
QPushButton#btnLogin:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #00b890,stop:1 #00e8c0); border-color: #00f5c4; }

#FbTree {
    background-color: #111827; border: 1px solid #1a2336; border-radius: 10px;
    color: #9aafcf; alternate-background-color: #0f1724; outline: none;
    gridline-color: #141f30; show-decoration-selected: 1;
}
#FbTree::item { padding: 4px 2px; border-bottom: 1px solid #141f30; min-height: 32px; }
#FbTree::item:selected { background-color: #0d1e38; color: #6ba3ff; }
#FbTree::item:hover:!selected { background-color: #131f33; }
#FbTree QHeaderView::section {
    background-color: #0f1724; color: #2e4570; padding: 7px 8px; border: none;
    border-right: 1px solid #1a2336; border-bottom: 1px solid #1a2336;
    font-weight: 700; font-size: 10px; font-family: 'Consolas', monospace;
    text-transform: uppercase; letter-spacing: 1px;
}
#FbTree::branch { background: #111827; }

QLineEdit, QComboBox {
    background-color: #111827; border: 1px solid #1a2336;
    border-radius: 7px; padding: 6px 10px; color: #c9d6ea; font-size: 12px; min-height: 28px;
}
QLineEdit:focus { border-color: rgba(45,111,255,0.5); }
QTextEdit, QPlainTextEdit {
    background-color: #050810; border: 1px solid #1a2336; border-radius: 7px;
    color: #00d4aa; font-family: 'Consolas', monospace; font-size: 11px; padding: 6px;
}
QGroupBox {
    border: 1px solid #1a2336; border-radius: 10px; margin-top: 12px;
    padding: 10px 8px 8px 8px; color: #2e4570; font-size: 9px;
    font-family: 'Consolas', monospace; text-transform: uppercase;
    letter-spacing: 2px; font-weight: 700; background: #111827;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; background: #111827; color: #2d6fff; }
QProgressBar { background: #111827; border: 1px solid #1a2336; border-radius: 4px; height: 6px; font-size: 0px; }
QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #2d6fff,stop:1 #00d4aa); border-radius: 4px; }
QScrollBar:vertical { background: #0b0f14; width: 6px; border-radius: 3px; }
QScrollBar::handle:vertical { background: #1a2848; border-radius: 3px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #2e4570; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #0b0f14; height: 6px; border-radius: 3px; }
QScrollBar::handle:horizontal { background: #1a2848; border-radius: 3px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QMenu { background: #111827; border: 1px solid #1a2336; border-radius: 8px; color: #9aafcf; padding: 4px; }
QMenu::item { padding: 7px 18px 7px 12px; border-radius: 5px; }
QMenu::item:selected { background: #0d1e38; color: #4d8fff; }
QMenu::separator { height: 1px; background: #1a2336; margin: 4px 8px; }
QStatusBar { background: #080c10; border-top: 1px solid #1a2336; color: #10b981; font-size: 11px; font-family: 'Consolas', monospace; padding: 3px 12px; }
QCheckBox { color: #5a7099; spacing: 5px; background: transparent; }
QCheckBox::indicator { width: 14px; height: 14px; border: 1px solid #1a2336; border-radius: 3px; background: #111827; }
QCheckBox::indicator:checked { background: #2d6fff; border-color: #4d8fff; }
QDialog { background: #0d1219; }
QSplitter::handle { background: #1a2336; }
QTabWidget::pane { border: 1px solid #1a2336; border-radius: 8px; background: #111827; }
QTabBar::tab { background: #0d1219; color: #3d5278; padding: 7px 18px; border: 1px solid #1a2336; border-bottom: none; border-radius: 6px 6px 0 0; font-size: 12px; font-weight: 600; margin-right: 2px; }
QTabBar::tab:selected { background: #111827; color: #c9d6ea; border-color: #1a2336; }
QTabBar::tab:hover:!selected { background: #131d2e; color: #8098bf; }
QListWidget { background-color: #111827; border: 1px solid #1a2336; border-radius: 8px; color: #9aafcf; alternate-background-color: #0f1724; outline: none; }
QListWidget::item { padding: 4px 8px; border-bottom: 1px solid #141f30; min-height: 28px; }
QListWidget::item:selected { background-color: #0d1e38; color: #6ba3ff; }
QListWidget::item:hover:!selected { background-color: #131f33; }
""" + SPINBOX_STYLE

EMBEDDED_CHECKBOX_STYLE = """
QCheckBox {
    background-color: transparent;
    color: #5a7099;
    padding: 2px 6px;
    spacing: 5px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #2e4570;
    border-radius: 3px;
    background-color: #0d1219;
}
QCheckBox::indicator:checked {
    background-color: #2d6fff;
    border-color: #4d8fff;
}
QCheckBox::indicator:hover {
    border-color: #4d8fff;
    background-color: #111827;
}
"""

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def rand_str(n):    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))
def rand_token():   return f"EAA{rand_str(8)}ZAAA{rand_str(20)}Bx4xZB{rand_str(10)}"
def rand_cookie():  return f"sb={rand_str(8)}; xs={rand_str(24)}; c_user={random.randint(10**14,10**15-1)}; fr={rand_str(30)}"
def rand_uid():     return str(random.randint(10**14, 10**15 - 1))

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "facebook_accounts.json")

AVATAR_COLORS = [
    ("#1877f2","#4298ff"), ("#8b5cf6","#a78bfa"),
    ("#c43333","#ef4444"), ("#0d9b6e","#10b981"),
    ("#b45309","#f59e0b"), ("#0891b2","#06b6d4"),
]

def make_avatar_pixmap(letter, size=26, idx=0):
    pix = QPixmap(size, size); pix.fill(Qt.transparent)
    p = QPainter(pix); p.setRenderHint(QPainter.Antialiasing)
    c1s, c2s = AVATAR_COLORS[idx % len(AVATAR_COLORS)]
    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0, QColor(c1s)); grad.setColorAt(1, QColor(c2s))
    p.setBrush(QBrush(grad)); p.setPen(Qt.NoPen)
    p.drawRoundedRect(QRectF(0, 0, size, size), size * 0.22, size * 0.22)
    p.setPen(QColor("white")); p.setFont(QFont("Segoe UI", int(size * 0.38), QFont.Bold))
    p.drawText(QRect(0, 0, size, size), Qt.AlignCenter, letter.upper()); p.end()
    return pix

def load_avatar_with_cache(url: str, uid: str, size: int = 24) -> QPixmap:
    import os, requests
    cache_dir = os.path.join(os.path.dirname(__file__), "image")
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"avatar_{uid}.png")
    if os.path.exists(cache_file):
        try:
            pix = QPixmap(cache_file)
            if not pix.isNull():
                return pix.scaledToWidth(size, Qt.SmoothTransformation).copy(0, 0, size, size)
        except Exception: pass
    if not url or not url.strip(): return QPixmap()
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            pix = QPixmap()
            pix.loadFromData(r.content)
            if not pix.isNull():
                try: pix.save(cache_file, "PNG")
                except Exception: pass
                return pix.scaledToWidth(size, Qt.SmoothTransformation).copy(0, 0, size, size)
    except Exception: pass
    return QPixmap()

def load_avatar_from_url(url: str, size: int = 24) -> QPixmap:
    if not url or not url.strip(): return QPixmap()
    try:
        import requests
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            pix = QPixmap()
            pix.loadFromData(r.content)
            if not pix.isNull():
                return pix.scaledToWidth(size, Qt.SmoothTransformation).copy(0, 0, size, size)
    except Exception: pass
    return QPixmap()

def make_embedded_checkbox(label="", checked=False):
    chk = QCheckBox(label)
    chk.setChecked(checked)
    chk.setStyleSheet(EMBEDDED_CHECKBOX_STYLE)
    return chk

def nav_btn(text, active=False, sub=False):
    b = QPushButton(text)
    b.setObjectName("SubNavBtnActive" if (sub and active) else
                    "SubNavBtn" if sub else
                    "NavBtnActive" if active else "NavBtn")
    b.setCursor(QCursor(Qt.PointingHandCursor))
    return b

def make_stat_card(label, value, color_id="blue"):
    card = QFrame(); card.setObjectName("StatCard")
    lay = QVBoxLayout(card); lay.setContentsMargins(14,10,14,10); lay.setSpacing(3)
    lbl = QLabel(label); lbl.setObjectName("StatLabel")
    ids = {"blue":"StatValueBlue","green":"StatValueGreen","red":"StatValueRed","yellow":"StatValueYellow"}
    val = QLabel(value); val.setObjectName(ids.get(color_id,"StatValueBlue"))
    lay.addWidget(lbl); lay.addWidget(val)
    return card, val

def make_search(ph="🔍 Tìm kiếm..."):
    s = QLineEdit(); s.setPlaceholderText(ph); s.setMaximumWidth(220); return s

def hline():
    f = QFrame(); f.setFrameShape(QFrame.HLine)
    f.setStyleSheet("background:#1a2336; max-height:1px; border:none;"); return f

def make_section_header(title, subtitle=""):
    w = QWidget(); w.setStyleSheet("background: transparent;")
    lay = QHBoxLayout(w); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(14)
    dot = QLabel("◈"); dot.setStyleSheet("color: #2d6fff; font-size: 14px; background: transparent;")
    txt_lay = QVBoxLayout(); txt_lay.setSpacing(1)
    t = QLabel(title); t.setStyleSheet("color: #c9d6ea; font-size: 11px; font-weight: 700; font-family: Consolas; letter-spacing: 1px; text-transform: uppercase; background: transparent;")
    txt_lay.addWidget(t)
    if subtitle:
        s = QLabel(subtitle); s.setStyleSheet("color: #2e4570; font-size: 10px; font-family: Consolas; background: transparent;")
        txt_lay.addWidget(s)
    lay.addWidget(dot); lay.addLayout(txt_lay); lay.addStretch()
    return w

def make_spinbox(val=1, mn=1, mx=100, suffix="", step=1):
    """Helper tạo QSpinBox đã áp style mũi tên"""
    s = QSpinBox()
    s.setRange(mn, mx)
    s.setValue(val)
    s.setSingleStep(step)
    if suffix:
        s.setSuffix(f" {suffix}")
    s.setStyleSheet(SPINBOX_STYLE)
    return s

def make_double_spinbox(val=1.0, mn=0.0, mx=100.0, suffix="", step=0.5, decimals=1):
    """Helper tạo QDoubleSpinBox đã áp style mũi tên"""
    s = QDoubleSpinBox()
    s.setRange(mn, mx)
    s.setValue(val)
    s.setSingleStep(step)
    s.setDecimals(decimals)
    if suffix:
        s.setSuffix(f" {suffix}")
    s.setStyleSheet(SPINBOX_STYLE)
    return s

# ═══════════════════════════════════════════════════════════════════════════
#  HƯỚNG DẪN TÍCH HỢP
#  1. Thay toàn bộ class DashboardPage bằng class dưới đây
#  2. Sửa MainWindow: thay placeholder_db bằng DashboardPage(...)
#  3. Sửa navigate mặc định từ "facebook" → "dashboard"
# ═══════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
#  DASHBOARD PAGE — Phiên bản đầy đủ, chuyên nghiệp
# ─────────────────────────────────────────────────────────────────────────────
class DashboardPage(QWidget):
    def __init__(self, facebook_page, ttc_page, tds_page, parent=None):
        super().__init__(parent)
        self._fb  = facebook_page
        self._ttc = ttc_page
        self._tds = tds_page
        self._task_history = []   # lưu lịch sử nhiệm vụ giả lập
        self._last_refresh = QDateTime.currentDateTime()

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        # ── Header ──────────────────────────────────────────────────────────
        hdr = QHBoxLayout(); hdr.setSpacing(14)
        icon = QLabel("⚡"); icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(
            "background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #0d1e38,stop:1 #1a4fd6);"
            "border-radius:12px;color:white;font-size:22px;font-weight:800;"
            "min-width:46px;max-width:46px;min-height:46px;max-height:46px;"
        )
        hdr.addWidget(icon)
        hdr_txt = QVBoxLayout(); hdr_txt.setSpacing(2)
        t1 = QLabel("Dashboard"); t1.setObjectName("PageTitle")
        t2 = QLabel("Tổng quan hệ thống · MMO Tool Pro v3.1")
        t2.setObjectName("PageSub")
        hdr_txt.addWidget(t1); hdr_txt.addWidget(t2)
        hdr.addLayout(hdr_txt); hdr.addStretch()

        self._online_badge = QLabel("● Online")
        self._online_badge.setStyleSheet(
            "color:#10b981;font-size:11px;font-family:Consolas;font-weight:700;"
            "background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);"
            "border-radius:20px;padding:4px 14px;"
        )
        self._refresh_lbl = QLabel("Cập nhật: —")
        self._refresh_lbl.setStyleSheet(
            "color:#2e3f5c;font-size:10px;font-family:Consolas;"
        )
        b_refresh = QPushButton("↻  Làm mới")
        b_refresh.setCursor(QCursor(Qt.PointingHandCursor))
        b_refresh.clicked.connect(self.refresh)
        hdr.addWidget(self._refresh_lbl)
        hdr.addWidget(self._online_badge)
        hdr.addWidget(b_refresh)
        root.addLayout(hdr)
        root.addWidget(hline())

        # ── Stat cards (hàng 1) ──────────────────────────────────────────────
        sr1 = QHBoxLayout(); sr1.setSpacing(10)
        defs1 = [
            ("TỔNG TÀI KHOẢN FB", "_sv_fb",    "blue"),
            ("TOKEN HỢP LỆ",      "_sv_tok",   "green"),
            ("THẤT BẠI LOGIN",    "_sv_fail",  "red"),
            ("TỔNG PAGES",        "_sv_pages", "yellow"),
            ("TTC / TDS",         "_sv_ttcds", "blue"),
        ]
        for lbl, attr, cid in defs1:
            card, val = make_stat_card(lbl, "0", cid)
            setattr(self, attr, val)
            sr1.addWidget(card)
        root.addLayout(sr1)

        # ── Hàng 2: Platform health + Trạng thái hệ thống ───────────────────
        row2 = QHBoxLayout(); row2.setSpacing(10)

        # -- Platform health (trái) --
        plat_box = QGroupBox("TRẠNG THÁI NỀN TẢNG")
        plat_box.setMinimumHeight(160)
        plat_lay = QVBoxLayout(plat_box); plat_lay.setSpacing(10); plat_lay.setContentsMargins(10,16,10,10)
        self._plat_widgets = {}
        for pname, c1, c2, bar_color in [
            ("Facebook",    "#1877f2", "#4298ff", "#2d6fff"),
            ("TTC",         "#0891b2", "#06b6d4", "#06b6d4"),
            ("Traodoisub",  "#0d9b6e", "#10b981", "#00d4aa"),
        ]:
            row = QHBoxLayout(); row.setSpacing(10)
            ico = QLabel(pname[0])
            ico.setAlignment(Qt.AlignCenter)
            ico.setFixedSize(28, 28)
            ico.setStyleSheet(
                f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {c1},stop:1 {c2});"
                f"border-radius:7px;color:white;font-size:13px;font-weight:800;"
            )
            name_lbl = QLabel(pname)
            name_lbl.setStyleSheet("color:#c9d6ea;font-size:12px;font-weight:700;background:transparent;min-width:80px;")
            bar = QProgressBar(); bar.setRange(0,100); bar.setValue(0)
            bar.setTextVisible(False); bar.setFixedHeight(6)
            bar.setStyleSheet(
                f"QProgressBar{{background:#0d1219;border:none;border-radius:3px;}}"
                f"QProgressBar::chunk{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"stop:0 {c1},stop:1 {c2});border-radius:3px;}}"
            )
            pct = QLabel("0%")
            pct.setStyleSheet(f"color:{bar_color};font-size:11px;font-weight:800;font-family:Consolas;background:transparent;min-width:36px;")
            pct.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            cnt = QLabel("0 TK")
            cnt.setStyleSheet("color:#3d5278;font-size:10px;font-family:Consolas;background:transparent;min-width:40px;")
            cnt.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.addWidget(ico); row.addWidget(name_lbl); row.addWidget(bar, 1)
            row.addWidget(pct); row.addWidget(cnt)
            plat_lay.addLayout(row)
            self._plat_widgets[pname] = (bar, pct, cnt)
        row2.addWidget(plat_box, 3)

        # -- Trạng thái hệ thống (phải) --
        sys_box = QGroupBox("TRẠNG THÁI HỆ THỐNG")
        sys_box.setMinimumHeight(160)
        sys_lay = QVBoxLayout(sys_box); sys_lay.setSpacing(8); sys_lay.setContentsMargins(10,16,10,10)
        self._sys_widgets = {}
        sys_defs = [
            ("Luồng đang chạy", "_sys_threads", "0 / 0",  "#4d8fff"),
            ("Login hàng đợi",  "_sys_queue",   "0",      "#f59e0b"),
            ("Request OK",      "_sys_req_ok",  "0%",     "#00d4aa"),
            ("Proxy hoạt động", "_sys_proxy",   "0%",     "#a78bfa"),
            ("Xu TTC tích lũy", "_sys_xu_ttc",  "0",      "#f59e0b"),
            ("Xu TDS tích lũy", "_sys_xu_tds",  "0",      "#06b6d4"),
        ]
        for lbl, attr, default, color in sys_defs:
            row = QHBoxLayout(); row.setSpacing(8)
            l = QLabel(lbl); l.setStyleSheet("color:#5a7099;font-size:11px;background:transparent;")
            v = QLabel(default)
            v.setStyleSheet(f"color:{color};font-size:11px;font-weight:800;font-family:Consolas;background:transparent;")
            v.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            setattr(self, attr, v)
            row.addWidget(l); row.addWidget(v)
            sys_lay.addLayout(row)
        row2.addWidget(sys_box, 2)
        root.addLayout(row2)

        # ── Hàng 3: Nhiệm vụ gần đây + Tài khoản mới nhất ──────────────────
        row3 = QHBoxLayout(); row3.setSpacing(10)

        # -- Nhiệm vụ gần đây (trái) --
        task_box = QGroupBox("NHIỆM VỤ GẦN ĐÂY")
        task_lay = QVBoxLayout(task_box); task_lay.setContentsMargins(8,14,8,8); task_lay.setSpacing(0)
        self._task_tree = QTreeWidget()
        self._task_tree.setObjectName("FbTree")
        self._task_tree.setColumnCount(5)
        self._task_tree.setHeaderLabels(["Nhiệm vụ", "Nền tảng", "TK", "Số lần", "Trạng thái"])
        self._task_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self._task_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._task_tree.header().setSectionResizeMode(2, QHeaderView.Interactive)
        self._task_tree.header().resizeSection(2, 120)
        self._task_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._task_tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self._task_tree.setIndentation(0)
        self._task_tree.setMaximumHeight(160)
        task_lay.addWidget(self._task_tree)
        row3.addWidget(task_box, 3)

        # -- Tài khoản mới nhất (phải) --
        acc_box = QGroupBox("TÀI KHOẢN MỚI NHẤT")
        acc_lay = QVBoxLayout(acc_box); acc_lay.setContentsMargins(8,14,8,8); acc_lay.setSpacing(0)
        self._acc_tree = QTreeWidget()
        self._acc_tree.setObjectName("FbTree")
        self._acc_tree.setColumnCount(3)
        self._acc_tree.setHeaderLabels(["Tên", "UID", "Trạng thái"])
        self._acc_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self._acc_tree.header().setSectionResizeMode(1, QHeaderView.Interactive)
        self._acc_tree.header().resizeSection(1, 130)
        self._acc_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._acc_tree.setIndentation(0)
        self._acc_tree.setMaximumHeight(160)
        acc_lay.addWidget(self._acc_tree)
        row3.addWidget(acc_box, 2)
        root.addLayout(row3)

        # ── Hàng 4: Xu thống kê + Tỷ lệ login mini-bars ────────────────────
        row4 = QHBoxLayout(); row4.setSpacing(10)

        # -- Xu thống kê (trái) --
        xu_box = QGroupBox("THỐNG KÊ XU TÍCH LŨY")
        xu_lay = QVBoxLayout(xu_box); xu_lay.setContentsMargins(10,16,10,10); xu_lay.setSpacing(10)
        self._xu_widgets = {}
        for label, attr, color in [
            ("TTC — Tổng xu",       "_xu_ttc_total",  "#f59e0b"),
            ("TDS — Tổng xu",       "_xu_tds_total",  "#06b6d4"),
            ("TTC — Trung bình/TK", "_xu_ttc_avg",    "#a78bfa"),
            ("TDS — Trung bình/TK", "_xu_tds_avg",    "#4d8fff"),
        ]:
            r = QHBoxLayout(); r.setSpacing(8)
            dot = QLabel("◆"); dot.setStyleSheet(f"color:{color};font-size:10px;background:transparent;")
            lbl = QLabel(label); lbl.setStyleSheet("color:#5a7099;font-size:11px;background:transparent;")
            val = QLabel("0"); val.setStyleSheet(f"color:{color};font-size:13px;font-weight:800;font-family:Consolas;background:transparent;")
            val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            setattr(self, attr, val)
            r.addWidget(dot); r.addWidget(lbl); r.addWidget(val)
            xu_lay.addLayout(r)
        row4.addWidget(xu_box, 1)

        # -- Tỷ lệ chi tiết (giữa) --
        rate_box = QGroupBox("TỶ LỆ THÀNH CÔNG")
        rate_lay = QVBoxLayout(rate_box); rate_lay.setContentsMargins(10,16,10,10); rate_lay.setSpacing(10)
        self._rate_widgets = {}
        for label, attr, color in [
            ("Login Facebook",    "_rate_fb_login",  "#2d6fff"),
            ("Lấy Token",         "_rate_fb_token",  "#00d4aa"),
            ("Lấy Pages",         "_rate_fb_pages",  "#f59e0b"),
            ("TTC Task hoàn thành","_rate_ttc",      "#06b6d4"),
        ]:
            r = QHBoxLayout(); r.setSpacing(8)
            lbl = QLabel(label); lbl.setStyleSheet("color:#5a7099;font-size:11px;background:transparent;min-width:120px;")
            bar = QProgressBar(); bar.setRange(0,100); bar.setValue(0)
            bar.setTextVisible(False); bar.setFixedHeight(5)
            bar.setStyleSheet(
                f"QProgressBar{{background:#0d1219;border:none;border-radius:3px;}}"
                f"QProgressBar::chunk{{background:{color};border-radius:3px;}}"
            )
            pct = QLabel("0%"); pct.setStyleSheet(f"color:{color};font-size:10px;font-weight:800;font-family:Consolas;background:transparent;min-width:32px;")
            pct.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            setattr(self, attr + "_bar", bar)
            setattr(self, attr + "_pct", pct)
            r.addWidget(lbl); r.addWidget(bar, 1); r.addWidget(pct)
            rate_lay.addLayout(r)
        row4.addWidget(rate_box, 2)

        # -- Thống kê nhóm (phải) --
        grp_box = QGroupBox("THỐNG KÊ NHÓM TÀI KHOẢN")
        grp_lay = QVBoxLayout(grp_box); grp_lay.setContentsMargins(10,16,10,10); grp_lay.setSpacing(0)
        self._grp_tree = QTreeWidget()
        self._grp_tree.setObjectName("FbTree")
        self._grp_tree.setColumnCount(4)
        self._grp_tree.setHeaderLabels(["Nhóm", "Tổng", "OK", "Pages"])
        self._grp_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1,4): self._grp_tree.header().setSectionResizeMode(c, QHeaderView.ResizeToContents)
        self._grp_tree.setIndentation(0)
        grp_lay.addWidget(self._grp_tree)
        row4.addWidget(grp_box, 2)
        root.addLayout(row4)

        # ── Timer tự refresh ─────────────────────────────────────────────────
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(15000)  # 15 giây auto-refresh

        self.refresh()

    # ─── Refresh toàn bộ dashboard ──────────────────────────────────────────
    def refresh(self):
        self._last_refresh = QDateTime.currentDateTime()
        self._refresh_lbl.setText(f"Cập nhật: {self._last_refresh.toString('hh:mm:ss')}")

        # ── Đọc dữ liệu FB ──
        all_uids  = []
        for g, gdata in self._fb._groups.items():
            all_uids.extend(gdata.get("accounts", []))
        all_uids = list(dict.fromkeys(all_uids))  # dedup

        total_fb  = len(all_uids)
        ok_fb     = sum(1 for u in all_uids if self._fb._acc_data.get(u,{}).get("token",""))
        fail_fb   = total_fb - ok_fb
        total_pages = sum(len(self._fb._acc_data.get(u,{}).get("pages",[])) for u in all_uids)
        ttc_n     = len(self._ttc._ttc_data)
        tds_n     = len(self._tds._tds_data)

        # ── Stat cards ──
        self._sv_fb.setText(str(total_fb))
        self._sv_tok.setText(str(ok_fb))
        self._sv_fail.setText(str(fail_fb))
        self._sv_pages.setText(str(total_pages))
        self._sv_ttcds.setText(f"{ttc_n}/{tds_n}")

        # ── Platform health ──
        fb_pct = int(ok_fb / total_fb * 100) if total_fb else 0
        ttc_active = sum(1 for d in self._ttc._ttc_data.values() if d.get("token",""))
        tds_active = sum(1 for d in self._tds._tds_data.values() if d.get("token",""))
        ttc_pct = int(ttc_active / ttc_n * 100) if ttc_n else 0
        tds_pct = int(tds_active / tds_n * 100) if tds_n else 0

        for pname, pct_val, cnt_val in [
            ("Facebook",   fb_pct,  f"{total_fb} TK"),
            ("TTC",        ttc_pct, f"{ttc_n} TK"),
            ("Traodoisub", tds_pct, f"{tds_n} TK"),
        ]:
            bar, pct_lbl, cnt_lbl = self._plat_widgets[pname]
            bar.setValue(pct_val)
            pct_lbl.setText(f"{pct_val}%")
            cnt_lbl.setText(cnt_val)

        # ── System status ──
        self._sys_threads.setText("0 / 0")
        self._sys_queue.setText("0")
        req_ok = fb_pct
        self._sys_req_ok.setText(f"{req_ok}%")
        self._sys_proxy.setText("—")
        xu_ttc_total = sum(d.get("xu", 0) for d in self._ttc._ttc_data.values())
        xu_tds_total = sum(d.get("xu", 0) for d in self._tds._tds_data.values())
        self._sys_xu_ttc.setText(str(xu_ttc_total))
        self._sys_xu_tds.setText(str(xu_tds_total))

        # ── Xu stats ──
        self._xu_ttc_total.setText(str(xu_ttc_total))
        self._xu_tds_total.setText(str(xu_tds_total))
        avg_ttc = int(xu_ttc_total / ttc_n) if ttc_n else 0
        avg_tds = int(xu_tds_total / tds_n) if tds_n else 0
        self._xu_ttc_avg.setText(str(avg_ttc))
        self._xu_tds_avg.setText(str(avg_tds))

        # ── Tỷ lệ ──
        for attr_base, val in [
            ("_rate_fb_login", fb_pct),
            ("_rate_fb_token", fb_pct),
            ("_rate_fb_pages", int(total_pages / total_fb * 20) if total_fb else 0),
            ("_rate_ttc",      ttc_pct),
        ]:
            bar = getattr(self, attr_base + "_bar", None)
            pct = getattr(self, attr_base + "_pct", None)
            if bar: bar.setValue(min(val, 100))
            if pct: pct.setText(f"{min(val,100)}%")

        # ── Tài khoản mới nhất (5 TK gần thêm) ──
        self._acc_tree.clear()
        shown = 0
        for uid in reversed(all_uids):
            if shown >= 8: break
            acc = self._fb._acc_data.get(uid, {})
            it = QTreeWidgetItem()
            it.setText(0, acc.get("name", uid)[:22])
            it.setText(1, uid[:18])
            has_token = bool(acc.get("token",""))
            it.setText(2, "✔ OK" if has_token else "✘ Chưa")
            it.setForeground(0, QColor("#d0d8e8"))
            it.setForeground(1, QColor("#4d8fff"))
            it.setForeground(2, QColor("#10b981") if has_token else QColor("#ef4444"))
            self._acc_tree.addTopLevelItem(it)
            shown += 1

        # ── Nhiệm vụ gần đây (giả lập nếu chưa có log thực) ──
        self._task_tree.clear()
        demo_tasks = [
            ("Like VIP",   "TTC",  "—", "0", "idle"),
            ("Theo Dõi",   "TDS",  "—", "0", "idle"),
            ("Share Post", "TTC",  "—", "0", "idle"),
            ("Bình Luận",  "TTC",  "—", "0", "idle"),
        ]
        for tname, plat, acc, cnt, status in demo_tasks:
            it = QTreeWidgetItem()
            it.setText(0, tname); it.setText(1, plat)
            it.setText(2, acc);   it.setText(3, cnt)
            status_map = {
                "ok":   ("✔ Xong",     "#10b981"),
                "run":  ("⏳ Đang chạy","#f59e0b"),
                "err":  ("✘ Lỗi",      "#ef4444"),
                "idle": ("— Chờ",      "#3d5278"),
            }
            stxt, sclr = status_map.get(status, ("—", "#3d5278"))
            it.setText(4, stxt)
            plat_clr = {"TTC":"#06b6d4","TDS":"#10b981","FB":"#4d8fff"}.get(plat,"#9aafcf")
            it.setForeground(0, QColor("#c9d6ea"))
            it.setForeground(1, QColor(plat_clr))
            it.setForeground(2, QColor("#5a7099"))
            it.setForeground(3, QColor("#9aafcf"))
            it.setForeground(4, QColor(sclr))
            self._task_tree.addTopLevelItem(it)

        # ── Thống kê nhóm ──
        self._grp_tree.clear()
        for grp_name, gdata in sorted(self._fb._groups.items()):
            uids_g = gdata.get("accounts", [])
            ok_g   = sum(1 for u in uids_g if self._fb._acc_data.get(u,{}).get("token",""))
            pages_g= sum(len(self._fb._acc_data.get(u,{}).get("pages",[])) for u in uids_g)
            it = QTreeWidgetItem()
            it.setText(0, grp_name); it.setText(1, str(len(uids_g)))
            it.setText(2, str(ok_g)); it.setText(3, str(pages_g))
            it.setForeground(0, QColor("#c9d6ea"))
            it.setForeground(1, QColor("#4d8fff"))
            it.setForeground(2, QColor("#10b981") if ok_g else QColor("#3d5278"))
            it.setForeground(3, QColor("#f59e0b"))
            self._grp_tree.addTopLevelItem(it)

    def add_task_log(self, task_name: str, platform: str, account: str, count: int, status: str):
        """Gọi từ các trang chạy để cập nhật nhiệm vụ gần đây."""
        self._task_history.insert(0, (task_name, platform, account, str(count), status))
        self._task_history = self._task_history[:20]
        self._task_tree.clear()
        for tname, plat, acc, cnt, st in self._task_history[:8]:
            it = QTreeWidgetItem()
            it.setText(0, tname); it.setText(1, plat)
            it.setText(2, acc[:18]); it.setText(3, cnt)
            status_map = {
                "ok":   ("✔ Xong",      "#10b981"),
                "run":  ("⏳ Đang chạy","#f59e0b"),
                "err":  ("✘ Lỗi",       "#ef4444"),
                "idle": ("— Chờ",       "#3d5278"),
            }
            stxt, sclr = status_map.get(st, (st, "#9aafcf"))
            it.setText(4, stxt)
            plat_clr = {"TTC":"#06b6d4","TDS":"#10b981","FB":"#4d8fff"}.get(plat,"#9aafcf")
            it.setForeground(0, QColor("#c9d6ea")); it.setForeground(1, QColor(plat_clr))
            it.setForeground(2, QColor("#5a7099")); it.setForeground(3, QColor("#9aafcf"))
            it.setForeground(4, QColor(sclr))
            self._task_tree.addTopLevelItem(it)


# ─────────────────────────────────────────────
#  LOGIN WORKER
# ─────────────────────────────────────────────
class LoginWorker(QThread):
    done    = pyqtSignal(str, dict)
    log_msg = pyqtSignal(str)

    def __init__(self, uid: str, acc_data: dict, parent=None):
        super().__init__(parent)
        self.uid      = uid
        self.acc_data = acc_data

    def run(self):
        from source.get_page import FacebookGetToken
        mail   = self.acc_data.get("mail",  "")
        passw  = self.acc_data.get("pass",  "")
        fa     = self.acc_data.get("2fa",   "")
        proxy  = self.acc_data.get("proxy", None)
        proxy_dict = None
        if proxy and proxy.strip():
            p = proxy.strip()
            if not p.startswith("http"): p = "http://" + p
            proxy_dict = {"http": p, "https": p}
        self.log_msg.emit(f"[→] Đang login: {mail or self.uid}")
        try:
            fb  = FacebookGetToken(mail or self.uid, passw, auth=fa, proxy=proxy_dict)
            res = fb.login()
            if res.get("ok"):
                self.log_msg.emit(f"[✔] OK: {mail} — {len(res.get('pages',[]))} pages")
            else:
                self.log_msg.emit(f"[✘] FAIL: {mail} — {res.get('msg','')}")
            self.done.emit(self.uid, res)
        except Exception as e:
            self.log_msg.emit(f"[✘] Exception: {mail} — {e}")
            self.done.emit(self.uid, {"ok": False, "msg": str(e)})


class LoginBatchManager(QObject):
    all_done = pyqtSignal()
    log_msg  = pyqtSignal(str)
    one_done = pyqtSignal(str, dict)

    def __init__(self, acc_list: list, max_threads: int = 5, parent=None):
        super().__init__(parent)
        self._queue      = list(acc_list)
        self._max        = max_threads
        self._active     = {}
        self._done_count = 0
        self._total      = len(acc_list)

    def start(self):
        self._fill()

    def _fill(self):
        while self._queue and len(self._active) < self._max:
            uid, acc = self._queue.pop(0)
            w = LoginWorker(uid, acc)
            w.done.connect(self._on_done)
            w.log_msg.connect(self.log_msg)
            self._active[uid] = w
            w.start()

    def _on_done(self, uid, result):
        w = self._active.pop(uid, None)
        if w: w.quit(); w.wait()
        self._done_count += 1
        self.one_done.emit(uid, result)
        self._fill()
        if not self._active and not self._queue:
            self.all_done.emit()

    def cleanup(self):
        for w in list(self._active.values()):
            w.quit(); w.wait()
        self._active.clear(); self._queue.clear()


# ─────────────────────────────────────────────
#  ADD ACCOUNT DIALOG
# ─────────────────────────────────────────────
class AddAccountDialog(QDialog):
    def __init__(self, mode="single", parent=None):
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle("Thêm tài khoản Facebook")
        self.setMinimumWidth(480)
        self.setStyleSheet(STYLE)
        lay = QVBoxLayout(self); lay.setContentsMargins(20,16,20,16); lay.setSpacing(12)
        t = QLabel("➕  Thêm tài khoản Facebook")
        t.setStyleSheet("color:#e8edf5;font-size:15px;font-weight:800;"); lay.addWidget(t)

        if mode == "single":
            form = QFormLayout(); form.setSpacing(10); form.setLabelAlignment(Qt.AlignRight)
            self.uid_in  = QLineEdit(); self.uid_in.setPlaceholderText("UID hoặc email@example.com")
            self.pass_in = QLineEdit(); self.pass_in.setPlaceholderText("Mật khẩu")
            self.pass_in.setEchoMode(QLineEdit.Password)
            self.fa_in   = QLineEdit(); self.fa_in.setPlaceholderText("Secret 2FA (tuỳ chọn)")
            self.proxy_in= QLineEdit(); self.proxy_in.setPlaceholderText("ip:port hoặc user:pass@ip:port (tuỳ chọn)")
            form.addRow("🆔  UID/Email:", self.uid_in)
            form.addRow("🔒  Pass:",      self.pass_in)
            form.addRow("🔐  2FA:",       self.fa_in)
            form.addRow("🌐  Proxy:",     self.proxy_in)
            lay.addLayout(form)
        else:
            hint = QLabel("Mỗi dòng:   uid|pass|2fa   hoặc   uid|pass|2fa|proxy\n(2fa và proxy có thể bỏ trống — vẫn cần dấu |)")
            hint.setStyleSheet("color:#3d5278;font-size:11px;font-family:Consolas;")
            lay.addWidget(hint)
            self.bulk_edit = QTextEdit()
            self.bulk_edit.setPlaceholderText(
                "100001234567890|pass123|JBSWY3DP|192.168.1.1:8080\n"
                "user@gmail.com|pass456||proxy.example.com:3128\n"
                "100009876543210|pass789||"
            )
            self.bulk_edit.setMinimumHeight(180); lay.addWidget(self.bulk_edit)

        btns = QHBoxLayout(); btns.addStretch()
        cancel = QPushButton("Huỷ"); cancel.setCursor(QCursor(Qt.PointingHandCursor)); cancel.clicked.connect(self.reject)
        ok = QPushButton("✔  Xác nhận"); ok.setObjectName("btnPrimary")
        ok.setCursor(QCursor(Qt.PointingHandCursor)); ok.setMinimumWidth(110); ok.clicked.connect(self._ok)
        btns.addWidget(cancel); btns.addWidget(ok); lay.addLayout(btns)

    def _ok(self):
        r = self._parse()
        if not r:
            QMessageBox.warning(self, "Lỗi", "Nhập ít nhất 1 tài khoản hợp lệ."); return
        self._result = r; self.accept()

    def _parse(self):
        out = []
        if self.mode == "single":
            uid   = self.uid_in.text().strip()
            passw = self.pass_in.text().strip()
            fa    = self.fa_in.text().strip()
            proxy = self.proxy_in.text().strip()
            if uid and passw:
                out.append({"mail": uid, "pass": passw, "2fa": fa, "proxy": proxy})
        else:
            for line in self.bulk_edit.toPlainText().splitlines():
                parts = [p.strip() for p in line.strip().split("|")]
                if len(parts) >= 2 and parts[0] and parts[1]:
                    out.append({
                        "mail":  parts[0],
                        "pass":  parts[1],
                        "2fa":   parts[2] if len(parts) > 2 else "",
                        "proxy": parts[3] if len(parts) > 3 else "",
                    })
        return out

    def get_accounts(self): return getattr(self, "_result", [])


# ─────────────────────────────────────────────
#  PROXY DIALOG
# ─────────────────────────────────────────────
class ProxyDialog(QDialog):
    def __init__(self, count: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm Proxy")
        self.setMinimumWidth(440); self.setStyleSheet(STYLE)
        lay = QVBoxLayout(self); lay.setContentsMargins(20,16,20,16); lay.setSpacing(12)
        lbl = QLabel(f"🌐  Gán proxy cho {count} tài khoản đã chọn")
        lbl.setStyleSheet("color:#e8edf5;font-size:14px;font-weight:800;"); lay.addWidget(lbl)
        tabs = QTabWidget(); lay.addWidget(tabs)
        w1 = QWidget(); f1 = QFormLayout(w1); f1.setSpacing(10); f1.setLabelAlignment(Qt.AlignRight)
        self.single_proxy = QLineEdit(); self.single_proxy.setPlaceholderText("ip:port hoặc user:pass@ip:port")
        f1.addRow("Proxy:", self.single_proxy); tabs.addTab(w1, "📌 Proxy chung")
        w2 = QWidget(); f2 = QVBoxLayout(w2); f2.setSpacing(8)
        hint2 = QLabel(f"Mỗi dòng 1 proxy — tổng cần {count} dòng (không đủ thì xoay vòng)")
        hint2.setStyleSheet("color:#3d5278;font-size:11px;font-family:Consolas;")
        f2.addWidget(hint2)
        self.multi_proxy = QTextEdit()
        self.multi_proxy.setPlaceholderText("proxy1.example.com:3128\nuser:pass@proxy2.example.com:8080\n...")
        f2.addWidget(self.multi_proxy); tabs.addTab(w2, "📋 Proxy theo dòng")
        self._tabs = tabs
        btns = QHBoxLayout(); btns.addStretch()
        cancel = QPushButton("Huỷ"); cancel.clicked.connect(self.reject)
        ok = QPushButton("✔  Gán Proxy"); ok.setObjectName("btnPrimary")
        ok.setCursor(QCursor(Qt.PointingHandCursor)); ok.clicked.connect(self.accept)
        btns.addWidget(cancel); btns.addWidget(ok); lay.addLayout(btns)

    def get_proxies(self, count: int) -> list:
        if self._tabs.currentIndex() == 0:
            p = self.single_proxy.text().strip()
            return [p] * count
        else:
            lines = [l.strip() for l in self.multi_proxy.toPlainText().splitlines() if l.strip()]
            if not lines: return [""] * count
            return [lines[i % len(lines)] for i in range(count)]


# ─────────────────────────────────────────────
#  DETAIL PANEL
# ─────────────────────────────────────────────
class DetailPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DetailPanel")
        self.setStyleSheet("#DetailPanel{background:#0d1219;border-left:1px solid #1a2336;}")
        self.setMinimumWidth(290); self.setMaximumWidth(320)
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)
        hdr = QFrame(); hdr.setStyleSheet("background:#0d1219;border-bottom:1px solid #1a2336;"); hdr.setFixedHeight(40)
        hl = QHBoxLayout(hdr); hl.setContentsMargins(14,0,14,0)
        self._hdr_lbl = QLabel("Chi tiết")
        self._hdr_lbl.setStyleSheet("color:#3d5278;font-size:10px;font-family:Consolas;font-weight:700;letter-spacing:2px;text-transform:uppercase;")
        hl.addWidget(self._hdr_lbl); outer.addWidget(hdr)
        self._scroll = QScrollArea(); self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setStyleSheet("QScrollArea{background:#0d1219;border:none;}")
        self._body_w = QWidget(); self._body_w.setStyleSheet("background:#0d1219;")
        self._body = QVBoxLayout(self._body_w); self._body.setContentsMargins(14,12,14,12)
        self._body.setSpacing(8); self._body.setAlignment(Qt.AlignTop)
        self._scroll.setWidget(self._body_w); outer.addWidget(self._scroll, 1)
        self._show_empty()

    def _clear(self):
        while self._body.count():
            it = self._body.takeAt(0)
            if it.widget(): it.widget().deleteLater()

    def _show_empty(self):
        self._clear(); self._hdr_lbl.setText("Chi tiết")
        lbl = QLabel("📋\n\nChọn tài khoản\nhoặc page")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color:#1e2e45;font-size:12px;font-family:Consolas;line-height:2;")
        self._body.addStretch(); self._body.addWidget(lbl); self._body.addStretch()

    def _avatar_from_url(self, url: str, fallback_letter: str, fallback_idx: int, uid: str = ""):
        av = QLabel(); av.setFixedSize(42, 42); av.setAlignment(Qt.AlignCenter)
        if url:
            avatar_pix = load_avatar_with_cache(url, uid, 42) if uid else load_avatar_from_url(url, 42)
            if not avatar_pix.isNull():
                av.setPixmap(avatar_pix); av.setStyleSheet("border-radius:10px;"); return av
        c1, c2 = AVATAR_COLORS[fallback_idx % len(AVATAR_COLORS)]
        av.setText(fallback_letter.upper())
        av.setStyleSheet(f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {c1},stop:1 {c2});border-radius:10px;color:white;font-size:17px;font-weight:800;")
        return av

    def _tag(self, text, color):
        l = QLabel(text); c = QColor(color)
        l.setStyleSheet(f"color:{color};font-size:10px;font-family:Consolas;font-weight:700;"
                        f"background:rgba({c.red()},{c.green()},{c.blue()},30);"
                        f"border:1px solid rgba({c.red()},{c.green()},{c.blue()},64);"
                        f"border-radius:4px;padding:1px 6px;")
        return l

    def _field(self, label, value, color="#5a7099"):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(3)
        lbl = QLabel(label)
        lbl.setStyleSheet("color:#1e2e45;font-size:9px;font-family:Consolas;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;")
        val = QLabel(str(value)); val.setWordWrap(True)
        val.setTextInteractionFlags(Qt.TextSelectableByMouse)
        val.setCursor(QCursor(Qt.IBeamCursor))
        val.setStyleSheet(f"background:#111827;border:1px solid #1a2336;border-radius:6px;color:{color};font-size:11px;font-family:Consolas;padding:5px 8px;")
        vl.addWidget(lbl); vl.addWidget(val)
        return w

    def clear(self): self._show_empty()

    def show_account(self, data):
        self._clear(); self._hdr_lbl.setText("TÀI KHOẢN")
        idx = sum(ord(c) for c in data.get("name","x")) % len(AVATAR_COLORS)
        top = QHBoxLayout(); top.setSpacing(10)
        top.addWidget(self._avatar_from_url(data.get("avatar",""), data.get("letter","?"), idx, data.get("uid","")))
        rc = QVBoxLayout(); rc.setSpacing(5)
        n = QLabel(data.get("name","")); n.setStyleSheet("color:#e0e6f0;font-size:13px;font-weight:800;"); n.setWordWrap(True)
        tags = QHBoxLayout(); tags.setSpacing(5)
        has_token = bool(data.get("token",""))
        tags.addWidget(self._tag("✔ Active" if has_token else "✘ Chưa login", "#10b981" if has_token else "#ef4444"))
        tags.addWidget(self._tag(f"📄 {len(data.get('pages',[]))} Pages","#ff8c5a"))
        tags.addStretch()
        rc.addWidget(n); rc.addLayout(tags); top.addLayout(rc, 1)
        top_w = QWidget(); top_w.setStyleSheet("background:transparent;"); top_w.setLayout(top)
        self._body.addWidget(top_w); self._body.addWidget(hline())
        self._body.addWidget(self._field("UID",    data.get("uid",""),    "#4d8fff"))
        self._body.addWidget(self._field("EMAIL/UID",  data.get("mail",""),   "#9aafcf"))
        self._body.addWidget(self._field("PASS",   data.get("pass",""),   "#9aafcf"))
        self._body.addWidget(self._field("2FA",    data.get("2fa","") or "(trống)", "#9aafcf"))
        self._body.addWidget(self._field("PROXY",  data.get("proxy","") or "(không có)", "#8b5cf6"))
        self._body.addWidget(self._field("TOKEN",  data.get("token","") or "(chưa login)",  "#00d4aa"))
        self._body.addWidget(self._field("COOKIE", data.get("cookie","") or "(chưa login)", "#00d4aa"))
        self._body.addStretch()

    def show_page(self, page, parent_name):
        self._clear(); self._hdr_lbl.setText("PAGE")
        top = QHBoxLayout(); top.setSpacing(10)
        page_avatar_url = page.get("avatar", "")
        if page_avatar_url:
            page_avatar_pix = load_avatar_with_cache(page_avatar_url, page.get("uid",""), 42)
            if not page_avatar_pix.isNull():
                av = QLabel(); av.setPixmap(page_avatar_pix); av.setFixedSize(42, 42); av.setStyleSheet("border-radius:10px;")
            else:
                av = QLabel("P"); av.setFixedSize(42,42); av.setAlignment(Qt.AlignCenter)
                av.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ff6b35,stop:1 #ff8c5a);border-radius:10px;color:white;font-size:17px;font-weight:800;")
        else:
            av = QLabel("P"); av.setFixedSize(42,42); av.setAlignment(Qt.AlignCenter)
            av.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ff6b35,stop:1 #ff8c5a);border-radius:10px;color:white;font-size:17px;font-weight:800;")
        top.addWidget(av)
        rc = QVBoxLayout(); rc.setSpacing(5)
        n = QLabel(page.get("name","")); n.setStyleSheet("color:#e0e6f0;font-size:13px;font-weight:800;"); n.setWordWrap(True)
        sub = QLabel(f"↳ {parent_name}"); sub.setStyleSheet("color:#3d5278;font-size:10px;font-family:Consolas;")
        tags = QHBoxLayout(); tags.setSpacing(5)
        tags.addWidget(self._tag(page.get("role","ADMIN"), "#f59e0b"))
        tags.addWidget(self._tag(f"👥 {page.get('fans',0):,}", "#a78bfa"))
        tags.addStretch()
        rc.addWidget(n); rc.addWidget(sub); rc.addLayout(tags); top.addLayout(rc, 1)
        top_w = QWidget(); top_w.setStyleSheet("background:transparent;"); top_w.setLayout(top)
        self._body.addWidget(top_w); self._body.addWidget(hline())
        self._body.addWidget(self._field("PAGE UID", page.get("uid",""),    "#ff8c5a"))
        self._body.addWidget(self._field("TOKEN",    page.get("token",""),  "#00d4aa"))
        self._body.addWidget(self._field("COOKIE",   page.get("cookie",""), "#00d4aa"))
        self._body.addStretch()

    def show_multi(self, count):
        self._clear(); self._hdr_lbl.setText("ĐÃ CHỌN")
        lbl = QLabel(f"✔  {count} mục được chọn"); lbl.setStyleSheet("color:#6ba3ff;font-size:13px;font-weight:700;")
        hint = QLabel("Chuột phải để thao tác hàng loạt"); hint.setStyleSheet("color:#2e3f5c;font-size:11px;font-family:Consolas;")
        self._body.addSpacing(16); self._body.addWidget(lbl); self._body.addWidget(hint); self._body.addStretch()


# ─────────────────────────────────────────────
#  LOG PANEL
# ─────────────────────────────────────────────
class LogPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#050810;border:1px solid #1a2336;border-radius:8px;")
        self.setMaximumHeight(160)
        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
        hdr = QFrame(); hdr.setStyleSheet("background:#0d1219;border-bottom:1px solid #1a2336;border-radius:8px 8px 0 0;"); hdr.setFixedHeight(30)
        hl = QHBoxLayout(hdr); hl.setContentsMargins(10,0,10,0)
        lbl = QLabel("📡  Login Log"); lbl.setStyleSheet("color:#3d5278;font-size:10px;font-family:Consolas;font-weight:700;")
        hl.addWidget(lbl); hl.addStretch()
        self._clr_btn = QPushButton("Xoá"); self._clr_btn.setMaximumWidth(50)
        self._clr_btn.setStyleSheet("background:transparent;border:none;color:#3d5278;font-size:11px;")
        self._clr_btn.clicked.connect(self.clear)
        hl.addWidget(self._clr_btn); lay.addWidget(hdr)
        self._log = QPlainTextEdit(); self._log.setReadOnly(True)
        self._log.setStyleSheet("background:#050810;border:none;color:#00d4aa;font-family:Consolas;font-size:11px;padding:6px;")
        lay.addWidget(self._log, 1)

    def append(self, msg: str):
        ts = QDateTime.currentDateTime().toString("hh:mm:ss")
        self._log.appendPlainText(f"[{ts}] {msg}")
        sb = self._log.verticalScrollBar(); sb.setValue(sb.maximum())

    def clear(self): self._log.clear()


COL_NAME   = 0
COL_UID    = 1
COL_PASS   = 2
COL_PROXY  = 3
COL_COOKIE = 4
COL_TOKEN  = 5
COL_TYPE   = 6


# ─────────────────────────────────────────────────────────────────────────────
#  FACEBOOK PAGE
# ─────────────────────────────────────────────────────────────────────────────
class FacebookPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._acc_data         = {}
        self._page_data        = {}
        self._uid_to_item      = {}
        self._page_uid_to_item = {}
        self._groups           = {}
        self._current_group    = "Default"
        self._block_check_sync = False
        self._data_file        = DATA_FILE
        self._batch_mgr        = None
        self._login_progress   = {}

        root_lay = QVBoxLayout(self); root_lay.setContentsMargins(20,16,20,16); root_lay.setSpacing(0)

        hdr = QHBoxLayout(); hdr.setSpacing(14)
        icon = QLabel("𝕗"); icon.setObjectName("PageIconFb"); icon.setAlignment(Qt.AlignCenter)
        hdr.addWidget(icon)
        hdr_text = QVBoxLayout(); hdr_text.setSpacing(2)
        t1 = QLabel("Facebook"); t1.setObjectName("PageTitle")
        t2 = QLabel("Quản lý tài khoản & token Facebook"); t2.setObjectName("PageSub")
        hdr_text.addWidget(t1); hdr_text.addWidget(t2)
        hdr.addLayout(hdr_text); hdr.addStretch()
        b_add = QPushButton("＋  Thêm tài khoản"); b_add.setObjectName("btnPrimary")
        b_add.setCursor(QCursor(Qt.PointingHandCursor)); b_add.clicked.connect(self._add_single)
        b_login = QPushButton("🔑  Login Chọn"); b_login.setObjectName("btnLogin")
        b_login.setCursor(QCursor(Qt.PointingHandCursor)); b_login.clicked.connect(self._login_selected_toolbar)
        hdr.addWidget(b_login); hdr.addWidget(b_add)
        root_lay.addLayout(hdr); root_lay.addSpacing(14)

        sr = QHBoxLayout(); sr.setSpacing(10)
        for lbl, attr, clr in [("TỔNG TÀI KHOẢN","_stat_total","blue"),
                                ("TỔNG PAGES",    "_stat_pages","yellow"),
                                ("CÓ TOKEN",      "_stat_ok",   "green"),
                                ("KHÔNG TOKEN",   "_stat_fail", "red")]:
            card = QFrame(); card.setObjectName("StatCard")
            cl = QVBoxLayout(card); cl.setContentsMargins(14,10,14,10); cl.setSpacing(3)
            ids = {"blue":"StatValueBlue","green":"StatValueGreen","red":"StatValueRed","yellow":"StatValueYellow"}
            l = QLabel(lbl); l.setObjectName("StatLabel")
            v = QLabel("0"); v.setObjectName(ids[clr])
            cl.addWidget(l); cl.addWidget(v); setattr(self, attr, v); sr.addWidget(card)
        root_lay.addLayout(sr); root_lay.addSpacing(12)

        tb = QHBoxLayout(); tb.setSpacing(8)
        self._search = make_search("🔍 Tìm tài khoản..."); self._search.textChanged.connect(self._filter)
        tb.addWidget(self._search); tb.addSpacing(12)
        tb.addWidget(QLabel("📁 Nhóm:"))
        self._group_combo = QComboBox(); self._group_combo.setMaximumWidth(150)
        self._group_combo.currentTextChanged.connect(self._on_group_changed)
        tb.addWidget(self._group_combo)
        b_new_grp = QPushButton("➕ Tạo nhóm"); b_new_grp.setObjectName("btnSuccess")
        b_new_grp.setCursor(QCursor(Qt.PointingHandCursor)); b_new_grp.clicked.connect(self._create_group_dialog)
        tb.addWidget(b_new_grp); tb.addStretch()
        tb.addWidget(QLabel("🧵 Luồng:"))
        self._thread_spin = make_spinbox(5, 1, 20)
        self._thread_spin.setMaximumWidth(90)
        tb.addWidget(self._thread_spin)
        b_import = QPushButton("📂  Import nhiều"); b_import.setObjectName("btnPrimary")
        b_import.setCursor(QCursor(Qt.PointingHandCursor)); b_import.clicked.connect(self._import_bulk)
        b_del = QPushButton("🗑  Xóa chọn"); b_del.setObjectName("btnDanger")
        b_del.setCursor(QCursor(Qt.PointingHandCursor)); b_del.clicked.connect(self._delete_selected)
        tb.addWidget(b_import); tb.addWidget(b_del)
        root_lay.addLayout(tb); root_lay.addSpacing(8)

        self._splitter = QSplitter(Qt.Horizontal); self._splitter.setHandleWidth(1)
        left_w = QWidget(); left_w.setStyleSheet("background:#0d1219;")
        left_lay = QVBoxLayout(left_w); left_lay.setContentsMargins(0,0,0,0); left_lay.setSpacing(6)

        self.tree = QTreeWidget(); self.tree.setObjectName("FbTree")
        self.tree.setColumnCount(7)
        self.tree.setHeaderLabels(["Tên / Page","UID","Pass","Proxy","Cookie","Token","Loại"])
        self.tree.header().setSectionResizeMode(COL_NAME, QHeaderView.Stretch)
        self.tree.header().setSectionResizeMode(COL_UID, QHeaderView.Interactive); self.tree.header().resizeSection(COL_UID, 140)
        self.tree.header().setSectionResizeMode(COL_PASS, QHeaderView.Interactive); self.tree.header().resizeSection(COL_PASS, 100)
        self.tree.header().setSectionResizeMode(COL_PROXY, QHeaderView.Interactive); self.tree.header().resizeSection(COL_PROXY, 140)
        self.tree.header().setSectionResizeMode(COL_COOKIE, QHeaderView.Interactive); self.tree.header().resizeSection(COL_COOKIE, 120)
        self.tree.header().setSectionResizeMode(COL_TOKEN, QHeaderView.Interactive); self.tree.header().resizeSection(COL_TOKEN, 140)
        self.tree.header().setSectionResizeMode(COL_TYPE, QHeaderView.ResizeToContents)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._ctx_menu)
        self.tree.itemSelectionChanged.connect(self._on_sel_changed)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tree.setIndentation(20); self.tree.setAnimated(True)
        left_lay.addWidget(self.tree, 1)
        self._log_panel = LogPanel()
        left_lay.addWidget(self._log_panel)
        self._detail = DetailPanel()
        self._splitter.addWidget(left_w); self._splitter.addWidget(self._detail)
        self._splitter.setStretchFactor(0, 1); self._splitter.setStretchFactor(1, 0)
        self._splitter.setSizes([900, 310])
        root_lay.addWidget(self._splitter, 1)

        self._load_data()
        self._refresh_group_list()

    def __del__(self):
        if self._batch_mgr: self._batch_mgr.cleanup(); self._batch_mgr = None

    def _load_data(self):
        if "Default" not in self._groups: self._groups["Default"] = {"accounts": []}
        loaded_ok = False
        if os.path.exists(self._data_file):
            try:
                with open(self._data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                g = data.get("groups", {}); a = data.get("accounts", {})
                if g and a:
                    self._groups = g; self._acc_data = {}; self._page_data = {}
                    for uid, acc in a.items():
                        self._acc_data[uid] = acc
                        for page in acc.get("pages", []): self._page_data[page["uid"]] = page
                    if "Default" not in self._groups: self._groups["Default"] = {"accounts": []}
                    loaded_ok = True
            except Exception as e: print(f"[load] error: {e}")
        if not loaded_ok: self._seed_demo(); self._save_data()
        self._refresh_tree()

    def _save_data(self):
        try:
            with open(self._data_file, "w", encoding="utf-8") as f:
                json.dump({"groups": self._groups, "accounts": self._acc_data}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[save] error: {e}"); QMessageBox.critical(self, "Lỗi lưu file", str(e))

    def _seed_demo(self):
        demo = [
            {"mail":"100030148766864","pass":"pass123","2fa":"JBSWY3DP","proxy":"",
             "name":"Hoàng Giang","uid":"100030148766864","letter":"H",
             "token":"","cookie":"","status":"✘ Chưa login","status_color":"#ef4444","pages":[]},
            {"mail":"quynh.danh@gmail.com","pass":"pass456","2fa":"","proxy":"proxy.example.com:3128",
             "name":"Hoàng Quỳnh Danh","uid":"100038524891021","letter":"Q",
             "token":"","cookie":"","status":"✘ Chưa login","status_color":"#ef4444","pages":[]},
        ]
        for d in demo:
            uid = d["uid"]; self._acc_data[uid] = d
            for page in d.get("pages", []): self._page_data[page["uid"]] = page
            if uid not in self._groups["Default"]["accounts"]:
                self._groups["Default"]["accounts"].append(uid)

    def _refresh_group_list(self):
        self._group_combo.blockSignals(True)
        prev = self._current_group
        self._group_combo.clear()
        for grp in sorted(self._groups.keys()): self._group_combo.addItem(grp)
        idx = self._group_combo.findText(prev if prev in self._groups else "Default")
        if idx >= 0: self._group_combo.setCurrentIndex(idx)
        self._group_combo.blockSignals(False)

    def _on_group_changed(self, name):
        if name and name in self._groups and name != self._current_group:
            self._current_group = name; self._refresh_tree()

    def _create_group_dialog(self):
        name, ok = QInputDialog.getText(self, "Tạo nhóm mới", "Tên nhóm:")
        if not (ok and name and name.strip()): return
        name = name.strip()
        if name in self._groups: QMessageBox.warning(self, "Lỗi", f"Nhóm '{name}' đã tồn tại!"); return
        self._groups[name] = {"accounts": []}
        self._current_group = name; self._save_data()
        self._refresh_group_list(); self._refresh_tree()

    def _refresh_tree(self):
        self.tree.clear(); self._uid_to_item = {}; self._page_uid_to_item = {}
        for uid in self._groups.get(self._current_group, {}).get("accounts", []):
            if uid in self._acc_data: self.tree.addTopLevelItem(self._create_account_item(self._acc_data[uid]))
        self._update_stats()

    def _create_account_item(self, data: dict) -> QTreeWidgetItem:
        uid = data["uid"]
        letter = data.get("letter", (data.get("name","?") or "?")[0])
        av_idx = sum(ord(c) for c in data.get("name","")) % len(AVATAR_COLORS)
        item = QTreeWidgetItem()
        avatar_url = data.get("avatar", "")
        if avatar_url:
            avatar_pix = load_avatar_with_cache(avatar_url, uid, 24)
            item.setIcon(COL_NAME, QIcon(avatar_pix if not avatar_pix.isNull() else make_avatar_pixmap(letter, 24, av_idx)))
        else:
            item.setIcon(COL_NAME, QIcon(make_avatar_pixmap(letter, 24, av_idx)))
        item.setText(COL_NAME, data["name"])
        item.setText(COL_UID,  uid)
        pass_len = len(data.get("pass",""))
        item.setText(COL_PASS, "●" * min(pass_len, 20) if pass_len > 0 else "(không có)")
        proxy = data.get("proxy","")
        item.setText(COL_PROXY, f"🌐 {proxy}" if proxy else "(không có)")
        cookie = data.get("cookie","")
        item.setText(COL_COOKIE, cookie[:20]+"…" if len(cookie)>20 else (cookie or "(không có)"))
        tk = data.get("token","")
        item.setText(COL_TOKEN, tk[:22]+"…" if len(tk)>22 else (tk or "(chưa login)"))
        is_running = self._login_progress.get(uid) == "running"
        status_txt = "⏳ Đang login…" if is_running else ("✔ Login OK" if tk else "✘ Chưa login")
        item.setText(COL_TYPE, status_txt)
        item.setCheckState(COL_NAME, Qt.Unchecked)
        item.setFont(COL_NAME, QFont("Segoe UI", 10, QFont.Bold))
        item.setForeground(COL_NAME,  QColor("#d0d8e8"))
        item.setForeground(COL_UID,   QColor("#4d8fff"))
        item.setForeground(COL_PASS,  QColor("#5a7099"))
        item.setForeground(COL_PROXY, QColor("#8b5cf6") if proxy else QColor("#5a7099"))
        item.setForeground(COL_COOKIE, QColor("#e8a87c") if cookie else QColor("#5a7099"))
        item.setForeground(COL_TOKEN, QColor("#00d4aa") if tk else QColor("#3d5278"))
        col_type_color = "#f59e0b" if is_running else ("#10b981" if tk else "#ef4444")
        item.setForeground(COL_TYPE, QColor(col_type_color))
        item.setData(0, Qt.UserRole, {"type":"account","uid":uid})
        for page in data.get("pages", []): self._add_page_child(item, page, uid)
        self._uid_to_item[uid] = item
        return item

    def _add_page_child(self, parent_item, page: dict, parent_uid: str):
        page_uid = page["uid"]; self._page_data[page_uid] = page
        child = QTreeWidgetItem(parent_item)
        page_avatar_url = page.get("avatar", "")
        if page_avatar_url:
            page_avatar_pix = load_avatar_with_cache(page_avatar_url, page_uid, 22)
            child.setIcon(COL_NAME, QIcon(page_avatar_pix if not page_avatar_pix.isNull() else make_avatar_pixmap("P", 22, 5)))
        else:
            child.setIcon(COL_NAME, QIcon(make_avatar_pixmap("P", 22, 5)))
        child.setText(COL_NAME, f"📄 {page['name']}")
        child.setText(COL_UID, page_uid)
        child.setText(COL_PASS, "")
        px = page.get("proxy",""); child.setText(COL_PROXY, px)
        ck = page.get("cookie",""); cookie_display = ck[:20]+"…" if len(ck)>20 else (ck or "(không có)")
        child.setText(COL_COOKIE, cookie_display)
        tk = page.get("token",""); child.setText(COL_TOKEN, tk[:22]+"…" if len(tk)>22 else tk)
        child.setText(COL_TYPE, "📄 Page")
        child.setCheckState(COL_NAME, Qt.Unchecked)
        child.setFont(COL_NAME, QFont("Segoe UI", 9))
        child.setForeground(COL_NAME,  QColor("#8899bb"))
        child.setForeground(COL_UID,   QColor("#ff8c5a"))
        child.setForeground(COL_PASS,  QColor("#4a5a70"))
        child.setForeground(COL_PROXY, QColor("#8b5cf6") if px else QColor("#5a7099"))
        child.setForeground(COL_COOKIE, QColor("#e8a87c") if ck else QColor("#4a5a70"))
        child.setForeground(COL_TOKEN, QColor("#00d4aa") if tk else QColor("#4a5a70"))
        child.setForeground(COL_TYPE,  QColor("#ffa657"))
        child.setData(0, Qt.UserRole, {"type":"page","uid":page_uid,"parent_uid":parent_uid})
        self._page_uid_to_item[page_uid] = child

    def _update_item_after_login(self, uid: str):
        item = self._uid_to_item.get(uid)
        if not item: return
        data = self._acc_data.get(uid, {})
        tk = data.get("token","")
        item.setText(COL_TOKEN, tk[:22]+"…" if len(tk)>22 else (tk or "(chưa login)"))
        is_running = self._login_progress.get(uid) == "running"
        status_txt = "⏳ Đang login…" if is_running else ("✔ Login OK" if tk else "✘ Login fail")
        item.setText(COL_TYPE, status_txt)
        col_type_color = "#f59e0b" if is_running else ("#10b981" if tk else "#ef4444")
        item.setForeground(COL_TOKEN, QColor("#00d4aa") if tk else QColor("#3d5278"))
        item.setForeground(COL_TYPE,  QColor(col_type_color))
        while item.childCount(): item.removeChild(item.child(0))
        for page in data.get("pages", []): self._add_page_child(item, page, uid)
        item.setExpanded(True)

    def _update_stats(self):
        uids  = self._groups.get(self._current_group, {}).get("accounts", [])
        total = len(uids)
        ok    = sum(1 for u in uids if self._acc_data.get(u, {}).get("token",""))
        pages = sum(len(self._acc_data.get(u, {}).get("pages",[])) for u in uids)
        self._stat_total.setText(str(total))
        self._stat_ok.setText(str(ok))
        self._stat_fail.setText(str(total - ok))
        self._stat_pages.setText(str(pages))

    def _login_accounts(self, uids: list):
        if not uids: QMessageBox.warning(self, "Không có gì", "Chọn ít nhất 1 tài khoản để login."); return
        if self._batch_mgr is not None: QMessageBox.warning(self, "Đang chạy", "Một batch login đang chạy, hãy đợi xong."); return
        for uid in uids: self._login_progress[uid] = "running"
        self._refresh_tree()
        max_t = self._thread_spin.value()
        acc_list = [(uid, dict(self._acc_data[uid])) for uid in uids if uid in self._acc_data]
        self._batch_mgr = LoginBatchManager(acc_list, max_threads=max_t, parent=self)
        self._batch_mgr.log_msg.connect(self._log_panel.append)
        self._batch_mgr.one_done.connect(self._on_one_login_done)
        self._batch_mgr.all_done.connect(self._on_all_login_done)
        self._log_panel.append(f"[START] Login {len(uids)} acc  — {max_t} luồng")
        self._batch_mgr.start()

    def _on_one_login_done(self, uid: str, result: dict):
        acc = self._acc_data.get(uid)
        if not acc: return
        self._login_progress[uid] = "done"
        if result.get("ok"):
            acc["token"]  = result.get("token","")
            acc["cookie"] = result.get("cookie","")
            if result.get("name"):  acc["name"]   = result["name"]
            if result.get("uid"):   acc["uid"]     = result["uid"]
            if result.get("avatar"):acc["avatar"]  = result["avatar"]
            acc["status"] = "✔ Active"; acc["status_color"] = "#10b981"
            pages_raw = result.get("pages", [])
            acc_cookie = acc.get("cookie", "")
            for p in pages_raw:
                if not p.get("proxy"): p["proxy"] = acc.get("proxy", "")
                page_uid = p.get("uid", "")
                p["cookie"] = f"{acc_cookie};ps_l=1;ps_n=1;wd=1920x919;i_user={page_uid};"
            acc["pages"] = pages_raw
            for p in pages_raw: self._page_data[p["uid"]] = p
            if pages_raw:
                page_info = ", ".join([f"{p.get('name','?')} (UID: {p.get('uid','?')}, Token: {'✔' if p.get('token','') else '✘'})" for p in pages_raw])
                self._log_panel.append(f"[PAGES] {acc['name']}: {page_info}")
            else:
                self._log_panel.append(f"[NO PAGES] {acc['name']} — Chưa có page nào")
        else:
            acc["status"] = f"✘ {result.get('msg','Fail')[:40]}"; acc["status_color"] = "#ef4444"
        self._save_data(); self._update_item_after_login(uid); self._update_stats()

    def _on_all_login_done(self):
        self._log_panel.append("[DONE] Hoàn tất tất cả!")
        if self._batch_mgr: self._batch_mgr.cleanup(); self._batch_mgr = None
        self._login_progress.clear(); self._update_stats()

    def _login_selected_toolbar(self):
        uids = self._get_selected_account_uids(); self._login_accounts(uids)

    def _get_selected_account_uids(self) -> list:
        uids = []
        for item in self.tree.selectedItems():
            meta = item.data(0, Qt.UserRole)
            if meta and meta["type"] == "account": uids.append(meta["uid"])
        return uids

    def _get_selected_metas(self) -> list:
        metas = []
        for item in self.tree.selectedItems():
            meta = item.data(0, Qt.UserRole)
            if meta: metas.append(meta)
        return metas

    def _add_accounts(self, accs: list) -> int:
        added = 0
        for acc in accs:
            mail = acc["mail"]
            parts = mail.split("@")[0].replace(".", " ").replace("_", " ").split()
            name  = " ".join(p.capitalize() for p in parts) if parts else mail
            uid = mail if mail.isdigit() else rand_uid()
            while uid in self._acc_data: uid = rand_uid()
            acc_obj = {"mail":mail,"pass":acc.get("pass",""),"2fa":acc.get("2fa",""),"proxy":acc.get("proxy",""),
                       "name":name,"uid":uid,"letter":mail[0].upper(),"token":"","cookie":"",
                       "status":"✘ Chưa login","status_color":"#ef4444","pages":[]}
            self._acc_data[uid] = acc_obj
            grp = self._groups.setdefault(self._current_group, {"accounts": []})
            if uid not in grp["accounts"]: grp["accounts"].append(uid)
            added += 1
        if added > 0: self._save_data(); self._refresh_tree()
        return added

    def _add_proxy_to_selected(self):
        metas = self._get_selected_metas()
        if not metas: QMessageBox.warning(self, "Chưa chọn", "Chọn ít nhất 1 tài khoản hoặc page."); return
        dlg = ProxyDialog(len(metas), self)
        if dlg.exec_() != QDialog.Accepted: return
        proxies = dlg.get_proxies(len(metas))
        for i, meta in enumerate(metas):
            if meta["type"] == "account" and meta["uid"] in self._acc_data:
                self._acc_data[meta["uid"]]["proxy"] = proxies[i]
            elif meta["type"] == "page" and meta["uid"] in self._page_data:
                self._page_data[meta["uid"]]["proxy"] = proxies[i]
                parent_uid = meta.get("parent_uid")
                if parent_uid and parent_uid in self._acc_data:
                    for page in self._acc_data[parent_uid].get("pages", []):
                        if page["uid"] == meta["uid"]: page["proxy"] = proxies[i]; break
        self._save_data(); self._refresh_tree()
        self._log_panel.append(f"[PROXY] Đã gán proxy cho {len(metas)} mục")

    def _on_item_clicked(self, item, col):
        if self._block_check_sync: return
        item.setSelected(True)

    def _on_item_double_clicked(self, item, col):
        meta = item.data(0, Qt.UserRole)
        if meta and meta["type"] == "account": item.setExpanded(not item.isExpanded())

    def _on_sel_changed(self):
        if self._block_check_sync: return
        self._block_check_sync = True
        selected = self.tree.selectedItems()
        for item in selected: item.setCheckState(COL_NAME, Qt.Checked)
        self._block_check_sync = False
        if not selected: self._detail.clear(); return
        if len(selected) > 1: self._detail.show_multi(len(selected)); return
        item = selected[0]; meta = item.data(0, Qt.UserRole)
        if not meta: return
        if meta["type"] == "account":
            d = self._acc_data.get(meta["uid"])
            if d: self._detail.show_account(d)
        elif meta["type"] == "page":
            page = self._page_data.get(meta["uid"])
            par  = self._acc_data.get(meta.get("parent_uid",""))
            if page: self._detail.show_page(page, par["name"] if par else "")

    def _select_all(self):
        self._block_check_sync = True
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            acc = root.child(i); acc.setSelected(True); acc.setCheckState(COL_NAME, Qt.Checked)
            for j in range(acc.childCount()):
                ch = acc.child(j); ch.setSelected(True); ch.setCheckState(COL_NAME, Qt.Checked)
        self._block_check_sync = False
        self._detail.show_multi(len(self.tree.selectedItems()))

    def _deselect_all(self):
        self._block_check_sync = True
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            acc = root.child(i); acc.setSelected(False); acc.setCheckState(COL_NAME, Qt.Unchecked)
            for j in range(acc.childCount()):
                ch = acc.child(j); ch.setSelected(False); ch.setCheckState(COL_NAME, Qt.Unchecked)
        self._block_check_sync = False; self._detail.clear()

    def _check_selected(self):
        self._block_check_sync = True
        for item in self.tree.selectedItems():
            meta = item.data(0, Qt.UserRole)
            if meta and meta["type"] == "account": item.setCheckState(COL_NAME, Qt.Checked)
        self._block_check_sync = False

    def _ctx_menu(self, pos):
        sel  = self.tree.selectedItems()
        menu = QMenu(self)
        add_sub = QMenu("➕  Thêm tài khoản", self); add_sub.setStyleSheet(STYLE)
        a1 = QAction("➕  Thêm 1 tài khoản", self); a1.triggered.connect(self._add_single)
        a2 = QAction("📋  Import nhiều (uid|pass|2fa|proxy)", self); a2.triggered.connect(self._import_bulk)
        add_sub.addAction(a1); add_sub.addAction(a2); menu.addMenu(add_sub)
        menu.addSeparator()
        a_sel   = QAction("☑  Chọn tất cả",    self); a_sel.triggered.connect(self._select_all)
        a_desel = QAction("☐  Bỏ chọn tất cả", self); a_desel.triggered.connect(self._deselect_all)
        a_check = QAction("✔  Tick tài khoản đã chọn", self); a_check.triggered.connect(self._check_selected)
        menu.addAction(a_sel); menu.addAction(a_desel); menu.addAction(a_check)
        if sel:
            sel_uids = [it.data(0,Qt.UserRole)["uid"] for it in sel
                        if it.data(0,Qt.UserRole) and it.data(0,Qt.UserRole)["type"]=="account"]
            menu.addSeparator()
            a_login = QAction("🔑  Login tài khoản đã chọn", self)
            a_login.triggered.connect(lambda: self._login_accounts(sel_uids))
            a_login_all = QAction("🔑  Login TẤT CẢ trong nhóm", self)
            a_login_all.triggered.connect(self._login_all_in_group)
            menu.addAction(a_login); menu.addAction(a_login_all)
            menu.addSeparator()
            a_proxy = QAction("🌐  Thêm / Sửa Proxy cho chọn", self)
            a_proxy.triggered.connect(self._add_proxy_to_selected)
            menu.addAction(a_proxy); menu.addSeparator()
            copy_sub = QMenu("📋  Copy", self); copy_sub.setStyleSheet(STYLE)
            def _copy(field):
                lines = []
                for it in sel:
                    meta = it.data(0, Qt.UserRole)
                    if not meta: continue
                    src = self._acc_data.get(meta["uid"]) if meta["type"]=="account" else self._page_data.get(meta["uid"])
                    if src: lines.append(str(src.get(field,"")))
                QApplication.clipboard().setText("\n".join(lines))
            def _copy_combined(fields):
                lines = []
                for it in sel:
                    meta = it.data(0, Qt.UserRole)
                    if not meta: continue
                    src = self._acc_data.get(meta["uid"]) if meta["type"]=="account" else self._page_data.get(meta["uid"])
                    if src: lines.append("|".join(str(src.get(f,"")) for f in fields))
                QApplication.clipboard().setText("\n".join(lines))
            for label, fn in [
                ("Copy UID",              lambda: _copy("uid")),
                ("Copy Mail/UID",         lambda: _copy("mail")),
                ("Copy Pass",             lambda: _copy("pass")),
                ("Copy Token",            lambda: _copy("token")),
                ("Copy Cookie",           lambda: _copy("cookie")),
                ("Copy Proxy",            lambda: _copy("proxy")),
                ("Copy UID|Pass",         lambda: _copy_combined(["uid","pass"])),
                ("Copy UID|Pass|2FA",     lambda: _copy_combined(["uid","pass","2fa"])),
                ("Copy UID|Pass|2FA|Proxy",lambda: _copy_combined(["uid","pass","2fa","proxy"])),
                ("Copy UID|Token",        lambda: _copy_combined(["uid","token"])),
                ("Copy UID|Cookie",       lambda: _copy_combined(["uid","cookie"])),
            ]:
                act = QAction(label, self); act.triggered.connect(fn); copy_sub.addAction(act)
            menu.addMenu(copy_sub); menu.addSeparator()
            a_del = QAction("🗑  Xóa chọn", self); a_del.triggered.connect(self._delete_selected)
            menu.addAction(a_del)
        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def _add_single(self):
        dlg = AddAccountDialog("single", self)
        if dlg.exec_() == QDialog.Accepted:
            n = self._add_accounts(dlg.get_accounts())
            QMessageBox.information(self, "Thêm thành công", f"Đã thêm {n} tài khoản vào nhóm '{self._current_group}'.")

    def _import_bulk(self):
        dlg = AddAccountDialog("bulk", self)
        if dlg.exec_() == QDialog.Accepted:
            n = self._add_accounts(dlg.get_accounts())
            QMessageBox.information(self, "Import thành công", f"Đã import {n} tài khoản vào nhóm '{self._current_group}'.")

    def _login_all_in_group(self):
        uids = [uid for uid in self._groups.get(self._current_group,{}).get("accounts",[]) if uid in self._acc_data]
        self._login_accounts(uids)

    def _delete_selected(self):
        for item in list(self.tree.selectedItems()):
            meta = item.data(0, Qt.UserRole)
            if not meta: continue
            if meta["type"] == "account":
                uid = meta["uid"]
                for grp in self._groups.values(): grp["accounts"] = [u for u in grp["accounts"] if u != uid]
                for page in self._acc_data.get(uid, {}).get("pages", []): self._page_data.pop(page["uid"], None)
                self._acc_data.pop(uid, None)
            elif meta["type"] == "page":
                puid = meta["uid"]; par_uid = meta.get("parent_uid","")
                self._page_data.pop(puid, None)
                if par_uid in self._acc_data:
                    self._acc_data[par_uid]["pages"] = [p for p in self._acc_data[par_uid]["pages"] if p["uid"] != puid]
        self._save_data(); self._refresh_tree(); self._detail.clear()

    def _filter(self, text):
        text = text.lower()
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setHidden(bool(text) and text not in item.text(COL_NAME).lower() and text not in item.text(COL_UID).lower())


# ─────────────────────────────────────────────────────────────────────────────
#  REGISTER PAGE
# ─────────────────────────────────────────────────────────────────────────────
class RegisterPage(QWidget):
    def __init__(self, facebook_page, parent=None):
        super().__init__(parent)
        self.facebook_page = facebook_page
        self._uid_to_item = {}
        self._page_items = []
        self._page_items_map = {}
        self._newly_registered_pages = {}
        self._block_check_sync = False
        self._batch_mgr = None
        self._settings = {
            "avatar_path": "", "cover_path": "",
            "names": "Trang Page|Trang Fan Page|Trang Business",
            "bios": "Chào mừng bạn|Welcome to my page|Cảm ơn bạn đã theo dõi",
            "pages_per_account": 1, "max_threads": 3, "demo_mode": False
        }

        root_lay = QVBoxLayout(self); root_lay.setContentsMargins(20,16,20,16); root_lay.setSpacing(0)

        hdr = QHBoxLayout(); hdr.setSpacing(14)
        icon = QLabel("📝"); icon.setObjectName("PageIconFb"); icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #6d28d9,stop:1 #8b5cf6);border-radius:12px;color:white;font-size:20px;font-weight:800;min-width:46px;max-width:46px;min-height:46px;max-height:46px;")
        hdr.addWidget(icon)
        hdr_text = QVBoxLayout(); hdr_text.setSpacing(2)
        t1 = QLabel("REG PAGEPRO5"); t1.setObjectName("PageTitle")
        t2 = QLabel("Đăng ký page cho tài khoản Facebook"); t2.setObjectName("PageSub")
        hdr_text.addWidget(t1); hdr_text.addWidget(t2)
        hdr.addLayout(hdr_text); hdr.addStretch()
        b_settings = QPushButton("⚙  Cài đặt"); b_settings.setObjectName("btnPrimary"); b_settings.clicked.connect(self._show_settings)
        b_reg = QPushButton("▶  Reg Page"); b_reg.setObjectName("btnSuccess"); b_reg.clicked.connect(self._reg_selected)
        hdr.addWidget(b_settings); hdr.addWidget(b_reg)
        root_lay.addLayout(hdr); root_lay.addSpacing(14)

        tb = QHBoxLayout(); tb.setSpacing(8)
        tb.addWidget(QLabel("📁 Nhóm:"))
        self._group_combo = QComboBox(); self._group_combo.setMaximumWidth(150)
        self._group_combo.currentTextChanged.connect(self._on_group_changed)
        tb.addWidget(self._group_combo)
        self._search = make_search("🔍 Tìm tài khoản..."); self._search.textChanged.connect(self._filter)
        tb.addWidget(self._search); tb.addStretch()
        b_del = QPushButton("🗑  Xóa chọn"); b_del.setObjectName("btnDanger"); b_del.clicked.connect(self._delete_selected)
        tb.addWidget(b_del)
        root_lay.addLayout(tb); root_lay.addSpacing(8)

        main_splitter = QSplitter(Qt.Horizontal); main_splitter.setHandleWidth(2)

        left_w = QWidget(); left_w.setStyleSheet("background:#0d1219;")
        left_lay = QVBoxLayout(left_w); left_lay.setContentsMargins(0,0,0,0); left_lay.setSpacing(4)
        left_lbl = make_section_header("ACCOUNTS", "Danh sách tài khoản Facebook")
        left_lay.addWidget(left_lbl)
        self.tree_acc = QTreeWidget(); self.tree_acc.setObjectName("FbTree")
        self.tree_acc.setColumnCount(5)
        self.tree_acc.setHeaderLabels(["Tên","UID","Pass/Proxy","Status","Loại"])
        self.tree_acc.header().setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 5): self.tree_acc.header().setSectionResizeMode(col, QHeaderView.Interactive)
        self.tree_acc.header().resizeSection(1, 140); self.tree_acc.header().resizeSection(2, 140); self.tree_acc.header().resizeSection(3, 100)
        self.tree_acc.setAlternatingRowColors(True)
        self.tree_acc.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree_acc.itemClicked.connect(self._on_acc_clicked)
        self.tree_acc.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_acc.customContextMenuRequested.connect(self._ctx_menu_acc)
        self.tree_acc.setIndentation(0)
        left_lay.addWidget(self.tree_acc, 1)

        right_w = QWidget(); right_w.setStyleSheet("background:#0d1219;")
        right_lay = QVBoxLayout(right_w); right_lay.setContentsMargins(0,0,0,0); right_lay.setSpacing(4)
        right_lbl = make_section_header("PAGES REGISTERED", "Pages đã được đăng ký")
        right_lay.addWidget(right_lbl)
        self.tree_pages = QTreeWidget(); self.tree_pages.setObjectName("FbTree")
        self.tree_pages.setColumnCount(5)
        self.tree_pages.setHeaderLabels(["Page Name","Page UID","Acc UID","Acc Name","Status"])
        self.tree_pages.header().setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 5): self.tree_pages.header().setSectionResizeMode(col, QHeaderView.Interactive)
        self.tree_pages.header().resizeSection(1, 130); self.tree_pages.header().resizeSection(2, 130); self.tree_pages.header().resizeSection(3, 130)
        self.tree_pages.setAlternatingRowColors(True)
        self.tree_pages.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree_pages.setIndentation(0)
        right_lay.addWidget(self.tree_pages, 1)

        main_splitter.addWidget(left_w); main_splitter.addWidget(right_w)
        main_splitter.setStretchFactor(0, 1); main_splitter.setStretchFactor(1, 1)
        main_splitter.setSizes([500, 500])
        root_lay.addWidget(main_splitter, 1); root_lay.addSpacing(8)
        self._log_panel = LogPanel()
        root_lay.addWidget(self._log_panel, 0)

        self._refresh_group_list(); self._refresh_trees()

    def _refresh_group_list(self):
        self._group_combo.blockSignals(True); self._group_combo.clear()
        for grp in sorted(self.facebook_page._groups.keys()): self._group_combo.addItem(grp)
        idx = self._group_combo.findText("Default")
        if idx >= 0: self._group_combo.setCurrentIndex(idx)
        self._group_combo.blockSignals(False)

    def _on_group_changed(self, name):
        if name and name in self.facebook_page._groups:
            self._newly_registered_pages.clear(); self._refresh_trees()

    def _get_current_group(self): return self._group_combo.currentText() or "Default"

    def _refresh_trees(self): self._refresh_acc_tree(); self._refresh_pages_tree()

    def _refresh_acc_tree(self):
        self.tree_acc.clear(); self._uid_to_item = {}
        group_name = self._get_current_group()
        for uid in self.facebook_page._groups.get(group_name, {}).get("accounts", []):
            if uid in self.facebook_page._acc_data:
                data = self.facebook_page._acc_data[uid]
                item = self._create_acc_item(data)
                self._uid_to_item[uid] = item
                self.tree_acc.addTopLevelItem(item)

    def _refresh_pages_tree(self):
        self.tree_pages.clear(); self._page_items = []
        for page_uid, (page, acc_uid, acc_name) in self._newly_registered_pages.items():
            item = self._create_page_item(page, acc_uid, acc_name)
            self.tree_pages.addTopLevelItem(item)
            self._page_items.append((page_uid, item))

    def _create_acc_item(self, data: dict):
        uid = data["uid"]
        letter = data.get("letter", (data.get("name","?") or "?")[0])
        av_idx = sum(ord(c) for c in data.get("name","")) % len(AVATAR_COLORS)
        item = QTreeWidgetItem()
        avatar_url = data.get("avatar", "")
        if avatar_url:
            avatar_pix = load_avatar_with_cache(avatar_url, uid, 24)
            item.setIcon(0, QIcon(avatar_pix if not avatar_pix.isNull() else make_avatar_pixmap(letter, 24, av_idx)))
        else:
            item.setIcon(0, QIcon(make_avatar_pixmap(letter, 24, av_idx)))
        item.setText(0, data["name"]); item.setText(1, uid)
        proxy = data.get("proxy","")
        col2 = f"🌐 {proxy}" if proxy else ("●" * min(len(data.get("pass","")), 20) if data.get("pass","") else "(không có)")
        item.setText(2, col2)
        status_txt = "✔ OK" if data.get("token","") else "✘ Chưa login"
        item.setText(3, status_txt); item.setText(4, "Acc")
        item.setCheckState(0, Qt.Unchecked)
        item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))
        item.setForeground(0, QColor("#d0d8e8")); item.setForeground(1, QColor("#4d8fff"))
        item.setForeground(2, QColor("#8b5cf6") if proxy else QColor("#5a7099"))
        item.setForeground(3, QColor("#10b981") if data.get("token","") else QColor("#ef4444"))
        item.setForeground(4, QColor("#ff8c5a"))
        item.setData(0, Qt.UserRole, {"type":"account","uid":uid})
        return item

    def _create_page_item(self, page: dict, acc_uid: str, acc_name: str):
        page_uid = page["uid"]; item = QTreeWidgetItem()
        page_avatar_url = page.get("avatar", "")
        if page_avatar_url:
            page_avatar_pix = load_avatar_with_cache(page_avatar_url, page_uid, 20)
            item.setIcon(0, QIcon(page_avatar_pix if not page_avatar_pix.isNull() else make_avatar_pixmap("P", 20, 5)))
        else:
            item.setIcon(0, QIcon(make_avatar_pixmap("P", 20, 5)))
        item.setText(0, page.get("name", "Untitled")); item.setText(1, page_uid)
        item.setText(2, acc_uid); item.setText(3, acc_name)
        tk = page.get("token", "")
        item.setText(4, "✔ OK" if tk else "✘ Chưa reg")
        item.setFont(0, QFont("Segoe UI", 9))
        item.setForeground(0, QColor("#a0d8ff")); item.setForeground(1, QColor("#ff8c5a"))
        item.setForeground(2, QColor("#8b5cf6")); item.setForeground(3, QColor("#d0d8e8"))
        item.setForeground(4, QColor("#10b981") if tk else QColor("#ef4444"))
        item.setData(0, Qt.UserRole, {"type":"page","uid":page_uid,"acc_uid":acc_uid})
        return item

    def _on_acc_clicked(self, item, col):
        if self._block_check_sync: return
        cur = item.checkState(0)
        item.setCheckState(0, Qt.Unchecked if cur == Qt.Checked else Qt.Checked)

    def _tick_selected_accounts(self, items):
        self._block_check_sync = True
        for item in items:
            meta = item.data(0, Qt.UserRole)
            if meta and meta["type"] == "account": item.setCheckState(0, Qt.Checked)
        self._block_check_sync = False

    def _get_selected_uids(self) -> list:
        uids = []
        root = self.tree_acc.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.checkState(0) == Qt.Checked:
                meta = item.data(0, Qt.UserRole)
                if meta and meta["type"] == "account": uids.append(meta["uid"])
        return uids

    def _show_settings(self):
        dlg = QDialog(self); dlg.setWindowTitle("Cài đặt REG PAGEPRO5"); dlg.setMinimumWidth(550); dlg.setStyleSheet(STYLE)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(20,16,20,16); lay.setSpacing(12)
        form = QFormLayout(); form.setSpacing(10); form.setLabelAlignment(Qt.AlignRight)
        avatar_lay = QHBoxLayout()
        self._avatar_file_in = QLineEdit(); self._avatar_file_in.setText(self._settings.get("avatar_path","")); self._avatar_file_in.setPlaceholderText("Chọn folder avatar..."); self._avatar_file_in.setReadOnly(True)
        b_avatar = QPushButton("Chọn..."); b_avatar.setMaximumWidth(80); b_avatar.clicked.connect(lambda: self._choose_image_file("avatar"))
        avatar_lay.addWidget(self._avatar_file_in); avatar_lay.addWidget(b_avatar)
        form.addRow("Avatar:", avatar_lay)
        cover_lay = QHBoxLayout()
        self._cover_file_in = QLineEdit(); self._cover_file_in.setText(self._settings.get("cover_path","")); self._cover_file_in.setPlaceholderText("Chọn folder cover..."); self._cover_file_in.setReadOnly(True)
        b_cover = QPushButton("Chọn..."); b_cover.setMaximumWidth(80); b_cover.clicked.connect(lambda: self._choose_image_file("cover"))
        cover_lay.addWidget(self._cover_file_in); cover_lay.addWidget(b_cover)
        form.addRow("Cover:", cover_lay)
        self._names_in = QTextEdit(); self._names_in.setPlainText(self._settings.get("names","")); self._names_in.setMinimumHeight(70); self._names_in.setPlaceholderText("Mỗi dòng 1 tên")
        form.addRow("Tên Pages:", self._names_in)
        self._bios_in = QTextEdit(); self._bios_in.setPlainText(self._settings.get("bios","")); self._bios_in.setMinimumHeight(70); self._bios_in.setPlaceholderText("Mỗi dòng 1 bio")
        form.addRow("Bios:", self._bios_in)
        self._pages_spin = make_spinbox(self._settings.get("pages_per_account",1), 1, 20)
        form.addRow("Pages/Acc:", self._pages_spin)
        self._threads_spin = make_spinbox(self._settings.get("max_threads",3), 1, 10)
        form.addRow("Luồng REG:", self._threads_spin)
        self._demo_check = QCheckBox("Chế độ demo (không đăng ký thực)"); self._demo_check.setChecked(self._settings.get("demo_mode",False))
        form.addRow("Demo:", self._demo_check)
        lay.addLayout(form)
        btns = QHBoxLayout(); btns.addStretch()
        cancel = QPushButton("Huỷ"); cancel.clicked.connect(dlg.reject)
        ok = QPushButton("✔  Lưu"); ok.setObjectName("btnPrimary"); ok.clicked.connect(dlg.accept)
        btns.addWidget(cancel); btns.addWidget(ok); lay.addLayout(btns)
        if dlg.exec_() == QDialog.Accepted:
            self._settings.update({"avatar_path":self._avatar_file_in.text().strip(),"cover_path":self._cover_file_in.text().strip(),
                                   "names":self._names_in.toPlainText().strip(),"bios":self._bios_in.toPlainText().strip(),
                                   "pages_per_account":self._pages_spin.value(),"max_threads":self._threads_spin.value(),
                                   "demo_mode":self._demo_check.isChecked()})
            self._log_panel.append("[SETTINGS] Cập nhật cài đặt REG PAGE")

    def _choose_image_file(self, file_type):
        folder_path = QFileDialog.getExistingDirectory(self, f"Chọn folder chứa ảnh {file_type}...", "")
        if folder_path:
            if file_type == "avatar": self._avatar_file_in.setText(folder_path)
            elif file_type == "cover": self._cover_file_in.setText(folder_path)

    def _reg_selected(self):
        from source.regpage_worker import RegisterBatchManager
        uids = self._get_selected_uids()
        if not uids: QMessageBox.warning(self, "Không có gì", "Chọn ít nhất 1 tài khoản để đăng ký page."); return
        if self._settings.get("demo_mode"):
            QMessageBox.information(self, "Demo Mode", "Chế độ demo: chỉ in log, không đăng ký thực")
            self._log_panel.append("[DEMO MODE] Bắt đầu test REG"); return
        count = self._settings.get("pages_per_account", 1)
        names_list = [n.strip() for n in self._settings.get("names","").split("\n") if n.strip()] or ["Page"]
        bios_list = [b.strip() for b in self._settings.get("bios","").split("\n") if b.strip()] or [""]
        reg_list = []; page_items_map = {}; total_to_reg = 0
        for uid in uids:
            acc = self.facebook_page._acc_data.get(uid)
            if not acc: self._log_panel.append(f"[SKIP] UID {uid} không tìm thấy"); continue
            if not acc.get("token"): self._log_panel.append(f"[SKIP] {acc.get('name', uid)} — Chưa login"); continue
            for i in range(count):
                name = names_list[i % len(names_list)]; bio = bios_list[i % len(bios_list)]
                page_id = f"{uid}_{int(time.time() * 1000)}_{i}"
                item = QTreeWidgetItem()
                item.setText(0, f"⏳ {name}"); item.setText(1, page_id); item.setText(2, uid); item.setText(3, acc["name"]); item.setText(4, "⏳ Pending")
                item.setForeground(0, QColor("#a0d8ff")); item.setForeground(1, QColor("#ff8c5a")); item.setForeground(2, QColor("#8b5cf6")); item.setForeground(3, QColor("#d0d8e8")); item.setForeground(4, QColor("#f59e0b"))
                self.tree_pages.addTopLevelItem(item)
                page_items_map[page_id] = (item, acc["name"])
                self._newly_registered_pages[page_id] = ({"uid": page_id, "name": name}, uid, acc["name"])
                reg_data = {"page_uid":uid,"name":name,"bio":bio,"cookie":acc.get("cookie",""),"token":acc.get("token",""),"avatar_path":self._settings.get("avatar_path",""),"cover_path":self._settings.get("cover_path","")}
                reg_list.append((page_id, reg_data)); total_to_reg += 1
        if not reg_list: QMessageBox.warning(self, "Lỗi", "Không có tài khoản nào đủ điều kiện (cần login)"); return
        self._log_panel.append(f"[START] Đăng ký {total_to_reg} pages (luồng: {self._settings.get('max_threads', 3)})")
        self._page_items_map = page_items_map
        callbacks = {"log_msg":self._log_panel.append,"status_update":self._on_page_status_update,"one_done":self._on_page_reg_done,"all_done":self._on_all_reg_done}
        self._batch_mgr = RegisterBatchManager(reg_list, settings=self._settings, max_threads=self._settings.get("max_threads",3), callbacks=callbacks)
        self._batch_mgr.start()

    def _on_page_status_update(self, page_id: str, status: str):
        if page_id in self._page_items_map:
            item, _ = self._page_items_map[page_id]; item.setText(4, status)
            color = "#f59e0b"
            if "✔" in status: color = "#10b981"
            elif "✘" in status: color = "#ef4444"
            item.setForeground(4, QColor(color))

    def _on_page_reg_done(self, page_id: str, result: dict):
        if not page_id in self._page_items_map: return
        item, acc_name = self._page_items_map[page_id]
        if result.get("ok"):
            page_name = result.get("name", "?"); page_fb_id = result.get("page_id", "")
            item.setText(0, f"✔ {page_name}"); item.setText(1, page_fb_id); item.setText(4, "✔ OK")
            item.setForeground(0, QColor("#10b981")); item.setForeground(4, QColor("#10b981"))
            if page_id in self._newly_registered_pages:
                page_data, uid, _ = self._newly_registered_pages[page_id]
                page_data["uid"] = page_fb_id
                self._newly_registered_pages[page_fb_id] = (page_data, uid, acc_name)
                del self._newly_registered_pages[page_id]
            av_set = result.get("avatar_set", False); cv_set = result.get("cover_set", False)
            extra = []
            if av_set: extra.append("Avt")
            if cv_set: extra.append("Cover")
            self._log_panel.append(f"[✔] {acc_name}: {page_name}" + (f" + {', '.join(extra)}" if extra else ""))
        else:
            msg = result.get("msg", "Lỗi không xác định")
            item.setForeground(0, QColor("#ef4444")); item.setForeground(4, QColor("#ef4444"))
            self._log_panel.append(f"[✘] {acc_name}: {msg}")

    def _on_all_reg_done(self):
        self._log_panel.append("[✔] Hoàn tất quá trình đăng ký page"); self.facebook_page._save_data()

    def _ctx_menu_acc(self, pos):
        sel = self.tree_acc.selectedItems(); menu = QMenu(self)
        a_sel = QAction("☑  Chọn tất cả", self); a_sel.triggered.connect(self._select_all)
        a_desel = QAction("☐  Bỏ chọn tất cả", self); a_desel.triggered.connect(self._deselect_all)
        menu.addAction(a_sel); menu.addAction(a_desel)
        if sel:
            a_tick = QAction("✔  Tick những tài khoản chọn", self); a_tick.triggered.connect(lambda: self._tick_selected_accounts(sel)); menu.addAction(a_tick)
        if sel:
            sel_uids = [it.data(0,Qt.UserRole)["uid"] for it in sel if it.data(0,Qt.UserRole) and it.data(0,Qt.UserRole)["type"]=="account"]
            menu.addSeparator()
            copy_sub = QMenu("📋  Copy", self); copy_sub.setStyleSheet(STYLE)
            def _copy(field):
                lines = [str(self.facebook_page._acc_data.get(uid, {}).get(field,"")) for uid in sel_uids]
                QApplication.clipboard().setText("\n".join(lines))
            for label, field in [("Copy UID","uid"),("Copy Mail","mail"),("Copy Pass","pass"),("Copy Token","token")]:
                act = QAction(label, self); act.triggered.connect(lambda _, f=field: _copy(f)); copy_sub.addAction(act)
            menu.addMenu(copy_sub); menu.addSeparator()
            a_del = QAction("🗑  Xóa chọn", self); a_del.triggered.connect(self._delete_selected); menu.addAction(a_del)
        menu.exec_(self.tree_acc.viewport().mapToGlobal(pos))

    def _select_all(self):
        self._block_check_sync = True
        root = self.tree_acc.invisibleRootItem()
        for i in range(root.childCount()): root.child(i).setCheckState(0, Qt.Checked)
        self._block_check_sync = False

    def _deselect_all(self):
        self._block_check_sync = True
        root = self.tree_acc.invisibleRootItem()
        for i in range(root.childCount()): root.child(i).setCheckState(0, Qt.Unchecked)
        self._block_check_sync = False

    def _delete_selected(self):
        uids_to_delete = self._get_selected_uids()
        if not uids_to_delete: QMessageBox.warning(self, "Không có gì", "Tick ít nhất 1 tài khoản để xóa."); return
        reply = QMessageBox.question(self, "Xác nhận", f"Xóa {len(uids_to_delete)} tài khoản?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No: return
        for uid in uids_to_delete:
            grp = self.facebook_page._groups.get(self._get_current_group())
            if grp: grp["accounts"] = [u for u in grp["accounts"] if u != uid]
            self.facebook_page._acc_data.pop(uid, None)
        self.facebook_page._save_data(); self._refresh_trees()

    def _filter(self, text):
        text = text.lower()
        root = self.tree_acc.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setHidden(bool(text) and text not in item.text(0).lower() and text not in item.text(1).lower())


# ─────────────────────────────────────────────────────────────────────────────
#  TTC MANAGEMENT PAGE
# ─────────────────────────────────────────────────────────────────────────────


class CheckXuProgressDialog(QDialog):
    """Custom dialog cho check xu với giao diện đẹp hơn."""
    
    def __init__(self, title: str = "Kiểm tra Xu", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 500, 280)
        self.setWindowModality(Qt.WindowModal)
        self.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
            }
            QLabel {
                color: #c9d6ea;
                font-size: 13px;
            }
            QProgressBar {
                border: 1px solid #2e4570;
                border-radius: 5px;
                background-color: #0d1e2d;
                text-align: center;
                color: #c9d6ea;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0d6eff, stop:1 #2d7fff);
                border-radius: 4px;
            }
            QPushButton {
                background-color: #0d2d47;
                border: 1px solid #2e4570;
                border-radius: 5px;
                color: #c9d6ea;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1c3d57;
                border-color: #4d78cc;
            }
            QPushButton:pressed {
                background-color: #0d1f37;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        self.title_label = QLabel("Bắt đầu kiểm tra xu...")
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0d6eff;")
        layout.addWidget(self.title_label)
        
        # Current account
        self.current_label = QLabel("Chờ bắt đầu...")
        self.current_label.setStyleSheet("font-size: 12px; color: #a0b0ca;")
        layout.addWidget(self.current_label)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        # Stats
        self.stats_label = QLabel("0/0 tài khoản")
        self.stats_label.setStyleSheet("font-size: 11px; color: #70808a;")
        layout.addWidget(self.stats_label)
        
        # Button
        self.cancel_btn = QPushButton("Huỷ")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
        
        self._total = 0
        self._current = 0
    
    def set_total(self, total: int):
        self._total = total
        self.progress.setMaximum(total)
        self.stats_label.setText(f"0/{total} tài khoản")
    
    def set_current(self, username: str, current: int, total: int):
        self._current = current
        self.current_label.setText(f"🔍 Kiểm tra: {username}")
        self.progress.setValue(current)
        self.stats_label.setText(f"{current}/{total} tài khoản")
        QApplication.processEvents()
    
    def is_cancelled(self) -> bool:
        return self.result() == QDialog.Rejected
    
    def finish(self):
        self.title_label.setText("✔ Hoàn thành!")
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #22c55e;")
        self.cancel_btn.setText("Đóng")
        self.progress.setValue(self._total)


class TTCManagementPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ttc_data = {}
        self._data_file = "ttc_accounts.json"
        self._log_panel = None
        self._reg_thread = None
        self._load_data()

        root_lay = QVBoxLayout(self); root_lay.setContentsMargins(20,16,20,16); root_lay.setSpacing(0)

        hdr = QHBoxLayout(); hdr.setSpacing(14)
        icon = QLabel("🌐"); icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0891b2,stop:1 #06b6d4);border-radius:12px;color:white;font-size:20px;font-weight:800;min-width:46px;max-width:46px;min-height:46px;max-height:46px;")
        hdr.addWidget(icon)
        hdr_text = QVBoxLayout(); hdr_text.setSpacing(2)
        t1 = QLabel("Quản Lý Tài Khoản TTC"); t1.setObjectName("PageTitle")
        t2 = QLabel("Quản lý & tạo tài khoản TTC tự động"); t2.setObjectName("PageSub")
        hdr_text.addWidget(t1); hdr_text.addWidget(t2)
        hdr.addLayout(hdr_text); hdr.addStretch()
        root_lay.addLayout(hdr); root_lay.addSpacing(14)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_manage_tab(), "📋  Quản lý tài khoản")
        self.tabs.addTab(self._create_create_tab(), "➕  Tạo tài khoản")
        root_lay.addWidget(self.tabs, 1)

    def _make_tree(self, columns, headers):
        tree = QTreeWidget(); tree.setObjectName("FbTree")
        tree.setColumnCount(columns)
        tree.setHeaderLabels(headers)
        tree.setAlternatingRowColors(True)
        tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        tree.setIndentation(0)
        return tree

    def _create_manage_tab(self):
        w = QWidget(); w.setStyleSheet("background:#0b0f14;")
        lay = QVBoxLayout(w); lay.setContentsMargins(12,12,12,12); lay.setSpacing(8)

        tb = QHBoxLayout(); tb.setSpacing(8)
        for label, obj_name, slot in [
            ("➕  Thêm 1 TK", "btnPrimary", self._add_single_account),
            ("📁  Import file", "btnPrimary", self._add_bulk_accounts),
            ("💰  Check Xu", "btnSuccess", self._check_xu_selected),
            ("🗑  Xóa chọn", "btnDanger", self._delete_selected_accounts),
        ]:
            btn = QPushButton(label); btn.setObjectName(obj_name)
            btn.setCursor(QCursor(Qt.PointingHandCursor)); btn.clicked.connect(slot)
            tb.addWidget(btn)
        tb.addStretch(); lay.addLayout(tb)

        self.tree_manage = self._make_tree(5, ["Tên tài khoản", "UID / User", "Pass", "Token", "Xu"])
        self.tree_manage.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree_manage.header().setSectionResizeMode(1, QHeaderView.Interactive); self.tree_manage.header().resizeSection(1, 160)
        self.tree_manage.header().setSectionResizeMode(2, QHeaderView.Interactive); self.tree_manage.header().resizeSection(2, 120)
        self.tree_manage.header().setSectionResizeMode(3, QHeaderView.Interactive); self.tree_manage.header().resizeSection(3, 200)
        self.tree_manage.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tree_manage.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_manage.customContextMenuRequested.connect(self._ctx_menu_manage)
        lay.addWidget(self.tree_manage, 1)
        self._refresh_tree_manage()
        return w

    def _create_create_tab(self):
        w = QWidget(); w.setStyleSheet("background:#0b0f14;")
        lay = QVBoxLayout(w); lay.setContentsMargins(12,12,12,12); lay.setSpacing(12)

        cfg_frame = QFrame(); cfg_frame.setStyleSheet("background:#111827;border:1px solid #1a2336;border-radius:8px;")
        cfg_lay = QHBoxLayout(cfg_frame); cfg_lay.setContentsMargins(14,10,14,10); cfg_lay.setSpacing(10)
        cfg_lay.addWidget(QLabel("🔑 Key 3xcaptcha:"))
        self.api_key_input = QLineEdit(); self.api_key_input.setPlaceholderText("Nhập API key..."); self.api_key_input.setMaximumWidth(360)
        cfg_lay.addWidget(self.api_key_input)
        cfg_lay.addWidget(QLabel("🧵 Luồng:"))
        self.thread_spin = make_spinbox(3, 1, 10)
        self.thread_spin.setMaximumWidth(90)
        cfg_lay.addWidget(self.thread_spin); cfg_lay.addStretch()
        self.start_btn_ttc = QPushButton("🚀  Bắt Đầu Tạo TK"); self.start_btn_ttc.setObjectName("btnSuccess")
        self.start_btn_ttc.setCursor(QCursor(Qt.PointingHandCursor)); self.start_btn_ttc.clicked.connect(self._start_creating)
        cfg_lay.addWidget(self.start_btn_ttc)
        lay.addWidget(cfg_frame)

        self.tree_create = self._make_tree(4, ["Tên tài khoản", "User", "Pass", "Token"])
        self.tree_create.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree_create.header().setSectionResizeMode(1, QHeaderView.Interactive); self.tree_create.header().resizeSection(1, 150)
        self.tree_create.header().setSectionResizeMode(2, QHeaderView.Interactive); self.tree_create.header().resizeSection(2, 120)
        self.tree_create.header().setSectionResizeMode(3, QHeaderView.Interactive); self.tree_create.header().resizeSection(3, 200)
        self.tree_create.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_create.customContextMenuRequested.connect(self._ctx_menu_create)
        lay.addWidget(self.tree_create, 1)

        self._log_panel = LogPanel()
        lay.addWidget(self._log_panel)
        return w

    def _refresh_tree_manage(self):
        self.tree_manage.clear()
        for idx, (user, data) in enumerate(self._ttc_data.items(), 1):
            item = QTreeWidgetItem()
            item.setCheckState(0, Qt.Unchecked)
            item.setIcon(0, QIcon(make_avatar_pixmap(user[0].upper() if user else "T", 22, idx % len(AVATAR_COLORS))))
            item.setText(0, user)
            item.setText(1, str(idx))
            pass_len = len(data.get("pass",""))
            item.setText(2, "●" * min(pass_len, 16) if pass_len else "(trống)")
            tk = data.get("token","")
            item.setText(3, tk[:36] + "…" if len(tk) > 36 else (tk or "(chưa có)"))
            xu = data.get("xu", 0)
            item.setText(4, str(xu))
            item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))
            item.setForeground(0, QColor("#d0d8e8"))
            item.setForeground(1, QColor("#4d8fff"))
            item.setForeground(2, QColor("#5a7099"))
            item.setForeground(3, QColor("#00d4aa") if tk else QColor("#3d5278"))
            item.setForeground(4, QColor("#f59e0b"))
            item.setData(0, Qt.UserRole, user)
            self.tree_manage.addTopLevelItem(item)

    def _get_checked_users(self, tree):
        users = []
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                user = item.data(0, Qt.UserRole)
                if user: users.append(user)
        return users

    def _ctx_menu_manage(self, pos):
        menu = QMenu(self); menu.setStyleSheet(STYLE)
        menu.addAction("☑  Chọn tất cả", lambda: self._select_all_tree(self.tree_manage))
        menu.addAction("☐  Bỏ chọn tất cả", lambda: self._deselect_all_tree(self.tree_manage))
        menu.addSeparator()
        menu.addAction("📋  Copy User", lambda: self._copy_col(self.tree_manage, 1, "user"))
        menu.addAction("📋  Copy Pass", lambda: self._copy_col(self.tree_manage, 2, "pass"))
        menu.addAction("📋  Copy Token", lambda: self._copy_col(self.tree_manage, 3, "token"))
        menu.addAction("📋  Copy User|Pass|Token", lambda: self._copy_all_col(self.tree_manage, [1,2,3]))
        menu.addSeparator()
        menu.addAction("�  Bôi đen tài khoản", lambda: self._select_single_account(self.tree_manage, pos))
        menu.addAction("�🗑  Xóa chọn", self._delete_selected_accounts)
        menu.exec_(self.tree_manage.viewport().mapToGlobal(pos))

    def _ctx_menu_create(self, pos):
        menu = QMenu(self); menu.setStyleSheet(STYLE)
        menu.addAction("☑  Chọn tất cả", lambda: self._select_all_tree(self.tree_create))
        menu.addAction("☐  Bỏ chọn tất cả", lambda: self._deselect_all_tree(self.tree_create))
        menu.addSeparator()
        menu.addAction("📋  Copy User", lambda: self._copy_col(self.tree_create, 1, "user"))
        menu.addAction("📋  Copy Pass", lambda: self._copy_col(self.tree_create, 2, "pass"))
        menu.addAction("📋  Copy Token", lambda: self._copy_col(self.tree_create, 3, "token"))
        menu.addAction("📋  Copy User|Pass|Token", lambda: self._copy_all_col(self.tree_create, [1,2,3]))
        menu.exec_(self.tree_create.viewport().mapToGlobal(pos))

    def _select_all_tree(self, tree):
        for i in range(tree.topLevelItemCount()): tree.topLevelItem(i).setCheckState(0, Qt.Checked)

    def _deselect_all_tree(self, tree):
        for i in range(tree.topLevelItemCount()): tree.topLevelItem(i).setCheckState(0, Qt.Unchecked)

    def _select_blacklisted_accounts(self, tree):
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            if item.background(0).color().name() == "#111111":
                item.setCheckState(0, Qt.Checked)

    def _select_single_account(self, tree, pos):
        item = tree.itemAt(pos)
        if not item: return
        for i in range(tree.topLevelItemCount()): tree.topLevelItem(i).setCheckState(0, Qt.Unchecked)
        item.setCheckState(0, Qt.Checked)
        for col in range(tree.columnCount()): item.setBackground(col, QColor("black"))

    def _copy_col(self, tree, col, field):
        texts = []
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                if field == "user": texts.append(item.data(0, Qt.UserRole) or "")
                elif field == "pass" and tree == self.tree_manage:
                    user = item.data(0, Qt.UserRole)
                    texts.append(self._ttc_data[user].get("pass", ""))
                else: texts.append(item.text(col))
        if texts: QApplication.clipboard().setText("\n".join(texts)); QMessageBox.information(self, "OK", f"Đã copy {len(texts)} dòng")

    def _copy_all_col(self, tree, cols):
        texts = []
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                row_parts = []
                for col in cols:
                    if col == 1 and tree == self.tree_manage:
                        user = item.data(0, Qt.UserRole)
                        row_parts.append(user or "")
                    elif col == 2 and tree == self.tree_manage:
                        user = item.data(0, Qt.UserRole)
                        row_parts.append(self._ttc_data[user].get("pass", ""))
                    else:
                        row_parts.append(item.text(col))
                row_data = "|".join(row_parts)
                texts.append(row_data)
        if texts: QApplication.clipboard().setText("\n".join(texts)); QMessageBox.information(self, "OK", f"Đã copy {len(texts)} dòng (user|pass|token)")

    def _add_single_account(self):
        dlg = QDialog(self); dlg.setWindowTitle("Thêm tài khoản TTC"); dlg.setMinimumWidth(400); dlg.setStyleSheet(STYLE)
        lay = QFormLayout(dlg); lay.setSpacing(10)
        user_in = QLineEdit(); pass_in = QLineEdit(); token_in = QLineEdit()
        pass_in.setEchoMode(QLineEdit.Password)
        lay.addRow("User:", user_in); lay.addRow("Pass:", pass_in); lay.addRow("Token:", token_in)
        btn_lay = QHBoxLayout()
        ok_btn = QPushButton("✔  Thêm"); ok_btn.setObjectName("btnPrimary"); ok_btn.clicked.connect(dlg.accept)
        cancel_btn = QPushButton("Huỷ"); cancel_btn.clicked.connect(dlg.reject)
        btn_lay.addStretch(); btn_lay.addWidget(cancel_btn); btn_lay.addWidget(ok_btn)
        lay.addRow("", btn_lay)
        if dlg.exec_() == QDialog.Accepted:
            user = user_in.text().strip()
            if user:
                self._ttc_data[user] = {"pass": pass_in.text(), "token": token_in.text(), "xu": 0}
                self._save_data(); self._refresh_tree_manage()

    def _add_bulk_accounts(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file tài khoản", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f: lines = f.readlines()
                for line in lines:
                    parts = line.strip().split('|')
                    if len(parts) >= 2 and parts[0]:
                        self._ttc_data[parts[0]] = {"pass": parts[1] if len(parts)>1 else "","token": parts[2] if len(parts)>2 else "","xu": 0}
                self._save_data(); self._refresh_tree_manage()
                QMessageBox.information(self, "Thành công", f"Đã import {len(lines)} tài khoản")
            except Exception as e: QMessageBox.warning(self, "Lỗi", f"Lỗi import: {str(e)}")

    def _delete_selected_accounts(self):
        to_delete = self._get_checked_users(self.tree_manage)
        if to_delete:
            ret = QMessageBox.question(self, "Xác nhận", f"Xóa {len(to_delete)} tài khoản?")
            if ret == QMessageBox.Yes:
                for user in to_delete: self._ttc_data.pop(user, None)
                self._save_data(); self._refresh_tree_manage()

    def _check_xu_selected(self):
        selected_users = self._get_checked_users(self.tree_manage)
        if not selected_users: QMessageBox.warning(self, "Thông báo", "Chọn ít nhất 1 tài khoản"); return
        
        try:
            from TTC.regworker import CheckXuBatchManager
            
            # Prepare user data with api keys
            users_list = [
                {"username": u, "api_key": self._ttc_data.get(u, {}).get("token", "")}
                for u in selected_users if self._ttc_data.get(u, {}).get("token")
            ]
            if not users_list: QMessageBox.warning(self, "Lỗi", "Không có token để kiểm tra"); return
            
            # Create progress dialog
            progress_dlg = CheckXuProgressDialog("Kiểm tra Xu TTC", self)
            progress_dlg.set_total(len(users_list))
            
            updated_count = 0
            
            def on_progress(username, current, total):
                progress_dlg.set_current(username, current, total)
            
            def on_done(username, xu):
                nonlocal updated_count
                self._ttc_data[username]["xu"] = xu
                updated_count += 1
            
            def on_all_done(results):
                progress_dlg.finish()
                self._save_data(); self._refresh_tree_manage()
                progress_dlg.accept()  # Close from callback
                QMessageBox.information(self, "Thành công", f"Đã cập nhật xu cho {updated_count}/{len(users_list)} tài khoản")
            
            # Start checking
            manager = CheckXuBatchManager(users_list, max_threads=5, callbacks={
                "progress": on_progress,
                "one_done": on_done,
                "all_done": on_all_done,
            })
            manager.start()
            
            # Show dialog
            progress_dlg.exec_()
        
        except ImportError as e:
            QMessageBox.warning(self, "Lỗi", f"Module chưa được cài đặt: {str(e)}")

    def _start_creating(self):
        num_accounts = self.thread_spin.value()
        num_threads = min(num_accounts, 5)  # Tối đa 5 luồng
        try:
            from TTC.regworker import TTCRegBatchManager
            
            self.tree_create.clear()
            if self._log_panel: self._log_panel.clear()
            if self._log_panel: self._log_panel.append(f"[→] Khởi động tạo {num_accounts} TK với {num_threads} luồng...")
            
            self.start_btn_ttc.setEnabled(False)
            
            callbacks = {
                "log_msg": self._log_panel.append if self._log_panel else None,
                "one_done": self._on_ttc_account_done,
                "all_done": self._on_ttc_all_finished,
            }
            
            self._reg_batch_manager = TTCRegBatchManager(num_accounts, num_threads, callbacks)
            self._reg_batch_manager.start()
        except ImportError as e: 
            self.start_btn_ttc.setEnabled(True)
            QMessageBox.warning(self, "Lỗi", f"Module chưa được cài đặt: {str(e)}")
        except Exception as e:
            self.start_btn_ttc.setEnabled(True)
            QMessageBox.warning(self, "Lỗi", f"Lỗi: {str(e)}")

    def _on_ttc_account_done(self, worker_id, result):
        """Khi tạo xong 1 tài khoản."""
        if result.get("ok"):
            user = result.get("username", "")
            item = QTreeWidgetItem(); item.setCheckState(0, Qt.Unchecked)
            item.setIcon(0, QIcon(make_avatar_pixmap(user[0].upper() if user else "T", 22)))
            item.setText(0, user); item.setText(1, user); item.setText(2, result.get('password',''))
            tk = result.get('token','')
            item.setText(3, tk[:40]+"…" if len(tk)>40 else tk)
            item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))
            item.setForeground(0, QColor("#d0d8e8")); item.setForeground(1, QColor("#4d8fff"))
            item.setForeground(2, QColor("#5a7099")); item.setForeground(3, QColor("#00d4aa"))
            item.setData(0, Qt.UserRole, user)
            self.tree_create.addTopLevelItem(item)
            self._ttc_data[user] = {"pass": result.get('password',''), "token": tk, "xu": 0}

    def _on_ttc_all_finished(self, results):
        """Khi tạo xong tất cả tài khoản."""
        if self._log_panel: self._log_panel.append(f"[✓] Hoàn thành! Tạo được {len(results)} tài khoản")
        self._save_data(); self._refresh_tree_manage()
        self.start_btn_ttc.setEnabled(True)

    def _on_ttc_finished(self, results):
        if self._log_panel: self._log_panel.append(f"[✓] Hoàn thành! Tạo được {len(results)} tài khoản")
        self.tree_create.clear()
        for idx, result in enumerate(results, 1):
            item = QTreeWidgetItem(); item.setCheckState(0, Qt.Unchecked)
            user = result.get('user', '')
            item.setIcon(0, QIcon(make_avatar_pixmap(user[0].upper() if user else "T", 22, idx % len(AVATAR_COLORS))))
            item.setText(0, user); item.setText(1, user); item.setText(2, result.get('password',''))
            tk = result.get('token','')
            item.setText(3, tk[:40]+"…" if len(tk)>40 else tk)
            item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))
            item.setForeground(0, QColor("#d0d8e8")); item.setForeground(1, QColor("#4d8fff"))
            item.setForeground(2, QColor("#5a7099")); item.setForeground(3, QColor("#00d4aa") if tk else QColor("#3d5278"))
            item.setData(0, Qt.UserRole, user)
            self.tree_create.addTopLevelItem(item)
            if user: self._ttc_data[user] = {"pass": result.get('password',''), "token": tk, "xu": 0}
        self._save_data(); self._refresh_tree_manage()

    def _on_ttc_error(self, error_msg):
        if self._log_panel: self._log_panel.append(f"[✘] Lỗi: {error_msg}")
        QMessageBox.warning(self, "Lỗi", error_msg)

    def _on_ttc_progress(self, msg):
        if self._log_panel: self._log_panel.append(msg)

    def _load_data(self):
        try:
            if os.path.exists(self._data_file):
                with open(self._data_file, 'r', encoding='utf-8') as f: self._ttc_data = json.load(f)
        except: self._ttc_data = {}

    def _save_data(self):
        try:
            with open(self._data_file, 'w', encoding='utf-8') as f: json.dump(self._ttc_data, f, ensure_ascii=False, indent=2)
        except: pass


# ─────────────────────────────────────────────────────────────────────────────
#  RUN LOG SIGNAL EMITTER (for thread-safe logging)
# ─────────────────────────────────────────────────────────────────────────────
class RunLogSignalEmitter(QObject):
    """Emit signals for logging from background threads - thread safe"""
    log_signal = pyqtSignal(str)
    tree_signal = pyqtSignal(str, str, str)  # user, status, xu (str)
    stats_signal = pyqtSignal(int, int, int)  # tasks_done, xu_earned, tasks_error
    button_state_signal = pyqtSignal(str, bool)  # button_name, enabled (True/False)

# ─────────────────────────────────────────────────────────────────────────────
#  TTC RUN PAGE
# ─────────────────────────────────────────────────────────────────────────────
class TTCRunPage(QWidget):
    def __init__(self, ttc_management_page, parent=None):
        super().__init__(parent)
        self.ttc_mgmt = ttc_management_page
        self._profiles = {}
        self._current_profile = "Default"
        self._profiles_file = "ttc_run_profiles.json"
        
        # Task definitions from tuongtaccheo
        self.AVAILABLE_TASKS = {
            "Like VIP": {"code_name": "likepostvipcheo", "min": 5, "max": 60, "count": 1, "icon": "👍"},
            "Like Thường": {"code_name": "likepostvipre", "min": 5, "max": 60, "count": 1, "icon": "👍"},
            "Cảm Xúc VIP": {"code_name": "camxucvipcheo", "min": 5, "max": 60, "count": 1, "icon": "❤️"},
            "Cảm Xúc Thường": {"code_name": "camxucvipre", "min": 5, "max": 60, "count": 1, "icon": "❤️"},
            "Bình Luận": {"code_name": "cmtcheo", "min": 10, "max": 120, "count": 5, "icon": "💬"},
            "Theo Dõi": {"code_name": "subcheo", "min": 5, "max": 60, "count": 1, "icon": "👤"},
            # "Theo Dõi VIP": {"code_name": "subcheofbvip", "min": 5, "max": 60, "count": 1, "icon": "👤"},
            "Share": {"code_name": "sharecheo", "min": 10, "max": 120, "count": 1, "icon": "↗️"},
        }
        
        self._run_settings = {
            "api_key": "", "delay_short": 5, "delay_long": 60,
            "delay_after_tasks": 5, "stop_after_tasks": 100,
            "tasks": [],
            "task_settings": {}
        }
        
        # Initialize default task settings
        for task_name, defaults in self.AVAILABLE_TASKS.items():
            self._run_settings["task_settings"][task_name] = {
                "enabled": False,
                "delay_min": defaults["min"],
                "delay_max": defaults["max"],
                "count": defaults["count"]
            }
        
        # Load profiles from file (UI independent)
        self._load_profiles_from_file()
        
        # Create signal emitter for thread-safe logging
        self.log_emitter = RunLogSignalEmitter()
        
        # Runner references (for stop functionality)
        self._ttc_runner = None
        self._ttc_run_thread = None

        root_lay = QVBoxLayout(self); root_lay.setContentsMargins(20,16,20,16); root_lay.setSpacing(12)

        # ── Header ──────────────────────────────────────────────────────
        hdr = QHBoxLayout(); hdr.setSpacing(14)
        icon = QLabel("🚀"); icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #b45309,stop:1 #f59e0b);border-radius:12px;color:white;font-size:20px;font-weight:800;min-width:46px;max-width:46px;min-height:46px;max-height:46px;")
        hdr.addWidget(icon)
        hdr_text = QVBoxLayout(); hdr_text.setSpacing(2)
        t1 = QLabel("Chạy TTC"); t1.setObjectName("PageTitle")
        t2 = QLabel("Chạy nhiệm vụ tương tác trên tài khoản TTC"); t2.setObjectName("PageSub")
        hdr_text.addWidget(t1); hdr_text.addWidget(t2)
        hdr.addLayout(hdr_text); hdr.addStretch()
        root_lay.addLayout(hdr)

        # ── Profile bar ──────────────────────────────────────────────────
        profile_bar = QFrame()
        profile_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0d1a2e,stop:1 #111827);
                border: 1px solid #1e3050;
                border-radius: 12px;
            }
        """)
        pb_lay = QHBoxLayout(profile_bar); pb_lay.setContentsMargins(16,12,16,12); pb_lay.setSpacing(10)

        pf_icon = QLabel("📁"); pf_icon.setStyleSheet("font-size:20px; background:transparent;")
        pb_lay.addWidget(pf_icon)

        pf_label_wrap = QVBoxLayout(); pf_label_wrap.setSpacing(2)
        pf_title = QLabel("PROFILE")
        pf_title.setStyleSheet("color:#3d6090;font-size:9px;font-family:Consolas;font-weight:700;letter-spacing:2px;text-transform:uppercase;background:transparent;")
        pf_label_wrap.addWidget(pf_title)
        pb_lay.addLayout(pf_label_wrap)

        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(180); self.profile_combo.setMinimumHeight(34)
        self.profile_combo.setStyleSheet("""
            QComboBox {
                background: #0d1629; border: 1px solid #2e4570;
                border-radius: 8px; padding: 5px 12px; color: #c9d6ea;
                font-size: 12px; font-weight: 600; min-height: 32px;
            }
            QComboBox:hover { border-color: #4d78cc; }
            QComboBox::drop-down { border: none; width: 24px; }
            QComboBox QAbstractItemView {
                background: #111827; border: 1px solid #2e4570;
                color: #c9d6ea; selection-background-color: #0d1e38;
            }
        """)
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        pb_lay.addWidget(self.profile_combo)

        # Profile action buttons
        for label, obj_name, slot in [
            ("💾  Lưu", "btnSuccess", self._save_current_profile),
            ("📂  Tải", "btnPrimary", self._load_profile_dialog),
            ("➕  Mới", "btnInfo", self._new_profile_dialog),
            ("🗑  Xóa", "btnDanger", self._delete_profile_dialog),
        ]:
            btn = QPushButton(label)
            btn.setObjectName(obj_name); btn.setMinimumHeight(34); btn.setMinimumWidth(90)
            btn.setCursor(QCursor(Qt.PointingHandCursor)); btn.clicked.connect(slot)
            pb_lay.addWidget(btn)

        pb_lay.addStretch()

        b_settings = QPushButton("⚙  Cài Đặt Chạy")
        b_settings.setObjectName("btnWarn"); b_settings.setMinimumHeight(34); b_settings.setMinimumWidth(130)
        b_settings.setCursor(QCursor(Qt.PointingHandCursor))
        b_settings.clicked.connect(self._open_settings_dialog)
        pb_lay.addWidget(b_settings)

        self._settings_badge = QLabel("⚙ Chưa cấu hình")
        self._settings_badge.setStyleSheet("color:#3d5278;font-size:10px;font-family:Consolas;background:transparent;")
        pb_lay.addWidget(self._settings_badge)
        
        # Now update UI with loaded profiles
        self._update_profile_ui()

        root_lay.addWidget(profile_bar)

        # ── Statistics bar ───────────────────────────────────────────────
        stats_bar = QFrame()
        stats_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0d1a2e,stop:1 #111827);
                border: 1px solid #1e3050;
                border-radius: 12px;
            }
        """)
        stats_lay = QHBoxLayout(stats_bar); stats_lay.setContentsMargins(16,12,16,12); stats_lay.setSpacing(20)
        
        # Stat 1: Tasks completed
        self._stat_tasks_done = self._create_stat_widget("✅ Nhiệm vụ đã làm", "0", "#4d8fff")
        stats_lay.addWidget(self._stat_tasks_done, 1)
        
        # Stat 2: XU earned
        self._stat_xu_earned = self._create_stat_widget("💰 Xu nhận được", "0", "#00d4aa")
        stats_lay.addWidget(self._stat_xu_earned, 1)
        
        # Stat 3: Tasks error
        self._stat_tasks_error = self._create_stat_widget("❌ Nhiệm vụ lỗi", "0", "#ef4444")
        stats_lay.addWidget(self._stat_tasks_error, 1)
        
        stats_lay.addStretch()
        root_lay.addWidget(stats_bar)

        # ── Main content ─────────────────────────────────────────────────
        content_row = QHBoxLayout(); content_row.setSpacing(10)

        tree_wrap = QWidget(); tree_wrap.setStyleSheet("background:#0d1219;")
        tree_lay = QVBoxLayout(tree_wrap); tree_lay.setContentsMargins(0,0,0,0); tree_lay.setSpacing(6)
        tree_hdr = make_section_header("DANH SÁCH TÀI KHOẢN", "TTC + Facebook pairing")
        tree_lay.addWidget(tree_hdr)

        self.tree_run = QTreeWidget(); self.tree_run.setObjectName("FbTree")
        self.tree_run.setColumnCount(10)
        self.tree_run.setHeaderLabels(["Tên","User TTC","Pass TTC","Token TTC","UID FB","Cookie FB","Proxy FB","Token FB","Status","Xu"])
        self.tree_run.header().setSectionResizeMode(0, QHeaderView.Stretch)
        for col, w in enumerate([100,85,100,80,100,90,100,100], 1):
            self.tree_run.header().setSectionResizeMode(col, QHeaderView.Interactive)
            self.tree_run.header().resizeSection(col, w)
        self.tree_run.header().setSectionResizeMode(8, QHeaderView.Interactive); self.tree_run.header().resizeSection(8, 100)
        self.tree_run.header().setSectionResizeMode(9, QHeaderView.Interactive); self.tree_run.header().resizeSection(9, 80)
        self.tree_run.setAlternatingRowColors(True)
        self.tree_run.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree_run.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tree_run.setIndentation(0)
        self.tree_run.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_run.customContextMenuRequested.connect(self._ctx_menu_run)
        tree_lay.addWidget(self.tree_run, 1)
        
        # Load accounts from current profile now that tree_run is created
        self._load_accounts_from_profile()
        
        content_row.addWidget(tree_wrap, 3)

        log_wrap = QWidget(); log_wrap.setStyleSheet("background:#0d1219;")
        log_lay = QVBoxLayout(log_wrap); log_lay.setContentsMargins(0,0,0,0); log_lay.setSpacing(6)
        log_hdr = make_section_header("RUN LOG", "Nhật ký hoạt động")
        log_lay.addWidget(log_hdr)
        self._run_log_panel = LogPanel()
        self._run_log_panel.setMaximumHeight(99999)
        log_lay.addWidget(self._run_log_panel, 1)
        
        # Connect signal emitter to log panel
        self.log_emitter.log_signal.connect(self._run_log_panel.append)
        self.log_emitter.tree_signal.connect(self._on_tree_update_signal)
        self.log_emitter.button_state_signal.connect(self._on_button_state_changed)
        
        content_row.addWidget(log_wrap, 1)
        root_lay.addLayout(content_row, 1)

        # ── Action buttons ───────────────────────────────────────────────
        btn_lay = QHBoxLayout(); btn_lay.setSpacing(8)
        self._btn_add_accounts = None
        self._btn_start_run = None
        self._btn_stop_run = None
        self._btn_clear_list = None
        
        for label, obj_name, slot, var_name in [
            ("➕  Thêm TK vào danh sách", "btnPrimary", self._add_accounts_to_run, "_btn_add_accounts"),
            ("▶  Bắt Đầu Chạy",          "btnSuccess", self._start_running, "_btn_start_run"),
            ("⏹  Dừng Chạy",             "btnDanger",  self._stop_running, "_btn_stop_run"),
            ("🗑  Xóa Danh Sách",         "btnDanger",  self._clear_run_list, "_btn_clear_list"),
        ]:
            btn = QPushButton(label); btn.setObjectName(obj_name); btn.setMinimumHeight(36)
            btn.setCursor(QCursor(Qt.PointingHandCursor)); btn.clicked.connect(slot); btn_lay.addWidget(btn)
            setattr(self, var_name, btn)
        
        # Initially disable stop button since nothing is running
        self._btn_stop_run.setEnabled(False)
        
        btn_lay.addStretch()
        root_lay.addLayout(btn_lay)

    # ── Profile Management ───────────────────────────────────────────────────
    def _load_profiles_from_file(self):
        """Load profiles từ file JSON (data only, no UI updates)."""
        try:
            if os.path.exists(self._profiles_file):
                with open(self._profiles_file, 'r', encoding='utf-8') as f:
                    self._profiles = json.load(f)
            else:
                self._profiles = {"Default": self._run_settings.copy()}
        except Exception:
            self._profiles = {"Default": self._run_settings.copy()}
    
    def _update_profile_ui(self):
        """Update UI elements with loaded profiles (called after UI is created)."""
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for pname in sorted(self._profiles.keys()):
            self.profile_combo.addItem(pname)
        self.profile_combo.blockSignals(False)
        self._load_profile_settings("Default")

    def _save_profiles(self):
        """Save profiles vào file JSON."""
        try:
            with open(self._profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self._profiles, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu profiles: {str(e)}")
    
    def _save_accounts_to_profile(self):
        """Lưu danh sách tài khoản hiện tại vào profile."""
        accounts = []
        for i in range(self.tree_run.topLevelItemCount()):
            item = self.tree_run.topLevelItem(i)
            # Lấy full data từ setData (không bị cắt)
            full_data = item.data(0, Qt.UserRole)
            if full_data:
                accounts.append(full_data)
            else:
                # Fallback: nếu không có setData, lấy từ text (cắt ngắn)
                account = {
                    "ttc_user": item.text(1),
                    "ttc_pass": item.text(2),
                    "ttc_token": item.text(3),
                    "fb_uid": item.text(4),
                    "fb_cookie": item.text(5),
                    "fb_proxy": item.text(6),
                    "fb_token": item.text(7),
                }
                accounts.append(account)
        
        pname = self._current_profile or "Default"
        if "accounts" not in self._profiles[pname]:
            self._profiles[pname]["accounts"] = []
        self._profiles[pname]["accounts"] = accounts
        self._save_profiles()
    
    def _load_accounts_from_profile(self):
        """Tải danh sách tài khoản từ profile."""
        self.tree_run.clear()
        pname = self._current_profile or "Default"
        accounts = self._profiles[pname].get("accounts", [])
        
        for idx, acc in enumerate(accounts):
            new_item = self._make_run_item(
                ttc_user=acc.get("ttc_user", ""),
                ttc_pass=acc.get("ttc_pass", ""),
                ttc_token=acc.get("ttc_token", ""),
                fb_uid=acc.get("fb_uid", ""),
                fb_cookie=acc.get("fb_cookie", ""),
                fb_proxy=acc.get("fb_proxy", ""),
                fb_token=acc.get("fb_token", ""),
                row_idx=idx
            )
            self.tree_run.addTopLevelItem(new_item)

    def _save_current_profile(self):
        """Lưu settings hiện tại vào profile được chọn."""
        pname = self.profile_combo.currentText() or "Default"
        if not pname:
            QMessageBox.warning(self, "Lỗi", "Chưa chọn profile"); return
        
        self._profiles[pname] = self._run_settings.copy()
        self._save_profiles()
        QMessageBox.information(self, "Thành công", f"Đã lưu profile: {pname}")

    def _load_profile_settings(self, pname):
        """Load settings từ profile."""
        if pname not in self._profiles:
            pname = "Default"
        
        self._current_profile = pname
        self._run_settings = self._profiles[pname].copy()
        
        # Update badge
        tasks_str = ", ".join(self._run_settings.get("tasks", [])) or "—"
        self._settings_badge.setText(f"📌 {pname} | {tasks_str[:30]}")
        
        # Load accounts from profile only if tree_run exists (after initialization)
        if hasattr(self, 'tree_run') and self.tree_run:
            self._load_accounts_from_profile()

    def _on_profile_changed(self, pname):
        """Khi chọn profile khác."""
        if pname:
            self._load_profile_settings(pname)

    def _new_profile_dialog(self):
        """Dialog tạo profile mới."""
        dlg = QDialog(self); dlg.setWindowTitle("📋 Tạo Profile Mới")
        dlg.setMinimumWidth(380); dlg.setStyleSheet(STYLE)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(20,16,20,16); lay.setSpacing(12)
        
        QLabel("Tên Profile:").setStyleSheet("color:#c9d6ea;font-size:12px;font-weight:600;")
        lay.addWidget(QLabel("Tên Profile:"))
        inp_name = QLineEdit(); inp_name.setMinimumHeight(36); inp_name.setPlaceholderText("VD: Config1, Config Nhanh, ...")
        lay.addWidget(inp_name)
        
        lay.addSpacing(8)
        QLabel("Chọn Profile để copy (optional):").setStyleSheet("color:#c9d6ea;font-size:12px;font-weight:600;")
        lay.addWidget(QLabel("Chọn Profile để copy (optional):"))
        combo = QComboBox(); combo.setMinimumHeight(36)
        combo.addItem("(Tạo mới từ trống)")
        for pname in sorted(self._profiles.keys()):
            combo.addItem(pname)
        lay.addWidget(combo)
        
        lay.addStretch()
        
        btn_lay = QHBoxLayout(); btn_lay.setSpacing(8)
        cancel_btn = QPushButton("Huỷ"); cancel_btn.setMinimumHeight(36); cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(dlg.reject)
        ok_btn = QPushButton("✔  Tạo"); ok_btn.setObjectName("btnSuccess")
        ok_btn.setMinimumHeight(36); ok_btn.setMinimumWidth(120)
        ok_btn.clicked.connect(dlg.accept)
        btn_lay.addStretch(); btn_lay.addWidget(cancel_btn); btn_lay.addWidget(ok_btn)
        lay.addLayout(btn_lay)
        
        if dlg.exec_() == QDialog.Accepted:
            pname = inp_name.text().strip()
            if not pname:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên profile"); return
            if pname in self._profiles:
                QMessageBox.warning(self, "Lỗi", f"Profile '{pname}' đã tồn tại"); return
            
            # Copy settings từ profile được chọn hoặc tạo mới
            source = combo.currentText()
            if source == "(Tạo mới từ trống)":
                self._profiles[pname] = {
                    "api_key": "", "delay_short": 5, "delay_long": 60,
                    "delay_after_tasks": 5, "stop_after_tasks": 100,
                    "tasks": [], "task_settings": {}
                }
                for task_name, defaults in self.AVAILABLE_TASKS.items():
                    self._profiles[pname]["task_settings"][task_name] = {
                        "enabled": False, "delay_min": defaults["min"],
                        "delay_max": defaults["max"], "count": defaults["count"]
                    }
            else:
                self._profiles[pname] = self._profiles[source].copy()
            
            self._save_profiles()
            self._update_profile_ui()
            self.profile_combo.setCurrentText(pname)
            QMessageBox.information(self, "Thành công", f"Đã tạo profile: {pname}")

    def _load_profile_dialog(self):
        """Dialog để chọn load profile."""
        dlg = QDialog(self); dlg.setWindowTitle("📂 Tải Profile")
        dlg.setMinimumWidth(300); dlg.setStyleSheet(STYLE)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(20,16,20,16); lay.setSpacing(12)
        
        lay.addWidget(QLabel("Chọn profile:"))
        combo = QComboBox(); combo.setMinimumHeight(36)
        for pname in sorted(self._profiles.keys()):
            combo.addItem(pname)
        lay.addWidget(combo)
        lay.addStretch()
        
        btn_lay = QHBoxLayout(); btn_lay.setSpacing(8)
        cancel_btn = QPushButton("Huỷ"); cancel_btn.setMinimumHeight(36)
        cancel_btn.clicked.connect(dlg.reject)
        ok_btn = QPushButton("✔  Tải"); ok_btn.setObjectName("btnSuccess")
        ok_btn.setMinimumHeight(36); ok_btn.clicked.connect(dlg.accept)
        btn_lay.addStretch(); btn_lay.addWidget(cancel_btn); btn_lay.addWidget(ok_btn)
        lay.addLayout(btn_lay)
        
        if dlg.exec_() == QDialog.Accepted:
            pname = combo.currentText()
            self.profile_combo.setCurrentText(pname)
            QMessageBox.information(self, "Thành công", f"Đã tải profile: {pname}")

    def _delete_profile_dialog(self):
        """Dialog xác nhận xóa profile."""
        pname = self.profile_combo.currentText()
        if not pname or pname == "Default":
            QMessageBox.warning(self, "Lỗi", "Không thể xóa profile 'Default'"); return
        
        ret = QMessageBox.question(self, "Xác nhận", f"Xóa profile '{pname}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            del self._profiles[pname]
            self._save_profiles()
            self._update_profile_ui()
            QMessageBox.information(self, "Thành công", f"Đã xóa profile: {pname}")

    # ── Settings Modal ───────────────────────────────────────────────────────
    def _open_settings_dialog(self):
        pname = self.profile_combo.currentText() or "Default"
        dlg = QDialog(self); dlg.setWindowTitle(f"⚙  Cài Đặt — {pname}")
        dlg.setMinimumWidth(720); dlg.setMinimumHeight(850); dlg.setStyleSheet(STYLE)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)

        # Title bar
        title_bar = QFrame()
        title_bar.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0d1629,stop:1 #111827);border-bottom:1px solid #1e3050;")
        title_bar.setFixedHeight(68)
        tb_lay = QHBoxLayout(title_bar); tb_lay.setContentsMargins(20,0,20,0); tb_lay.setSpacing(14)
        tb_icon = QLabel("⚙"); tb_icon.setStyleSheet("font-size:28px;background:transparent;")
        tb_title = QVBoxLayout(); tb_title.setSpacing(2)
        tb_t1 = QLabel(f"Cài Đặt Profile: {pname}"); tb_t1.setStyleSheet("color:#e8edf5;font-size:15px;font-weight:800;background:transparent;")
        tb_t2 = QLabel("Cấu hình tasks, delays & API key"); tb_t2.setStyleSheet("color:#6b7d9f;font-size:11px;font-family:Consolas;background:transparent;")
        tb_title.addWidget(tb_t1); tb_title.addWidget(tb_t2)
        tb_lay.addWidget(tb_icon); tb_lay.addLayout(tb_title); tb_lay.addStretch()
        lay.addWidget(title_bar)

        # Body
        body = QWidget(); body.setStyleSheet("background:#0b0f14;")
        body_lay = QVBoxLayout(body); body_lay.setContentsMargins(20,16,20,16); body_lay.setSpacing(16)

        # API Key Section
        api_section = QFrame(); api_section.setStyleSheet("background:#111827;border:1px solid #1a2336;border-radius:10px;")
        api_lay = QVBoxLayout(api_section); api_lay.setContentsMargins(14,12,14,12); api_lay.setSpacing(8)
        api_hdr = QLabel("🔑  API Key 3xcaptcha"); api_hdr.setStyleSheet("color:#c9d6ea;font-size:11px;font-weight:700;font-family:Consolas;letter-spacing:1px;text-transform:uppercase;background:transparent;")
        api_lay.addWidget(api_hdr)
        self._dlg_api_key = QLineEdit(); self._dlg_api_key.setPlaceholderText("Nhập API key từ 3xcaptcha.com...")
        self._dlg_api_key.setText(self._run_settings.get("api_key",""))
        self._dlg_api_key.setMinimumHeight(36)
        api_lay.addWidget(self._dlg_api_key)
        body_lay.addWidget(api_section)

        # Tasks — Mở rộng với delay settings từng task
        tasks_section = QFrame(); tasks_section.setStyleSheet("background:#111827;border:1px solid #1a2336;border-radius:10px;")
        tasks_lay = QVBoxLayout(tasks_section); tasks_lay.setContentsMargins(14,12,14,12); tasks_lay.setSpacing(10)
        tasks_hdr = QLabel("⚡  NHIỆM VỤ & CẤU HÌNH"); tasks_hdr.setStyleSheet("color:#c9d6ea;font-size:11px;font-weight:700;font-family:Consolas;letter-spacing:1px;text-transform:uppercase;background:transparent;")
        tasks_lay.addWidget(tasks_hdr)
        
        # Scroll area for tasks
        task_scroll = QScrollArea(); task_scroll.setWidgetResizable(True); task_scroll.setFrameShape(QFrame.NoFrame)
        task_scroll.setStyleSheet("QScrollArea{background:#0d1629;border:1px solid #1e3050;border-radius:8px;}")
        task_scroll.setMaximumHeight(320)
        task_container = QWidget(); task_container.setStyleSheet("background:#0d1629;")
        task_scroll_lay = QVBoxLayout(task_container); task_scroll_lay.setContentsMargins(8,8,8,8); task_scroll_lay.setSpacing(8)
        
        self._dlg_task_spins = {}
        for task_name in self.AVAILABLE_TASKS.keys():
            task_cfg = self._run_settings["task_settings"].get(task_name, self.AVAILABLE_TASKS[task_name])
            
            task_item = QFrame(); task_item.setStyleSheet("background:#0b0f14;border:1px solid #1a2336;border-radius:6px;")
            task_item_lay = QVBoxLayout(task_item); task_item_lay.setContentsMargins(10,8,10,8); task_item_lay.setSpacing(6)
            
            # Header with checkbox
            task_header = QHBoxLayout(); task_header.setSpacing(8)
            icon = QLabel(self.AVAILABLE_TASKS[task_name]["icon"]); icon.setStyleSheet("font-size:14px;")
            chk = QCheckBox(task_name); chk.setChecked(task_cfg.get("enabled", False))
            chk.setStyleSheet("QCheckBox{color:#c9d6ea;font-size:11px;font-weight:600;background:transparent;spacing:6px;} QCheckBox::indicator{width:14px;height:14px;border:1px solid #2e4570;border-radius:3px;background:#0a1020;} QCheckBox::indicator:checked{background:#4d8fff;border-color:#4d8fff;}")
            task_header.addWidget(icon); task_header.addWidget(chk); task_header.addStretch()
            task_item_lay.addLayout(task_header)
            
            # Settings for this task
            settings_lay = QGridLayout(); settings_lay.setSpacing(6)
            spins = {}
            
            for col, (label, key, suffix) in enumerate([("Min (s)", "delay_min", "s"), ("Max (s)", "delay_max", "s"), ("Số lần", "count", "")]):
                lbl = QLabel(label); lbl.setStyleSheet("color:#8b9aaf;font-size:9px;font-family:Consolas;background:transparent;")
                spin = make_spinbox(task_cfg.get(key, self.AVAILABLE_TASKS[task_name].get(key, 1)), 1, 600 if "delay" in key else 10000, suffix)
                spin.setMaximumWidth(120); spin.setMinimumHeight(28)
                spins[key] = spin
                settings_lay.addWidget(lbl, 0, col)
                settings_lay.addWidget(spin, 1, col)
            
            # Add stretch column for proper layout
            settings_lay.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 1, 3)
            
            self._dlg_task_spins[task_name] = (chk, spins)
            task_item_lay.addLayout(settings_lay)
            task_scroll_lay.addWidget(task_item)
        
        task_scroll_lay.addStretch()
        task_scroll.setWidget(task_container)
        tasks_lay.addWidget(task_scroll)
        body_lay.addWidget(tasks_section)

        # Timing — Global delays
        timing_section = QFrame(); timing_section.setStyleSheet("background:#111827;border:1px solid #1a2336;border-radius:10px;")
        timing_lay = QVBoxLayout(timing_section); timing_lay.setContentsMargins(14,12,14,12); timing_lay.setSpacing(10)
        timing_hdr = QLabel("⏱  Delay Toàn Cục & Giới Hạn"); timing_hdr.setStyleSheet("color:#c9d6ea;font-size:11px;font-weight:700;font-family:Consolas;letter-spacing:1px;text-transform:uppercase;background:transparent;")
        timing_lay.addWidget(timing_hdr)
        timing_grid = QHBoxLayout(); timing_grid.setSpacing(8)

        self._dlg_spins = {}
        for label, key, val, suffix, mn, mx, color in [
            ("Delay Ngắn",       "delay_short",       5,   "s", 1,   300, "#4d8fff"),
            ("Delay Dài",        "delay_long",         60,  "s", 10,  600, "#a78bfa"),
            ("Sau N Task",       "delay_after_tasks",  5,   "",  1,   50,  "#f59e0b"),
            ("Dừng Sau",         "stop_after_tasks",   100, "",  1,   10000,"#ef4444"),
        ]:
            spin_card = QFrame(); spin_card.setStyleSheet("background:#0d1629;border:1px solid #1e3050;border-radius:8px;")
            spin_card_lay = QVBoxLayout(spin_card); spin_card_lay.setContentsMargins(10,8,10,8); spin_card_lay.setSpacing(4)
            lbl = QLabel(label); lbl.setStyleSheet(f"color:{color};font-size:9px;font-family:Consolas;font-weight:700;letter-spacing:1px;text-transform:uppercase;background:transparent;")
            spin = make_spinbox(self._run_settings.get(key, val), mn, mx, suffix)
            spin.setMinimumHeight(34); spin.setMaximumWidth(140)
            self._dlg_spins[key] = spin
            spin_card_lay.addWidget(lbl); spin_card_lay.addWidget(spin)
            timing_grid.addWidget(spin_card)
        timing_lay.addLayout(timing_grid)
        body_lay.addWidget(timing_section)
        body_lay.addStretch()
        lay.addWidget(body, 1)

        # Footer
        footer = QFrame(); footer.setStyleSheet("background:#0d1219;border-top:1px solid #1a2336;")
        footer.setFixedHeight(60)
        ft_lay = QHBoxLayout(footer); ft_lay.setContentsMargins(20,0,20,0); ft_lay.setSpacing(8)
        
        reset_btn = QPushButton("🔄  Reset"); reset_btn.setMinimumHeight(36); reset_btn.setMinimumWidth(100)
        reset_btn.setCursor(QCursor(Qt.PointingHandCursor))
        reset_btn.clicked.connect(lambda: self._reload_settings_dialog_values(dlg) if hasattr(self, '_dlg_spins') else None)
        ft_lay.addWidget(reset_btn)
        
        ft_lay.addStretch()
        
        cancel_btn = QPushButton("❌  Đóng"); cancel_btn.setMinimumHeight(36); cancel_btn.setMinimumWidth(100)
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor)); cancel_btn.clicked.connect(dlg.reject)
        
        apply_btn = QPushButton("✔  Áp Dụng & Lưu"); apply_btn.setObjectName("btnSuccess")
        apply_btn.setMinimumHeight(36); apply_btn.setMinimumWidth(150)
        apply_btn.setCursor(QCursor(Qt.PointingHandCursor)); apply_btn.clicked.connect(dlg.accept)
        
        ft_lay.addWidget(cancel_btn); ft_lay.addWidget(apply_btn)
        lay.addWidget(footer)

        if dlg.exec_() == QDialog.Accepted:
            self._run_settings["api_key"] = self._dlg_api_key.text().strip()
            
            # Save per-task settings
            self._run_settings["task_settings"] = {}
            self._run_settings["tasks"] = []
            for task_name, (chk, spins) in self._dlg_task_spins.items():
                is_enabled = chk.isChecked()
                self._run_settings["task_settings"][task_name] = {
                    "enabled": is_enabled,
                    "delay_min": spins["delay_min"].value(),
                    "delay_max": spins["delay_max"].value(),
                    "count": spins["count"].value()
                }
                if is_enabled:
                    self._run_settings["tasks"].append(task_name)
            
            # Save global timing settings
            for key, spin in self._dlg_spins.items():
                self._run_settings[key] = spin.value()
            
            # Save profile
            self._profiles[self._current_profile] = self._run_settings.copy()
            self._save_profiles()
            
            tasks_str = ", ".join(self._run_settings["tasks"]) or "—"
            self._settings_badge.setText(f"📌 {self._current_profile} | {tasks_str[:40]}")
            self._settings_badge.setStyleSheet("color:#10b981;font-size:10px;font-family:Consolas;background:transparent;")
            QMessageBox.information(self, "Thành công", f"Đã lưu cài đặt cho profile '{self._current_profile}'")

    def _reload_settings_dialog_values(self, dlg):
        """Reset values về trạng thái ban đầu."""
        self._dlg_api_key.setText(self._run_settings.get("api_key", ""))
        for task_name, (chk, spins) in self._dlg_task_spins.items():
            cfg = self._run_settings["task_settings"].get(task_name, {})
            chk.setChecked(cfg.get("enabled", False))
            spins["delay_min"].setValue(cfg.get("delay_min", 5))
            spins["delay_max"].setValue(cfg.get("delay_max", 60))
            spins["count"].setValue(cfg.get("count", 1))
        for key, spin in self._dlg_spins.items():
            spin.setValue(self._run_settings.get(key, 100))

    # ── Profile Dialog ───────────────────────────────────────────────────────
    def _create_profile_dialog(self):
        dlg = QDialog(self); dlg.setWindowTitle("Tạo Profile Mới"); dlg.setMinimumWidth(340); dlg.setStyleSheet(STYLE)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(20,16,20,16); lay.setSpacing(12)

        title = QLabel("📁  Tạo Profile Mới")
        title.setStyleSheet("color:#e8edf5;font-size:14px;font-weight:800;background:transparent;")
        lay.addWidget(title)

        form = QFormLayout(); form.setSpacing(10); form.setLabelAlignment(Qt.AlignRight)
        name_in = QLineEdit(); name_in.setPlaceholderText("VD: Campaign 01...")
        name_in.setMinimumHeight(34)
        desc_in = QLineEdit(); desc_in.setPlaceholderText("Mô tả ngắn...")
        desc_in.setMinimumHeight(34)
        form.addRow("Tên Profile:", name_in)
        form.addRow("Mô Tả:", desc_in)
        lay.addLayout(form)

        btns = QHBoxLayout(); btns.addStretch()
        cancel_btn = QPushButton("Huỷ"); cancel_btn.setMinimumHeight(32); cancel_btn.setMinimumWidth(80)
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor)); cancel_btn.clicked.connect(dlg.reject)
        ok_btn = QPushButton("✔  Tạo Profile"); ok_btn.setObjectName("btnPrimary")
        ok_btn.setMinimumHeight(32); ok_btn.setMinimumWidth(120)
        ok_btn.setCursor(QCursor(Qt.PointingHandCursor)); ok_btn.clicked.connect(dlg.accept)
        btns.addWidget(cancel_btn); btns.addWidget(ok_btn)
        lay.addLayout(btns)

        if dlg.exec_() == QDialog.Accepted:
            profile_name = name_in.text().strip()
            if profile_name:
                self._profiles[profile_name] = {"description": desc_in.text(), "accounts": []}
                self.profile_combo.addItem(profile_name)
                self.profile_combo.setCurrentText(profile_name)
                self._run_log_panel.append(f"[PROFILE] Đã tạo profile: {profile_name}")

    # ── Context menu ─────────────────────────────────────────────────────────
    def _ctx_menu_run(self, pos):
        menu = QMenu(self); menu.setStyleSheet(STYLE)
        menu.addAction("☑  Chọn tất cả", self._select_all)
        menu.addAction("☐ Bỏ chọn tất cả", self._deselect_all)
        menu.addSeparator()
        menu.addAction("➕  Thêm TTC", self._add_ttc_from_context)
        menu.addAction("➕  Thêm Facebook", self._add_facebook_from_context)
        menu.addSeparator()
        menu.addAction("🗑  Xóa dòng chọn", self._delete_selected_rows)
        menu.exec_(self.tree_run.viewport().mapToGlobal(pos))
    
    def _add_ttc_from_context(self):
        """Thêm nhiều TTC account từ context menu."""
        dlg = QDialog(self); dlg.setWindowTitle("➕ Thêm Tài Khoản TTC")
        dlg.setMinimumSize(500, 400); dlg.setStyleSheet(STYLE)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(16,16,16,16); lay.setSpacing(12)
        
        hint = QLabel("💡 Nhập mỗi dòng 1 tài khoản TTC theo định dạng:   user|pass|token")
        hint.setStyleSheet("color:#3d5278;font-size:11px;font-family:Consolas;")
        lay.addWidget(hint)
        
        text_input = QTextEdit()
        text_input.setPlaceholderText(
            "user1|pass123|EAAtoken1...\n"
            "user2|pass456|EAAtoken2...\n"
            "user3|pass789|\n"
            "(token có thể trống nếu chưa có)"
        )
        text_input.setStyleSheet(
            "QTextEdit{background:#050810;border:1px solid #1a2336;border-radius:8px;"
            "color:#6ba3ff;font-family:Consolas;font-size:12px;padding:8px;line-height:1.6;}"
        )
        lay.addWidget(text_input, 1)
        
        btn_lay = QHBoxLayout()
        ok_btn = QPushButton("✔  Thêm"); ok_btn.setObjectName("btnSuccess"); ok_btn.setMinimumHeight(36)
        cancel_btn = QPushButton("Huỷ"); cancel_btn.setMinimumHeight(36)
        ok_btn.clicked.connect(dlg.accept); cancel_btn.clicked.connect(dlg.reject)
        btn_lay.addStretch(); btn_lay.addWidget(cancel_btn); btn_lay.addWidget(ok_btn)
        lay.addLayout(btn_lay)
        
        if dlg.exec_() == QDialog.Accepted:
            lines = [l.strip() for l in text_input.toPlainText().strip().split('\n') if l.strip()]
            count = 0
            for line in lines:
                parts = [p.strip() for p in line.split('|')]
                if not parts[0]: continue
                
                ttc_user = parts[0]
                ttc_pass = parts[1] if len(parts) > 1 else ""
                ttc_token = parts[2] if len(parts) > 2 else ""
                
                new_item = self._make_run_item(
                    ttc_user=ttc_user, ttc_pass=ttc_pass, ttc_token=ttc_token,
                    fb_uid="", fb_cookie="", fb_proxy="", fb_token="",
                    row_idx=self.tree_run.topLevelItemCount()
                )
                self.tree_run.addTopLevelItem(new_item)
                count += 1
            
            if count > 0:
                self._save_accounts_to_profile()
                QMessageBox.information(self, "Thành công", f"Đã thêm {count} tài khoản TTC")
            else:
                QMessageBox.warning(self, "Lỗi", "Không có dòng hợp lệ nào")
    
    def _add_facebook_from_context(self):
        """Thêm nhiều Facebook vào dòng TTC đang chọn."""
        selected_items = self.tree_run.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Lỗi", "Chọn 1 dòng TTC trước!"); return
        
        current_item = selected_items[0]
        
        dlg = QDialog(self); dlg.setWindowTitle("➕ Thêm Tài Khoản Facebook")
        dlg.setMinimumSize(500, 400); dlg.setStyleSheet(STYLE)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(16,16,16,16); lay.setSpacing(12)
        
        hint = QLabel("💡 Nhập mỗi dòng 1 tài khoản Facebook theo định dạng:   uid|cookie|proxy|token")
        hint.setStyleSheet("color:#3d5278;font-size:11px;font-family:Consolas;")
        lay.addWidget(hint)
        
        text_input = QTextEdit()
        text_input.setPlaceholderText(
            "12345|EAAB...|http://proxy:port|EAA...\n"
            "67890|DABC...|http://proxy:port|\n"
            "(proxy & token có thể trống)"
        )
        text_input.setStyleSheet(
            "QTextEdit{background:#050810;border:1px solid #1a2336;border-radius:8px;"
            "color:#6ba3ff;font-family:Consolas;font-size:12px;padding:8px;line-height:1.6;}"
        )
        lay.addWidget(text_input, 1)
        
        # Option: thêm nhiều dòng hay ghép vào dòng đã chọn
        option_lay = QHBoxLayout()
        radio1 = QRadioButton("Thêm nhiều dòng FB mới"); radio1.setChecked(True)
        radio2 = QRadioButton("Ghép vào dòng TTC đã chọn")
        option_lay.addWidget(radio1); option_lay.addWidget(radio2)
        lay.addLayout(option_lay)
        
        btn_lay = QHBoxLayout()
        ok_btn = QPushButton("✔  Thêm"); ok_btn.setObjectName("btnSuccess"); ok_btn.setMinimumHeight(36)
        cancel_btn = QPushButton("Huỷ"); cancel_btn.setMinimumHeight(36)
        ok_btn.clicked.connect(dlg.accept); cancel_btn.clicked.connect(dlg.reject)
        btn_lay.addStretch(); btn_lay.addWidget(cancel_btn); btn_lay.addWidget(ok_btn)
        lay.addLayout(btn_lay)
        
        if dlg.exec_() == QDialog.Accepted:
            lines = [l.strip() for l in text_input.toPlainText().strip().split('\n') if l.strip()]
            count = 0
            
            if radio1.isChecked():
                # Thêm nhiều dòng FB mới
                for line in lines:
                    parts = [p.strip() for p in line.split('|')]
                    if not parts[0]: continue
                    
                    fb_uid = parts[0]
                    fb_cookie = parts[1] if len(parts) > 1 else ""
                    fb_proxy = parts[2] if len(parts) > 2 else ""
                    fb_token = parts[3] if len(parts) > 3 else ""
                    
                    new_item = self._make_run_item(
                        ttc_user="(chưa có TTC)", ttc_pass="", ttc_token="",
                        fb_uid=fb_uid, fb_cookie=fb_cookie, fb_proxy=fb_proxy, fb_token=fb_token,
                        row_idx=self.tree_run.topLevelItemCount()
                    )
                    self.tree_run.addTopLevelItem(new_item)
                    count += 1
            else:
                # Ghép vào dòng TTC đã chọn
                if len(lines) > 0:
                    parts = [p.strip() for p in lines[0].split('|')]
                    fb_uid = parts[0] if len(parts) > 0 else ""
                    fb_cookie = parts[1] if len(parts) > 1 else ""
                    fb_proxy = parts[2] if len(parts) > 2 else ""
                    fb_token = parts[3] if len(parts) > 3 else ""
                    
                    current_item.setText(4, fb_uid)
                    current_item.setText(5, fb_cookie[:40]+"…" if len(fb_cookie)>40 else fb_cookie)
                    current_item.setText(6, fb_proxy)
                    current_item.setText(7, fb_token[:40]+"…" if len(fb_token)>40 else fb_token)
                    current_item.setForeground(4, QColor("#ff8c5a"))
                    current_item.setForeground(5, QColor("#5a7099"))
                    current_item.setForeground(6, QColor("#8b5cf6"))
                    current_item.setForeground(7, QColor("#00d4aa") if fb_token else QColor("#3d5278"))
                    
                    # Update full data (setData) with new FB info
                    full_data = current_item.data(0, Qt.UserRole) or {}
                    full_data.update({
                        "fb_uid": fb_uid,
                        "fb_cookie": fb_cookie,
                        "fb_proxy": fb_proxy,
                        "fb_token": fb_token,
                    })
                    current_item.setData(0, Qt.UserRole, full_data)
                    count = 1
            
            if count > 0:
                self._save_accounts_to_profile()
                QMessageBox.information(self, "Thành công", f"Đã thêm {count} tài khoản Facebook")
            else:
                QMessageBox.warning(self, "Lỗi", "Không có dòng hợp lệ nào")


    def _select_all(self):
        for i in range(self.tree_run.topLevelItemCount()): self.tree_run.topLevelItem(i).setCheckState(0, Qt.Checked)

    def _deselect_all(self):
        for i in range(self.tree_run.topLevelItemCount()): self.tree_run.topLevelItem(i).setCheckState(0, Qt.Unchecked)

    def _delete_selected_rows(self):
        to_remove = []
        root = self.tree_run.invisibleRootItem()
        for i in range(self.tree_run.topLevelItemCount()):
            item = self.tree_run.topLevelItem(i)
            if item.isSelected(): to_remove.append(item)
        for item in to_remove: root.removeChild(item)
        if to_remove:
            self._save_accounts_to_profile()

    # ─────────────────────────────────────────────────────────────────────────
    #  THÊM TÀI KHOẢN VÀO DANH SÁCH CHẠY — 3 tab: Chọn TTC / Nhập TTC / Nhập FB
    # ─────────────────────────────────────────────────────────────────────────
    def _add_accounts_to_run(self):
        if not self.profile_combo.count():
            QMessageBox.warning(self, "Lỗi", "Tạo profile trước!"); return

        dlg = QDialog(self); dlg.setWindowTitle("Thêm Tài Khoản vào Chạy")
        dlg.setMinimumSize(660, 500); dlg.setStyleSheet(STYLE)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(16, 14, 16, 14); lay.setSpacing(10)

        tabs = QTabWidget(); lay.addWidget(tabs, 1)

        # ─── Tab 1: Chọn TTC có sẵn ──────────────────────────────────────
        tab1 = QWidget(); tab1_lay = QVBoxLayout(tab1); tab1_lay.setContentsMargins(0, 6, 0, 0); tab1_lay.setSpacing(8)
        title1 = QLabel("Chọn tài khoản TTC đã có trong hệ thống")
        title1.setStyleSheet("color:#c9d6ea;font-size:12px;font-weight:700;font-family:Consolas;")
        tab1_lay.addWidget(title1)
        tree_ttc = QTreeWidget(); tree_ttc.setObjectName("FbTree"); tree_ttc.setColumnCount(3)
        tree_ttc.setHeaderLabels(["Tài khoản TTC", "User", "Token"])
        tree_ttc.header().setSectionResizeMode(0, QHeaderView.Stretch)
        tree_ttc.header().setSectionResizeMode(1, QHeaderView.Interactive); tree_ttc.header().resizeSection(1, 140)
        tree_ttc.header().setSectionResizeMode(2, QHeaderView.Interactive); tree_ttc.header().resizeSection(2, 180)
        tree_ttc.setAlternatingRowColors(True); tree_ttc.setIndentation(0)
        ttc_data = self.ttc_mgmt._ttc_data if self.ttc_mgmt else {}
        for idx, (user, data) in enumerate(ttc_data.items(), 1):
            item = QTreeWidgetItem(); item.setCheckState(0, Qt.Unchecked)
            item.setIcon(0, QIcon(make_avatar_pixmap(user[0].upper() if user else "T", 22, idx % len(AVATAR_COLORS))))
            item.setText(0, user); item.setText(1, user)
            tk = data.get("token","")
            item.setText(2, tk[:40]+"…" if len(tk)>40 else (tk or "(chưa có)"))
            item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))
            item.setForeground(0, QColor("#d0d8e8")); item.setForeground(1, QColor("#4d8fff"))
            item.setForeground(2, QColor("#00d4aa") if tk else QColor("#3d5278"))
            item.setData(0, Qt.UserRole, user)
            tree_ttc.addTopLevelItem(item)
        tab1_lay.addWidget(tree_ttc, 1)
        tabs.addTab(tab1, "✓  Chọn TTC có sẵn")

        # ─── Tab 2: Nhập TTC riêng ───────────────────────────────────────
        tab2 = QWidget(); tab2_lay = QVBoxLayout(tab2); tab2_lay.setContentsMargins(0, 6, 0, 0); tab2_lay.setSpacing(8)

        ttc_hdr_frame = QFrame()
        ttc_hdr_frame.setStyleSheet("background:#111827;border:1px solid #1a2336;border-radius:8px;")
        ttc_hdr_lay = QHBoxLayout(ttc_hdr_frame); ttc_hdr_lay.setContentsMargins(12,8,12,8)
        ttc_icon = QLabel("🔵"); ttc_icon.setStyleSheet("font-size:16px;background:transparent;")
        ttc_hint_lay = QVBoxLayout(); ttc_hint_lay.setSpacing(2)
        ttc_hint_t = QLabel("Nhập danh sách tài khoản TTC")
        ttc_hint_t.setStyleSheet("color:#c9d6ea;font-size:11px;font-weight:700;background:transparent;")
        ttc_hint_s = QLabel("Mỗi dòng 1 tài khoản TTC theo định dạng:   user|pass|token")
        ttc_hint_s.setStyleSheet("color:#3d5278;font-size:10px;font-family:Consolas;background:transparent;")
        ttc_hint_lay.addWidget(ttc_hint_t); ttc_hint_lay.addWidget(ttc_hint_s)
        ttc_hdr_lay.addWidget(ttc_icon); ttc_hdr_lay.addLayout(ttc_hint_lay); ttc_hdr_lay.addStretch()
        tab2_lay.addWidget(ttc_hdr_frame)

        ttc_text_input = QTextEdit()
        ttc_text_input.setPlaceholderText(
            "user1|pass123|EAAtoken1...\n"
            "user2|pass456|EAAtoken2...\n"
            "user3|pass789|\n"
            "(token có thể trống nếu chưa có)"
        )
        ttc_text_input.setStyleSheet(
            "QTextEdit{background:#050810;border:1px solid #1a2336;border-radius:8px;"
            "color:#6ba3ff;font-family:Consolas;font-size:12px;padding:8px;line-height:1.6;}"
        )
        tab2_lay.addWidget(ttc_text_input, 1)
        tabs.addTab(tab2, "📋  Nhập TTC")

        # ─── Tab 3: Nhập Facebook riêng ──────────────────────────────────
        tab3 = QWidget(); tab3_lay = QVBoxLayout(tab3); tab3_lay.setContentsMargins(0, 6, 0, 0); tab3_lay.setSpacing(8)

        fb_hdr_frame = QFrame()
        fb_hdr_frame.setStyleSheet("background:#111827;border:1px solid #1a2336;border-radius:8px;")
        fb_hdr_lay = QHBoxLayout(fb_hdr_frame); fb_hdr_lay.setContentsMargins(12,8,12,8)
        fb_icon = QLabel("𝕗"); fb_icon.setStyleSheet("font-size:16px;color:#1877f2;background:transparent;font-weight:800;")
        fb_hint_lay = QVBoxLayout(); fb_hint_lay.setSpacing(2)
        fb_hint_t = QLabel("Nhập danh sách tài khoản Facebook")
        fb_hint_t.setStyleSheet("color:#c9d6ea;font-size:11px;font-weight:700;background:transparent;")
        fb_hint_s = QLabel("Mỗi dòng 1 tài khoản FB theo định dạng:   uid|cookie|proxy|token_page")
        fb_hint_s.setStyleSheet("color:#3d5278;font-size:10px;font-family:Consolas;background:transparent;")
        fb_hint_lay.addWidget(fb_hint_t); fb_hint_lay.addWidget(fb_hint_s)
        fb_hdr_lay.addWidget(fb_icon); fb_hdr_lay.addLayout(fb_hint_lay); fb_hdr_lay.addStretch()
        tab3_lay.addWidget(fb_hdr_frame)

        # Ghép TTC+FB note
        pair_note = QLabel("💡  Ghép theo thứ tự dòng: dòng 1 TTC ↔ dòng 1 FB, dòng 2 TTC ↔ dòng 2 FB, ...")
        pair_note.setStyleSheet(
            "background:rgba(45,111,255,0.08);border:1px solid rgba(45,111,255,0.25);"
            "border-radius:6px;color:#4d8fff;font-size:10px;font-family:Consolas;padding:5px 10px;"
        )
        tab3_lay.addWidget(pair_note)

        fb_text_input = QTextEdit()
        fb_text_input.setPlaceholderText(
            "100001234567890|c_user=100001234|proxy.com:8080|EAApage_token1...\n"
            "100009876543210|c_user=100009876|proxy.com:8081|EAApage_token2...\n"
            "100005555666777|c_user=100005555||"
        )
        fb_text_input.setStyleSheet(
            "QTextEdit{background:#050810;border:1px solid #1a2336;border-radius:8px;"
            "color:#ff8c5a;font-family:Consolas;font-size:12px;padding:8px;line-height:1.6;}"
        )
        tab3_lay.addWidget(fb_text_input, 1)
        tabs.addTab(tab3, "𝕗  Nhập Facebook")

        # ─── Buttons ───────────────────────────────────────────────────
        btn_row = QHBoxLayout(); btn_row.addStretch()
        cancel_btn = QPushButton("Huỷ"); cancel_btn.setMinimumHeight(34); cancel_btn.setMinimumWidth(80)
        cancel_btn.clicked.connect(dlg.reject)
        ok_btn = QPushButton("✔  Thêm vào danh sách"); ok_btn.setObjectName("btnSuccess")
        ok_btn.setMinimumHeight(34); ok_btn.setMinimumWidth(160)
        ok_btn.setCursor(QCursor(Qt.PointingHandCursor)); ok_btn.clicked.connect(dlg.accept)
        btn_row.addWidget(cancel_btn); btn_row.addWidget(ok_btn); lay.addLayout(btn_row)

        if dlg.exec_() != QDialog.Accepted:
            return

        tab_idx = tabs.currentIndex()
        count = 0

        if tab_idx == 0:
            # ─── Chọn TTC có sẵn ──────────────────────────────────────
            for i in range(tree_ttc.topLevelItemCount()):
                item = tree_ttc.topLevelItem(i)
                if item.checkState(0) == Qt.Checked:
                    user = item.data(0, Qt.UserRole); user_data = ttc_data.get(user, {})
                    new_item = self._make_run_item(
                        ttc_user=user, ttc_pass=user_data.get("pass","***"),
                        ttc_token=user_data.get("token",""),
                        fb_uid="", fb_cookie="", fb_proxy="", fb_token="",
                        row_idx=self.tree_run.topLevelItemCount()
                    )
                    self.tree_run.addTopLevelItem(new_item); count += 1

        elif tab_idx == 1:
            # ─── Nhập TTC riêng ───────────────────────────────────────
            lines = [l.strip() for l in ttc_text_input.toPlainText().strip().split('\n') if l.strip()]
            for line in lines:
                parts = [p.strip() for p in line.split('|')]
                if not parts[0]: continue
                ttc_user  = parts[0]
                ttc_pass  = parts[1] if len(parts) > 1 else ""
                ttc_token = parts[2] if len(parts) > 2 else ""
                new_item = self._make_run_item(
                    ttc_user=ttc_user, ttc_pass=ttc_pass, ttc_token=ttc_token,
                    fb_uid="", fb_cookie="", fb_proxy="", fb_token="",
                    row_idx=self.tree_run.topLevelItemCount()
                )
                self.tree_run.addTopLevelItem(new_item); count += 1

        elif tab_idx == 2:
            # ─── Nhập Facebook riêng — ghép với hàng TTC hiện có ─────────
            fb_lines = [l.strip() for l in fb_text_input.toPlainText().strip().split('\n') if l.strip()]
            total_existing = self.tree_run.topLevelItemCount()

            for i, line in enumerate(fb_lines):
                parts = [p.strip() for p in line.split('|')]
                fb_uid    = parts[0] if len(parts) > 0 else ""
                fb_cookie = parts[1] if len(parts) > 1 else ""
                fb_proxy  = parts[2] if len(parts) > 2 else ""
                fb_token  = parts[3] if len(parts) > 3 else ""

                if i < total_existing:
                    # Ghép vào hàng TTC đã có theo thứ tự
                    existing = self.tree_run.topLevelItem(i)
                    existing.setText(4, fb_uid)
                    existing.setText(5, fb_cookie[:40]+"…" if len(fb_cookie)>40 else fb_cookie)
                    existing.setText(6, fb_proxy)
                    existing.setText(7, fb_token[:40]+"…" if len(fb_token)>40 else fb_token)
                    existing.setForeground(4, QColor("#ff8c5a"))
                    existing.setForeground(5, QColor("#5a7099"))
                    existing.setForeground(6, QColor("#8b5cf6"))
                    existing.setForeground(7, QColor("#00d4aa") if fb_token else QColor("#3d5278"))
                    count += 1
                else:
                    # Nếu dư FB hơn TTC, tạo dòng mới chỉ có FB
                    new_item = self._make_run_item(
                        ttc_user="(chưa có TTC)", ttc_pass="", ttc_token="",
                        fb_uid=fb_uid, fb_cookie=fb_cookie,
                        fb_proxy=fb_proxy, fb_token=fb_token,
                        row_idx=self.tree_run.topLevelItemCount()
                    )
                    self.tree_run.addTopLevelItem(new_item); count += 1

        if count > 0:
            self._save_accounts_to_profile()
            self._run_log_panel.append(f"[+] Đã thêm/cập nhật {count} tài khoản vào danh sách chạy")
        else:
            QMessageBox.warning(self, "Lỗi", "Không có dòng hợp lệ nào. Kiểm tra lại định dạng nhập.")

    def _create_stat_widget(self, label, value, color):
        """Tạo widget hiển thị thống kê"""
        stat_widget = QFrame()
        stat_widget.setStyleSheet(f"background:#0b0f14;border:1px solid #1a2336;border-radius:8px;")
        stat_lay = QVBoxLayout(stat_widget); stat_lay.setContentsMargins(12,10,12,10); stat_lay.setSpacing(4)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color:{color};font-size:11px;font-family:Consolas;font-weight:700;background:transparent;")
        stat_lay.addWidget(lbl)
        
        val = QLabel(value)
        val.setObjectName("stat_value")
        val.setStyleSheet(f"color:white;font-size:24px;font-weight:800;background:transparent;")
        val.setAlignment(Qt.AlignCenter)
        stat_lay.addWidget(val)
        
        # Store reference cho update sau
        stat_widget._value_label = val
        
        return stat_widget
    
    def update_stats(self, tasks_done=None, xu_earned=None, tasks_error=None):
        """Update các stat widgets"""
        if tasks_done is not None:
            self._stat_tasks_done._value_label.setText(str(tasks_done))
        if xu_earned is not None:
            self._stat_xu_earned._value_label.setText(str(xu_earned))
        if tasks_error is not None:
            self._stat_tasks_error._value_label.setText(str(tasks_error))
    
    def _on_tree_update_signal(self, ttc_user, status, xu):
        """Slot handler for tree updates from background thread"""
        for i in range(self.tree_run.topLevelItemCount()):
            item = self.tree_run.topLevelItem(i)
            if item.text(1) == ttc_user:
                item.setText(8, status)
                item.setText(9, str(xu))
                # Update color based on status
                if "✅" in status:
                    item.setForeground(8, QColor("#00d4aa"))
                elif "❌" in status:
                    item.setForeground(8, QColor("#ef4444"))
                elif "⏳" in status:
                    item.setForeground(8, QColor("#f59e0b"))
                item.setForeground(9, QColor("#00d4aa"))
                self.tree_run.update()
                break

    def _on_button_state_changed(self, button_name, enabled):
        """Slot handler to update button state from background thread"""
        btn = getattr(self, button_name, None)
        if btn:
            btn.setEnabled(enabled)

    def _make_run_item(self, ttc_user, ttc_pass, ttc_token,
                       fb_uid, fb_cookie, fb_proxy, fb_token, row_idx=0):
        """Tạo QTreeWidgetItem cho tree_run"""
        new_item = QTreeWidgetItem()
        new_item.setCheckState(0, Qt.Unchecked)
        new_item.setIcon(0, QIcon(make_avatar_pixmap(
            ttc_user[0].upper() if ttc_user and ttc_user[0].isalpha() else "T",
            22, row_idx % len(AVATAR_COLORS)
        )))
        new_item.setText(0, ttc_user)
        new_item.setText(1, ttc_user)
        new_item.setText(2, ttc_pass)
        new_item.setText(3, ttc_token)
        new_item.setText(4, fb_uid)
        new_item.setText(5, fb_cookie)
        new_item.setText(6, fb_proxy)
        new_item.setText(7, fb_token)
        new_item.setText(8, "⏳ Chờ")
        new_item.setText(9, "0")
        
        # Store full data (không bị cắt) để save vào file sau
        full_data = {
            "ttc_user": ttc_user,
            "ttc_pass": ttc_pass,
            "ttc_token": ttc_token,
            "fb_uid": fb_uid,
            "fb_cookie": fb_cookie,
            "fb_proxy": fb_proxy,
            "fb_token": fb_token,
        }
        new_item.setData(0, Qt.UserRole, full_data)
        
        # Add tooltip with full data
        tooltip = f"""<b>== FULL ACCOUNT DATA ==</b>
<b>TTC User:</b> {ttc_user}
<b>TTC Pass:</b> {ttc_pass}
<b>TTC Token:</b> {ttc_token}
<b>FB UID:</b> {fb_uid}
<b>FB Cookie:</b> {fb_cookie}
<b>FB Proxy:</b> {fb_proxy if fb_proxy else '(empty)'}
<b>FB Token:</b> {fb_token}"""
        new_item.setToolTip(0, tooltip)
        
        new_item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))
        new_item.setForeground(0, QColor("#d0d8e8"))
        new_item.setForeground(1, QColor("#4d8fff"))
        new_item.setForeground(2, QColor("#5a7099"))
        new_item.setForeground(3, QColor("#00d4aa") if ttc_token else QColor("#3d5278"))
        new_item.setForeground(4, QColor("#ff8c5a") if fb_uid else QColor("#3d5278"))
        new_item.setForeground(5, QColor("#5a7099"))
        new_item.setForeground(6, QColor("#8b5cf6") if fb_proxy else QColor("#3d5278"))
        new_item.setForeground(7, QColor("#00d4aa") if fb_token else QColor("#3d5278"))
        new_item.setForeground(8, QColor("#f59e0b"))
        new_item.setForeground(9, QColor("#00d4aa"))
        return new_item

    def _start_running(self):
        if not self.tree_run.topLevelItemCount():
            QMessageBox.warning(self, "Lỗi", "Thêm tài khoản trước!"); return
        tasks = self._run_settings.get("tasks", [])
        if not tasks:
            QMessageBox.warning(self, "Lỗi", "Chọn nhiệm vụ trong Cài Đặt Chạy trước!"); return
        api_key = self._run_settings.get("api_key", "")
        if not api_key:
            QMessageBox.warning(self, "Lỗi", "Nhập API key trong Cài Đặt Chạy!"); return
        
        # ───────────────────────────────────────────────────────────────
        # Gộp tất cả dữ liệu: Collect tất cả accounts được check
        # ───────────────────────────────────────────────────────────────
        accounts = []
        for i in range(self.tree_run.topLevelItemCount()):
            item = self.tree_run.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                full_data = item.data(0, Qt.UserRole) or {}
                account = {
                    "ttc_user": full_data.get("ttc_user", item.text(1)),
                    "ttc_pass": full_data.get("ttc_pass", item.text(2)),
                    "ttc_token": full_data.get("ttc_token", item.text(3)),
                    "fb_uid": full_data.get("fb_uid", item.text(4)),
                    "fb_cookie": full_data.get("fb_cookie", item.text(5)),
                    "fb_proxy": full_data.get("fb_proxy", item.text(6)),
                    "fb_token": full_data.get("fb_token", item.text(7))
                }
                accounts.append(account)
        
        if not accounts:
            QMessageBox.warning(self, "Lỗi", "Chọn ít nhất 1 tài khoản để chạy!"); return
        
        # Tạo JSON data gộp settings + accounts + task_settings
        tasks_data = []
        for task_name, task_cfg in self._run_settings.get("task_settings", {}).items():
            if task_cfg.get("enabled", False):
                code_name = self.AVAILABLE_TASKS.get(task_name, {}).get("code_name", task_name)
                tasks_data.append({
                    "type_job": code_name,
                    "display_name": task_name,
                    "delay_min": task_cfg.get("delay_min", 5),
                    "delay_max": task_cfg.get("delay_max", 60),
                    "count": task_cfg.get("count", 1)
                })
        
        data = {
            "settings": {
                "api_key": api_key,
                "delay_short": self._run_settings.get("delay_short", 5),
                "delay_long": self._run_settings.get("delay_long", 60),
                "delay_after_tasks": self._run_settings.get("delay_after_tasks", 5),
                "stop_after_tasks": self._run_settings.get("stop_after_tasks", 100)
            },
            "tasks": tasks_data,
            "accounts": accounts
        }
        
        # Print data for debugging
        print("[DEBUG] Data gửi đến RUN_TTC:")
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Print full account data without truncation
        print("\n[DEBUG] ===== FULL ACCOUNT DATA (không bị cắt) =====")
        for acc in data.get('accounts', []):
            print(f"\nAccount: {acc.get('ttc_user', 'Unknown')}")
            print(f"  TTC User: {acc.get('ttc_user', '')}")
            print(f"  TTC Pass: {acc.get('ttc_pass', '')}")
            print(f"  TTC Token: {acc.get('ttc_token', '')}")
            print(f"  FB UID: {acc.get('fb_uid', '')}")
            print(f"  FB Cookie (length: {len(acc.get('fb_cookie', ''))}): {acc.get('fb_cookie', '')}")
            print(f"  FB Proxy: {acc.get('fb_proxy', '')}")
            print(f"  FB Token (length: {len(acc.get('fb_token', ''))}): {acc.get('fb_token', '')}")
        
        # Save full data to file for inspection
        try:
            with open('run_data_full.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("\n[DEBUG] ✓ Full data saved to: run_data_full.json")
        except Exception as e:
            print(f"[DEBUG] ✗ Error saving file: {e}")
        
        # Define callbacks with signal emitter for thread-safe marshalling
        def log_callback(msg):
            """Callback để update log panel - thread safe"""
            self.log_emitter.log_signal.emit(msg)
        
        def tree_callback(ttc_user, status, xu):
            """Callback để update treeview - thread safe"""
            print(f"[DEBUG] Tree callback received - User: {ttc_user}, Status: {status}, Xu: {xu}")
            self.log_emitter.tree_signal.emit(ttc_user, status, xu)
        
        def stats_callback(tasks_done, xu_earned, tasks_error):
            """Callback để update stats - thread safe"""
            self.update_stats(tasks_done=tasks_done, xu_earned=xu_earned, tasks_error=tasks_error)
        
        # Gọi RUN_TTC với data và callbacks
        from TTC.run_TTC import RUN_TTC
        runner = RUN_TTC(data, callbacks={
            'log': log_callback,
            'tree': tree_callback,
            'stats': stats_callback
        })
        self._ttc_runner = runner  # Store reference for stop functionality
        
        task_names = [t.get("type_job", "") for t in tasks_data]
        self._run_log_panel.append(f"[START] Chạy {len(task_names)} nhiệm vụ: {', '.join(task_names)}")
        self._run_log_panel.append(f"[INFO] Delay: {self._run_settings['delay_short']}s–{self._run_settings['delay_long']}s | Dừng sau: {self._run_settings['stop_after_tasks']} task")
        self._run_log_panel.append(f"[ACCOUNTS] Đã select {len(accounts)} tài khoản để chạy")
        
        # Disable Start button, enable Stop button (via signal for thread safety)
        self.log_emitter.button_state_signal.emit("_btn_start_run", False)
        self.log_emitter.button_state_signal.emit("_btn_stop_run", True)
        
        # Wrapper function to run and then re-enable buttons
        def run_with_cleanup():
            try:
                runner.main()
            finally:
                # Re-enable Start button when done (via signal for thread safety)
                self.log_emitter.button_state_signal.emit("_btn_start_run", True)
                self.log_emitter.button_state_signal.emit("_btn_stop_run", False)
                self._run_log_panel.append("[END] Quá trình chạy kết thúc")
        
        # Chạy runner trong thread riêng để không lag UI
        import threading
        run_thread = threading.Thread(target=run_with_cleanup, daemon=True)
        self._ttc_run_thread = run_thread  # Store reference for potential cleanup
        run_thread.start()
        
        QMessageBox.information(self, "Thông báo", f"Cấu hình OK — {len(task_names)} nhiệm vụ với {len(accounts)} tài khoản được chọn")

    def _stop_running(self):
        """Stop the running TTC process"""
        if not self._ttc_runner:
            QMessageBox.warning(self, "Lỗi", "Chưa có quá trình chạy nào!")
            return
        
        self._run_log_panel.append("[STOP] Yêu cầu dừng chương trình...")
        self._ttc_runner.stop()
        
        # Disable stop button (will be re-enabled by wrapper when thread finishes)
        self.log_emitter.button_state_signal.emit("_btn_stop_run", False)

    def _clear_run_list(self):
        self.tree_run.clear()


# ─────────────────────────────────────────────────────────────────────────────
#  TDS RUN PAGE (Chạy Traodoisub)
# ─────────────────────────────────────────────────────────────────────────────
class TDSRunPage(QWidget):
    def __init__(self, traodoisub_management_page, parent=None):
        super().__init__(parent)
        self.tds_mgmt = traodoisub_management_page
        self._profiles = {}
        self._current_profile = "Default"
        self._profiles_file = "tds_run_profiles.json"
        
        self._run_settings = {
            "api_key": "", "delay_short": 5, "delay_long": 60,
            "delay_after_tasks": 5, "stop_after_tasks": 100,
            "tasks": [], "task_settings": {}
        }
        self.AVAILABLE_TASKS = {
            "Like VIP":        {"code_name": "facebook_reaction", "min": 5,  "max": 60,  "count": 1, "icon": "👍"},
            "Like Thường":     {"code_name": "facebook_reaction2",   "min": 5,  "max": 60,  "count": 1, "icon": "👍"},
            "Theo Dõi":        {"code_name": "facebook_follow",         "min": 5,  "max": 60,  "count": 1, "icon": "👤"},
            "Share":           {"code_name": "facebook_share",       "min": 10, "max": 120, "count": 1, "icon": "↗️"},
        }

        # Initialize default task settings
        for task_name, defaults in self.AVAILABLE_TASKS.items():
            self._run_settings["task_settings"][task_name] = {
                "enabled": False,
                "delay_min": defaults["min"], 
                "delay_max": defaults["max"],
                "count": defaults["count"]
            }
        
        self._load_profiles_from_file()
        self.log_emitter = RunLogSignalEmitter()
        
        # Runner references (for stop functionality)
        self._tds_runner = None
        self._tds_run_thread = None
        
        root_lay = QVBoxLayout(self)
        root_lay.setContentsMargins(20, 16, 20, 16)
        root_lay.setSpacing(12)

        # Header
        hdr = QHBoxLayout(); hdr.setSpacing(14)
        icon = QLabel("🚀"); icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #06b6d4,stop:1 #22d3ee);border-radius:12px;color:white;font-size:20px;font-weight:800;min-width:46px;max-width:46px;min-height:46px;max-height:46px;")
        hdr.addWidget(icon)
        hdr_text = QVBoxLayout(); hdr_text.setSpacing(2)
        t1 = QLabel("Chạy TDS"); t1.setObjectName("PageTitle")
        t2 = QLabel("Quản lý & chạy tương tác trên tài khoản Traodoisub"); t2.setObjectName("PageSub")
        hdr_text.addWidget(t1); hdr_text.addWidget(t2)
        hdr.addLayout(hdr_text); hdr.addStretch()
        root_lay.addLayout(hdr)

        # Profile bar
        profile_bar = QFrame()
        profile_bar.setStyleSheet("QFrame{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0d1a2e,stop:1 #111827);border:1px solid #1e3050;border-radius:12px;}")
        pb_lay = QHBoxLayout(profile_bar); pb_lay.setContentsMargins(16,12,16,12); pb_lay.setSpacing(10)
        pb_lay.addWidget(QLabel("📁"))
        
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(180); self.profile_combo.setMinimumHeight(34)
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        pb_lay.addWidget(self.profile_combo)

        for label, obj_name, slot in [
            ("💾  Lưu", "btnSuccess", self._save_current_profile),
            ("📂  Tải", "btnPrimary", self._load_profile_dialog),
            ("➕  Mới", "btnPrimary", self._new_profile_dialog),
            ("🗑  Xóa", "btnDanger",  self._delete_profile_dialog),
        ]:
            btn = QPushButton(label); btn.setObjectName(obj_name)
            btn.setMinimumHeight(34); btn.setMinimumWidth(90)
            btn.setCursor(QCursor(Qt.PointingHandCursor)); btn.clicked.connect(slot)
            pb_lay.addWidget(btn)

        pb_lay.addStretch()
        b_settings = QPushButton("⚙  Cài Đặt"); b_settings.setObjectName("btnWarn")
        b_settings.setMinimumHeight(34); b_settings.setMinimumWidth(130)
        b_settings.setCursor(QCursor(Qt.PointingHandCursor))
        b_settings.clicked.connect(self._open_settings_dialog)
        pb_lay.addWidget(b_settings)
        self._settings_badge = QLabel("⚙ Chưa cấu hình")
        self._settings_badge.setStyleSheet("color:#3d5278;font-size:10px;font-family:Consolas;background:transparent;")
        pb_lay.addWidget(self._settings_badge)
        root_lay.addWidget(profile_bar)

        # Stats bar
        stats_bar = QFrame()
        stats_bar.setStyleSheet("QFrame{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0d1a2e,stop:1 #111827);border:1px solid #1e3050;border-radius:12px;}")
        stats_lay = QHBoxLayout(stats_bar); stats_lay.setContentsMargins(16,12,16,12); stats_lay.setSpacing(20)
        self._stat_tasks_done  = self._create_stat_widget("✅ Nhiệm vụ đã làm", "0", "#4d8fff")
        self._stat_xu_earned   = self._create_stat_widget("💰 Xu nhận được",    "0", "#00d4aa")
        self._stat_tasks_error = self._create_stat_widget("❌ Nhiệm vụ lỗi",    "0", "#ef4444")
        stats_lay.addWidget(self._stat_tasks_done, 1)
        stats_lay.addWidget(self._stat_xu_earned, 1)
        stats_lay.addWidget(self._stat_tasks_error, 1)
        stats_lay.addStretch()
        root_lay.addWidget(stats_bar)

        # Main content
        content_row = QHBoxLayout(); content_row.setSpacing(10)

        tree_wrap = QWidget(); tree_wrap.setStyleSheet("background:#0d1219;")
        tree_lay = QVBoxLayout(tree_wrap); tree_lay.setContentsMargins(0,0,0,0); tree_lay.setSpacing(6)
        tree_lay.addWidget(make_section_header("DANH SÁCH TÀI KHOẢN", "TDS/Traodoisub"))

        self.tree_run = QTreeWidget(); self.tree_run.setObjectName("FbTree")
        self.tree_run.setColumnCount(10)
        self.tree_run.setHeaderLabels(["Tài Khoản","User TDS","Pass TDS","Token TDS","UID FB","Cookie FB","Proxy FB","Token FB","Status","Xu"])
        self.tree_run.header().setSectionResizeMode(0, QHeaderView.Stretch)
        for col, w in enumerate([100,85,100,80,100,90,100,100], 1):
            self.tree_run.header().setSectionResizeMode(col, QHeaderView.Interactive)
            self.tree_run.header().resizeSection(col, w)
        self.tree_run.header().setSectionResizeMode(8, QHeaderView.Interactive); self.tree_run.header().resizeSection(8, 100)
        self.tree_run.header().setSectionResizeMode(9, QHeaderView.Interactive); self.tree_run.header().resizeSection(9, 80)
        self.tree_run.setAlternatingRowColors(True)
        self.tree_run.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree_run.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tree_run.setIndentation(0)
        self.tree_run.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_run.customContextMenuRequested.connect(self._ctx_menu_run)
        tree_lay.addWidget(self.tree_run, 1)
        content_row.addWidget(tree_wrap, 3)

        log_wrap = QWidget(); log_wrap.setStyleSheet("background:#0d1219;")
        log_lay = QVBoxLayout(log_wrap); log_lay.setContentsMargins(0,0,0,0); log_lay.setSpacing(6)
        log_lay.addWidget(make_section_header("RUN LOG", "Nhật ký hoạt động"))
        self._run_log_panel = LogPanel()
        self._run_log_panel.setMaximumHeight(99999)
        log_lay.addWidget(self._run_log_panel, 1)
        self.log_emitter.log_signal.connect(self._run_log_panel.append)
        self.log_emitter.tree_signal.connect(self._on_tree_update_signal)
        self.log_emitter.button_state_signal.connect(self._on_button_state_changed)
        content_row.addWidget(log_wrap, 1)
        root_lay.addLayout(content_row, 1)

        # Action buttons
        btn_lay = QHBoxLayout(); btn_lay.setSpacing(8)
        self._tds_btn_add_accounts = None
        self._tds_btn_start_run = None
        self._tds_btn_stop_run = None
        self._tds_btn_clear_list = None
        
        for label, obj_name, slot, var_name in [
            ("➕  Thêm TK vào danh sách", "btnPrimary", self._add_accounts_to_run, "_tds_btn_add_accounts"),
            ("▶  Bắt Đầu Chạy",          "btnSuccess", self._start_running, "_tds_btn_start_run"),
            ("⏹  Dừng Chạy",             "btnDanger",  self._stop_running, "_tds_btn_stop_run"),
            ("🗑  Xóa Danh Sách",         "btnDanger",  self._clear_run_list, "_tds_btn_clear_list"),
        ]:
            btn = QPushButton(label); btn.setObjectName(obj_name); btn.setMinimumHeight(36)
            btn.setCursor(QCursor(Qt.PointingHandCursor)); btn.clicked.connect(slot); btn_lay.addWidget(btn)
            setattr(self, var_name, btn)
        
        # Initially disable stop button since nothing is running
        self._tds_btn_stop_run.setEnabled(False)
        
        btn_lay.addStretch()
        root_lay.addLayout(btn_lay)

        # Init UI với profiles đã load
        self._update_profile_ui()
        self._load_accounts_from_profile()

    def _load_profiles_from_file(self):
        """Load profiles từ file JSON — chỉ load data, không đụng UI."""
        try:
            if os.path.exists(self._profiles_file):
                with open(self._profiles_file, 'r', encoding='utf-8') as f:
                    self._profiles = json.load(f)
            else:
                self._profiles = {"Default": self._run_settings.copy()}
        except Exception:
            self._profiles = {"Default": self._run_settings.copy()}

    # ── Profile Management ───────────────────────────────────────────────────
    def _load_profiles_from_file(self):
        """Load profiles từ file JSON."""
        try:
            if os.path.exists(self._profiles_file):
                with open(self._profiles_file, 'r', encoding='utf-8') as f:
                    self._profiles = json.load(f)
            else:
                self._profiles = {"Default": self._run_settings.copy()}
        except Exception:
            self._profiles = {"Default": self._run_settings.copy()}
    
    def _update_profile_ui(self):
        """Update UI elements with loaded profiles."""
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for pname in sorted(self._profiles.keys()):
            self.profile_combo.addItem(pname)
        self.profile_combo.blockSignals(False)
        self._load_profile_settings("Default")

    def _save_profiles(self):
        """Save profiles vào file JSON."""
        try:
            with open(self._profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self._profiles, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu profiles: {str(e)}")
    
    def _save_accounts_to_profile(self):
        """Lưu danh sách tài khoản hiện tại vào profile."""
        accounts = []
        for i in range(self.tree_run.topLevelItemCount()):
            item = self.tree_run.topLevelItem(i)
            full_data = item.data(0, Qt.UserRole)
            if full_data:
                accounts.append(full_data)
            else:
                account = {
                    "user": item.text(1),
                    "pass": item.text(2),
                    "token": item.text(3),
                    "fb_uid": item.text(4),
                    "fb_cookie": item.text(5),
                    "fb_proxy": item.text(6),
                    "fb_token": item.text(7),
                }
                accounts.append(account)
        
        pname = self._current_profile or "Default"
        if "accounts" not in self._profiles[pname]:
            self._profiles[pname]["accounts"] = []
        self._profiles[pname]["accounts"] = accounts
        self._save_profiles()
    
    def _load_accounts_from_profile(self):
        """Tải danh sách tài khoản từ profile."""
        self.tree_run.clear()
        pname = self._current_profile or "Default"
        accounts = self._profiles[pname].get("accounts", [])
        
        for idx, acc in enumerate(accounts):
            new_item = self._make_run_item(
                user=acc.get("user", ""),
                pass_=acc.get("pass", ""),
                token=acc.get("token", ""),
                fb_uid=acc.get("fb_uid", ""),
                fb_cookie=acc.get("fb_cookie", ""),
                fb_proxy=acc.get("fb_proxy", ""),
                fb_token=acc.get("fb_token", ""),
                row_idx=idx
            )
            self.tree_run.addTopLevelItem(new_item)

    def _save_current_profile(self):
        """Lưu settings hiện tại vào profile được chọn."""
        pname = self.profile_combo.currentText() or "Default"
        if not pname:
            QMessageBox.warning(self, "Lỗi", "Chưa chọn profile"); return
        
        self._profiles[pname] = self._run_settings.copy()
        self._save_profiles()
        QMessageBox.information(self, "Thành công", f"Đã lưu profile: {pname}")

    def _load_profile_settings(self, pname):
        """Load settings từ profile."""
        if pname not in self._profiles:
            pname = "Default"
        
        self._current_profile = pname
        self._run_settings = self._profiles[pname].copy()
        
        self._settings_badge.setText(f"📌 {pname}")
        
        if hasattr(self, 'tree_run') and self.tree_run:
            self._load_accounts_from_profile()

    def _on_profile_changed(self, pname):
        """Khi chọn profile khác."""
        if pname:
            self._load_profile_settings(pname)

    def _new_profile_dialog(self):
        """Dialog tạo profile mới."""
        dlg = QDialog(self); dlg.setWindowTitle("📋 Tạo Profile Mới")
        dlg.setMinimumWidth(380); dlg.setStyleSheet(STYLE)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(20,16,20,16); lay.setSpacing(12)
        
        lay.addWidget(QLabel("Tên Profile:"))
        inp_name = QLineEdit(); inp_name.setMinimumHeight(36); inp_name.setPlaceholderText("VD: Config1, Config Nhanh, ...")
        lay.addWidget(inp_name)
        
        lay.addSpacing(8)
        lay.addWidget(QLabel("Chọn Profile để copy (optional):"))
        combo = QComboBox(); combo.setMinimumHeight(36)
        combo.addItem("(Tạo mới từ trống)")
        for pname in sorted(self._profiles.keys()):
            combo.addItem(pname)
        lay.addWidget(combo)
        
        lay.addStretch()
        
        btn_lay = QHBoxLayout(); btn_lay.setSpacing(8)
        cancel_btn = QPushButton("Huỷ"); cancel_btn.setMinimumHeight(36); cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(dlg.reject)
        ok_btn = QPushButton("✔  Tạo"); ok_btn.setObjectName("btnSuccess")
        ok_btn.setMinimumHeight(36); ok_btn.setMinimumWidth(120)
        ok_btn.clicked.connect(dlg.accept)
        btn_lay.addStretch(); btn_lay.addWidget(cancel_btn); btn_lay.addWidget(ok_btn)
        lay.addLayout(btn_lay)
        
        if dlg.exec_() == QDialog.Accepted:
            pname = inp_name.text().strip()
            if not pname:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên profile"); return
            if pname in self._profiles:
                QMessageBox.warning(self, "Lỗi", f"Profile '{pname}' đã tồn tại"); return
            
            source = combo.currentText()
            if source == "(Tạo mới từ trống)":
                self._profiles[pname] = {
                    "api_key": "", "delay_short": 5, "delay_long": 60,
                    "delay_after_tasks": 5, "stop_after_tasks": 100,
                    "tasks": [], "task_settings": {}, "accounts": []
                }
            else:
                self._profiles[pname] = self._profiles[source].copy()
            
            self._save_profiles()
            self._update_profile_ui()
            self.profile_combo.setCurrentText(pname)
            QMessageBox.information(self, "Thành công", f"Đã tạo profile: {pname}")

    def _load_profile_dialog(self):
        """Dialog để chọn load profile."""
        dlg = QDialog(self); dlg.setWindowTitle("📂 Tải Profile")
        dlg.setMinimumWidth(300); dlg.setStyleSheet(STYLE)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(20,16,20,16); lay.setSpacing(12)
        
        lay.addWidget(QLabel("Chọn profile:"))
        combo = QComboBox(); combo.setMinimumHeight(36)
        for pname in sorted(self._profiles.keys()):
            combo.addItem(pname)
        lay.addWidget(combo)
        lay.addStretch()
        
        btn_lay = QHBoxLayout(); btn_lay.setSpacing(8)
        cancel_btn = QPushButton("Huỷ"); cancel_btn.setMinimumHeight(36)
        cancel_btn.clicked.connect(dlg.reject)
        ok_btn = QPushButton("✔  Tải"); ok_btn.setObjectName("btnSuccess")
        ok_btn.setMinimumHeight(36); ok_btn.clicked.connect(dlg.accept)
        btn_lay.addStretch(); btn_lay.addWidget(cancel_btn); btn_lay.addWidget(ok_btn)
        lay.addLayout(btn_lay)
        
        if dlg.exec_() == QDialog.Accepted:
            pname = combo.currentText()
            self.profile_combo.setCurrentText(pname)
            QMessageBox.information(self, "Thành công", f"Đã tải profile: {pname}")

    def _delete_profile_dialog(self):
        """Dialog xác nhận xóa profile."""
        pname = self.profile_combo.currentText()
        if not pname or pname == "Default":
            QMessageBox.warning(self, "Lỗi", "Không thể xóa profile 'Default'"); return
        
        ret = QMessageBox.question(self, "Xác nhận", f"Xóa profile '{pname}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            del self._profiles[pname]
            self._save_profiles()
            self._update_profile_ui()
            QMessageBox.information(self, "Thành công", f"Đã xóa profile: {pname}")

    # ── Settings Dialog ───────────────────────────────────────────────────────
    def _open_settings_dialog(self):
        pname = self.profile_combo.currentText() or "Default"
        dlg = QDialog(self); dlg.setWindowTitle(f"⚙  Cài Đặt — {pname}")
        dlg.setMinimumWidth(720); dlg.setMinimumHeight(850); dlg.setStyleSheet(STYLE)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)

        # Title bar
        title_bar = QFrame()
        title_bar.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0d1629,stop:1 #111827);border-bottom:1px solid #1e3050;")
        title_bar.setFixedHeight(68)
        tb_lay = QHBoxLayout(title_bar); tb_lay.setContentsMargins(20,0,20,0); tb_lay.setSpacing(14)
        tb_icon = QLabel("⚙"); tb_icon.setStyleSheet("font-size:28px;background:transparent;")
        tb_title = QVBoxLayout(); tb_title.setSpacing(2)
        tb_t1 = QLabel(f"Cài Đặt Profile: {pname}"); tb_t1.setStyleSheet("color:#e8edf5;font-size:15px;font-weight:800;background:transparent;")
        tb_t2 = QLabel("Cấu hình tasks, delays & API key"); tb_t2.setStyleSheet("color:#6b7d9f;font-size:11px;font-family:Consolas;background:transparent;")
        tb_title.addWidget(tb_t1); tb_title.addWidget(tb_t2)
        tb_lay.addWidget(tb_icon); tb_lay.addLayout(tb_title); tb_lay.addStretch()
        lay.addWidget(title_bar)

        # Body
        body = QWidget(); body.setStyleSheet("background:#0b0f14;")
        body_lay = QVBoxLayout(body); body_lay.setContentsMargins(20,16,20,16); body_lay.setSpacing(16)

        # API Key
        api_section = QFrame(); api_section.setStyleSheet("background:#111827;border:1px solid #1a2336;border-radius:10px;")
        api_lay = QVBoxLayout(api_section); api_lay.setContentsMargins(14,12,14,12); api_lay.setSpacing(8)
        api_hdr = QLabel("🔑  API Key"); api_hdr.setStyleSheet("color:#c9d6ea;font-size:11px;font-weight:700;font-family:Consolas;letter-spacing:1px;text-transform:uppercase;background:transparent;")
        api_lay.addWidget(api_hdr)
        self._dlg_api_key = QLineEdit(); self._dlg_api_key.setPlaceholderText("Nhập API key...")
        self._dlg_api_key.setText(self._run_settings.get("api_key",""))
        self._dlg_api_key.setMinimumHeight(36)
        api_lay.addWidget(self._dlg_api_key)
        body_lay.addWidget(api_section)

        # Tasks
        tasks_section = QFrame(); tasks_section.setStyleSheet("background:#111827;border:1px solid #1a2336;border-radius:10px;")
        tasks_lay = QVBoxLayout(tasks_section); tasks_lay.setContentsMargins(14,12,14,12); tasks_lay.setSpacing(10)
        tasks_hdr = QLabel("⚡  NHIỆM VỤ & CẤU HÌNH"); tasks_hdr.setStyleSheet("color:#c9d6ea;font-size:11px;font-weight:700;font-family:Consolas;letter-spacing:1px;text-transform:uppercase;background:transparent;")
        tasks_lay.addWidget(tasks_hdr)

        task_scroll = QScrollArea(); task_scroll.setWidgetResizable(True); task_scroll.setFrameShape(QFrame.NoFrame)
        task_scroll.setStyleSheet("QScrollArea{background:#0d1629;border:1px solid #1e3050;border-radius:8px;}")
        task_scroll.setMaximumHeight(320)
        task_container = QWidget(); task_container.setStyleSheet("background:#0d1629;")
        task_scroll_lay = QVBoxLayout(task_container); task_scroll_lay.setContentsMargins(8,8,8,8); task_scroll_lay.setSpacing(8)

        self._dlg_task_spins = {}
        for task_name in self.AVAILABLE_TASKS.keys():
            task_cfg = self._run_settings["task_settings"].get(task_name, self.AVAILABLE_TASKS[task_name])
            task_item = QFrame(); task_item.setStyleSheet("background:#0b0f14;border:1px solid #1a2336;border-radius:6px;")
            task_item_lay = QVBoxLayout(task_item); task_item_lay.setContentsMargins(10,8,10,8); task_item_lay.setSpacing(6)

            task_header = QHBoxLayout(); task_header.setSpacing(8)
            icon_lbl = QLabel(self.AVAILABLE_TASKS[task_name]["icon"]); icon_lbl.setStyleSheet("font-size:14px;")
            chk = QCheckBox(task_name); chk.setChecked(task_cfg.get("enabled", False))
            chk.setStyleSheet("QCheckBox{color:#c9d6ea;font-size:11px;font-weight:600;background:transparent;spacing:6px;} QCheckBox::indicator{width:14px;height:14px;border:1px solid #2e4570;border-radius:3px;background:#0a1020;} QCheckBox::indicator:checked{background:#4d8fff;border-color:#4d8fff;}")
            task_header.addWidget(icon_lbl); task_header.addWidget(chk); task_header.addStretch()
            task_item_lay.addLayout(task_header)

            settings_lay = QGridLayout(); settings_lay.setSpacing(6)
            spins = {}
            for col, (label, key, suffix) in enumerate([("Min (s)", "delay_min", "s"), ("Max (s)", "delay_max", "s"), ("Số lần", "count", "")]):
                lbl = QLabel(label); lbl.setStyleSheet("color:#8b9aaf;font-size:9px;font-family:Consolas;background:transparent;")
                spin = make_spinbox(task_cfg.get(key, self.AVAILABLE_TASKS[task_name].get(key, 1)), 1, 600 if "delay" in key else 100, suffix)
                spin.setMaximumWidth(120); spin.setMinimumHeight(28)
                spins[key] = spin
                settings_lay.addWidget(lbl, 0, col)
                settings_lay.addWidget(spin, 1, col)
            
            # Add stretch column for proper layout
            settings_lay.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 1, 3)

            self._dlg_task_spins[task_name] = (chk, spins)
            task_item_lay.addLayout(settings_lay)
            task_scroll_lay.addWidget(task_item)

        task_scroll_lay.addStretch()
        task_scroll.setWidget(task_container)
        tasks_lay.addWidget(task_scroll)
        body_lay.addWidget(tasks_section)

        # Timing
        timing_section = QFrame(); timing_section.setStyleSheet("background:#111827;border:1px solid #1a2336;border-radius:10px;")
        timing_lay = QVBoxLayout(timing_section); timing_lay.setContentsMargins(14,12,14,12); timing_lay.setSpacing(10)
        timing_hdr = QLabel("⏱  Delay Toàn Cục & Giới Hạn"); timing_hdr.setStyleSheet("color:#c9d6ea;font-size:11px;font-weight:700;font-family:Consolas;letter-spacing:1px;text-transform:uppercase;background:transparent;")
        timing_lay.addWidget(timing_hdr)
        timing_grid = QHBoxLayout(); timing_grid.setSpacing(8)

        self._dlg_spins = {}
        for label, key, val, suffix, mn, mx, color in [
            ("Delay Ngắn",  "delay_short",      5,   "s", 1,  300,  "#4d8fff"),
            ("Delay Dài",   "delay_long",       60,  "s", 10, 600,  "#a78bfa"),
            ("Sau N Task",  "delay_after_tasks", 5,  "",  1,  50,   "#f59e0b"),
            ("Dừng Sau",    "stop_after_tasks",  100, "", 1,  1000, "#ef4444"),
        ]:
            spin_card = QFrame(); spin_card.setStyleSheet("background:#0d1629;border:1px solid #1e3050;border-radius:8px;")
            spin_card_lay = QVBoxLayout(spin_card); spin_card_lay.setContentsMargins(10,8,10,8); spin_card_lay.setSpacing(4)
            lbl = QLabel(label); lbl.setStyleSheet(f"color:{color};font-size:9px;font-family:Consolas;font-weight:700;letter-spacing:1px;text-transform:uppercase;background:transparent;")
            spin = make_spinbox(self._run_settings.get(key, val), mn, mx, suffix)
            spin.setMinimumHeight(34); spin.setMaximumWidth(140)
            self._dlg_spins[key] = spin
            spin_card_lay.addWidget(lbl); spin_card_lay.addWidget(spin)
            timing_grid.addWidget(spin_card)
        timing_lay.addLayout(timing_grid)
        body_lay.addWidget(timing_section)
        body_lay.addStretch()
        lay.addWidget(body, 1)

        # Footer
        footer = QFrame(); footer.setStyleSheet("background:#0d1219;border-top:1px solid #1a2336;")
        footer.setFixedHeight(60)
        ft_lay = QHBoxLayout(footer); ft_lay.setContentsMargins(20,0,20,0); ft_lay.setSpacing(8)
        ft_lay.addStretch()
        cancel_btn = QPushButton("❌  Đóng"); cancel_btn.setMinimumHeight(36); cancel_btn.setMinimumWidth(100)
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor)); cancel_btn.clicked.connect(dlg.reject)
        apply_btn = QPushButton("✔  Áp Dụng & Lưu"); apply_btn.setObjectName("btnSuccess")
        apply_btn.setMinimumHeight(36); apply_btn.setMinimumWidth(150)
        apply_btn.setCursor(QCursor(Qt.PointingHandCursor)); apply_btn.clicked.connect(dlg.accept)
        ft_lay.addWidget(cancel_btn); ft_lay.addWidget(apply_btn)
        lay.addWidget(footer)

        if dlg.exec_() == QDialog.Accepted:
            self._run_settings["api_key"] = self._dlg_api_key.text().strip()
            self._run_settings["task_settings"] = {}
            self._run_settings["tasks"] = []
            for task_name, (chk, spins) in self._dlg_task_spins.items():
                is_enabled = chk.isChecked()
                self._run_settings["task_settings"][task_name] = {
                    "enabled": is_enabled,
                    "delay_min": spins["delay_min"].value(),
                    "delay_max": spins["delay_max"].value(),
                    "count": spins["count"].value()
                }
                if is_enabled:
                    self._run_settings["tasks"].append(task_name)
            for key, spin in self._dlg_spins.items():
                self._run_settings[key] = spin.value()
            self._profiles[self._current_profile] = self._run_settings.copy()
            self._save_profiles()
            tasks_str = ", ".join(self._run_settings["tasks"]) or "—"
            self._settings_badge.setText(f"📌 {self._current_profile} | {tasks_str[:40]}")
            self._settings_badge.setStyleSheet("color:#10b981;font-size:10px;font-family:Consolas;background:transparent;")
            QMessageBox.information(self, "Thành công", f"Đã lưu cài đặt cho profile '{self._current_profile}'")
    # ── Context menu ─────────────────────────────────────────────────────────
    def _ctx_menu_run(self, pos):
        menu = QMenu(self); menu.setStyleSheet(STYLE)
        menu.addAction("☑  Chọn tất cả", self._select_all)
        menu.addAction("☐ Bỏ chọn tất cả", self._deselect_all)
        menu.addSeparator()
        menu.addAction("➕  Thêm TDS", self._add_tds_from_context)
        menu.addAction("➕  Thêm Facebook", self._add_facebook_from_context)
        menu.addSeparator()
        menu.addAction("🗑  Xóa dòng chọn", self._delete_selected_rows)
        menu.exec_(self.tree_run.viewport().mapToGlobal(pos))

    def _select_all(self):
        for i in range(self.tree_run.topLevelItemCount()): self.tree_run.topLevelItem(i).setCheckState(0, Qt.Checked)

    def _deselect_all(self):
        for i in range(self.tree_run.topLevelItemCount()): self.tree_run.topLevelItem(i).setCheckState(0, Qt.Unchecked)

    def _delete_selected_rows(self):
        to_remove = []
        root = self.tree_run.invisibleRootItem()
        for i in range(self.tree_run.topLevelItemCount()):
            item = self.tree_run.topLevelItem(i)
            if item.isSelected(): to_remove.append(item)
        for item in to_remove: root.removeChild(item)
        if to_remove:
            self._save_accounts_to_profile()

    def _add_accounts_to_run(self):
        if not self.profile_combo.count():
            QMessageBox.warning(self, "Lỗi", "Tạo profile trước!"); return

        dlg = QDialog(self); dlg.setWindowTitle("Thêm Tài Khoản vào Chạy")
        dlg.setMinimumSize(520, 400); dlg.setStyleSheet(STYLE)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(16, 14, 16, 14); lay.setSpacing(10)

        tabs = QTabWidget(); lay.addWidget(tabs, 1)

        # ─── Tab 1: Chọn TDS có sẵn ──────────────────────────────────────
        tab1 = QWidget(); tab1_lay = QVBoxLayout(tab1); tab1_lay.setContentsMargins(0, 6, 0, 0); tab1_lay.setSpacing(8)
        title1 = QLabel("Chọn tài khoản TDS đã có trong hệ thống")
        title1.setStyleSheet("color:#c9d6ea;font-size:12px;font-weight:700;font-family:Consolas;")
        tab1_lay.addWidget(title1)
        tree_tds = QTreeWidget(); tree_tds.setObjectName("FbTree"); tree_tds.setColumnCount(3)
        tree_tds.setHeaderLabels(["Tài khoản TDS", "User", "Token"])
        tree_tds.header().setSectionResizeMode(0, QHeaderView.Stretch)
        tree_tds.header().setSectionResizeMode(1, QHeaderView.Interactive); tree_tds.header().resizeSection(1, 140)
        tree_tds.header().setSectionResizeMode(2, QHeaderView.Interactive); tree_tds.header().resizeSection(2, 180)
        tree_tds.setAlternatingRowColors(True); tree_tds.setIndentation(0)
        tds_data = self.tds_mgmt._tds_data if self.tds_mgmt else {}
        for idx, (user, data) in enumerate(tds_data.items(), 1):
            item = QTreeWidgetItem(); item.setCheckState(0, Qt.Unchecked)
            item.setIcon(0, QIcon(make_avatar_pixmap(user[0].upper() if user else "T", 22, idx % len(AVATAR_COLORS))))
            item.setText(0, user); item.setText(1, user)
            tk = data.get("token","")
            item.setText(2, tk[:40]+"…" if len(tk)>40 else (tk or "(chưa có)"))
            item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))
            item.setForeground(0, QColor("#d0d8e8")); item.setForeground(1, QColor("#4d8fff"))
            item.setForeground(2, QColor("#00d4aa") if tk else QColor("#3d5278"))
            item.setData(0, Qt.UserRole, user)
            tree_tds.addTopLevelItem(item)
        tab1_lay.addWidget(tree_tds, 1)
        tabs.addTab(tab1, "✓  Chọn TDS có sẵn")

        # ─── Tab 2: Nhập TDS riêng ───────────────────────────────────────
        tab2 = QWidget(); tab2_lay = QVBoxLayout(tab2); tab2_lay.setContentsMargins(0, 6, 0, 0); tab2_lay.setSpacing(8)

        tds_hdr_frame = QFrame()
        tds_hdr_frame.setStyleSheet("background:#111827;border:1px solid #1a2336;border-radius:8px;")
        tds_hdr_lay = QHBoxLayout(tds_hdr_frame); tds_hdr_lay.setContentsMargins(12,8,12,8)
        tds_icon = QLabel("🔵"); tds_icon.setStyleSheet("font-size:16px;background:transparent;")
        tds_hint_lay = QVBoxLayout(); tds_hint_lay.setSpacing(2)
        tds_hint_t = QLabel("Nhập danh sách tài khoản TDS")
        tds_hint_t.setStyleSheet("color:#c9d6ea;font-size:11px;font-weight:700;background:transparent;")
        tds_hint_s = QLabel("Mỗi dòng 1 tài khoản theo định dạng:   user|pass|token")
        tds_hint_s.setStyleSheet("color:#3d5278;font-size:10px;font-family:Consolas;background:transparent;")
        tds_hint_lay.addWidget(tds_hint_t); tds_hint_lay.addWidget(tds_hint_s)
        tds_hdr_lay.addWidget(tds_icon); tds_hdr_lay.addLayout(tds_hint_lay); tds_hdr_lay.addStretch()
        tab2_lay.addWidget(tds_hdr_frame)

        tds_text_input = QTextEdit()
        tds_text_input.setPlaceholderText(
            "user1|pass123|token1...\n"
            "user2|pass456|token2...\n"
            "user3|pass789|\n"
            "(token có thể trống nếu chưa có)"
        )
        tds_text_input.setStyleSheet(
            "QTextEdit{background:#050810;border:1px solid #1a2336;border-radius:8px;"
            "color:#6ba3ff;font-family:Consolas;font-size:12px;padding:8px;line-height:1.6;}"
        )
        tab2_lay.addWidget(tds_text_input, 1)
        tabs.addTab(tab2, "📋  Nhập TDS")

        # ─── Tab 3: Nhập Facebook riêng ──────────────────────────────────
        tab3 = QWidget(); tab3_lay = QVBoxLayout(tab3); tab3_lay.setContentsMargins(0, 6, 0, 0); tab3_lay.setSpacing(8)

        fb_hdr_frame = QFrame()
        fb_hdr_frame.setStyleSheet("background:#111827;border:1px solid #1a2336;border-radius:8px;")
        fb_hdr_lay = QHBoxLayout(fb_hdr_frame); fb_hdr_lay.setContentsMargins(12,8,12,8)
        fb_icon = QLabel("𝕗"); fb_icon.setStyleSheet("font-size:16px;color:#1877f2;background:transparent;font-weight:800;")
        fb_hint_lay = QVBoxLayout(); fb_hint_lay.setSpacing(2)
        fb_hint_t = QLabel("Nhập danh sách tài khoản Facebook")
        fb_hint_t.setStyleSheet("color:#c9d6ea;font-size:11px;font-weight:700;background:transparent;")
        fb_hint_s = QLabel("Mỗi dòng 1 tài khoản FB theo định dạng:   uid|cookie|proxy|token_page")
        fb_hint_s.setStyleSheet("color:#3d5278;font-size:10px;font-family:Consolas;background:transparent;")
        fb_hint_lay.addWidget(fb_hint_t); fb_hint_lay.addWidget(fb_hint_s)
        fb_hdr_lay.addWidget(fb_icon); fb_hdr_lay.addLayout(fb_hint_lay); fb_hdr_lay.addStretch()
        tab3_lay.addWidget(fb_hdr_frame)

        # Ghép TDS+FB note
        pair_note = QLabel("💡  Ghép theo thứ tự dòng: dòng 1 FB ↔ dòng 1 TDS, dòng 2 FB ↔ dòng 2 TDS, ...")
        pair_note.setStyleSheet(
            "background:rgba(45,111,255,0.08);border:1px solid rgba(45,111,255,0.25);"
            "border-radius:6px;color:#4d8fff;font-size:10px;font-family:Consolas;padding:5px 10px;"
        )
        tab3_lay.addWidget(pair_note)

        fb_text_input = QTextEdit()
        fb_text_input.setPlaceholderText(
            "100001234567890|c_user=100001234|proxy.com:8080|EAApage_token1...\n"
            "100009876543210|c_user=100009876|proxy.com:8081|EAApage_token2...\n"
            "100005555666777|c_user=100005555||"
        )
        fb_text_input.setStyleSheet(
            "QTextEdit{background:#050810;border:1px solid #1a2336;border-radius:8px;"
            "color:#ff8c5a;font-family:Consolas;font-size:12px;padding:8px;line-height:1.6;}"
        )
        tab3_lay.addWidget(fb_text_input, 1)
        tabs.addTab(tab3, "𝕗  Nhập Facebook")

        # ─── Buttons ───────────────────────────────────────────────────
        btn_row = QHBoxLayout(); btn_row.addStretch()
        cancel_btn = QPushButton("Huỷ"); cancel_btn.setMinimumHeight(34); cancel_btn.setMinimumWidth(80)
        cancel_btn.clicked.connect(dlg.reject)
        ok_btn = QPushButton("✔  Thêm vào danh sách"); ok_btn.setObjectName("btnSuccess")
        ok_btn.setMinimumHeight(34); ok_btn.setMinimumWidth(160)
        ok_btn.setCursor(QCursor(Qt.PointingHandCursor)); ok_btn.clicked.connect(dlg.accept)
        btn_row.addWidget(cancel_btn); btn_row.addWidget(ok_btn); lay.addLayout(btn_row)

        if dlg.exec_() != QDialog.Accepted:
            return

        tab_idx = tabs.currentIndex()
        count = 0

        if tab_idx == 0:
            # ─── Chọn TDS có sẵn ──────────────────────────────────────
            for i in range(tree_tds.topLevelItemCount()):
                item = tree_tds.topLevelItem(i)
                if item.checkState(0) == Qt.Checked:
                    user = item.data(0, Qt.UserRole); user_data = tds_data.get(user, {})
                    new_item = self._make_run_item(
                        user=user, pass_=user_data.get("pass","***"),
                        token=user_data.get("token",""),
                        row_idx=self.tree_run.topLevelItemCount()
                    )
                    self.tree_run.addTopLevelItem(new_item); count += 1

        elif tab_idx == 1:
            # ─── Nhập TDS riêng ───────────────────────────────────────
            lines = [l.strip() for l in tds_text_input.toPlainText().strip().split('\n') if l.strip()]
            for line in lines:
                parts = [p.strip() for p in line.split('|')]
                if not parts[0]: continue
                user  = parts[0]
                pass_ = parts[1] if len(parts) > 1 else ""
                token = parts[2] if len(parts) > 2 else ""
                new_item = self._make_run_item(
                    user=user, pass_=pass_, token=token,
                    row_idx=self.tree_run.topLevelItemCount()
                )
                self.tree_run.addTopLevelItem(new_item); count += 1

        elif tab_idx == 2:
            # ─── Nhập Facebook riêng — ghép với hàng TDS hiện có ─────────
            fb_lines = [l.strip() for l in fb_text_input.toPlainText().strip().split('\n') if l.strip()]
            total_existing = self.tree_run.topLevelItemCount()

            for i, line in enumerate(fb_lines):
                parts = [p.strip() for p in line.split('|')]
                fb_uid    = parts[0] if len(parts) > 0 else ""
                fb_cookie = parts[1] if len(parts) > 1 else ""
                fb_proxy  = parts[2] if len(parts) > 2 else ""
                fb_token  = parts[3] if len(parts) > 3 else ""

                if i < total_existing:
                    # Ghép vào hàng TDS đã có theo thứ tự
                    existing = self.tree_run.topLevelItem(i)
                    existing.setText(4, fb_uid)
                    existing.setText(5, fb_cookie[:40]+"…" if len(fb_cookie)>40 else fb_cookie)
                    existing.setText(6, fb_proxy)
                    existing.setText(7, fb_token[:40]+"…" if len(fb_token)>40 else fb_token)
                    existing.setForeground(4, QColor("#ff8c5a"))
                    existing.setForeground(5, QColor("#5a7099"))
                    existing.setForeground(6, QColor("#8b5cf6"))
                    existing.setForeground(7, QColor("#00d4aa") if fb_token else QColor("#3d5278"))
                    count += 1
                else:
                    # Nếu dư FB hơn TDS, tạo dòng mới chỉ có FB
                    new_item = self._make_run_item(
                        user="(chưa có TDS)", pass_="", token="",
                        fb_uid=fb_uid, fb_cookie=fb_cookie,
                        fb_proxy=fb_proxy, fb_token=fb_token,
                        row_idx=self.tree_run.topLevelItemCount()
                    )
                    self.tree_run.addTopLevelItem(new_item); count += 1

        if count > 0:
            self._save_accounts_to_profile()
            self._run_log_panel.append(f"[+] Đã thêm {count} tài khoản vào danh sách chạy") if hasattr(self, '_run_log_panel') else None
        else:
            QMessageBox.warning(self, "Lỗi", "Không có dòng hợp lệ nào. Kiểm tra lại định dạng nhập.")

    def _make_run_item(self, user, pass_, token, fb_uid="", fb_cookie="", fb_proxy="", fb_token="", row_idx=0):
        """Tạo QTreeWidgetItem cho tree_run"""
        new_item = QTreeWidgetItem()
        new_item.setCheckState(0, Qt.Unchecked)
        new_item.setIcon(0, QIcon(make_avatar_pixmap(
            user[0].upper() if user and user[0].isalpha() else "T",
            22, row_idx % len(AVATAR_COLORS)
        )))
        new_item.setText(0, user)
        new_item.setText(1, user)
        new_item.setText(2, pass_)
        new_item.setText(3, token)
        new_item.setText(4, fb_uid)
        new_item.setText(5, fb_cookie)
        new_item.setText(6, fb_proxy)
        new_item.setText(7, fb_token)
        # Initialize columns 8 and 9 for Status and Xu
        new_item.setText(8, "⏳ Chờ")
        new_item.setText(9, "0")
        
        full_data = {
            "user": user,
            "pass": pass_,
            "token": token,
            "fb_uid": fb_uid,
            "fb_cookie": fb_cookie,
            "fb_proxy": fb_proxy,
            "fb_token": fb_token,
        }
        new_item.setData(0, Qt.UserRole, full_data)
        
        tooltip = f"""<b>== FULL ACCOUNT DATA ==</b>
<b>User TDS:</b> {user}
<b>Pass TDS:</b> {pass_}
<b>Token TDS:</b> {token}
<b>FB UID:</b> {fb_uid}
<b>FB Cookie:</b> {fb_cookie}
<b>FB Proxy:</b> {fb_proxy if fb_proxy else '(empty)'}
<b>FB Token:</b> {fb_token}"""
        new_item.setToolTip(0, tooltip)
        
        new_item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))
        new_item.setForeground(0, QColor("#d0d8e8"))
        new_item.setForeground(1, QColor("#4d8fff"))
        new_item.setForeground(2, QColor("#5a7099"))
        new_item.setForeground(3, QColor("#00d4aa") if token else QColor("#3d5278"))
        new_item.setForeground(4, QColor("#ff8c5a") if fb_uid else QColor("#3d5278"))
        new_item.setForeground(5, QColor("#5a7099"))
        new_item.setForeground(6, QColor("#8b5cf6") if fb_proxy else QColor("#3d5278"))
        new_item.setForeground(7, QColor("#00d4aa") if fb_token else QColor("#3d5278"))
        return new_item

    def _create_stat_widget(self, label, value, color):
        """Tạo widget hiển thị thống kê"""
        stat_widget = QFrame()
        stat_widget.setStyleSheet(f"background:#0b0f14;border:1px solid #1a2336;border-radius:8px;")
        stat_lay = QVBoxLayout(stat_widget); stat_lay.setContentsMargins(12,10,12,10); stat_lay.setSpacing(4)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color:{color};font-size:11px;font-family:Consolas;font-weight:700;background:transparent;")
        stat_lay.addWidget(lbl)
        
        val = QLabel(value)
        val.setObjectName("stat_value")
        val.setStyleSheet(f"color:white;font-size:24px;font-weight:800;background:transparent;")
        val.setAlignment(Qt.AlignCenter)
        stat_lay.addWidget(val)
        
        # Store reference cho update sau
        stat_widget._value_label = val
        
        return stat_widget
    
    def update_stats(self, tasks_done=None, xu_earned=None, tasks_error=None):
        """Update các stat widgets"""
        if tasks_done is not None:
            self._stat_tasks_done._value_label.setText(str(tasks_done))
        if xu_earned is not None:
            self._stat_xu_earned._value_label.setText(str(xu_earned))
        if tasks_error is not None:
            self._stat_tasks_error._value_label.setText(str(tasks_error))
    
    def _on_tree_update_signal(self, tds_user, status, xu):
        """Slot handler for tree updates from background thread"""
        for i in range(self.tree_run.topLevelItemCount()):
            item = self.tree_run.topLevelItem(i)
            if item.text(1) == tds_user:
                item.setText(8, status)
                item.setText(9, str(xu))
                # Update color based on status
                if "✅" in status:
                    item.setForeground(8, QColor("#00d4aa"))
                elif "❌" in status:
                    item.setForeground(8, QColor("#ef4444"))
                elif "⏳" in status:
                    item.setForeground(8, QColor("#f59e0b"))
                item.setForeground(9, QColor("#00d4aa"))
                # Force repaint
                self.tree_run.scrollToItem(item)
                self.tree_run.resizeColumnToContents(8)
                self.tree_run.resizeColumnToContents(9)
                break

    def _on_button_state_changed(self, button_name, enabled):
        """Slot handler to update button state from background thread"""
        btn = getattr(self, button_name, None)
        if btn:
            btn.setEnabled(enabled)

    def _add_tds_from_context(self):
        """Thêm nhiều TDS account từ context menu."""
        dlg = QDialog(self); dlg.setWindowTitle("➕ Thêm Tài Khoản TDS")
        dlg.setMinimumSize(500, 400); dlg.setStyleSheet(STYLE)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(16,16,16,16); lay.setSpacing(12)
        
        hint = QLabel("💡 Nhập mỗi dòng 1 tài khoản TDS theo định dạng:   user|pass|token")
        hint.setStyleSheet("color:#3d5278;font-size:11px;font-family:Consolas;")
        lay.addWidget(hint)
        
        text_input = QTextEdit()
        text_input.setPlaceholderText(
            "user1|pass123|token1...\n"
            "user2|pass456|token2...\n"
            "user3|pass789|\n"
            "(token có thể trống nếu chưa có)"
        )
        text_input.setStyleSheet(
            "QTextEdit{background:#050810;border:1px solid #1a2336;border-radius:8px;"
            "color:#6ba3ff;font-family:Consolas;font-size:12px;padding:8px;line-height:1.6;}"
        )
        lay.addWidget(text_input, 1)
        
        btn_lay = QHBoxLayout()
        ok_btn = QPushButton("✔  Thêm"); ok_btn.setObjectName("btnSuccess"); ok_btn.setMinimumHeight(36)
        cancel_btn = QPushButton("Huỷ"); cancel_btn.setMinimumHeight(36)
        ok_btn.clicked.connect(dlg.accept); cancel_btn.clicked.connect(dlg.reject)
        btn_lay.addStretch(); btn_lay.addWidget(cancel_btn); btn_lay.addWidget(ok_btn)
        lay.addLayout(btn_lay)
        
        if dlg.exec_() == QDialog.Accepted:
            lines = [l.strip() for l in text_input.toPlainText().strip().split('\n') if l.strip()]
            count = 0
            for line in lines:
                parts = [p.strip() for p in line.split('|')]
                if not parts[0]: continue
                
                user = parts[0]
                pass_ = parts[1] if len(parts) > 1 else ""
                token = parts[2] if len(parts) > 2 else ""
                
                new_item = self._make_run_item(
                    user=user, pass_=pass_, token=token,
                    row_idx=self.tree_run.topLevelItemCount()
                )
                self.tree_run.addTopLevelItem(new_item)
                count += 1
            
            if count > 0:
                self._save_accounts_to_profile()
                if hasattr(self, '_run_log_panel'):
                    self._run_log_panel.append(f"[+] Đã thêm {count} tài khoản TDS từ context menu")
                QMessageBox.information(self, "Thành công", f"Đã thêm {count} tài khoản TDS")
            else:
                QMessageBox.warning(self, "Lỗi", "Không có dòng hợp lệ nào")

    def _add_facebook_from_context(self):
        """Thêm nhiều Facebook vào dòng TDS đang chọn."""
        selected_items = self.tree_run.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Lỗi", "Chọn 1 dòng TDS trước!"); return
        
        current_item = selected_items[0]
        
        dlg = QDialog(self); dlg.setWindowTitle("➕ Thêm Tài Khoản Facebook")
        dlg.setMinimumSize(500, 400); dlg.setStyleSheet(STYLE)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(16,16,16,16); lay.setSpacing(12)
        
        hint = QLabel("💡 Nhập mỗi dòng 1 tài khoản Facebook theo định dạng:   uid|cookie|proxy|token")
        hint.setStyleSheet("color:#3d5278;font-size:11px;font-family:Consolas;")
        lay.addWidget(hint)
        
        text_input = QTextEdit()
        text_input.setPlaceholderText(
            "12345|EAAB...|http://proxy:port|EAA...\n"
            "67890|DABC...|http://proxy:port|\n"
            "(proxy & token có thể trống)"
        )
        text_input.setStyleSheet(
            "QTextEdit{background:#050810;border:1px solid #1a2336;border-radius:8px;"
            "color:#6ba3ff;font-family:Consolas;font-size:12px;padding:8px;line-height:1.6;}"
        )
        lay.addWidget(text_input, 1)
        
        # Option: thêm nhiều dòng hay ghép vào dòng đã chọn
        option_lay = QHBoxLayout()
        radio1 = QRadioButton("Thêm nhiều dòng FB mới"); radio1.setChecked(True)
        radio2 = QRadioButton("Ghép vào dòng TDS đã chọn")
        option_lay.addWidget(radio1); option_lay.addWidget(radio2)
        lay.addLayout(option_lay)
        
        btn_lay = QHBoxLayout()
        ok_btn = QPushButton("✔  Thêm"); ok_btn.setObjectName("btnSuccess"); ok_btn.setMinimumHeight(36)
        cancel_btn = QPushButton("Huỷ"); cancel_btn.setMinimumHeight(36)
        ok_btn.clicked.connect(dlg.accept); cancel_btn.clicked.connect(dlg.reject)
        btn_lay.addStretch(); btn_lay.addWidget(cancel_btn); btn_lay.addWidget(ok_btn)
        lay.addLayout(btn_lay)
        
        if dlg.exec_() == QDialog.Accepted:
            lines = [l.strip() for l in text_input.toPlainText().strip().split('\n') if l.strip()]
            count = 0
            
            if radio1.isChecked():
                # Thêm nhiều dòng FB mới
                for line in lines:
                    parts = [p.strip() for p in line.split('|')]
                    if not parts[0]: continue
                    
                    fb_uid = parts[0]
                    fb_cookie = parts[1] if len(parts) > 1 else ""
                    fb_proxy = parts[2] if len(parts) > 2 else ""
                    fb_token = parts[3] if len(parts) > 3 else ""
                    
                    new_item = self._make_run_item(
                        user="(chưa có TDS)", pass_="", token="",
                        fb_uid=fb_uid, fb_cookie=fb_cookie, fb_proxy=fb_proxy, fb_token=fb_token,
                        row_idx=self.tree_run.topLevelItemCount()
                    )
                    self.tree_run.addTopLevelItem(new_item)
                    count += 1
            else:
                # Ghép vào dòng TDS đã chọn
                if len(lines) > 0:
                    parts = [p.strip() for p in lines[0].split('|')]
                    fb_uid = parts[0] if len(parts) > 0 else ""
                    fb_cookie = parts[1] if len(parts) > 1 else ""
                    fb_proxy = parts[2] if len(parts) > 2 else ""
                    fb_token = parts[3] if len(parts) > 3 else ""
                    
                    current_item.setText(4, fb_uid)
                    current_item.setText(5, fb_cookie[:40]+"…" if len(fb_cookie)>40 else fb_cookie)
                    current_item.setText(6, fb_proxy)
                    current_item.setText(7, fb_token[:40]+"…" if len(fb_token)>40 else fb_token)
                    current_item.setForeground(4, QColor("#ff8c5a"))
                    current_item.setForeground(5, QColor("#5a7099"))
                    current_item.setForeground(6, QColor("#8b5cf6"))
                    current_item.setForeground(7, QColor("#00d4aa") if fb_token else QColor("#3d5278"))
                    
                    # Update full data (setData) with new FB info
                    full_data = current_item.data(0, Qt.UserRole) or {}
                    full_data.update({
                        "fb_uid": fb_uid,
                        "fb_cookie": fb_cookie,
                        "fb_proxy": fb_proxy,
                        "fb_token": fb_token,
                    })
                    current_item.setData(0, Qt.UserRole, full_data)
                    count = 1
            
            if count > 0:
                self._save_accounts_to_profile()
                QMessageBox.information(self, "Thành công", f"Đã thêm {count} tài khoản Facebook")
            else:
                QMessageBox.warning(self, "Lỗi", "Không có dòng hợp lệ nào")
    def _start_running(self):
        if not self.tree_run.topLevelItemCount():
            QMessageBox.warning(self, "Lỗi", "Thêm tài khoản trước!"); return
        tasks = self._run_settings.get("tasks", [])
        if not tasks:
            QMessageBox.warning(self, "Lỗi", "Chọn nhiệm vụ trong Cài Đặt Chạy trước!"); return
        api_key = self._run_settings.get("api_key", "")
        if not api_key:
            QMessageBox.warning(self, "Lỗi", "Nhập API key trong Cài Đặt Chạy!"); return

        accounts = []
        for i in range(self.tree_run.topLevelItemCount()):
            item = self.tree_run.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                full_data = item.data(0, Qt.UserRole) or {}
                accounts.append({
                    "tds_user":  full_data.get("user",     item.text(1)),
                    "tds_pass":  full_data.get("pass",     item.text(2)),
                    "tds_token": full_data.get("token",    item.text(3)),
                    "fb_uid":    full_data.get("fb_uid",   item.text(4)),
                    "fb_cookie": full_data.get("fb_cookie",item.text(5)),
                    "fb_proxy":  full_data.get("fb_proxy", item.text(6)),
                    "fb_token":  full_data.get("fb_token", item.text(7)),
                })

        if not accounts:
            QMessageBox.warning(self, "Lỗi", "Chọn ít nhất 1 tài khoản để chạy!"); return

        tasks_data = []
        for task_name, task_cfg in self._run_settings.get("task_settings", {}).items():
            if task_cfg.get("enabled", False):
                code_name = self.AVAILABLE_TASKS.get(task_name, {}).get("code_name", task_name)
                tasks_data.append({
                    "type_job":    code_name,
                    "display_name": task_name,
                    "delay_min":   task_cfg.get("delay_min", 5),
                    "delay_max":   task_cfg.get("delay_max", 60),
                    "count":       task_cfg.get("count", 1)
                })

        data = {
            "settings": {
                "api_key":          api_key,
                "delay_short":      self._run_settings.get("delay_short", 5),
                "delay_long":       self._run_settings.get("delay_long", 60),
                "delay_after_tasks":self._run_settings.get("delay_after_tasks", 5),
                "stop_after_tasks": self._run_settings.get("stop_after_tasks", 100)
            },
            "tasks":    tasks_data,
            "accounts": accounts
        }

        print("[DEBUG TDS] Data gửi đến RUN_TDS:")
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))

        print("\n[DEBUG TDS] ===== FULL ACCOUNT DATA =====")
        for acc in accounts:
            print(f"\n  TDS User:   {acc.get('tds_user','')}")
            print(f"  TDS Pass:   {acc.get('tds_pass','')}")
            print(f"  TDS Token:  {acc.get('tds_token','')}")
            print(f"  FB UID:     {acc.get('fb_uid','')}")
            print(f"  FB Cookie:  {acc.get('fb_cookie','')}")
            print(f"  FB Proxy:   {acc.get('fb_proxy','')}")
            print(f"  FB Token:   {acc.get('fb_token','')}")

        try:
            with open('tds_run_data_full.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("\n[DEBUG TDS] ✓ Saved to: tds_run_data_full.json")
        except Exception as e:
            print(f"[DEBUG TDS] ✗ Error saving: {e}")

        def log_callback(msg):
            self.log_emitter.log_signal.emit(msg)

        def tree_callback(tds_user, status, xu):
            self.log_emitter.tree_signal.emit(tds_user, status, xu)

        def stats_callback(tasks_done, xu_earned, tasks_error):
            self.update_stats(tasks_done=tasks_done, xu_earned=xu_earned, tasks_error=tasks_error)

        from TDS.run_TDS import TDS_RUN
        runner = TDS_RUN(data, callbacks={
            'log':   log_callback,
            'tree':  tree_callback,
            'stats': stats_callback
        })
        self._tds_runner = runner  # Store reference for stop functionality

        task_names = [t.get("type_job","") for t in tasks_data]
        self._run_log_panel.append(f"[START] Chạy {len(task_names)} nhiệm vụ: {', '.join(task_names)}")
        self._run_log_panel.append(f"[INFO] Delay: {self._run_settings['delay_short']}s–{self._run_settings['delay_long']}s | Dừng sau: {self._run_settings['stop_after_tasks']} task")
        self._run_log_panel.append(f"[ACCOUNTS] Đã select {len(accounts)} tài khoản")

        # Disable Start button, enable Stop button (via signal for thread safety)
        self.log_emitter.button_state_signal.emit("_tds_btn_start_run", False)
        self.log_emitter.button_state_signal.emit("_tds_btn_stop_run", True)
        
        # Wrapper function to run and then re-enable buttons
        def run_with_cleanup():
            try:
                runner.main()
            finally:
                # Re-enable Start button when done (via signal for thread safety)
                self.log_emitter.button_state_signal.emit("_tds_btn_start_run", True)
                self.log_emitter.button_state_signal.emit("_tds_btn_stop_run", False)
                self._run_log_panel.append("[END] Quá trình chạy kết thúc")

        import threading
        run_thread = threading.Thread(target=run_with_cleanup, daemon=True)
        self._tds_run_thread = run_thread  # Store reference for potential cleanup
        run_thread.start()

        QMessageBox.information(self, "Thông báo", f"Cấu hình OK — {len(task_names)} nhiệm vụ với {len(accounts)} tài khoản")
    
    def _stop_running(self):
        """Stop the running TDS process"""
        if not self._tds_runner:
            QMessageBox.warning(self, "Lỗi", "Chưa có quá trình chạy nào!")
            return
        
        self._run_log_panel.append("[STOP] Yêu cầu dừng chương trình...")
        self._tds_runner.stop()
        
        # Disable stop button (via signal for thread safety)
        self.log_emitter.button_state_signal.emit("_tds_btn_stop_run", False)

    def _clear_run_list(self):
        self.tree_run.clear()


# ─────────────────────────────────────────────────────────────────────────────
#  TRAODOISUB MANAGEMENT PAGE
# ─────────────────────────────────────────────────────────────────────────────
class TraodoisubManagementPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tds_data = {}
        self._data_file = "traodoisub_accounts.json"
        self._log_panel = None
        self._reg_thread = None
        self._load_data()

        root_lay = QVBoxLayout(self); root_lay.setContentsMargins(20,16,20,16); root_lay.setSpacing(0)

        hdr = QHBoxLayout(); hdr.setSpacing(14)
        icon = QLabel("🌐"); icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #06b6d4,stop:1 #22d3ee);border-radius:12px;color:white;font-size:20px;font-weight:800;min-width:46px;max-width:46px;min-height:46px;max-height:46px;")
        hdr.addWidget(icon)
        hdr_text = QVBoxLayout(); hdr_text.setSpacing(2)
        t1 = QLabel("Quản Lý Tài Khoản Traodoisub"); t1.setObjectName("PageTitle")
        t2 = QLabel("Quản lý & tạo tài khoản Traodoisub tự động"); t2.setObjectName("PageSub")
        hdr_text.addWidget(t1); hdr_text.addWidget(t2)
        hdr.addLayout(hdr_text); hdr.addStretch()
        root_lay.addLayout(hdr); root_lay.addSpacing(14)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_manage_tab(), "📋  Quản lý tài khoản")
        self.tabs.addTab(self._create_create_tab(), "➕  Tạo tài khoản")
        root_lay.addWidget(self.tabs, 1)

    def _make_tree(self, columns, headers):
        tree = QTreeWidget(); tree.setObjectName("FbTree")
        tree.setColumnCount(columns)
        tree.setHeaderLabels(headers)
        tree.setAlternatingRowColors(True)
        tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        tree.setIndentation(0)
        return tree

    def _create_manage_tab(self):
        w = QWidget(); w.setStyleSheet("background:#0b0f14;")
        lay = QVBoxLayout(w); lay.setContentsMargins(12,12,12,12); lay.setSpacing(8)

        tb = QHBoxLayout(); tb.setSpacing(8)
        for label, obj_name, slot in [
            ("➕  Thêm 1 TK", "btnPrimary", self._add_single_account),
            ("📁  Import file", "btnPrimary", self._add_bulk_accounts),
            ("💰  Check Xu", "btnSuccess", self._check_xu_selected),
            ("🗑  Xóa chọn", "btnDanger", self._delete_selected_accounts),
        ]:
            btn = QPushButton(label); btn.setObjectName(obj_name)
            btn.setCursor(QCursor(Qt.PointingHandCursor)); btn.clicked.connect(slot)
            tb.addWidget(btn)
        tb.addStretch(); lay.addLayout(tb)

        self.tree_manage = self._make_tree(5, ["Tên tài khoản", "UID / User", "Pass", "Token", "Xu"])
        self.tree_manage.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree_manage.header().setSectionResizeMode(1, QHeaderView.Interactive); self.tree_manage.header().resizeSection(1, 160)
        self.tree_manage.header().setSectionResizeMode(2, QHeaderView.Interactive); self.tree_manage.header().resizeSection(2, 120)
        self.tree_manage.header().setSectionResizeMode(3, QHeaderView.Interactive); self.tree_manage.header().resizeSection(3, 200)
        self.tree_manage.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tree_manage.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_manage.customContextMenuRequested.connect(self._ctx_menu_manage)
        lay.addWidget(self.tree_manage, 1)
        self._refresh_tree_manage()
        return w

    def _create_create_tab(self):
        w = QWidget(); w.setStyleSheet("background:#0b0f14;")
        lay = QVBoxLayout(w); lay.setContentsMargins(12,12,12,12); lay.setSpacing(12)

        cfg_frame = QFrame(); cfg_frame.setStyleSheet("background:#111827;border:1px solid #1a2336;border-radius:8px;")
        cfg_lay = QHBoxLayout(cfg_frame); cfg_lay.setContentsMargins(14,10,14,10); cfg_lay.setSpacing(10)
        cfg_lay.addWidget(QLabel("🔑 Key 3xcaptcha:"))
        self.api_key_input = QLineEdit(); self.api_key_input.setPlaceholderText("Nhập API key..."); self.api_key_input.setMaximumWidth(360)
        cfg_lay.addWidget(self.api_key_input)
        cfg_lay.addWidget(QLabel("🧵 Luồng:"))
        self.thread_spin = make_spinbox(3, 1, 10)
        self.thread_spin.setMaximumWidth(90)
        cfg_lay.addWidget(self.thread_spin); cfg_lay.addStretch()
        self.start_btn_tds = QPushButton("🚀  Bắt Đầu Tạo TK"); self.start_btn_tds.setObjectName("btnSuccess")
        self.start_btn_tds.setCursor(QCursor(Qt.PointingHandCursor)); self.start_btn_tds.clicked.connect(self._start_creating)
        cfg_lay.addWidget(self.start_btn_tds)
        lay.addWidget(cfg_frame)

        self.tree_create = self._make_tree(4, ["Tên tài khoản", "User", "Pass", "Token"])
        self.tree_create.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree_create.header().setSectionResizeMode(1, QHeaderView.Interactive); self.tree_create.header().resizeSection(1, 150)
        self.tree_create.header().setSectionResizeMode(2, QHeaderView.Interactive); self.tree_create.header().resizeSection(2, 120)
        self.tree_create.header().setSectionResizeMode(3, QHeaderView.Interactive); self.tree_create.header().resizeSection(3, 200)
        self.tree_create.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_create.customContextMenuRequested.connect(self._ctx_menu_create)
        lay.addWidget(self.tree_create, 1)

        self._log_panel = LogPanel()
        lay.addWidget(self._log_panel)
        return w

    def _refresh_tree_manage(self):
        self.tree_manage.clear()
        for idx, (user, data) in enumerate(self._tds_data.items(), 1):
            item = QTreeWidgetItem()
            item.setCheckState(0, Qt.Unchecked)
            item.setIcon(0, QIcon(make_avatar_pixmap(user[0].upper() if user else "T", 22, idx % len(AVATAR_COLORS))))
            item.setText(0, user)
            item.setText(1, str(idx))
            pass_len = len(data.get("pass",""))
            item.setText(2, "●" * min(pass_len, 16) if pass_len else "(trống)")
            tk = data.get("token","")
            item.setText(3, tk[:36] + "…" if len(tk) > 36 else (tk or "(chưa có)"))
            xu = data.get("xu", 0)
            item.setText(4, str(xu))
            item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))
            item.setForeground(0, QColor("#d0d8e8"))
            item.setForeground(1, QColor("#4d8fff"))
            item.setForeground(2, QColor("#5a7099"))
            item.setForeground(3, QColor("#00d4aa") if tk else QColor("#3d5278"))
            item.setForeground(4, QColor("#f59e0b"))
            item.setData(0, Qt.UserRole, user)
            self.tree_manage.addTopLevelItem(item)

    def _get_checked_users(self, tree):
        users = []
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                user = item.data(0, Qt.UserRole)
                if user: users.append(user)
        return users

    def _ctx_menu_manage(self, pos):
        menu = QMenu(self); menu.setStyleSheet(STYLE)
        menu.addAction("☑  Chọn tất cả", lambda: self._select_all_tree(self.tree_manage))
        menu.addAction("☐  Bỏ chọn tất cả", lambda: self._deselect_all_tree(self.tree_manage))
        menu.addSeparator()
        menu.addAction("📋  Copy User", lambda: self._copy_col(self.tree_manage, 1, "user"))
        menu.addAction("📋  Copy Pass", lambda: self._copy_col(self.tree_manage, 2, "pass"))
        menu.addAction("📋  Copy Token", lambda: self._copy_col(self.tree_manage, 3, "token"))
        menu.addAction("📋  Copy User|Pass|Token", lambda: self._copy_all_col(self.tree_manage, [1,2,3]))
        menu.addSeparator()
        menu.addAction("🗑  Xóa chọn", self._delete_selected_accounts)
        menu.exec_(self.tree_manage.viewport().mapToGlobal(pos))

    def _ctx_menu_create(self, pos):
        menu = QMenu(self); menu.setStyleSheet(STYLE)
        menu.addAction("☑  Chọn tất cả", lambda: self._select_all_tree(self.tree_create))
        menu.addAction("☐  Bỏ chọn tất cả", lambda: self._deselect_all_tree(self.tree_create))
        menu.addSeparator()
        menu.addAction("📋  Copy User", lambda: self._copy_col(self.tree_create, 1, "user"))
        menu.addAction("📋  Copy Pass", lambda: self._copy_col(self.tree_create, 2, "pass"))
        menu.addAction("📋  Copy Token", lambda: self._copy_col(self.tree_create, 3, "token"))
        menu.addAction("📋  Copy User|Pass|Token", lambda: self._copy_all_col(self.tree_create, [1,2,3]))
        menu.exec_(self.tree_create.viewport().mapToGlobal(pos))

    def _select_all_tree(self, tree):
        for i in range(tree.topLevelItemCount()): tree.topLevelItem(i).setCheckState(0, Qt.Checked)

    def _deselect_all_tree(self, tree):
        for i in range(tree.topLevelItemCount()): tree.topLevelItem(i).setCheckState(0, Qt.Unchecked)

    def _copy_col(self, tree, col, field):
        texts = []
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                if field == "user": texts.append(item.data(0, Qt.UserRole) or "")
                else: texts.append(item.text(col))
        if texts: QApplication.clipboard().setText("\n".join(texts)); QMessageBox.information(self, "OK", f"Đã copy {len(texts)} dòng")

    def _copy_all_col(self, tree, cols):
        texts = []
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                row_data = "|".join([item.text(col) for col in cols])
                texts.append(row_data)
        if texts: QApplication.clipboard().setText("\n".join(texts)); QMessageBox.information(self, "OK", f"Đã copy {len(texts)} dòng (user|pass|token)")

    def _add_single_account(self):
        dlg = QDialog(self); dlg.setWindowTitle("Thêm tài khoản Traodoisub"); dlg.setMinimumWidth(400); dlg.setStyleSheet(STYLE)
        lay = QFormLayout(dlg); lay.setSpacing(10)
        user_in = QLineEdit(); pass_in = QLineEdit(); token_in = QLineEdit()
        pass_in.setEchoMode(QLineEdit.Password)
        lay.addRow("User:", user_in); lay.addRow("Pass:", pass_in); lay.addRow("Token:", token_in)
        btn_lay = QHBoxLayout()
        ok_btn = QPushButton("✔  Thêm"); ok_btn.setObjectName("btnPrimary"); ok_btn.clicked.connect(dlg.accept)
        cancel_btn = QPushButton("Huỷ"); cancel_btn.clicked.connect(dlg.reject)
        btn_lay.addStretch(); btn_lay.addWidget(cancel_btn); btn_lay.addWidget(ok_btn)
        lay.addRow("", btn_lay)
        if dlg.exec_() == QDialog.Accepted:
            user = user_in.text().strip()
            if user:
                self._tds_data[user] = {"pass": pass_in.text(), "token": token_in.text(), "xu": 0}
                self._save_data(); self._refresh_tree_manage()

    def _add_bulk_accounts(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file tài khoản", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f: lines = f.readlines()
                for line in lines:
                    parts = line.strip().split('|')
                    if len(parts) >= 2 and parts[0]:
                        self._tds_data[parts[0]] = {"pass": parts[1] if len(parts)>1 else "","token": parts[2] if len(parts)>2 else "","xu": 0}
                self._save_data(); self._refresh_tree_manage()
                QMessageBox.information(self, "Thành công", f"Đã import {len(lines)} tài khoản")
            except Exception as e: QMessageBox.warning(self, "Lỗi", f"Lỗi import: {str(e)}")

    def _delete_selected_accounts(self):
        to_delete = self._get_checked_users(self.tree_manage)
        if to_delete:
            ret = QMessageBox.question(self, "Xác nhận", f"Xóa {len(to_delete)} tài khoản?")
            if ret == QMessageBox.Yes:
                for user in to_delete: self._tds_data.pop(user, None)
                self._save_data(); self._refresh_tree_manage()

    def _check_xu_selected(self):
        selected_users = self._get_checked_users(self.tree_manage)
        if not selected_users: QMessageBox.warning(self, "Thông báo", "Chọn ít nhất 1 tài khoản"); return
        
        try:
            from TDS.regworker import CheckXuBatchManager
            
            # Prepare user data with api keys
            users_list = [
                {"username": u, "api_key": self._tds_data.get(u, {}).get("token", "")}
                for u in selected_users if self._tds_data.get(u, {}).get("token")
            ]
            if not users_list: QMessageBox.warning(self, "Lỗi", "Không có token để kiểm tra"); return
            
            # Create progress dialog
            progress_dlg = CheckXuProgressDialog("Kiểm tra Xu Traodoisub", self)
            progress_dlg.set_total(len(users_list))
            
            updated_count = 0
            
            def on_progress(username, current, total):
                progress_dlg.set_current(username, current, total)
            
            def on_done(username, xu):
                nonlocal updated_count
                self._tds_data[username]["xu"] = xu
                updated_count += 1
            
            def on_all_done(results):
                progress_dlg.finish()
                self._save_data(); self._refresh_tree_manage()
                progress_dlg.accept()  # Close from callback
                QMessageBox.information(self, "Thành công", f"Đã cập nhật xu cho {updated_count}/{len(users_list)} tài khoản")
            
            # Start checking
            manager = CheckXuBatchManager(users_list, max_threads=5, callbacks={
                "progress": on_progress,
                "one_done": on_done,
                "all_done": on_all_done,
            })
            manager.start()
            
            # Show dialog
            progress_dlg.exec_()
        
        except ImportError as e:
            QMessageBox.warning(self, "Lỗi", f"Module chưa được cài đặt: {str(e)}")

    def _start_creating(self):
        num_accounts = self.thread_spin.value()
        num_threads = min(num_accounts, 5)  # Tối đa 5 luồng
        try:
            from TDS.regworker import TDSRegBatchManager
            
            self.tree_create.clear()
            if self._log_panel: self._log_panel.clear()
            if self._log_panel: self._log_panel.append(f"[→] Khởi động tạo {num_accounts} TK Traodoisub với {num_threads} luồng...")
            
            self.start_btn_tds.setEnabled(False)
            
            callbacks = {
                "log_msg": self._log_panel.append if self._log_panel else None,
                "one_done": self._on_tds_account_done,
                "all_done": self._on_tds_all_finished,
            }
            
            self._reg_batch_manager = TDSRegBatchManager(num_accounts, num_threads, callbacks)
            self._reg_batch_manager.start()
        except ImportError as e: 
            self.start_btn_tds.setEnabled(True)
            QMessageBox.warning(self, "Lỗi", f"Module chưa được cài đặt: {str(e)}")
        except Exception as e:
            self.start_btn_tds.setEnabled(True)
            QMessageBox.warning(self, "Lỗi", f"Lỗi: {str(e)}")

    def _on_tds_account_done(self, worker_id, result):
        """Khi tạo xong 1 tài khoản."""
        if result.get("ok"):
            user = result.get("username", "")
            item = QTreeWidgetItem(); item.setCheckState(0, Qt.Unchecked)
            item.setIcon(0, QIcon(make_avatar_pixmap(user[0].upper() if user else "T", 22)))
            item.setText(0, user); item.setText(1, user); item.setText(2, result.get('password',''))
            tk = result.get('token','')
            item.setText(3, tk[:40]+"…" if len(tk)>40 else tk)
            item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))
            item.setForeground(0, QColor("#d0d8e8")); item.setForeground(1, QColor("#4d8fff"))
            item.setForeground(2, QColor("#5a7099")); item.setForeground(3, QColor("#00d4aa"))
            item.setData(0, Qt.UserRole, user)
            self.tree_create.addTopLevelItem(item)
            self._tds_data[user] = {"pass": result.get('password',''), "token": tk, "xu": 0}

    def _on_tds_all_finished(self, results):
        """Khi tạo xong tất cả tài khoản."""
        if self._log_panel: self._log_panel.append(f"[✓] Hoàn thành! Tạo được {len(results)} tài khoản")
        self._save_data(); self._refresh_tree_manage()
        self.start_btn_tds.setEnabled(True)

    def _load_data(self):
        try:
            if os.path.exists(self._data_file):
                with open(self._data_file, 'r', encoding='utf-8') as f: self._tds_data = json.load(f)
        except: self._tds_data = {}

    def _save_data(self):
        try:
            with open(self._data_file, 'w', encoding='utf-8') as f: json.dump(self._tds_data, f, ensure_ascii=False, indent=2)
        except: pass


# ─────────────────────────────────────────────────────────────────────────────
#  ACCOUNT PLATFORM PAGE
# ─────────────────────────────────────────────────────────────────────────────
class AccountPlatformPage(QWidget):
    def __init__(self, platform="TDS", parent=None):
        super().__init__(parent)
        self.platform = platform
        layout = QVBoxLayout(self); layout.setContentsMargins(20,16,20,16); layout.setSpacing(0)
        hdr = QHBoxLayout()
        icon = QLabel("🌍"); icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #1f6feb,stop:1 #4d8fff);border-radius:12px;color:white;font-size:20px;min-width:46px;max-width:46px;min-height:46px;max-height:46px;")
        hdr.addWidget(icon); col = QVBoxLayout()
        t1 = QLabel(f"Tài Khoản {platform}"); t1.setObjectName("PageTitle")
        t2 = QLabel(f"Tạo & quản lý tài khoản {platform} tự động"); t2.setObjectName("PageSub")
        col.addWidget(t1); col.addWidget(t2); hdr.addLayout(col); hdr.addStretch()
        layout.addLayout(hdr); layout.addSpacing(14)
        lbl = QLabel("(Nội dung TDS)"); lbl.setStyleSheet("color:#2e4570;font-size:13px;font-family:Consolas;")
        layout.addWidget(lbl)


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR / TOPBAR / PLACEHOLDER
# ─────────────────────────────────────────────────────────────────────────────
class Sidebar(QFrame):
    def __init__(self, on_nav, parent=None):
        super().__init__(parent); self.setObjectName("Sidebar"); self.on_nav = on_nav
        self._current_page = "facebook"
        self._nav_buttons = {}
        out=QVBoxLayout(self); out.setContentsMargins(0,0,0,0); out.setSpacing(0)
        lf=QFrame(); lf.setObjectName("LogoFrame")
        ll=QHBoxLayout(lf); ll.setContentsMargins(14,0,14,0)
        ic=QLabel("⚡"); ic.setStyleSheet("font-size:22px;")
        ln=QLabel("MMO TOOL"); ln.setObjectName("LogoTitle")
        ls=QLabel("Professional v3.1"); ls.setObjectName("LogoSub")
        lt=QVBoxLayout(); lt.setSpacing(0); lt.addWidget(ln); lt.addWidget(ls)
        ll.addWidget(ic); ll.addLayout(lt); ll.addStretch(); out.addWidget(lf)
        sc=QScrollArea(); sc.setWidgetResizable(True); sc.setFrameShape(QFrame.NoFrame)
        sc.setStyleSheet("QScrollArea{background:#080c10;border:none;}")
        sc.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); sc.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nw=QWidget(); nw.setStyleSheet("background:#080c10;")
        self.nl=QVBoxLayout(nw); self.nl.setContentsMargins(0,4,0,4); self.nl.setSpacing(0)
        self._sec("Tổng Quan"); self._nav("⊞  Dashboard","dashboard")
        self._sec("Quản Lý TK")
        self._nav("𝕗  Facebook","facebook")
        self._sub("◈  Quản lý tài khoản","facebook",False,"sub_fb_manage")
        self._sub("◈  REG PAGEPRO5","facebook_reg",False,"sub_fb_reg")
        self._nav("🌐  Quản Lý TTC","ttc_manage")
        self._sub("◈  Quản lý tài khoản","ttc_manage",False,"sub_ttc_manage")
        self._sub("◈  Chạy TTC","run",False,"sub_ttc_run")
        self._nav("🔗  Quản Lý Traodoisub","traodoisub_manage")
        self._sub("◈  Quản lý tài khoản","traodoisub_manage",False,"sub_tds_manage")
        self._sub("◈  Chạy TDS","tds_run",False,"sub_tds_run")
        self._sec("Thao Tác"); self._nav("⚙  Cài Đặt","settings")
        self.nl.addStretch(); sc.setWidget(nw); out.addWidget(sc,1)
        ft=QFrame(); ft.setObjectName("SidebarFooter")
        fl=QHBoxLayout(ft); fl.setContentsMargins(0,0,0,0)
        sl=QLabel("● Online · v3.1.0"); sl.setObjectName("StatusLabel"); fl.addWidget(sl); out.addWidget(ft)
        self._set_active_sub_nav("facebook")

    def _sec(self,t): l=QLabel(t); l.setObjectName("NavSection"); self.nl.addWidget(l)

    def _nav(self,t,p,a=False):
        b=nav_btn(t,a); b.clicked.connect(lambda _,pg=p:self.on_nav(pg))
        self._nav_buttons[p] = b; self.nl.addWidget(b); return b

    def _sub(self,t,p,a=False,key=None):
        b=nav_btn(t,a,True); b.clicked.connect(lambda _,pg=p:self.on_nav(pg))
        if key: self._nav_buttons[key] = b
        else: self._nav_buttons[p] = b
        self.nl.addWidget(b); return b

    def _set_active_sub_nav(self, page):
        parent_map = {
            "facebook":     "facebook",
            "facebook_reg": "facebook",
            "ttc_manage":   "ttc_manage",
            "run":          "ttc_manage",
            "traodoisub_manage":"traodoisub_manage",
            "tds_run":      "traodoisub_manage",
            "dashboard":    "dashboard",
            "settings":     "settings",
        }
        sub_map = {
            "facebook":     "sub_fb_manage",
            "facebook_reg": "sub_fb_reg",
            "ttc_manage":   "sub_ttc_manage",
            "run":          "sub_ttc_run",
            "traodoisub_manage": "sub_tds_manage",
            "tds_run":      "sub_tds_run",
        }
        active_parent = parent_map.get(page, page)
        active_sub    = sub_map.get(page)

        for key in ["facebook", "ttc_manage", "traodoisub_manage", "dashboard", "settings"]:
            if key in self._nav_buttons:
                btn = self._nav_buttons[key]
                is_active = (key == active_parent)
                btn.setObjectName("NavBtnActive" if is_active else "NavBtn")
                btn.style().unpolish(btn); btn.style().polish(btn)

        for key in ["sub_fb_manage","sub_fb_reg","sub_ttc_manage","sub_ttc_run","sub_tds_manage","sub_tds_run"]:
            if key in self._nav_buttons:
                btn = self._nav_buttons[key]
                is_active = (key == active_sub)
                btn.setObjectName("SubNavBtnActive" if is_active else "SubNavBtn")
                btn.style().unpolish(btn); btn.style().polish(btn)


class Topbar(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent); self.setObjectName("Topbar")
        lay=QHBoxLayout(self); lay.setContentsMargins(16,0,16,0); lay.setSpacing(10)
        self.bc_pre=QLabel("Tổng quan  ›  "); self.bc_pre.setObjectName("Breadcrumb")
        self.bc_cur=QLabel("Facebook"); self.bc_cur.setObjectName("BreadcrumbCurrent")
        lay.addWidget(self.bc_pre); lay.addWidget(self.bc_cur); lay.addStretch()
        b1=QLabel("TTC: 12"); b1.setObjectName("BadgeBlue")
        b2=QLabel("TDS: 8");  b2.setObjectName("BadgeGreen")
        self.clk=QLabel("00:00:00"); self.clk.setObjectName("ClockLabel")
        lay.addWidget(b1); lay.addWidget(b2); lay.addWidget(self.clk)
    def set_page(self,n): self.bc_cur.setText(n)
    def update_clock(self): self.clk.setText(QDateTime.currentDateTime().toString("hh:mm:ss"))


class PlaceholderPage(QWidget):
    def __init__(self,icon,title,sub,parent=None):
        super().__init__(parent)
        lay=QVBoxLayout(self); lay.setAlignment(Qt.AlignCenter)
        for txt,css in [(icon,"font-size:40px;"),(title,"color:#2e3f5c;font-size:15px;font-weight:700;font-family:Consolas;"),(sub,"color:#1e2e45;font-size:11px;font-family:Consolas;")]:
            l=QLabel(txt); l.setAlignment(Qt.AlignCenter); l.setStyleSheet(css); lay.addWidget(l)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    PAGE_NAMES = {
        "facebook":"Facebook","facebook_reg":"Facebook - Register",
        "ttc_manage":"TTC - Manage","traodoisub_manage":"Traodoisub - Manage",
        "run":"TTC - Run","tds_run":"Traodoisub - Run","dashboard":"Dashboard","settings":"Settings"
    }

    def __init__(self):
        try:
            with open("debug.log", "a") as f:
                f.write("MainWindow init start\n"); f.flush()
                super().__init__()
                f.write("after super\n"); f.flush()
                self.setWindowTitle("MMO Tool Pro v3.1")
                self.resize(1440, 880); self.setMinimumSize(1100,650); self.setStyleSheet(STYLE)
                f.write("window settings done\n"); f.flush()
                cw=QWidget(); self.setCentralWidget(cw)
                root=QHBoxLayout(cw); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
                f.write("creating sidebar\n"); f.flush()
                self.sidebar=Sidebar(self.navigate); root.addWidget(self.sidebar)
                f.write("sidebar created\n"); f.flush()
                rw=QWidget(); rl=QVBoxLayout(rw); rl.setContentsMargins(0,0,0,0); rl.setSpacing(0)
                f.write("creating topbar\n"); f.flush()
                self.topbar=Topbar(); rl.addWidget(self.topbar)
                f.write("topbar created\n"); f.flush()
                self.stack=QStackedWidget()
                f.write("creating facebook page\n"); f.flush()
                self._facebook_page = FacebookPage()
                f.write("ttc page\n"); f.flush()
                self._ttc_manage_page = TTCManagementPage()
                f.write("traodoisub page\n"); f.flush()
                self._traodoisub_manage_page = TraodoisubManagementPage()
                f.write("register page\n"); f.flush()
                self._reg_page = RegisterPage(self._facebook_page)
                f.write("ttc run page\n"); f.flush()
                try:
                    ttc_run = TTCRunPage(self._ttc_manage_page)
                except:
                    ttc_run = PlaceholderPage("x","TTC","E1")
                
                f.write("tds run page\n"); f.flush()
                try:
                    tds_run = TDSRunPage(self._traodoisub_manage_page)
                except:
                    tds_run = PlaceholderPage("y","TDS","E2")
                
                f.write("creating pages dict\n"); f.flush()
                self._dashboard_page = DashboardPage(
                    self._facebook_page,
                    self._ttc_manage_page,
                    self._traodoisub_manage_page
                )
                
                placeholder_st = QWidget()
                placeholder_st_lay = QVBoxLayout(placeholder_st)
                placeholder_st_lay.addWidget(QLabel("Settings"))
                
                self.pages={
                    "facebook"          : self._facebook_page,
                    "facebook_reg"      : self._reg_page,
                    "ttc_manage"        : self._ttc_manage_page,
                    "traodoisub_manage" : self._traodoisub_manage_page,
                    "run"               : ttc_run,
                    "tds_run"           : tds_run,
                    "dashboard"         : self._dashboard_page,
                    "settings"          : placeholder_st,
                }
                f.write("pages dict created\n"); f.flush()
                f.write("adding pages to stack\n"); f.flush()
                for p in self.pages.values(): self.stack.addWidget(p)
                f.write("pages added\n"); f.flush()
                rl.addWidget(self.stack,1); root.addWidget(rw,1)
                f.write("statusbar\n"); f.flush()
                self.statusBar().showMessage("  MMO Tool Pro v3.1  |  Status: Online")
                self.statusBar().setStyleSheet("QStatusBar{background:#080c10;border-top:1px solid #1a2336;color:#10b981;font-size:11px;font-family:Consolas;padding:3px 12px;}")
                f.write("timer\n"); f.flush()
                self.timer=QTimer(); self.timer.timeout.connect(self.topbar.update_clock); self.timer.start(1000)
                self.topbar.update_clock(); 
                f.write("navigate\n"); f.flush()
                self.navigate("dashboard")
                f.write("MainWindow init DONE\n"); f.flush()
        except Exception as e:
            import traceback
            with open("debug.log", "a") as f:
                f.write(f"ERROR in MainWindow: {str(e)}\n")
                f.write(traceback.format_exc())
                f.flush()
            raise e

    def navigate(self, page):
        if page not in self.pages: page="dashboard"
        self.stack.setCurrentIndex(list(self.pages).index(page))
        self.topbar.set_page(self.PAGE_NAMES.get(page, page))
        self.sidebar._set_active_sub_nav(page)

    def closeEvent(self, event):
        fb_page = self.pages.get("facebook")
        if fb_page and hasattr(fb_page, '_batch_mgr') and fb_page._batch_mgr:
            fb_page._batch_mgr.cleanup()
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        super().closeEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY
# ─────────────────────────────────────────────────────────────────────────────
def _create_arrow_pngs():
    """Tạo file PNG mũi tên ▲▼ để dùng trong SPINBOX_STYLE (PyQt5 không hỗ trợ data URI)."""
    global SPINBOX_STYLE
    arrow_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_arrows")
    os.makedirs(arrow_dir, exist_ok=True)

    def _make_arrow(path, pointing_up, color):
        pix = QPixmap(10, 6)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        from PyQt5.QtGui import QPolygon
        from PyQt5.QtCore import QPoint
        p.setBrush(QColor(color))
        p.setPen(Qt.NoPen)
        if pointing_up:
            pts = QPolygon([QPoint(5, 0), QPoint(10, 6), QPoint(0, 6)])
        else:
            pts = QPolygon([QPoint(0, 0), QPoint(10, 0), QPoint(5, 6)])
        p.drawPolygon(pts)
        p.end()
        pix.save(path, "PNG")

    files = {
        "up_normal":   (os.path.join(arrow_dir, "up_normal.png"),   True,  "#6ba3ff"),
        "up_hover":    (os.path.join(arrow_dir, "up_hover.png"),    True,  "#ffffff"),
        "up_dim":      (os.path.join(arrow_dir, "up_dim.png"),      True,  "#2e4570"),
        "down_normal": (os.path.join(arrow_dir, "down_normal.png"), False, "#6ba3ff"),
        "down_hover":  (os.path.join(arrow_dir, "down_hover.png"),  False, "#ffffff"),
        "down_dim":    (os.path.join(arrow_dir, "down_dim.png"),    False, "#2e4570"),
    }
    for key, (path, up, clr) in files.items():
        _make_arrow(path, up, clr)

    # Thay placeholder bằng đường dẫn thật (dùng forward slash cho Qt)
    def _fwd(p): return p.replace("\\", "/")
    SPINBOX_STYLE = (
        SPINBOX_STYLE
        .replace("ARROW_UP_NORMAL",   _fwd(files["up_normal"][0]))
        .replace("ARROW_UP_HOVER",    _fwd(files["up_hover"][0]))
        .replace("ARROW_UP_DIM",      _fwd(files["up_dim"][0]))
        .replace("ARROW_DOWN_NORMAL", _fwd(files["down_normal"][0]))
        .replace("ARROW_DOWN_HOVER",  _fwd(files["down_hover"][0]))
        .replace("ARROW_DOWN_DIM",    _fwd(files["down_dim"][0]))
    )
    # Patch STYLE tổng hợp (STYLE đã nhúng SPINBOX_STYLE khi định nghĩa dưới dạng chuỗi tĩnh)
    global STYLE
    STYLE = (
        STYLE
        .replace("ARROW_UP_NORMAL",   _fwd(files["up_normal"][0]))
        .replace("ARROW_UP_HOVER",    _fwd(files["up_hover"][0]))
        .replace("ARROW_UP_DIM",      _fwd(files["up_dim"][0]))
        .replace("ARROW_DOWN_NORMAL", _fwd(files["down_normal"][0]))
        .replace("ARROW_DOWN_HOVER",  _fwd(files["down_hover"][0]))
        .replace("ARROW_DOWN_DIM",    _fwd(files["down_dim"][0]))
    )


def main():
    log_file = open("debug.log", "w", encoding='utf-8', errors='replace')
    try:
        log_file.write("Starting app\n")
        log_file.flush()
        app=QApplication(sys.argv); app.setStyle("Fusion")
        log_file.write("QApplication created\n")
        log_file.flush()
        _create_arrow_pngs()
        log_file.write("arrows created\n")
        log_file.flush()
        pal=QPalette()
        pal.setColor(QPalette.Window,          QColor("#0b0f14"))
        pal.setColor(QPalette.WindowText,      QColor("#dde4ef"))
        pal.setColor(QPalette.Base,            QColor("#111827"))
        pal.setColor(QPalette.AlternateBase,   QColor("#0f1724"))
        pal.setColor(QPalette.Text,            QColor("#c9d6ea"))
        pal.setColor(QPalette.Button,          QColor("#131d2e"))
        pal.setColor(QPalette.ButtonText,      QColor("#9aafcf"))
        pal.setColor(QPalette.Highlight,       QColor("#0d1e38"))
        pal.setColor(QPalette.HighlightedText, QColor("#6ba3ff"))
        pal.setColor(QPalette.ToolTipBase,     QColor("#111827"))
        pal.setColor(QPalette.ToolTipText,     QColor("#c9d6ea"))
        app.setPalette(pal)
        log_file.write("Palette set\n")
        log_file.flush()
        win=MainWindow()
        log_file.write("MainWindow created\n")
        log_file.flush()
        win.setGeometry(100, 100, 1400, 900)
        win.show()
        log_file.write("Window shown\n")
        log_file.flush()
        sys.exit(app.exec_())
    except BaseException as e:
        import traceback
        log_file.write(f"ERROR: {str(e)}\n")
        log_file.write(traceback.format_exc())
        log_file.flush()
        log_file.close()
        raise

if __name__ == "__main__":
    main()