#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Broyder Juja Savdo - Telegram Bot
# Token: Sizning tokeningiz

import json
import os
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

TOKEN = "8867385397:AAFlV4A6XZfYsjoonE4mjw5UAttwZqnuR9A"
DATA_FILE = "data.json"

# Conversation states
(MENU, MIJOZ_ISM, MIJOZ_TEL, MIJOZ_MANZIL,
 BUY_MIJOZ, BUY_MIQDOR, BUY_NARX, BUY_ESLAT,
 INK_NOM, INK_TUXUM, INK_SANA, INK_HARORAT,
 KALC_MIQDOR, KALC_NARX) = range(14)

# ─── Ma'lumotlar ───────────────────────────────────────────

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"mijozlar": [], "buyurtmalar": [], "inkubatorlar": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── Klaviaturalar ─────────────────────────────────────────

def main_keyboard():
    return ReplyKeyboardMarkup([
        ["👥 Mijozlar", "📦 Buyurtmalar"],
        ["🥚 Inkubator", "🧮 Narx hisob"],
        ["📊 Statistika"]
    ], resize_keyboard=True)

def back_keyboard():
    return ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)

def skip_keyboard():
    return ReplyKeyboardMarkup([["⏭ O'tkazib yuborish", "🔙 Orqaga"]], resize_keyboard=True)

def mijoz_keyboard():
    return ReplyKeyboardMarkup([
        ["➕ Mijoz qo'shish", "📋 Mijozlar ro'yxati"],
        ["🔙 Orqaga"]
    ], resize_keyboard=True)

def buy_keyboard():
    return ReplyKeyboardMarkup([
        ["➕ Buyurtma qabul", "📋 Buyurtmalar ro'yxati"],
        ["🔙 Orqaga"]
    ], resize_keyboard=True)

def ink_keyboard():
    return ReplyKeyboardMarkup([
        ["➕ Partiya qo'shish", "📋 Partiyalar ro'yxati"],
        ["🔙 Orqaga"]
    ], resize_keyboard=True)

# ─── Start ─────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🐣 *Broyder Jo'ja Savdo botiga xush kelibsiz!*\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )
    return MENU

# ─── Menu handler ──────────────────────────────────────────

async def menu_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "👥 Mijozlar":
        await update.message.reply_text("👥 *Mijozlar bo'limi*", parse_mode="Markdown", reply_markup=mijoz_keyboard())
        return MENU

    elif text == "📦 Buyurtmalar":
        await update.message.reply_text("📦 *Buyurtmalar bo'limi*", parse_mode="Markdown", reply_markup=buy_keyboard())
        return MENU

    elif text == "🥚 Inkubator":
        await update.message.reply_text("🥚 *Inkubator bo'limi*", parse_mode="Markdown", reply_markup=ink_keyboard())
        return MENU

    elif text == "🧮 Narx hisob":
        await update.message.reply_text(
            "🧮 Jo'ja sonini kiriting:",
            reply_markup=back_keyboard()
        )
        return KALC_MIQDOR

    elif text == "📊 Statistika":
        await statistika(update, ctx)
        return MENU

    # Mijoz
    elif text == "➕ Mijoz qo'shish":
        await update.message.reply_text("👤 Mijozning ism-familiyasini kiriting:", reply_markup=back_keyboard())
        return MIJOZ_ISM

    elif text == "📋 Mijozlar ro'yxati":
        await mijozlar_royxati(update, ctx)
        return MENU

    # Buyurtma
    elif text == "➕ Buyurtma qabul":
        await update.message.reply_text("👤 Mijoz ismini kiriting:", reply_markup=back_keyboard())
        return BUY_MIJOZ

    elif text == "📋 Buyurtmalar ro'yxati":
        await buyurtmalar_royxati(update, ctx)
        return MENU

    # Inkubator
    elif text == "➕ Partiya qo'shish":
        await update.message.reply_text("📝 Partiya nomini kiriting (masalan: May 2025):", reply_markup=back_keyboard())
        return INK_NOM

    elif text == "📋 Partiyalar ro'yxati":
        await inkubatorlar_royxati(update, ctx)
        return MENU

    elif text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=main_keyboard())
        return MENU

    return MENU

# ─── Mijoz qo'shish ────────────────────────────────────────

async def mijoz_ism(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=main_keyboard())
        return MENU
    ctx.user_data["yangi_mijoz"] = {"ism": update.message.text}
    await update.message.reply_text("📞 Telefon raqamini kiriting:", reply_markup=back_keyboard())
    return MIJOZ_TEL

async def mijoz_tel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=main_keyboard())
        return MENU
    ctx.user_data["yangi_mijoz"]["tel"] = update.message.text
    await update.message.reply_text("📍 Manzilini kiriting (o'tkazish uchun bosing):", reply_markup=skip_keyboard())
    return MIJOZ_MANZIL

async def mijoz_manzil(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=main_keyboard())
        return MENU
    manzil = "" if update.message.text == "⏭ O'tkazib yuborish" else update.message.text
    ctx.user_data["yangi_mijoz"]["manzil"] = manzil
    ctx.user_data["yangi_mijoz"]["sana"] = datetime.now().strftime("%d.%m.%Y")

    data = load_data()
    data["mijozlar"].append(ctx.user_data["yangi_mijoz"])
    save_data(data)

    m = ctx.user_data["yangi_mijoz"]
    await update.message.reply_text(
        f"✅ *Mijoz qo'shildi!*\n\n"
        f"👤 Ism: {m['ism']}\n"
        f"📞 Tel: {m['tel']}\n"
        f"📍 Manzil: {m['manzil'] or 'Kiritilmagan'}",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )
    return MENU

# ─── Mijozlar ro'yxati ─────────────────────────────────────

async def mijozlar_royxati(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data["mijozlar"]:
        await update.message.reply_text("📭 Hali mijoz qo'shilmagan.", reply_markup=main_keyboard())
        return
    text = "👥 *Mijozlar ro'yxati:*\n\n"
    for i, m in enumerate(data["mijozlar"], 1):
        text += f"{i}. *{m['ism']}*\n   📞 {m['tel']}"
        if m.get("manzil"):
            text += f"\n   📍 {m['manzil']}"
        text += f"\n   📅 {m.get('sana', '')}\n\n"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

# ─── Buyurtma qo'shish ─────────────────────────────────────

async def buy_mijoz(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=main_keyboard())
        return MENU
    ctx.user_data["yangi_buy"] = {"mijoz": update.message.text}
    await update.message.reply_text("🐣 Jo'ja miqdorini kiriting (dona):", reply_markup=back_keyboard())
    return BUY_MIQDOR

async def buy_miqdor(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=main_keyboard())
        return MENU
    try:
        ctx.user_data["yangi_buy"]["miqdor"] = int(update.message.text)
    except:
        await update.message.reply_text("❌ Faqat son kiriting!")
        return BUY_MIQDOR
    await update.message.reply_text("💰 1 dona narxini kiriting (so'm):", reply_markup=back_keyboard())
    return BUY_NARX

async def buy_narx(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=main_keyboard())
        return MENU
    try:
        ctx.user_data["yangi_buy"]["narx"] = int(update.message.text)
    except:
        await update.message.reply_text("❌ Faqat son kiriting!")
        return BUY_NARX
    await update.message.reply_text("📝 Eslatma kiriting (o'tkazish mumkin):", reply_markup=skip_keyboard())
    return BUY_ESLAT

async def buy_eslat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=main_keyboard())
        return MENU
    eslat = "" if update.message.text == "⏭ O'tkazib yuborish" else update.message.text
    b = ctx.user_data["yangi_buy"]
    b["eslat"] = eslat
    b["jami"] = b["miqdor"] * b["narx"]
    b["sana"] = datetime.now().strftime("%d.%m.%Y")
    b["holat"] = "Kutilmoqda"

    data = load_data()
    data["buyurtmalar"].append(b)
    save_data(data)

    await update.message.reply_text(
        f"✅ *Buyurtma qabul qilindi!*\n\n"
        f"👤 Mijoz: {b['mijoz']}\n"
        f"🐣 Miqdor: {b['miqdor']} ta\n"
        f"💰 Narx: {b['narx']:,} so'm/dona\n"
        f"💵 Jami: *{b['jami']:,} so'm*\n"
        f"📝 Eslatma: {b['eslat'] or 'Yoq'}\n"
        f"📅 Sana: {b['sana']}",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )
    return MENU

# ─── Buyurtmalar ro'yxati ──────────────────────────────────

async def buyurtmalar_royxati(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data["buyurtmalar"]:
        await update.message.reply_text("📭 Hali buyurtma yo'q.", reply_markup=main_keyboard())
        return
    text = "📦 *Buyurtmalar ro'yxati:*\n\n"
    for i, b in enumerate(data["buyurtmalar"], 1):
        holat_emoji = {"Kutilmoqda": "⏳", "Tugallandi": "✅", "Bekor qilindi": "❌"}.get(b["holat"], "❓")
        text += (f"{i}. *{b['mijoz']}*\n"
                 f"   🐣 {b['miqdor']} ta - {b['jami']:,} so'm\n"
                 f"   {holat_emoji} {b['holat']} | 📅 {b.get('sana','')}\n\n")
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

# ─── Inkubator ─────────────────────────────────────────────

async def ink_nom(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=main_keyboard())
        return MENU
    ctx.user_data["yangi_ink"] = {"nom": update.message.text}
    await update.message.reply_text("🥚 Tuxum sonini kiriting (dona):", reply_markup=back_keyboard())
    return INK_TUXUM

async def ink_tuxum(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=main_keyboard())
        return MENU
    try:
        ctx.user_data["yangi_ink"]["tuxum"] = int(update.message.text)
    except:
        await update.message.reply_text("❌ Faqat son kiriting!")
        return INK_TUXUM
    await update.message.reply_text(
        "📅 Boshlash sanasini kiriting (KK.OO.YYYY):\nMasalan: 17.05.2025",
        reply_markup=back_keyboard()
    )
    return INK_SANA

async def ink_sana(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=main_keyboard())
        return MENU
    try:
        bosh = datetime.strptime(update.message.text, "%d.%m.%Y")
        chiqish = bosh + timedelta(days=21)
        ctx.user_data["yangi_ink"]["boshlanish"] = update.message.text
        ctx.user_data["yangi_ink"]["chiqish"] = chiqish.strftime("%d.%m.%Y")
    except:
        await update.message.reply_text("❌ Sana formati noto'g'ri! KK.OO.YYYY kiriting:")
        return INK_SANA
    await update.message.reply_text(
        f"✅ Chiqish sanasi: *{ctx.user_data['yangi_ink']['chiqish']}*\n\n🌡 Haroratni kiriting (o'tkazish mumkin):",
        parse_mode="Markdown",
        reply_markup=skip_keyboard()
    )
    return INK_HARORAT

async def ink_harorat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=main_keyboard())
        return MENU
    harorat = "" if update.message.text == "⏭ O'tkazib yuborish" else update.message.text
    ink = ctx.user_data["yangi_ink"]
    ink["harorat"] = harorat
    ink["holat"] = "Davom etmoqda"

    data = load_data()
    data["inkubatorlar"].append(ink)
    save_data(data)

    await update.message.reply_text(
        f"✅ *Inkubator partiyasi qo'shildi!*\n\n"
        f"📝 Nom: {ink['nom']}\n"
        f"🥚 Tuxum: {ink['tuxum']} ta\n"
        f"📅 Boshlanish: {ink['boshlanish']}\n"
        f"📅 Chiqish: *{ink['chiqish']}*\n"
        f"🌡 Harorat: {ink['harorat'] or 'Kiritilmagan'}",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )
    return MENU

# ─── Inkubatorlar ro'yxati ─────────────────────────────────

async def inkubatorlar_royxati(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data["inkubatorlar"]:
        await update.message.reply_text("📭 Hali inkubator partiyasi yo'q.", reply_markup=main_keyboard())
        return
    text = "🥚 *Inkubator partiyalari:*\n\n"
    today = datetime.now()
    for i, ink in enumerate(data["inkubatorlar"], 1):
        try:
            chiqish = datetime.strptime(ink["chiqish"], "%d.%m.%Y")
            qoldi = (chiqish - today).days
            kun_txt = f"{qoldi} kun qoldi" if qoldi > 0 else "Tayyor!"
        except:
            kun_txt = ""
        holat_e = "🟢" if ink["holat"] == "Davom etmoqda" else "✅"
        text += (f"{i}. *{ink['nom']}*\n"
                 f"   🥚 {ink['tuxum']} ta | {holat_e} {ink['holat']}\n"
                 f"   📅 {ink['boshlanish']} → {ink['chiqish']}\n"
                 f"   ⏱ {kun_txt}\n\n")
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

# ─── Kalkulyator ───────────────────────────────────────────

async def kalc_miqdor(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=main_keyboard())
        return MENU
    try:
        ctx.user_data["kalc_miqdor"] = int(update.message.text)
    except:
        await update.message.reply_text("❌ Faqat son kiriting!")
        return KALC_MIQDOR
    await update.message.reply_text("💰 1 dona narxini kiriting (so'm):", reply_markup=back_keyboard())
    return KALC_NARX

async def kalc_narx(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=main_keyboard())
        return MENU
    try:
        narx = int(update.message.text)
        miqdor = ctx.user_data["kalc_miqdor"]
        jami = miqdor * narx
        await update.message.reply_text(
            f"🧮 *Hisob natijasi:*\n\n"
            f"🐣 {miqdor} ta × {narx:,} so'm\n"
            f"💵 *Jami: {jami:,} so'm*",
            parse_mode="Markdown",
            reply_markup=main_keyboard()
        )
    except:
        await update.message.reply_text("❌ Faqat son kiriting!")
        return KALC_NARX
    return MENU

# ─── Statistika ────────────────────────────────────────────

async def statistika(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    jami_daromad = sum(b["jami"] for b in data["buyurtmalar"])
    tugallangan = sum(1 for b in data["buyurtmalar"] if b["holat"] == "Tugallandi")
    kutilmoqda = sum(1 for b in data["buyurtmalar"] if b["holat"] == "Kutilmoqda")
    aktiv_ink = sum(1 for i in data["inkubatorlar"] if i["holat"] == "Davom etmoqda")

    await update.message.reply_text(
        f"📊 *Umumiy statistika:*\n\n"
        f"👥 Mijozlar: *{len(data['mijozlar'])} ta*\n"
        f"📦 Jami buyurtmalar: *{len(data['buyurtmalar'])} ta*\n"
        f"   ✅ Tugallangan: {tugallangan}\n"
        f"   ⏳ Kutilmoqda: {kutilmoqda}\n"
        f"🥚 Aktiv inkubatorlar: *{aktiv_ink} ta*\n"
        f"💰 Jami daromad: *{jami_daromad:,} so'm*",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

# ─── Main ──────────────────────────────────────────────────

def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start), MessageHandler(filters.TEXT, menu_handler)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler)],
            MIJOZ_ISM: [MessageHandler(filters.TEXT & ~filters.COMMAND, mijoz_ism)],
            MIJOZ_TEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, mijoz_tel)],
            MIJOZ_MANZIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, mijoz_manzil)],
            BUY_MIJOZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_mijoz)],
            BUY_MIQDOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_miqdor)],
            BUY_NARX: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_narx)],
            BUY_ESLAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_eslat)],
            INK_NOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ink_nom)],
            INK_TUXUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ink_tuxum)],
            INK_SANA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ink_sana)],
            INK_HARORAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ink_harorat)],
            KALC_MIQDOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, kalc_miqdor)],
            KALC_NARX: [MessageHandler(filters.TEXT & ~filters.COMMAND, kalc_narx)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv)
    print("Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
