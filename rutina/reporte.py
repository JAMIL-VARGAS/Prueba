#!/usr/bin/env python3
"""Genera la captura (PNG) del reporte diario de campañas "PRENDER CLAUDE".

Uso:
    python3 rutina/reporte.py datos.json carpeta_salida

datos.json:
{
  "cuenta": "KHAOS SOLES",
  "archivo": "reporte-khaos-soles",
  "prueba": false,
  "campanas": [
    {"nombre": "PRENDER CLAUDE ...", "antes": "PAUSED", "ahora": "ACTIVE"}
  ],
  "total_activas_cuenta": 6
}
"""
import datetime
import html
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

CHROMIUM = "/opt/pw-browsers/chromium"

ESTADOS = {"ACTIVE": "Prendida", "PAUSED": "Apagada"}


def estado(valor):
    return ESTADOS.get(valor, valor)


def generar_html(datos):
    ahora = datetime.datetime.now(ZoneInfo("America/Lima"))
    campanas = datos["campanas"]
    prendidas_hoy = sum(1 for c in campanas if c["antes"] != "ACTIVE" and c["ahora"] == "ACTIVE")
    quedan = sum(1 for c in campanas if c["ahora"] == "ACTIVE")
    filas = []
    for c in campanas:
        hoy = c["antes"] != "ACTIVE" and c["ahora"] == "ACTIVE"
        clase = "on" if c["ahora"] == "ACTIVE" else "off"
        filas.append(
            f"<tr><td>{html.escape(c['nombre'])}</td>"
            f"<td>{estado(c['antes'])}</td>"
            f"<td class='{clase}'>{estado(c['ahora'])}</td>"
            f"<td>{'Sí' if hoy else '—'}</td></tr>"
        )
    aviso = "<p class='prueba'>PRUEBA — no se prendió nada</p>" if datos.get("prueba") else ""
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><title>Reporte {html.escape(datos['cuenta'])}</title>
<style>
body {{ font-family: Arial, sans-serif; background:#fff; color:#1c1e21; margin:24px; width:860px; }}
h1 {{ font-size:22px; margin:0 0 4px; }}
.sub {{ color:#65676b; margin:0 0 16px; }}
.prueba {{ background:#fff3cd; border:1px solid #e0c36b; padding:8px 12px; font-weight:bold; }}
.totales {{ display:flex; gap:12px; margin:16px 0; }}
.box {{ border:1px solid #dddfe2; border-radius:8px; padding:10px 16px; }}
.box b {{ display:block; font-size:26px; }}
table {{ border-collapse:collapse; width:100%; font-size:14px; }}
th, td {{ border:1px solid #dddfe2; padding:8px; text-align:left; }}
th {{ background:#f0f2f5; }}
.on {{ color:#1a7f37; font-weight:bold; }}
.off {{ color:#b42318; font-weight:bold; }}
.nota {{ color:#65676b; font-size:12px; margin-top:12px; }}
</style></head><body>
<h1>{html.escape(datos['cuenta'])}</h1>
<p class="sub">{ahora:%d/%m/%Y %H:%M} (hora de Lima)</p>
{aviso}
<div class="totales">
  <div class="box"><b>{prendidas_hoy}</b>prendidas hoy</div>
  <div class="box"><b>{quedan}</b>"PRENDER CLAUDE" prendidas</div>
  <div class="box"><b>{datos.get('total_activas_cuenta', quedan)}</b>campañas activas en la cuenta</div>
</div>
<table><tr><th>Campaña</th><th>Antes</th><th>Ahora</th><th>¿Prendida hoy?</th></tr>
{''.join(filas) or "<tr><td colspan='4'>No hay campañas PRENDER CLAUDE</td></tr>"}
</table>
<p class="nota">Reporte generado con los datos de Meta Ads (no es captura del Administrador de anuncios).</p>
</body></html>"""


def main():
    datos = json.load(open(sys.argv[1], encoding="utf-8"))
    salida = sys.argv[2]
    os.makedirs(salida, exist_ok=True)
    base = os.path.join(salida, datos["archivo"])
    with open(base + ".html", "w", encoding="utf-8") as f:
        f.write(generar_html(datos))
    alto = 330 + 40 * max(len(datos["campanas"]), 1)
    subprocess.run(
        [CHROMIUM, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
         f"--screenshot={os.path.abspath(base)}.png", f"--window-size=910,{alto}",
         "file://" + os.path.abspath(base) + ".html"],
        check=True, capture_output=True, timeout=60,
    )
    print(base + ".png")


if __name__ == "__main__":
    main()
