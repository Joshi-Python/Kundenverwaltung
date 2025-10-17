import sys, os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QListWidget,
    QLabel,
    QMessageBox,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QIcon

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "kundenverwaltung.jpg")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kundenverwaltung")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setMinimumSize(860, 560)

        # ===== Datenmodell =====
        self.kunden = []  # Originalnamen
        self.kunden_keys = set()  # normalisierte Schlüssel (für Dublettenprüfung)

        # ===== Inneres Layout (kommt in die Card) =====
        inner = QVBoxLayout()
        inner.setContentsMargins(20, 20, 20, 20)
        inner.setSpacing(12)

        # Eingabezeile + Buttons
        row = QHBoxLayout()
        row.setSpacing(10)
        self.eingabe_name = QLineEdit()
        self.eingabe_name.setPlaceholderText("Name eingeben …")
        self.add_btn = QPushButton("Kunden anlegen")
        self.del_btn = QPushButton("Kunden löschen")

        # IDs für gezieltes Styling (WICHTIG vor setStyleSheet)
        self.add_btn.setObjectName("add_btn")
        self.del_btn.setObjectName("del_btn")

        row.addWidget(self.eingabe_name, 1)
        row.addWidget(self.add_btn)
        row.addWidget(self.del_btn)
        inner.addLayout(row)

        # Liste + Info
        self.liste = QListWidget()
        inner.addWidget(self.liste)

        self.info = QLabel("")  # optionales Statuslabel
        inner.addWidget(self.info)

        # ===== Outer Layout + Card-Wrapper =====
        container = QWidget()
        outer = QVBoxLayout(container)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(0)

        card = QWidget()
        card.setObjectName("card")
        card.setLayout(inner)
        outer.addWidget(card)

        # Weicher Schatten unter der Card
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(0, 0, 0, 60))
        card.setGraphicsEffect(shadow)

        self.setCentralWidget(container)

        # ===== Verhalten =====
        self.add_btn.clicked.connect(self._add_customer)
        self.del_btn.clicked.connect(self._delete_selected)

        # Delete-Button nur aktiv, wenn Auswahl vorhanden
        self.del_btn.setEnabled(False)
        self.liste.itemSelectionChanged.connect(self._enable_delete)

        # ===== Stylesheet (Gradient + Card + Button-Farben) =====
        self.setStyleSheet("""
        /* Hintergrund: sanfter Verlauf */
        QMainWindow, QWidget#qt_scrollarea_viewport {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #f5f7fa,
                stop:1 #cfe9ff
            );
            color: #111827;
            font-family: "Segoe UI", Cantarell, Arial;
            font-size: 25px;
        }

        /* Card in der Mitte */
        #card {
            background: rgba(255,255,255,0.92);
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 16px;
        }

        /* Labels schlicht */
        QLabel { background: transparent; color: #111827; }

        /* Eingabefeld */
        QLineEdit {
            background: #ffffff;
            color: #111827;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 6px 8px;
        }
        QLineEdit:focus {
            border: 1px solid #3b82f6;
            background: #ffffff;
        }

        /* Basis-Buttons */
        QPushButton {
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 8px 12px;
            font-weight: 600;
            background: #e5e7eb;
            color: #111827;
        }
        QPushButton:hover  { background: #dfe3e8; }
        QPushButton:pressed{ background: #d6dbe1; }
        QPushButton:disabled {
            background: #eceff3; color:#9aa4b2; border-color:#d1d5db;
        }

        /* Spezifisch: Kunden anlegen = GRÜN */
        QPushButton#add_btn {
            background: #22c55e; color:#063619; border-color:#16a34a;
        }
        QPushButton#add_btn:hover   { background:#26d267; }
        QPushButton#add_btn:pressed { background:#1fb157; }
        QPushButton#add_btn:disabled{
            background:#a7f3d0; color:#0b4222; border-color:#86efac;
        }

        /* Spezifisch: Kunden löschen = ROT */
        QPushButton#del_btn {
            background: #ef4444; color:#3f0a0a; border-color:#dc2626;
        }
        QPushButton#del_btn:hover   { background:#f25555; }
        QPushButton#del_btn:pressed { background:#dc3a3a; }
        QPushButton#del_btn:disabled{
            background:#fecaca; color:#4b0c0c; border-color:#fca5a5;
        }

        /* Liste */
        QListWidget {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 4px;
        }
        QListWidget::item { padding: 6px 8px; border-radius: 6px; }
        QListWidget::item:hover { background: #eef2f7; }
        QListWidget::item:selected {
            background: #155e75; color: #e5e7eb; border: 1px solid #0ea5e9;
        }
        """)

    # ---------- Logik ----------
    def _add_customer(self):
        name = self.eingabe_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Eingabe fehlt", "Bitte einen Namen eingeben.")
            return

        key = self._norm(name)
        if key in self.kunden_keys:
            QMessageBox.warning(self, "Fehler", f"Der Kunde „{name}“ existiert bereits.")
            self.eingabe_name.clear()
            self._enable_delete()
            return

        self.kunden.append(name)
        self.info.setText(f'Der Kunde {name} wurde erfolgreich angelegt.')
        self.kunden_keys.add(key)
        self.liste.addItem(name)

        self.eingabe_name.clear()
        self.eingabe_name.setFocus()
        self._enable_delete()

    def _delete_selected(self):
        row = self.liste.currentRow()
        if row < 0:
            QMessageBox.information(self, "Hinweis", "Bitte zuerst einen Kunden auswählen.")
            return

        name = self.liste.item(row).text()
        reply = QMessageBox.question(
            self, "Löschen bestätigen",
            f'Den Kunden „{name}“ wirklich löschen?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        key = self._norm(name)
        if key in self.kunden_keys:
            self.kunden_keys.remove(key)
        if name in self.kunden:
            self.kunden.remove(name)

        self.liste.takeItem(row)
        self.info.setText(f'Der Kunde {name} wurde gelöscht.')
        self._enable_delete()

    def _enable_delete(self):
        self.del_btn.setEnabled(self.liste.currentRow() >= 0)

    @staticmethod
    def _norm(s: str) -> str:
        return " ".join(s.split()).lower()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())























