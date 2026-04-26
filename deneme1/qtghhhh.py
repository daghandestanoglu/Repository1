import sys
import json
import os
from datetime import datetime, date, timedelta
from collections import defaultdict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QScrollArea,
    QDialog, QDialogButtonBox, QDateEdit, QDoubleSpinBox, QMessageBox,
    QProgressBar, QTabWidget, QSizePolicy, QSplitter, QTextEdit,
    QListWidget, QListWidgetItem, QAbstractItemView, QSlider, QCheckBox,
    QGroupBox, QFormLayout, QSpacerItem
)
from PyQt6.QtCore import (
    Qt, QDate, QTimer, QPropertyAnimation, QEasingCurve,
    QAbstractAnimation, pyqtSignal, QRect, QPoint, QSize, QThread
)
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QBrush, QPen, QLinearGradient,
    QRadialGradient, QPalette, QIcon, QPixmap, QFontMetrics,
    QCursor, QKeySequence
)
from PyQt6.QtCharts import (
    QChart, QChartView, QPieSeries, QBarSeries, QBarSet,
    QBarCategoryAxis, QValueAxis, QLineSeries, QSplineSeries,
    QAreaSeries, QScatterSeries
)
import math
import random

# ─── VERİ KATMANI ────────────────────────────────────────────────────────────

DATA_FILE = os.path.expanduser("~/.finans_takip.json")

KATEGORILER = {
    "gelir": ["Maaş", "Serbest Çalışma", "Yatırım", "Kira Geliri", "Diğer Gelir"],
    "gider": ["Kira", "Market", "Faturalar", "Ulaşım", "Sağlık", "Eğlence",
              "Giyim", "Restoran", "Eğitim", "Teknoloji", "Tatil", "Diğer"]
}

KATEGORİ_EMOJİ = {
    "Maaş": "💼", "Serbest Çalışma": "🖥️", "Yatırım": "📈", "Kira Geliri": "🏠",
    "Diğer Gelir": "💰", "Kira": "🏠", "Market": "🛒", "Faturalar": "⚡",
    "Ulaşım": "🚌", "Sağlık": "💊", "Eğlence": "🎮", "Giyim": "👕",
    "Restoran": "🍽️", "Eğitim": "📚", "Teknoloji": "💻", "Tatil": "✈️", "Diğer": "📦"
}

KATEGORİ_RENK = {
    "Maaş": "#4ade80", "Serbest Çalışma": "#34d399", "Yatırım": "#6ee7b7",
    "Kira Geliri": "#a7f3d0", "Diğer Gelir": "#d1fae5",
    "Kira": "#f87171", "Market": "#fb923c", "Faturalar": "#fbbf24",
    "Ulaşım": "#a78bfa", "Sağlık": "#f472b6", "Eğlence": "#60a5fa",
    "Giyim": "#818cf8", "Restoran": "#e879f9", "Eğitim": "#38bdf8",
    "Teknoloji": "#34d399", "Tatil": "#fcd34d", "Diğer": "#9ca3af"
}

def veri_yukle():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"islemler": [], "butceler": {}, "hedefler": []}

def veri_kaydet(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Demo veri oluştur
def demo_veri_olustur():
    islemler = []
    bugun = date.today()
    kategoriler_gelir = KATEGORILER["gelir"]
    kategoriler_gider = KATEGORILER["gider"]
    
    for ay_offset in range(6):
        gun = bugun - timedelta(days=ay_offset * 30)
        # Maaş
        islemler.append({
            "id": f"g_{ay_offset}_1",
            "tarih": (gun.replace(day=1)).isoformat(),
            "tür": "gelir",
            "kategori": "Maaş",
            "açıklama": "Aylık maaş",
            "tutar": 25000 + random.randint(-2000, 2000)
        })
        # Çeşitli giderler
        gider_data = [
            ("Kira", "Ev kirası", 8500),
            ("Market", "Haftalık alışveriş", 1200 + random.randint(-300, 300)),
            ("Faturalar", "Elektrik/Su/İnternet", 600 + random.randint(-100, 100)),
            ("Ulaşım", "Toplu taşıma kartı", 350),
            ("Restoran", "Yemek dışarıda", 800 + random.randint(-200, 200)),
            ("Eğlence", "Netflix/Spotify", 200),
            ("Sağlık", "Eczane", 150 + random.randint(-50, 100)),
            ("Teknoloji", "Online abonelikler", 300),
        ]
        for i, (kat, acik, tutar) in enumerate(gider_data):
            gun_offset = random.randint(1, 28)
            islemler.append({
                "id": f"gi_{ay_offset}_{i}",
                "tarih": (gun.replace(day=min(gun_offset, 28))).isoformat(),
                "tür": "gider",
                "kategori": kat,
                "açıklama": acik,
                "tutar": tutar
            })
    
    return islemler

# ─── STİL ────────────────────────────────────────────────────────────────────

DARK_STYLE = """
QMainWindow, QDialog {
    background-color: #0a0a0f;
    color: #e2e8f0;
}
QWidget {
    background-color: transparent;
    color: #e2e8f0;
    font-family: 'Segoe UI', Arial;
}
QLabel {
    color: #e2e8f0;
    background: transparent;
}
QPushButton {
    background-color: #1e1e2e;
    color: #e2e8f0;
    border: 1px solid #2d2d44;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #2d2d44;
    border: 1px solid #7c3aed;
}
QPushButton:pressed {
    background-color: #7c3aed;
}
QPushButton#primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #4f46e5);
    border: none;
    color: white;
    font-weight: bold;
}
QPushButton#primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6d28d9, stop:1 #4338ca);
}
QPushButton#danger {
    background-color: #7f1d1d;
    border: 1px solid #991b1b;
    color: #fca5a5;
}
QPushButton#danger:hover {
    background-color: #991b1b;
}
QPushButton#success {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #065f46, stop:1 #047857);
    border: none;
    color: #6ee7b7;
    font-weight: bold;
}
QPushButton#success:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #047857, stop:1 #059669);
}
QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox {
    background-color: #1e1e2e;
    border: 1px solid #2d2d44;
    border-radius: 8px;
    padding: 8px 12px;
    color: #e2e8f0;
    font-size: 13px;
    selection-background-color: #7c3aed;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {
    border: 1px solid #7c3aed;
    outline: none;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #1e1e2e;
    border: 1px solid #2d2d44;
    selection-background-color: #7c3aed;
    color: #e2e8f0;
    border-radius: 8px;
}
QTableWidget {
    background-color: #111118;
    alternate-background-color: #16161f;
    border: 1px solid #2d2d44;
    border-radius: 12px;
    gridline-color: #1e1e2e;
    color: #e2e8f0;
    font-size: 13px;
}
QTableWidget::item {
    padding: 8px 12px;
    border: none;
}
QTableWidget::item:selected {
    background-color: #2d1b69;
    color: white;
}
QHeaderView::section {
    background-color: #1e1e2e;
    color: #94a3b8;
    border: none;
    border-bottom: 1px solid #2d2d44;
    padding: 10px 12px;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
}
QScrollBar:vertical {
    background: #111118;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #2d2d44;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #7c3aed;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QTabWidget::pane {
    border: 1px solid #2d2d44;
    border-radius: 12px;
    background-color: #111118;
}
QTabBar::tab {
    background: #1e1e2e;
    color: #64748b;
    border: 1px solid #2d2d44;
    padding: 10px 20px;
    margin-right: 4px;
    border-radius: 8px;
    font-size: 13px;
}
QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #4f46e5);
    color: white;
    border: none;
}
QTabBar::tab:hover:!selected {
    background: #2d2d44;
    color: #e2e8f0;
}
QProgressBar {
    background-color: #1e1e2e;
    border: none;
    border-radius: 6px;
    height: 12px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #4f46e5);
    border-radius: 6px;
}
QFrame#card {
    background-color: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 16px;
}
QFrame#sidebar {
    background-color: #0d0d16;
    border-right: 1px solid #1e1e2e;
}
QGroupBox {
    color: #94a3b8;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
    border: 1px solid #2d2d44;
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: #7c3aed;
}
QSplitter::handle {
    background: #1e1e2e;
    width: 1px;
}
"""

# ─── ÖZEL WİDGET'LAR ─────────────────────────────────────────────────────────

class AnimatedCard(QFrame):
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._glow = 0
        self._anim = QPropertyAnimation(self, b"minimumHeight")
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def mousePressEvent(self, e):
        self.clicked.emit()
        super().mousePressEvent(e)
    
    def enterEvent(self, e):
        self.setStyleSheet(self.styleSheet() + "QFrame#card { border: 1px solid #7c3aed; }")
        super().enterEvent(e)
    
    def leaveEvent(self, e):
        self.setStyleSheet("")
        super().leaveEvent(e)


class StatCard(QFrame):
    def __init__(self, başlık, değer, alt_text="", renk="#7c3aed", ikon="💰", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumHeight(130)
        self._renk = renk
        self._değer = değer
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)
        
        # Üst kısım
        üst = QHBoxLayout()
        ikon_label = QLabel(ikon)
        ikon_label.setFont(QFont("Segoe UI Emoji", 22))
        ikon_label.setFixedSize(44, 44)
        ikon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ikon_label.setStyleSheet(f"""
            background: {renk}22;
            border-radius: 12px;
            color: {renk};
        """)
        
        başlık_label = QLabel(başlık)
        başlık_label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: bold; letter-spacing: 1px;")
        başlık_label.setWordWrap(True)
        
        üst_sağ = QVBoxLayout()
        üst_sağ.addStretch()
        üst_sağ.addWidget(başlık_label)
        
        üst.addWidget(ikon_label)
        üst.addSpacing(12)
        üst.addLayout(üst_sağ)
        üst.addStretch()
        
        # Değer
        self.değer_label = QLabel(değer)
        self.değer_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.değer_label.setStyleSheet(f"color: {renk};")
        
        # Alt text
        self.alt_label = QLabel(alt_text)
        self.alt_label.setStyleSheet("color: #475569; font-size: 12px;")
        
        layout.addLayout(üst)
        layout.addWidget(self.değer_label)
        layout.addWidget(self.alt_label)
    
    def güncelle(self, değer, alt_text=""):
        self.değer_label.setText(değer)
        self.alt_label.setText(alt_text)


class MiniGrafik(QWidget):
    """Küçük trend grafiği"""
    def __init__(self, veri, renk="#7c3aed", parent=None):
        super().__init__(parent)
        self.veri = veri
        self.renk = QColor(renk)
        self.setMinimumHeight(50)
        self.setMinimumWidth(120)
    
    def paintEvent(self, event):
        if not self.veri or len(self.veri) < 2:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        mn, mx = min(self.veri), max(self.veri)
        if mx == mn:
            mx = mn + 1
        
        pts = []
        for i, v in enumerate(self.veri):
            x = i * (w - 4) / (len(self.veri) - 1) + 2
            y = h - 4 - (v - mn) / (mx - mn) * (h - 8)
            pts.append(QPoint(int(x), int(y)))
        
        # Alan dolgusu
        grad = QLinearGradient(0, 0, 0, h)
        c1 = QColor(self.renk)
        c1.setAlpha(80)
        c2 = QColor(self.renk)
        c2.setAlpha(0)
        grad.setColorAt(0, c1)
        grad.setColorAt(1, c2)
        
        from PyQt6.QtGui import QPolygon
        poly_pts = [pts[0]] + pts + [QPoint(pts[-1].x(), h), QPoint(pts[0].x(), h)]
        p.fillPath(self._path_from_points(pts, h), QBrush(grad))
        
        # Çizgi
        pen = QPen(self.renk, 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        for i in range(len(pts) - 1):
            p.drawLine(pts[i], pts[i+1])
        
        # Son nokta
        p.setBrush(QBrush(self.renk))
        p.setPen(QPen(QColor("#0a0a0f"), 2))
        p.drawEllipse(pts[-1], 4, 4)
        
        p.end()
    
    def _path_from_points(self, pts, h):
        from PyQt6.QtGui import QPainterPath
        path = QPainterPath()
        path.moveTo(pts[0].x(), h)
        path.lineTo(pts[0].x(), pts[0].y())
        for i in range(1, len(pts)):
            path.lineTo(pts[i].x(), pts[i].y())
        path.lineTo(pts[-1].x(), h)
        path.closeSubpath()
        return path


class IslemEkleDialog(QDialog):
    def __init__(self, parent=None, islem=None):
        super().__init__(parent)
        self.setWindowTitle("İşlem Ekle" if not islem else "İşlem Düzenle")
        self.setModal(True)
        self.setMinimumWidth(480)
        self.setStyleSheet(DARK_STYLE + """
            QDialog { background-color: #0d0d16; border-radius: 16px; }
        """)
        
        self.islem = islem
        self._kur()
    
    def _kur(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Başlık
        başlık = QLabel("➕  Yeni İşlem" if not self.islem else "✏️  İşlem Düzenle")
        başlık.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        başlık.setStyleSheet("color: white; margin-bottom: 8px;")
        layout.addWidget(başlık)
        
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #1e1e2e;")
        layout.addWidget(sep)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        lbl_style = "color: #94a3b8; font-size: 13px; min-width: 80px;"
        
        # Tür
        self.tür_combo = QComboBox()
        self.tür_combo.addItems(["💹  Gelir", "💸  Gider"])
        self.tür_combo.currentIndexChanged.connect(self._tür_değişti)
        lbl = QLabel("Tür:"); lbl.setStyleSheet(lbl_style)
        form.addRow(lbl, self.tür_combo)
        
        # Kategori
        self.kat_combo = QComboBox()
        lbl = QLabel("Kategori:"); lbl.setStyleSheet(lbl_style)
        form.addRow(lbl, self.kat_combo)
        
        # Tutar
        self.tutar_spin = QDoubleSpinBox()
        self.tutar_spin.setRange(0.01, 9999999)
        self.tutar_spin.setDecimals(2)
        self.tutar_spin.setSuffix(" ₺")
        self.tutar_spin.setValue(1000)
        lbl = QLabel("Tutar:"); lbl.setStyleSheet(lbl_style)
        form.addRow(lbl, self.tutar_spin)
        
        # Açıklama
        self.açıklama_edit = QLineEdit()
        self.açıklama_edit.setPlaceholderText("İşlem açıklaması...")
        lbl = QLabel("Açıklama:"); lbl.setStyleSheet(lbl_style)
        form.addRow(lbl, self.açıklama_edit)
        
        # Tarih
        self.tarih_edit = QDateEdit()
        self.tarih_edit.setDate(QDate.currentDate())
        self.tarih_edit.setCalendarPopup(True)
        lbl = QLabel("Tarih:"); lbl.setStyleSheet(lbl_style)
        form.addRow(lbl, self.tarih_edit)
        
        layout.addLayout(form)
        
        # Doldur
        self._tür_değişti(0)
        if self.islem:
            self._doldur()
        
        # Butonlar
        btn_layout = QHBoxLayout()
        iptal_btn = QPushButton("İptal")
        iptal_btn.setFixedHeight(40)
        iptal_btn.clicked.connect(self.reject)
        
        kaydet_btn = QPushButton("💾  Kaydet")
        kaydet_btn.setObjectName("primary")
        kaydet_btn.setFixedHeight(40)
        kaydet_btn.clicked.connect(self._kaydet)
        
        btn_layout.addWidget(iptal_btn)
        btn_layout.addWidget(kaydet_btn)
        layout.addLayout(btn_layout)
    
    def _tür_değişti(self, idx):
        self.kat_combo.clear()
        tür = "gelir" if idx == 0 else "gider"
        for kat in KATEGORILER[tür]:
            emoji = KATEGORİ_EMOJİ.get(kat, "📦")
            self.kat_combo.addItem(f"{emoji}  {kat}", kat)
    
    def _doldur(self):
        idx = 0 if self.islem["tür"] == "gelir" else 1
        self.tür_combo.setCurrentIndex(idx)
        self._tür_değişti(idx)
        for i in range(self.kat_combo.count()):
            if self.kat_combo.itemData(i) == self.islem["kategori"]:
                self.kat_combo.setCurrentIndex(i)
                break
        self.tutar_spin.setValue(self.islem["tutar"])
        self.açıklama_edit.setText(self.islem.get("açıklama", ""))
        tarih = date.fromisoformat(self.islem["tarih"])
        self.tarih_edit.setDate(QDate(tarih.year, tarih.month, tarih.day))
    
    def _kaydet(self):
        tutar = self.tutar_spin.value()
        if tutar <= 0:
            QMessageBox.warning(self, "Hata", "Tutar 0'dan büyük olmalı!")
            return
        
        tür = "gelir" if self.tür_combo.currentIndex() == 0 else "gider"
        kat = self.kat_combo.currentData()
        açıklama = self.açıklama_edit.text().strip() or f"{kat} işlemi"
        tarih_q = self.tarih_edit.date()
        tarih = date(tarih_q.year(), tarih_q.month(), tarih_q.day())
        
        self.sonuç = {
            "id": self.islem["id"] if self.islem else f"i_{datetime.now().timestamp()}",
            "tarih": tarih.isoformat(),
            "tür": tür,
            "kategori": kat,
            "açıklama": açıklama,
            "tutar": tutar
        }
        self.accept()


class BütçeDialog(QDialog):
    def __init__(self, mevcut_bütçeler, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bütçe Hedefleri")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
        self.setStyleSheet(DARK_STYLE)
        self.bütçeler = dict(mevcut_bütçeler)
        self._kur()
    
    def _kur(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        
        başlık = QLabel("🎯  Aylık Bütçe Hedefleri")
        başlık.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(başlık)
        
        açık = QLabel("Her kategori için aylık harcama limitinizi belirleyin.")
        açık.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(açık)
        
        sep = QFrame(); sep.setFixedHeight(1)
        sep.setStyleSheet("background: #1e1e2e;")
        layout.addWidget(sep)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)
        
        self.spinler = {}
        for kat in KATEGORILER["gider"]:
            satır = QHBoxLayout()
            emoji = KATEGORİ_EMOJİ.get(kat, "📦")
            renk = KATEGORİ_RENK.get(kat, "#9ca3af")
            
            ikon = QLabel(emoji)
            ikon.setFixedSize(36, 36)
            ikon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ikon.setStyleSheet(f"background: {renk}22; border-radius: 8px;")
            
            kat_label = QLabel(kat)
            kat_label.setFixedWidth(140)
            kat_label.setStyleSheet("font-size: 13px;")
            
            spin = QDoubleSpinBox()
            spin.setRange(0, 999999)
            spin.setSuffix(" ₺")
            spin.setDecimals(0)
            spin.setValue(self.bütçeler.get(kat, 0))
            spin.setFixedWidth(140)
            spin.setSpecialValueText("Limit yok")
            
            aktif = QCheckBox()
            aktif.setChecked(kat in self.bütçeler and self.bütçeler[kat] > 0)
            aktif.toggled.connect(lambda checked, s=spin: s.setEnabled(checked))
            spin.setEnabled(aktif.isChecked())
            
            self.spinler[kat] = (spin, aktif)
            
            satır.addWidget(ikon)
            satır.addSpacing(8)
            satır.addWidget(kat_label)
            satır.addStretch()
            satır.addWidget(aktif)
            satır.addWidget(spin)
            scroll_layout.addLayout(satır)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        btn_layout = QHBoxLayout()
        iptal_btn = QPushButton("İptal")
        iptal_btn.clicked.connect(self.reject)
        
        kaydet_btn = QPushButton("💾  Kaydet")
        kaydet_btn.setObjectName("primary")
        kaydet_btn.clicked.connect(self._kaydet)
        
        btn_layout.addWidget(iptal_btn)
        btn_layout.addWidget(kaydet_btn)
        layout.addLayout(btn_layout)
    
    def _kaydet(self):
        self.bütçeler = {}
        for kat, (spin, aktif) in self.spinler.items():
            if aktif.isChecked() and spin.value() > 0:
                self.bütçeler[kat] = spin.value()
        self.accept()


# ─── ANA PENCERE ─────────────────────────────────────────────────────────────

class FinansTakip(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💎 Finans Takip Pro")
        self.setMinimumSize(1280, 800)
        self.resize(1400, 900)
        self.setStyleSheet(DARK_STYLE)
        
        # Veri
        self.veri = veri_yukle()
        if not self.veri["islemler"]:
            self.veri["islemler"] = demo_veri_olustur()
            veri_kaydet(self.veri)
        
        self.aktif_filtre_ay = None
        self._kur_ui()
        self._güncelle()
        
        # Zaman damgası timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._saat_güncelle)
        self.timer.start(1000)
        self._saat_güncelle()
    
    def _kur_ui(self):
        merkez = QWidget()
        self.setCentralWidget(merkez)
        
        ana = QHBoxLayout(merkez)
        ana.setContentsMargins(0, 0, 0, 0)
        ana.setSpacing(0)
        
        # Sidebar
        sidebar = self._sidebar_kur()
        ana.addWidget(sidebar)
        
        # Ana içerik
        self.içerik_stack = QTabWidget()
        self.içerik_stack.tabBar().setVisible(False)
        ana.addWidget(self.içerik_stack, 1)
        
        # Sayfalar
        self.içerik_stack.addTab(self._ana_sayfa_kur(), "Ana Sayfa")     # 0
        self.içerik_stack.addTab(self._islemler_kur(), "İşlemler")       # 1
        self.içerik_stack.addTab(self._grafikler_kur(), "Grafikler")     # 2
        self.içerik_stack.addTab(self._bütçe_kur(), "Bütçe")             # 3
        self.içerik_stack.addTab(self._rapor_kur(), "Rapor")             # 4
    
    def _sidebar_kur(self):
        frame = QFrame()
        frame.setObjectName("sidebar")
        frame.setFixedWidth(220)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)
        
        # Logo
        logo = QLabel("💎")
        logo.setFont(QFont("Segoe UI Emoji", 30))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        
        isim = QLabel("Finans Takip")
        isim.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        isim.setAlignment(Qt.AlignmentFlag.AlignCenter)
        isim.setStyleSheet("color: white; letter-spacing: 1px;")
        layout.addWidget(isim)
        
        self.saat_label = QLabel()
        self.saat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.saat_label.setStyleSheet("color: #475569; font-size: 11px;")
        layout.addWidget(self.saat_label)
        
        layout.addSpacing(20)
        
        sep = QFrame(); sep.setFixedHeight(1)
        sep.setStyleSheet("background: #1e1e2e;")
        layout.addWidget(sep)
        layout.addSpacing(8)
        
        # Menü butonları
        menü_items = [
            ("🏠", "Özet", 0),
            ("📋", "İşlemler", 1),
            ("📊", "Grafikler", 2),
            ("🎯", "Bütçe", 3),
            ("📑", "Rapor", 4),
        ]
        
        self.menü_butonları = []
        for emoji, isim_str, idx in menü_items:
            btn = QPushButton(f"  {emoji}  {isim_str}")
            btn.setFixedHeight(44)
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 16px;
                    border-radius: 10px;
                    border: none;
                    font-size: 14px;
                    color: #64748b;
                    background: transparent;
                }
                QPushButton:checked {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2d1b6922, stop:1 #4f46e522);
                    color: white;
                    border-left: 3px solid #7c3aed;
                }
                QPushButton:hover:!checked {
                    background: #1e1e2e;
                    color: #e2e8f0;
                }
            """)
            btn.clicked.connect(lambda checked, i=idx: self._sayfa_değiştir(i))
            layout.addWidget(btn)
            self.menü_butonları.append(btn)
        
        self.menü_butonları[0].setChecked(True)
        
        layout.addStretch()
        
        # Alt: Hızlı ekle butonu
        ekle_btn = QPushButton("  ➕  İşlem Ekle")
        ekle_btn.setFixedHeight(44)
        ekle_btn.setObjectName("primary")
        ekle_btn.clicked.connect(self._islem_ekle)
        layout.addWidget(ekle_btn)
        
        bütçe_btn = QPushButton("  ⚙️  Bütçe Ayarla")
        bütçe_btn.setFixedHeight(40)
        bütçe_btn.clicked.connect(self._bütçe_ayarla)
        layout.addWidget(bütçe_btn)
        
        return frame
    
    def _ana_sayfa_kur(self):
        sayfa = QWidget()
        sayfa.setStyleSheet("background-color: #0a0a0f;")
        layout = QVBoxLayout(sayfa)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Başlık
        üst = QHBoxLayout()
        başlık = QLabel("Finansal Özet")
        başlık.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        başlık.setStyleSheet("color: white;")
        
        self.dönem_label = QLabel()
        self.dönem_label.setStyleSheet("""
            background: #1e1e2e;
            border-radius: 8px;
            padding: 6px 14px;
            color: #94a3b8;
            font-size: 13px;
        """)
        
        üst.addWidget(başlık)
        üst.addStretch()
        üst.addWidget(self.dönem_label)
        layout.addLayout(üst)
        
        # Stat kartları
        kartlar_grid = QGridLayout()
        kartlar_grid.setSpacing(16)
        
        self.toplam_gelir_kart = StatCard("TOPLAM GELİR", "₺0", "", "#4ade80", "💹")
        self.toplam_gider_kart = StatCard("TOPLAM GİDER", "₺0", "", "#f87171", "💸")
        self.bakiye_kart = StatCard("NET BAKİYE", "₺0", "", "#60a5fa", "💎")
        self.tasarruf_kart = StatCard("TASARRUF ORANI", "%0", "", "#a78bfa", "🏦")
        
        kartlar_grid.addWidget(self.toplam_gelir_kart, 0, 0)
        kartlar_grid.addWidget(self.toplam_gider_kart, 0, 1)
        kartlar_grid.addWidget(self.bakiye_kart, 0, 2)
        kartlar_grid.addWidget(self.tasarruf_kart, 0, 3)
        layout.addLayout(kartlar_grid)
        
        # Alt kısım: grafik + hızlı liste
        alt_splitter = QSplitter(Qt.Orientation.Horizontal)
        alt_splitter.setChildrenCollapsible(False)
        
        # Pasta grafik
        grafik_frame = QFrame()
        grafik_frame.setObjectName("card")
        grafik_layout = QVBoxLayout(grafik_frame)
        grafik_layout.setContentsMargins(16, 16, 16, 16)
        
        grafik_başlık = QLabel("📊  Harcama Dağılımı")
        grafik_başlık.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        grafik_layout.addWidget(grafik_başlık)
        
        self.pie_chart = self._pie_chart_kur()
        grafik_layout.addWidget(self.pie_chart, 1)
        alt_splitter.addWidget(grafik_frame)
        
        # Son işlemler
        son_frame = QFrame()
        son_frame.setObjectName("card")
        son_layout = QVBoxLayout(son_frame)
        son_layout.setContentsMargins(16, 16, 16, 16)
        
        son_üst = QHBoxLayout()
        son_başlık = QLabel("🕐  Son İşlemler")
        son_başlık.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        tümü_btn = QPushButton("Tümü →")
        tümü_btn.setFixedHeight(28)
        tümü_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #7c3aed; border: none; font-size: 13px; }
            QPushButton:hover { color: #a855f7; }
        """)
        tümü_btn.clicked.connect(lambda: self._sayfa_değiştir(1))
        son_üst.addWidget(son_başlık)
        son_üst.addStretch()
        son_üst.addWidget(tümü_btn)
        son_layout.addLayout(son_üst)
        
        self.son_islemler_liste = QWidget()
        self.son_liste_layout = QVBoxLayout(self.son_islemler_liste)
        self.son_liste_layout.setSpacing(4)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setWidget(self.son_islemler_liste)
        son_layout.addWidget(scroll)
        alt_splitter.addWidget(son_frame)
        
        alt_splitter.setSizes([500, 350])
        layout.addWidget(alt_splitter, 1)
        
        return sayfa
    
    def _pie_chart_kur(self):
        seri = QPieSeries()
        chart = QChart()
        chart.addSeries(seri)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setBackgroundBrush(QBrush(QColor("#111118")))
        chart.setTitle("")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 10))
        chart.legend().setColor(QColor("#94a3b8"))
        chart.legend().setMarkerShape(QLegend_MarkerShape_FromSeries())
        chart.setMargins(QRect(0, 0, 0, 0).marginsAdded(QRect()))
        
        view = QChartView(chart)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setStyleSheet("background: transparent; border: none;")
        view.setMinimumHeight(280)
        
        self._pie_seri = seri
        self._pie_chart_obj = chart
        return view
    
    def _islemler_kur(self):
        sayfa = QWidget()
        sayfa.setStyleSheet("background-color: #0a0a0f;")
        layout = QVBoxLayout(sayfa)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Başlık + araçlar
        üst = QHBoxLayout()
        başlık = QLabel("İşlem Geçmişi")
        başlık.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        başlık.setStyleSheet("color: white;")
        
        # Filtre
        self.arama = QLineEdit()
        self.arama.setPlaceholderText("🔍  Ara...")
        self.arama.setFixedHeight(36)
        self.arama.setFixedWidth(200)
        self.arama.textChanged.connect(self._filtrele)
        
        self.tür_filtre = QComboBox()
        self.tür_filtre.addItems(["Tümü", "💹 Gelir", "💸 Gider"])
        self.tür_filtre.setFixedHeight(36)
        self.tür_filtre.currentIndexChanged.connect(self._filtrele)
        
        self.kat_filtre = QComboBox()
        self.kat_filtre.addItem("Tüm Kategoriler", None)
        for kat in KATEGORILER["gelir"] + KATEGORILER["gider"]:
            self.kat_filtre.addItem(f"{KATEGORİ_EMOJİ.get(kat,'📦')} {kat}", kat)
        self.kat_filtre.setFixedHeight(36)
        self.kat_filtre.currentIndexChanged.connect(self._filtrele)
        
        ekle_btn = QPushButton("  ➕  Ekle")
        ekle_btn.setObjectName("primary")
        ekle_btn.setFixedHeight(36)
        ekle_btn.clicked.connect(self._islem_ekle)
        
        üst.addWidget(başlık)
        üst.addStretch()
        üst.addWidget(self.arama)
        üst.addWidget(self.tür_filtre)
        üst.addWidget(self.kat_filtre)
        üst.addWidget(ekle_btn)
        layout.addLayout(üst)
        
        # Tablo
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(6)
        self.tablo.setHorizontalHeaderLabels(["Tarih", "Tür", "Kategori", "Açıklama", "Tutar", "İşlemler"])
        self.tablo.horizontalHeader().setStretchLastSection(False)
        self.tablo.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tablo.setColumnWidth(0, 100)
        self.tablo.setColumnWidth(1, 80)
        self.tablo.setColumnWidth(2, 130)
        self.tablo.setColumnWidth(4, 120)
        self.tablo.setColumnWidth(5, 120)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tablo.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setShowGrid(False)
        self.tablo.setRowHeight(0, 52)
        layout.addWidget(self.tablo)
        
        # Özet bar
        özet_frame = QFrame()
        özet_frame.setObjectName("card")
        özet_frame.setFixedHeight(56)
        özet_layout = QHBoxLayout(özet_frame)
        özet_layout.setContentsMargins(16, 8, 16, 8)
        
        self.tablo_özet = QLabel()
        self.tablo_özet.setStyleSheet("color: #64748b; font-size: 13px;")
        özet_layout.addWidget(self.tablo_özet)
        özet_layout.addStretch()
        
        layout.addWidget(özet_frame)
        
        return sayfa
    
    def _grafikler_kur(self):
        sayfa = QWidget()
        sayfa.setStyleSheet("background-color: #0a0a0f;")
        layout = QVBoxLayout(sayfa)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        başlık = QLabel("Grafikler & Analiz")
        başlık.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        başlık.setStyleSheet("color: white;")
        layout.addWidget(başlık)
        
        tab = QTabWidget()
        tab.setStyleSheet(DARK_STYLE)
        
        # Aylık trend
        self.trend_view = self._trend_grafik_kur()
        tab.addTab(self.trend_view, "📈  Aylık Trend")
        
        # Kategori bar
        self.bar_view = self._bar_grafik_kur()
        tab.addTab(self.bar_view, "📊  Kategori Analizi")
        
        layout.addWidget(tab)
        
        return sayfa
    
    def _trend_grafik_kur(self):
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setBackgroundBrush(QBrush(QColor("#111118")))
        chart.setTitle("Son 6 Ay Gelir / Gider Trendi")
        chart.setTitleFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        chart.setTitleBrush(QBrush(QColor("#e2e8f0")))
        
        self._trend_chart = chart
        
        view = QChartView(chart)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setStyleSheet("background: transparent; border: none;")
        
        return view
    
    def _bar_grafik_kur(self):
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setBackgroundBrush(QBrush(QColor("#111118")))
        chart.setTitle("Kategori Bazlı Harcama")
        chart.setTitleFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        chart.setTitleBrush(QBrush(QColor("#e2e8f0")))
        
        self._bar_chart = chart
        
        view = QChartView(chart)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setStyleSheet("background: transparent; border: none;")
        
        return view
    
    def _bütçe_kur(self):
        sayfa = QWidget()
        sayfa.setStyleSheet("background-color: #0a0a0f;")
        layout = QVBoxLayout(sayfa)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        üst = QHBoxLayout()
        başlık = QLabel("Bütçe Takibi")
        başlık.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        başlık.setStyleSheet("color: white;")
        
        ayarla_btn = QPushButton("⚙️  Bütçe Ayarla")
        ayarla_btn.setObjectName("primary")
        ayarla_btn.clicked.connect(self._bütçe_ayarla)
        
        üst.addWidget(başlık)
        üst.addStretch()
        üst.addWidget(ayarla_btn)
        layout.addLayout(üst)
        
        # Bütçe kartları
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.bütçe_widget = QWidget()
        self.bütçe_grid = QGridLayout(self.bütçe_widget)
        self.bütçe_grid.setSpacing(16)
        
        scroll.setWidget(self.bütçe_widget)
        layout.addWidget(scroll)
        
        return sayfa
    
    def _rapor_kur(self):
        sayfa = QWidget()
        sayfa.setStyleSheet("background-color: #0a0a0f;")
        layout = QVBoxLayout(sayfa)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        başlık = QLabel("Finansal Rapor")
        başlık.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        başlık.setStyleSheet("color: white;")
        layout.addWidget(başlık)
        
        self.rapor_text = QTextEdit()
        self.rapor_text.setReadOnly(True)
        self.rapor_text.setStyleSheet("""
            QTextEdit {
                background: #111118;
                border: 1px solid #1e1e2e;
                border-radius: 12px;
                padding: 16px;
                color: #e2e8f0;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(self.rapor_text)
        
        return sayfa
    
    # ─── VERİ GÜNCELLEME ─────────────────────────────────────────────────────
    
    def _güncelle(self):
        islemler = self.veri["islemler"]
        bugun = date.today()
        
        # Bu ay filtrele
        bu_ay = [i for i in islemler
                 if date.fromisoformat(i["tarih"]).year == bugun.year
                 and date.fromisoformat(i["tarih"]).month == bugun.month]
        
        toplam_gelir = sum(i["tutar"] for i in bu_ay if i["tür"] == "gelir")
        toplam_gider = sum(i["tutar"] for i in bu_ay if i["tür"] == "gider")
        bakiye = toplam_gelir - toplam_gider
        tasarruf = (bakiye / toplam_gelir * 100) if toplam_gelir > 0 else 0
        
        # Dönem etiketi
        ay_adları = ["Oca", "Şub", "Mar", "Nis", "May", "Haz",
                     "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
        self.dönem_label.setText(f"📅  {ay_adları[bugun.month-1]} {bugun.year}")
        
        # Kartlar
        self.toplam_gelir_kart.güncelle(
            f"₺{toplam_gelir:,.0f}",
            f"{len([i for i in bu_ay if i['tür']=='gelir'])} işlem"
        )
        self.toplam_gider_kart.güncelle(
            f"₺{toplam_gider:,.0f}",
            f"{len([i for i in bu_ay if i['tür']=='gider'])} işlem"
        )
        bakiye_renk = "#4ade80" if bakiye >= 0 else "#f87171"
        self.bakiye_kart.değer_label.setStyleSheet(f"color: {bakiye_renk};")
        self.bakiye_kart.güncelle(
            f"{'+'if bakiye>=0 else ''}₺{bakiye:,.0f}",
            "Bu ay net"
        )
        self.tasarruf_kart.güncelle(
            f"%{tasarruf:.1f}",
            "Gelirinizin tasarrufu"
        )
        
        # Pasta grafik
        self._pie_güncelle(bu_ay)
        
        # Son işlemler
        self._son_islemler_güncelle(islemler)
        
        # İşlemler tablosu
        self._tablo_güncelle(islemler)
        
        # Grafikler
        self._trend_güncelle(islemler)
        self._bar_güncelle(islemler)
        
        # Bütçe
        self._bütçe_güncelle(bu_ay)
        
        # Rapor
        self._rapor_güncelle(islemler, bu_ay, toplam_gelir, toplam_gider, bakiye)
    
    def _pie_güncelle(self, islemler):
        self._pie_seri.clear()
        
        gider_katlar = defaultdict(float)
        for i in islemler:
            if i["tür"] == "gider":
                gider_katlar[i["kategori"]] += i["tutar"]
        
        if not gider_katlar:
            return
        
        for kat, tutar in sorted(gider_katlar.items(), key=lambda x: -x[1]):
            dilim = self._pie_seri.append(
                f"{KATEGORİ_EMOJİ.get(kat,'')} {kat}\n₺{tutar:,.0f}",
                tutar
            )
            renk = QColor(KATEGORİ_RENK.get(kat, "#9ca3af"))
            dilim.setBrush(QBrush(renk))
            dilim.setLabelVisible(False)
            dilim.setPen(QPen(QColor("#0a0a0f"), 2))
        
        # En büyüğü vurgula
        if self._pie_seri.slices():
            en_büyük = max(self._pie_seri.slices(), key=lambda s: s.value())
            en_büyük.setExploded(True)
            en_büyük.setExplodeDistanceFactor(0.1)
        
        self._pie_chart_obj.legend().setFont(QFont("Segoe UI", 9))
        self._pie_chart_obj.legend().setColor(QColor("#94a3b8"))
    
    def _son_islemler_güncelle(self, islemler):
        # Eski öğeleri temizle
        while self.son_liste_layout.count():
            item = self.son_liste_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        son_10 = sorted(islemler, key=lambda x: x["tarih"], reverse=True)[:10]
        
        for i in son_10:
            satır = QFrame()
            satır.setStyleSheet("""
                QFrame {
                    background: #16161f;
                    border-radius: 10px;
                    border: 1px solid #1e1e2e;
                }
                QFrame:hover {
                    border: 1px solid #2d2d44;
                    background: #1e1e2e;
                }
            """)
            satır.setFixedHeight(52)
            
            sl = QHBoxLayout(satır)
            sl.setContentsMargins(12, 8, 12, 8)
            
            emoji = KATEGORİ_EMOJİ.get(i["kategori"], "📦")
            renk = KATEGORİ_RENK.get(i["kategori"], "#9ca3af")
            
            ikon = QLabel(emoji)
            ikon.setFixedSize(32, 32)
            ikon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ikon.setStyleSheet(f"background: {renk}22; border-radius: 8px; font-size: 16px;")
            
            metin_layout = QVBoxLayout()
            metin_layout.setSpacing(0)
            
            açıklama = QLabel(i.get("açıklama", i["kategori"]))
            açıklama.setStyleSheet("font-size: 13px; color: #e2e8f0;")
            
            tarih_kat = QLabel(f"{i['tarih']}  ·  {i['kategori']}")
            tarih_kat.setStyleSheet("font-size: 11px; color: #475569;")
            
            metin_layout.addWidget(açıklama)
            metin_layout.addWidget(tarih_kat)
            
            tutar_renk = "#4ade80" if i["tür"] == "gelir" else "#f87171"
            işaret = "+" if i["tür"] == "gelir" else "-"
            tutar_label = QLabel(f"{işaret}₺{i['tutar']:,.0f}")
            tutar_label.setStyleSheet(f"color: {tutar_renk}; font-size: 14px; font-weight: bold;")
            tutar_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            sl.addWidget(ikon)
            sl.addSpacing(8)
            sl.addLayout(metin_layout)
            sl.addStretch()
            sl.addWidget(tutar_label)
            
            self.son_liste_layout.addWidget(satır)
        
        self.son_liste_layout.addStretch()
    
    def _tablo_güncelle(self, islemler=None):
        if islemler is None:
            islemler = self.veri["islemler"]
        
        # Filtreleri uygula
        arama = self.arama.text().lower()
        tür_idx = self.tür_filtre.currentIndex()
        kat_filtre = self.kat_filtre.currentData()
        
        filtrelendi = []
        for i in islemler:
            if arama and arama not in i.get("açıklama", "").lower() and arama not in i["kategori"].lower():
                continue
            if tür_idx == 1 and i["tür"] != "gelir":
                continue
            if tür_idx == 2 and i["tür"] != "gider":
                continue
            if kat_filtre and i["kategori"] != kat_filtre:
                continue
            filtrelendi.append(i)
        
        filtrelendi.sort(key=lambda x: x["tarih"], reverse=True)
        
        self.tablo.setRowCount(len(filtrelendi))
        
        for row, i in enumerate(filtrelendi):
            self.tablo.setRowHeight(row, 48)
            
            # Tarih
            t = QTableWidgetItem(i["tarih"])
            t.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tablo.setItem(row, 0, t)
            
            # Tür
            tür_item = QTableWidgetItem("💹 Gelir" if i["tür"]=="gelir" else "💸 Gider")
            tür_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            renk = QColor("#4ade80") if i["tür"]=="gelir" else QColor("#f87171")
            tür_item.setForeground(QBrush(renk))
            self.tablo.setItem(row, 1, tür_item)
            
            # Kategori
            emoji = KATEGORİ_EMOJİ.get(i["kategori"], "📦")
            kat_item = QTableWidgetItem(f"{emoji} {i['kategori']}")
            kat_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tablo.setItem(row, 2, kat_item)
            
            # Açıklama
            ac_item = QTableWidgetItem(i.get("açıklama", ""))
            self.tablo.setItem(row, 3, ac_item)
            
            # Tutar
            işaret = "+" if i["tür"]=="gelir" else "-"
            tutar_item = QTableWidgetItem(f"{işaret}₺{i['tutar']:,.2f}")
            tutar_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tutar_item.setForeground(QBrush(renk))
            tutar_item.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            self.tablo.setItem(row, 4, tutar_item)
            
            # İşlemler butonları
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            btn_layout.setSpacing(4)
            
            düzenle_btn = QPushButton("✏️")
            düzenle_btn.setFixedSize(32, 32)
            düzenle_btn.setStyleSheet("""
                QPushButton { background: #1e3a5f; border: none; border-radius: 6px; font-size: 14px; }
                QPushButton:hover { background: #1e40af; }
            """)
            düzenle_btn.clicked.connect(lambda checked, islem=i: self._islem_düzenle(islem))
            
            sil_btn = QPushButton("🗑️")
            sil_btn.setFixedSize(32, 32)
            sil_btn.setStyleSheet("""
                QPushButton { background: #3f1212; border: none; border-radius: 6px; font-size: 14px; }
                QPushButton:hover { background: #7f1d1d; }
            """)
            sil_btn.clicked.connect(lambda checked, id=i["id"]: self._islem_sil(id))
            
            btn_layout.addWidget(düzenle_btn)
            btn_layout.addWidget(sil_btn)
            self.tablo.setCellWidget(row, 5, btn_widget)
        
        # Özet
        toplam_g = sum(i["tutar"] for i in filtrelendi if i["tür"]=="gelir")
        toplam_gi = sum(i["tutar"] for i in filtrelendi if i["tür"]=="gider")
        self.tablo_özet.setText(
            f"{len(filtrelendi)} işlem  ·  "
            f"Gelir: ₺{toplam_g:,.0f}  ·  "
            f"Gider: ₺{toplam_gi:,.0f}  ·  "
            f"Net: {'+'if toplam_g>=toplam_gi else ''}₺{toplam_g-toplam_gi:,.0f}"
        )
    
    def _trend_güncelle(self, islemler):
        self._trend_chart.removeAllSeries()
        for ax in self._trend_chart.axes():
            self._trend_chart.removeAxis(ax)
        
        bugun = date.today()
        aylar = []
        for offset in range(5, -1, -1):
            ay = bugun.month - offset
            yıl = bugun.year
            while ay <= 0:
                ay += 12
                yıl -= 1
            aylar.append((yıl, ay))
        
        ay_adları = ["Oca", "Şub", "Mar", "Nis", "May", "Haz",
                     "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
        
        gelir_seri = QLineSeries()
        gelir_seri.setName("Gelir")
        
        gider_seri = QLineSeries()
        gider_seri.setName("Gider")
        
        kat_eksen = QBarCategoryAxis()
        kat_eksen.setLabelsColor(QColor("#94a3b8"))
        kat_eksen.setGridLineColor(QColor("#1e1e2e"))
        
        etiketler = []
        for idx, (yıl, ay) in enumerate(aylar):
            ay_islemleri = [i for i in islemler
                           if date.fromisoformat(i["tarih"]).year == yıl
                           and date.fromisoformat(i["tarih"]).month == ay]
            
            gelir = sum(i["tutar"] for i in ay_islemleri if i["tür"]=="gelir")
            gider = sum(i["tutar"] for i in ay_islemleri if i["tür"]=="gider")
            
            gelir_seri.append(idx, gelir)
            gider_seri.append(idx, gider)
            etiketler.append(f"{ay_adları[ay-1]}\n{yıl}")
        
        pen_gelir = QPen(QColor("#4ade80"), 3)
        pen_gelir.setCapStyle(Qt.PenCapStyle.RoundCap)
        gelir_seri.setPen(pen_gelir)
        
        pen_gider = QPen(QColor("#f87171"), 3)
        pen_gider.setCapStyle(Qt.PenCapStyle.RoundCap)
        gider_seri.setPen(pen_gider)
        
        gelir_alan = QAreaSeries(gelir_seri)
        gelir_alan.setName("Gelir")
        grad1 = QLinearGradient(0, 0, 0, 1)
        grad1.setCoordinateMode(QLinearGradient.CoordinateMode.ObjectBoundingMode)
        grad1.setColorAt(0, QColor("#4ade8055"))
        grad1.setColorAt(1, QColor("#4ade8000"))
        gelir_alan.setBrush(QBrush(grad1))
        gelir_alan.setPen(QPen(QColor("#4ade80"), 2))
        
        gider_alan = QAreaSeries(gider_seri)
        gider_alan.setName("Gider")
        grad2 = QLinearGradient(0, 0, 0, 1)
        grad2.setCoordinateMode(QLinearGradient.CoordinateMode.ObjectBoundingMode)
        grad2.setColorAt(0, QColor("#f8717155"))
        grad2.setColorAt(1, QColor("#f8717100"))
        gider_alan.setBrush(QBrush(grad2))
        gider_alan.setPen(QPen(QColor("#f87171"), 2))
        
        self._trend_chart.addSeries(gelir_alan)
        self._trend_chart.addSeries(gider_alan)
        
        x_eksen = QValueAxis()
        x_eksen.setRange(0, 5)
        x_eksen.setLabelsColor(QColor("#94a3b8"))
        x_eksen.setGridLineColor(QColor("#1e1e2e"))
        x_eksen.setLabelsVisible(False)
        x_eksen.setTickCount(6)
        
        y_eksen = QValueAxis()
        y_eksen.setLabelsColor(QColor("#94a3b8"))
        y_eksen.setGridLineColor(QColor("#1e1e2e"))
        y_eksen.setLabelFormat("₺%'.0f")
        
        self._trend_chart.addAxis(x_eksen, Qt.AlignmentFlag.AlignBottom)
        self._trend_chart.addAxis(y_eksen, Qt.AlignmentFlag.AlignLeft)
        
        gelir_alan.attachAxis(x_eksen)
        gelir_alan.attachAxis(y_eksen)
        gider_alan.attachAxis(x_eksen)
        gider_alan.attachAxis(y_eksen)
        
        self._trend_chart.legend().setColor(QColor("#94a3b8"))
        self._trend_chart.legend().setFont(QFont("Segoe UI", 10))
    
    def _bar_güncelle(self, islemler):
        self._bar_chart.removeAllSeries()
        for ax in self._bar_chart.axes():
            self._bar_chart.removeAxis(ax)
        
        bugun = date.today()
        bu_ay = [i for i in islemler
                 if date.fromisoformat(i["tarih"]).year == bugun.year
                 and date.fromisoformat(i["tarih"]).month == bugun.month
                 and i["tür"] == "gider"]
        
        kat_tutarlar = defaultdict(float)
        for i in bu_ay:
            kat_tutarlar[i["kategori"]] += i["tutar"]
        
        if not kat_tutarlar:
            return
        
        sirali = sorted(kat_tutarlar.items(), key=lambda x: -x[1])[:8]
        
        bar_set = QBarSet("Harcama")
        bar_set.setColor(QColor("#7c3aed"))
        
        kategoriler = []
        for kat, tutar in sirali:
            bar_set.append(tutar)
            kategoriler.append(f"{KATEGORİ_EMOJİ.get(kat,'')} {kat}")
        
        seri = QBarSeries()
        seri.append(bar_set)
        
        self._bar_chart.addSeries(seri)
        
        x_eksen = QBarCategoryAxis()
        x_eksen.append(kategoriler)
        x_eksen.setLabelsColor(QColor("#94a3b8"))
        x_eksen.setGridLineColor(QColor("#1e1e2e"))
        
        y_eksen = QValueAxis()
        y_eksen.setLabelsColor(QColor("#94a3b8"))
        y_eksen.setGridLineColor(QColor("#1e1e2e"))
        y_eksen.setLabelFormat("₺%.0f")
        
        self._bar_chart.addAxis(x_eksen, Qt.AlignmentFlag.AlignBottom)
        self._bar_chart.addAxis(y_eksen, Qt.AlignmentFlag.AlignLeft)
        seri.attachAxis(x_eksen)
        seri.attachAxis(y_eksen)
    
    def _bütçe_güncelle(self, bu_ay_islemler):
        # Layoutu temizle
        while self.bütçe_grid.count():
            item = self.bütçe_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        bütçeler = self.veri.get("butceler", {})
        if not bütçeler:
            boş = QLabel("Henüz bütçe hedefi yok.\n'Bütçe Ayarla' butonuna tıklayarak başlayın.")
            boş.setAlignment(Qt.AlignmentFlag.AlignCenter)
            boş.setStyleSheet("color: #475569; font-size: 16px;")
            self.bütçe_grid.addWidget(boş, 0, 0)
            return
        
        gider_katlar = defaultdict(float)
        for i in bu_ay_islemler:
            if i["tür"] == "gider":
                gider_katlar[i["kategori"]] += i["tutar"]
        
        sütunlar = 3
        for idx, (kat, limit) in enumerate(bütçeler.items()):
            harcama = gider_katlar.get(kat, 0)
            yüzde = min(harcama / limit * 100, 100) if limit > 0 else 0
            
            kart = QFrame()
            kart.setObjectName("card")
            kart_layout = QVBoxLayout(kart)
            kart_layout.setContentsMargins(16, 16, 16, 16)
            kart_layout.setSpacing(8)
            
            emoji = KATEGORİ_EMOJİ.get(kat, "📦")
            renk = KATEGORİ_RENK.get(kat, "#9ca3af")
            
            # Başlık
            üst = QHBoxLayout()
            ikon = QLabel(emoji)
            ikon.setFixedSize(36, 36)
            ikon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ikon.setStyleSheet(f"background: {renk}22; border-radius: 8px; font-size: 18px;")
            
            kat_label = QLabel(kat)
            kat_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            
            üst.addWidget(ikon)
            üst.addSpacing(8)
            üst.addWidget(kat_label)
            üst.addStretch()
            
            # Durum rozeti
            if yüzde >= 90:
                durum = "⚠️ Limit Doldu"
                durum_renk = "#fbbf24"
            elif yüzde >= 75:
                durum = "🔶 Dikkat"
                durum_renk = "#f97316"
            else:
                durum = "✅ İyi"
                durum_renk = "#4ade80"
            
            durum_label = QLabel(durum)
            durum_label.setStyleSheet(f"color: {durum_renk}; font-size: 11px; font-weight: bold;")
            üst.addWidget(durum_label)
            
            kart_layout.addLayout(üst)
            
            # Rakamlar
            rakam_layout = QHBoxLayout()
            harcama_label = QLabel(f"₺{harcama:,.0f}")
            harcama_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            harcama_label.setStyleSheet(f"color: {renk};")
            
            limit_label = QLabel(f"/ ₺{limit:,.0f}")
            limit_label.setStyleSheet("color: #475569; font-size: 13px;")
            
            kalan_label = QLabel(f"Kalan: ₺{max(0, limit-harcama):,.0f}")
            kalan_label.setStyleSheet("color: #64748b; font-size: 11px;")
            
            rakam_layout.addWidget(harcama_label)
            rakam_layout.addWidget(limit_label)
            rakam_layout.addStretch()
            rakam_layout.addWidget(kalan_label)
            kart_layout.addLayout(rakam_layout)
            
            # Progress bar
            pb = QProgressBar()
            pb.setValue(int(yüzde))
            pb.setFixedHeight(8)
            pb.setTextVisible(False)
            
            if yüzde >= 90:
                pb.setStyleSheet("""
                    QProgressBar { background: #1e1e2e; border-radius: 4px; }
                    QProgressBar::chunk { background: #f97316; border-radius: 4px; }
                """)
            elif yüzde >= 75:
                pb.setStyleSheet("""
                    QProgressBar { background: #1e1e2e; border-radius: 4px; }
                    QProgressBar::chunk { background: #fbbf24; border-radius: 4px; }
                """)
            else:
                pb.setStyleSheet(f"""
                    QProgressBar {{ background: #1e1e2e; border-radius: 4px; }}
                    QProgressBar::chunk {{ background: {renk}; border-radius: 4px; }}
                """)
            
            kart_layout.addWidget(pb)
            
            yüzde_label = QLabel(f"%{yüzde:.0f} kullanıldı")
            yüzde_label.setStyleSheet("color: #475569; font-size: 11px;")
            kart_layout.addWidget(yüzde_label)
            
            satır = idx // sütunlar
            sütun = idx % sütunlar
            self.bütçe_grid.addWidget(kart, satır, sütun)
    
    def _rapor_güncelle(self, tüm_islemler, bu_ay, gelir, gider, bakiye):
        bugun = date.today()
        ay_adları = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                     "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        
        # Kategori dağılımı
        kat_tutarlar = defaultdict(float)
        for i in bu_ay:
            if i["tür"] == "gider":
                kat_tutarlar[i["kategori"]] += i["tutar"]
        
        en_fazla = sorted(kat_tutarlar.items(), key=lambda x: -x[1])
        
        rapor = f"""
══════════════════════════════════════════════════════
   💎 FİNANSAL RAPOR — {ay_adları[bugun.month-1].upper()} {bugun.year}
══════════════════════════════════════════════════════

📊 GENEL ÖZET
─────────────────────────────────────────────────────
  Toplam Gelir:     ₺{gelir:>12,.2f}
  Toplam Gider:     ₺{gider:>12,.2f}
  Net Bakiye:       ₺{bakiye:>12,.2f}  {'▲ Pozitif' if bakiye >= 0 else '▼ Negatif'}
  Tasarruf Oranı:    %{(bakiye/gelir*100 if gelir>0 else 0):>11.1f}

📈 GELİR DAĞILIMI
─────────────────────────────────────────────────────"""
        
        gelir_katlar = defaultdict(float)
        for i in bu_ay:
            if i["tür"] == "gelir":
                gelir_katlar[i["kategori"]] += i["tutar"]
        
        for kat, tutar in sorted(gelir_katlar.items(), key=lambda x: -x[1]):
            yüzde = tutar / gelir * 100 if gelir > 0 else 0
            bar = "█" * int(yüzde / 5) + "░" * (20 - int(yüzde / 5))
            rapor += f"\n  {KATEGORİ_EMOJİ.get(kat, '📦')} {kat:<20} {bar} %{yüzde:.1f}  ₺{tutar:,.0f}"
        
        rapor += f"""

💸 GİDER DAĞILIMI
─────────────────────────────────────────────────────"""
        
        for kat, tutar in en_fazla[:8]:
            yüzde = tutar / gider * 100 if gider > 0 else 0
            bar = "█" * int(yüzde / 5) + "░" * (20 - int(yüzde / 5))
            rapor += f"\n  {KATEGORİ_EMOJİ.get(kat, '📦')} {kat:<20} {bar} %{yüzde:.1f}  ₺{tutar:,.0f}"
        
        # Bütçe analizi
        bütçeler = self.veri.get("butceler", {})
        if bütçeler:
            rapor += f"""

🎯 BÜTÇE ANALİZİ
─────────────────────────────────────────────────────"""
            for kat, limit in bütçeler.items():
                harcama = kat_tutarlar.get(kat, 0)
                yüzde = harcama / limit * 100 if limit > 0 else 0
                durum = "⚠️ AŞILDI" if yüzde > 100 else ("🔶 DİKKAT" if yüzde > 75 else "✅ İYİ")
                rapor += f"\n  {kat:<22} ₺{harcama:>8,.0f} / ₺{limit:>8,.0f}  {durum}"
        
        rapor += f"""

📅 TÜM ZAMANLAR ÖZETİ
─────────────────────────────────────────────────────
  Toplam İşlem:     {len(tüm_islemler):>5} adet
  Tüm Gelirler:    ₺{sum(i['tutar'] for i in tüm_islemler if i['tür']=='gelir'):>12,.2f}
  Tüm Giderler:    ₺{sum(i['tutar'] for i in tüm_islemler if i['tür']=='gider'):>12,.2f}

══════════════════════════════════════════════════════
   Rapor tarihi: {bugun.strftime('%d.%m.%Y %H:%M')}
══════════════════════════════════════════════════════
"""
        self.rapor_text.setPlainText(rapor)
    
    # ─── EYLEMLER ────────────────────────────────────────────────────────────
    
    def _sayfa_değiştir(self, idx):
        for i, btn in enumerate(self.menü_butonları):
            btn.setChecked(i == idx)
        self.içerik_stack.setCurrentIndex(idx)
    
    def _islem_ekle(self):
        dialog = IslemEkleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.veri["islemler"].append(dialog.sonuç)
            veri_kaydet(self.veri)
            self._güncelle()
    
    def _islem_düzenle(self, islem):
        dialog = IslemEkleDialog(self, islem)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            for i, item in enumerate(self.veri["islemler"]):
                if item["id"] == islem["id"]:
                    self.veri["islemler"][i] = dialog.sonuç
                    break
            veri_kaydet(self.veri)
            self._güncelle()
    
    def _islem_sil(self, id_):
        cevap = QMessageBox.question(
            self, "Sil", "Bu işlemi silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if cevap == QMessageBox.StandardButton.Yes:
            self.veri["islemler"] = [i for i in self.veri["islemler"] if i["id"] != id_]
            veri_kaydet(self.veri)
            self._güncelle()
    
    def _bütçe_ayarla(self):
        dialog = BütçeDialog(self.veri.get("butceler", {}), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.veri["butceler"] = dialog.bütçeler
            veri_kaydet(self.veri)
            self._güncelle()
    
    def _filtrele(self):
        self._tablo_güncelle()
    
    def _saat_güncelle(self):
        şimdi = datetime.now()
        self.saat_label.setText(şimdi.strftime("%d.%m.%Y  %H:%M:%S"))


def QLegend_MarkerShape_FromSeries():
    return QLegend_MarkerShape_FromSeries


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Finans Takip Pro")
    
    # Genel font
    font = QFont("Segoe UI", 12)
    app.setFont(font)
    
    pencere = FinansTakip()
    pencere.show()
    
    sys.exit(app.exec())