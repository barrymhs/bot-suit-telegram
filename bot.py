import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]

EMOJI = {
    "paper": "🤚",
    "scissors": "✌️",
    "rock": "✊",
}

NAMA = {
    "paper": "Kertas",
    "scissors": "Gunting",
    "rock": "Batu",
}

SESI = {}


def papan_pilihan() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🤚", callback_data="pilih_paper"),
            InlineKeyboardButton("✌️", callback_data="pilih_scissors"),
            InlineKeyboardButton("✊", callback_data="pilih_rock"),
        ]
    ])


def tentukan_hasil(p1_pilihan: str, p2_pilihan: str, p1_nama: str, p2_nama: str) -> str:
    if p1_pilihan == p2_pilihan:
        return "🤝 **SERI!**"

    menang_p1 = {
        ("paper", "rock"),
        ("scissors", "paper"),
        ("rock", "scissors"),
    }

    if (p1_pilihan, p2_pilihan) in menang_p1:
        return f"🏆 **{p1_nama} MENANG!**"
    return f"🏆 **{p2_nama} MENANG!**"


async def mulai_suit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pesan = await update.message.reply_text(
        "Pilih 🤚 ✌️ ✊ (untuk 2 pemain)",
        reply_markup=papan_pilihan(),
    )

    SESI[pesan.message_id] = {
        "p1_id": None,
        "p1_nama": None,
        "p1_pilihan": None,
        "p2_id": None,
        "p2_nama": None,
        "p2_pilihan": None,
    }


async def proses_pilihan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = query.from_user
    msg_id = query.message.message_id

    if msg_id not in SESI:
        await query.answer("Ronde ini sudah selesai. Ketik /suit untuk mulai lagi.", show_alert=True)
        return

    sesi = SESI[msg_id]
    pilihan = query.data.replace("pilih_", "")

    if sesi["p1_pilihan"] and sesi["p2_pilihan"]:
        await query.answer("Ronde ini sudah selesai.", show_alert=True)
        return

    if sesi["p1_id"] is None:
        sesi["p1_id"] = user.id
        sesi["p1_nama"] = user.first_name
        sesi["p1_pilihan"] = pilihan
        await query.answer("Pilihanmu disimpan (rahasia).", show_alert=False)

    elif user.id == sesi["p1_id"]:
        sesi["p1_pilihan"] = pilihan
        await query.answer("Pilihanmu diperbarui (rahasia).", show_alert=False)

    elif sesi["p2_id"] is None:
        sesi["p2_id"] = user.id
        sesi["p2_nama"] = user.first_name
        sesi["p2_pilihan"] = pilihan
        await query.answer("Pilihanmu disimpan (rahasia).", show_alert=False)

    elif user.id == sesi["p2_id"]:
        sesi["p2_pilihan"] = pilihan
        await query.answer("Pilihanmu diperbarui (rahasia).", show_alert=False)

    else:
        await query.answer("Permainan ini khusus 2 orang.", show_alert=True)
        return

    if sesi["p1_pilihan"] and sesi["p2_pilihan"]:
        p1_p = sesi["p1_pilihan"]
        p2_p = sesi["p2_pilihan"]
        hasil = tentukan_hasil(p1_p, p2_p, sesi["p1_nama"], sesi["p2_nama"])

        teks_hasil = (
            f"🤚 ✌️ ✊ **Hasil (2 Pemain)**\n\n"
            f"• **{sesi['p1_nama']}**: {EMOJI[p1_p]} ({NAMA[p1_p]})\n"
            f"• **{sesi['p2_nama']}**: {EMOJI[p2_p]} ({NAMA[p2_p]})\n\n"
            f"{hasil}"
        )
        await query.edit_message_text(text=teks_hasil, parse_mode="Markdown")
        del SESI[msg_id]
        return

    teks_menunggu = (
        f"Pilih 🤚 ✌️ ✊ (untuk 2 pemain)\n\n"
        f"• **{sesi['p1_nama']}**: Sudah memilih ✅ (pilihan disembunyikan)\n"
        f"• **Pemain 2**: Menunggu memilih..."
    )
    await query.edit_message_text(
        text=teks_menunggu,
        reply_markup=papan_pilihan(),
        parse_mode="Markdown",
    )


def main() -> None:
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("suit", mulai_suit))
    app.add_handler(CallbackQueryHandler(proses_pilihan, pattern="^pilih_"))
    print("Bot suit 2 pemain aktif 24 jam...")
    app.run_polling()


if __name__ == "__main__":
    main()
      
