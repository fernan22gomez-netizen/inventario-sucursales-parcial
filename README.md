# Panel de inventario por sucursal

**Actividad:** Parcial del segundo cómputo - Programación Computacional III  
**Integrantes:** Fernando Obispo y Kevin Portillo  
**Institución:** Universidad Gerardo Barrios (UGB)

## Descripción

Aplicación de escritorio para revisar un inventario de ejemplo en cinco sucursales salvadoreñas. Permite filtrar por sucursal, consultar unidades y valor estimado, revisar productos en la tabla y cambiar entre dos gráficos.

> Los registros son simulados para la actividad. No son ventas ni existencias reales de una empresa.

## Archivos

- `inventario_app.py`: interfaz en PyQt5; usa pandas para leer y resumir los datos y Matplotlib para los gráficos.
- `datos.csv`: 40 registros de inventario, con sucursal, producto, categoría, cantidad, costo unitario, punto de reorden y valor estimado.
- `informe_consultoria.pdf`: análisis, conclusiones por variable, recomendaciones y gráficos. La primera página se dejó en blanco para agregar la portada.
- `requirements.txt`: dependencias de Python.

## Preparación en Windows

Se recomienda Python 3.11 o 3.12. Abre PowerShell dentro de esta carpeta y ejecuta:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python inventario_app.py
```

Si PowerShell bloquea la activación del entorno, también puedes instalar y ejecutar sin activarlo:

```powershell
py -m pip install -r requirements.txt
py inventario_app.py
```

Al iniciar, la terminal muestra `head()`, `info()`, `describe()` y las unidades agrupadas por sucursal. La ventana permite cambiar la sucursal y el gráfico.

## Datos y cálculo

El conjunto tiene 5 sucursales × 8 productos = 40 filas. `Valor_inventario_USD` se calcula como `Cantidad × Costo_unitario_USD`. `Punto_reorden` es un umbral académico de ejemplo. Para decisiones reales, se necesitarían movimientos, ventas, proveedores, fechas y costos verificados.
