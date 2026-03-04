import asyncio

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8580445815:AAGxvw6bqyGiSHA6g2SCdgH5L-S5-dk1dQc"

# =========================
# BASE DE DATOS
# =========================

def crear_base_datos():
    conexion = sqlite3.connect("clientes.db")
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        fecha_inicio TEXT,
        fecha_expiracion TEXT
    )
    """)

    conexion.commit()
    conexion.close()


def agregar_cliente(nombre, inicio, expiracion):
    conexion = sqlite3.connect("clientes.db")
    cursor = conexion.cursor()

    cursor.execute(
        "INSERT INTO clientes (nombre, fecha_inicio, fecha_expiracion) VALUES (?, ?, ?)",
        (nombre, inicio, expiracion),
    )

    conexion.commit()
    conexion.close()


def obtener_clientes():
    conexion = sqlite3.connect("clientes.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM clientes")
    datos = cursor.fetchall()
    conexion.close()
    return datos


def eliminar_cliente(id_cliente):
    conexion = sqlite3.connect("clientes.db")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = ?", (id_cliente,))
    conexion.commit()
    conexion.close()


def renovar_cliente(id_cliente, nueva_fecha):
    conexion = sqlite3.connect("clientes.db")
    cursor = conexion.cursor()

    cursor.execute(
        "UPDATE clientes SET fecha_expiracion = ? WHERE id = ?",
        (nueva_fecha, id_cliente),
    )

    conexion.commit()
    conexion.close()


def buscar_cliente(nombre):
    conexion = sqlite3.connect("clientes.db")
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM clientes WHERE nombre LIKE ?",
        ('%' + nombre + '%',),
    )
    datos = cursor.fetchall()
    conexion.close()
    return datos


# =========================
# MENÚ
# =========================

MENU = """
===== SISTEMA IPTV =====

1️⃣ Agregar cliente  →  /agregar nombre inicio expiracion
2️⃣ Mostrar clientes →  /clientes
3️⃣ Ver estado       →  /estado
4️⃣ Eliminar         →  /eliminar id
5️⃣ Renovar          →  /renovar id nueva_fecha
6️⃣ Buscar           →  /buscar nombre
7️⃣ Salir            →  /salir
"""


# =========================
# COMANDOS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MENU)


async def agregar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        nombre = context.args[0]
        inicio = context.args[1]
        expiracion = context.args[2]

        agregar_cliente(nombre, inicio, expiracion)

        await update.message.reply_text("✅ Cliente agregado correctamente.\n" + MENU)
    except:
        await update.message.reply_text(
            "Usa:\n/agregar nombre YYYY-MM-DD YYYY-MM-DD"
        )


async def clientes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    datos = obtener_clientes()

    if not datos:
        await update.message.reply_text("No hay clientes.\n" + MENU)
        return

    mensaje = "📋 CLIENTES:\n\n"
    for c in datos:
        mensaje += f"ID:{c[0]} | {c[1]} | Inicio:{c[2]} | Exp:{c[3]}\n"

    await update.message.reply_text(mensaje + "\n" + MENU)


async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    datos = obtener_clientes()

    if not datos:
        await update.message.reply_text("No hay clientes.\n" + MENU)
        return

    hoy = datetime.now()
    mensaje = "📊 ESTADO:\n\n"

    for c in datos:
        try:
            fecha = datetime.strptime(c[3], "%Y-%m-%d")
            if fecha >= hoy:
                estado_texto = "✅ ACTIVO"
            else:
                estado_texto = "❌ VENCIDO"
        except:
            estado_texto = "⚠️ Fecha inválida"

        mensaje += f"{c[1]} → {estado_texto}\n"

    await update.message.reply_text(mensaje + "\n" + MENU)


async def eliminar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        id_cliente = int(context.args[0])
        eliminar_cliente(id_cliente)
        await update.message.reply_text("🗑 Cliente eliminado.\n" + MENU)
    except:
        await update.message.reply_text("Usa: /eliminar id")


async def renovar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        id_cliente = int(context.args[0])
        nueva_fecha = context.args[1]
        renovar_cliente(id_cliente, nueva_fecha)
        await update.message.reply_text("🔄 Cliente renovado.\n" + MENU)
    except:
        await update.message.reply_text(
            "Usa: /renovar id YYYY-MM-DD"
        )


async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        nombre = context.args[0]
        resultados = buscar_cliente(nombre)

        if not resultados:
            await update.message.reply_text("No encontrado.\n" + MENU)
            return

        mensaje = "🔎 RESULTADOS:\n\n"
        for r in resultados:
            mensaje += f"ID:{r[0]} | {r[1]} | Exp:{r[3]}\n"

        await update.message.reply_text(mensaje + "\n" + MENU)

    except:
        await update.message.reply_text("Usa: /buscar nombre")


async def salir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Saliendo del sistema.")


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    crear_base_datos()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("agregar", agregar))
    app.add_handler(CommandHandler("clientes", clientes))
    app.add_handler(CommandHandler("estado", estado))
    app.add_handler(CommandHandler("eliminar", eliminar))
    app.add_handler(CommandHandler("renovar", renovar))
    app.add_handler(CommandHandler("buscar", buscar))
    app.add_handler(CommandHandler("salir", salir))

    print("🤖 Bot funcionando correctamente...")
    app.run_polling()

