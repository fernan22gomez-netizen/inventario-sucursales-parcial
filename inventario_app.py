"""Aplicación académica para consultar el inventario de cinco sucursales."""
from pathlib import Path
import sys
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout, QLabel,
                             QMainWindow, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget, QHeaderView)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

CSV_PATH = Path(__file__).with_name("datos.csv")
PALETA = ["#5B8E7D", "#8EA78D", "#D5A04E", "#CD7765", "#748CAB", "#9A7AA0", "#4F7C8A", "#C89A6C"]


def cargar_datos():
    datos = pd.read_csv(CSV_PATH)
    print("\nPrimeras filas:")
    print(datos.head())
    print("\nEstructura y tipos:")
    datos.info()
    print("\nEstadísticas básicas:")
    print(datos.describe())
    print("\nUnidades por sucursal:")
    print(datos.groupby("Sucursal")["Cantidad"].sum().sort_values(ascending=False))
    return datos


class PanelGrafico(FigureCanvas):
    def __init__(self, parent=None):
        self.figura = Figure(figsize=(6.2, 4.4), dpi=100, facecolor="white")
        self.ax = self.figura.add_subplot(111)
        super().__init__(self.figura)
        self.setParent(parent)

    def dibujar(self, datos, tipo):
        self.ax.clear()
        if tipo == "Unidades por producto":
            resumen = datos.groupby("Producto")["Cantidad"].sum().sort_values()
            resumen.plot(kind="barh", ax=self.ax, color=PALETA[:len(resumen)], width=.72)
            self.ax.set_xlabel("Unidades")
            self.ax.set_title("Existencias por producto", color="#243B36", pad=12)
        else:
            resumen = datos.groupby("Categoria")["Valor_inventario_USD"].sum().sort_values()
            resumen.plot(kind="bar", ax=self.ax, color=PALETA[:len(resumen)], width=.68)
            self.ax.set_ylabel("Valor estimado (USD)")
            self.ax.set_title("Valor del inventario por categoría", color="#243B36", pad=12)
            self.ax.tick_params(axis="x", rotation=18)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.grid(axis="x" if tipo == "Unidades por producto" else "y", alpha=.18)
        self.ax.set_axisbelow(True)
        self.figura.tight_layout()
        self.draw()


class VentanaInventario(QMainWindow):
    def __init__(self, datos):
        super().__init__()
        self.datos = datos
        self.setWindowTitle("Inventario | Panel de sucursales")
        self.resize(1220, 760)
        self.setMinimumSize(980, 640)
        self.setStyleSheet("""
            QWidget { background: #F5F7F6; color: #243B36; font-family: Segoe UI; }
            QLabel#title { font-size: 24px; font-weight: 650; }
            QLabel#muted { color: #697A75; font-size: 12px; }
            QFrame#card, QFrame#panel { background: white; border: 1px solid #E1E9E6; border-radius: 10px; }
            QLabel#value { font-size: 21px; font-weight: 650; color: #24594F; }
            QComboBox { background: white; border: 1px solid #D5E0DC; border-radius: 6px; padding: 8px 10px; min-width: 190px; }
            QTableWidget { background: white; border: 0; gridline-color: #E7EEEB; selection-background-color: #DCEBE6; selection-color: #243B36; }
            QHeaderView::section { background: #EDF3F1; color: #40534D; padding: 8px; border: 0; font-weight: 600; }
        """)
        self._construir()
        self.actualizar()

    def _tarjeta(self, etiqueta):
        card = QFrame(); card.setObjectName("card")
        layout = QVBoxLayout(card); layout.setContentsMargins(16, 12, 16, 12)
        label = QLabel(etiqueta); label.setObjectName("muted")
        value = QLabel("-"); value.setObjectName("value")
        layout.addWidget(label); layout.addWidget(value)
        return card, value

    def _construir(self):
        central = QWidget(); self.setCentralWidget(central)
        main = QVBoxLayout(central); main.setContentsMargins(24, 20, 24, 18); main.setSpacing(14)
        heading = QHBoxLayout()
        titles = QVBoxLayout()
        title = QLabel("Inventario de productos"); title.setObjectName("title")
        subtitle = QLabel("Consulta de existencias, valor estimado y niveles de reposición")
        subtitle.setObjectName("muted")
        titles.addWidget(title); titles.addWidget(subtitle)
        heading.addLayout(titles); heading.addStretch()
        self.sucursal = QComboBox(); self.sucursal.addItem("Todas las sucursales")
        self.sucursal.addItems(sorted(self.datos["Sucursal"].unique()))
        self.sucursal.currentIndexChanged.connect(self.actualizar)
        heading.addWidget(QLabel("Sucursal")); heading.addWidget(self.sucursal)
        main.addLayout(heading)

        cards = QHBoxLayout(); cards.setSpacing(12)
        card1,self.total_units = self._tarjeta("UNIDADES DISPONIBLES")
        card2,self.total_value = self._tarjeta("VALOR ESTIMADO")
        card3,self.alert_count = self._tarjeta("BAJO PUNTO DE REORDEN")
        for card in (card1,card2,card3): cards.addWidget(card)
        main.addLayout(cards)

        content = QHBoxLayout(); content.setSpacing(14)
        table_panel = QFrame(); table_panel.setObjectName("panel")
        tl=QVBoxLayout(table_panel); tl.setContentsMargins(14,14,14,14)
        table_heading=QLabel("Detalle por producto"); table_heading.setStyleSheet("font-size:15px;font-weight:600")
        tl.addWidget(table_heading)
        self.tabla=QTableWidget(); self.tabla.setAlternatingRowColors(True)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers); self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.verticalHeader().setVisible(False); self.tabla.setShowGrid(False)
        tl.addWidget(self.tabla)
        chart_panel=QFrame(); chart_panel.setObjectName("panel")
        cl=QVBoxLayout(chart_panel); cl.setContentsMargins(14,14,14,14)
        chart_head=QHBoxLayout(); chart_label=QLabel("Resumen visual"); chart_label.setStyleSheet("font-size:15px;font-weight:600")
        self.tipo_grafico=QComboBox(); self.tipo_grafico.addItems(["Unidades por producto","Valor por categoría"])
        self.tipo_grafico.currentIndexChanged.connect(self.actualizar)
        chart_head.addWidget(chart_label); chart_head.addStretch(); chart_head.addWidget(self.tipo_grafico)
        cl.addLayout(chart_head); self.grafico=PanelGrafico(self); cl.addWidget(self.grafico)
        content.addWidget(table_panel, 6); content.addWidget(chart_panel, 5)
        main.addLayout(content,1)
        foot=QLabel("Datos simulados con fines académicos · El valor es una estimación de cantidad por costo unitario")
        foot.setObjectName("muted"); main.addWidget(foot)

    def actualizar(self):
        if not hasattr(self, "tabla"):
            return
        branch=self.sucursal.currentText()
        datos=self.datos if branch=="Todas las sucursales" else self.datos[self.datos["Sucursal"]==branch]
        self.total_units.setText(f"{int(datos['Cantidad'].sum()):,}")
        self.total_value.setText(f"${datos['Valor_inventario_USD'].sum():,.2f}")
        alerts=int((datos["Cantidad"]<datos["Punto_reorden"]).sum())
        self.alert_count.setText(str(alerts))
        shown=datos[["Sucursal","Producto","Cantidad","Punto_reorden","Valor_inventario_USD"]].copy()
        headers=["Sucursal","Producto","Unidades","Reorden","Valor (USD)"]
        self.tabla.setColumnCount(len(headers)); self.tabla.setHorizontalHeaderLabels(headers)
        self.tabla.setRowCount(len(shown))
        for row_idx,(_,row) in enumerate(shown.iterrows()):
            values=[row.Sucursal,row.Producto,str(int(row.Cantidad)),str(int(row.Punto_reorden)),f"${row.Valor_inventario_USD:,.2f}"]
            for col_idx,value in enumerate(values):
                item=QTableWidgetItem(value)
                if col_idx in (2,3,4): item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                self.tabla.setItem(row_idx,col_idx,item)
        self.grafico.dibujar(datos,self.tipo_grafico.currentText())


def main():
    datos=cargar_datos()
    app=QApplication(sys.argv)
    ventana=VentanaInventario(datos)
    ventana.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
