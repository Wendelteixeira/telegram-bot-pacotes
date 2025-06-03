from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8089655986:AAHUmJM9U8KafOqs2VbHUcHafx_mN5Nnyy8"  # ⬅️ Substitua pelo seu token do BotFather
ADMIN_ID = 1266652962
PIX_KEY = "leide.mari.mari1@gmail.com"

PACKAGES = {
    "bronze": {"name": "Pacote Bronze", "price": "R$30,00"},
    "prata": {"name": "Pacote Prata", "price": "R$45,00"},
    "ouro": {"name": "Pacote Ouro", "price": "R$55,00"},
    "diamante": {"name": "Pacote Diamante", "price": "R$65,00"},
}

user_orders = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🥉 Bronze – R$30", callback_data="bronze")],
        [InlineKeyboardButton("🥈 Prata – R$45", callback_data="prata")],
        [InlineKeyboardButton("🥇 Ouro – R$55", callback_data="ouro")],
        [InlineKeyboardButton("💎 Diamante – R$65", callback_data="diamante")],
    ]
    await update.message.reply_text(
        "Escolha um pacote:", reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def pacote_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    package_key = query.data
    package = PACKAGES.get(package_key)

    if package:
        user_orders[query.from_user.id] = package_key
        text = (
            f"Você escolheu o *{package['name']}* no valor de *{package['price']}*.\n\n"
            f"Faça o pagamento via PIX para:\n\n🔑 *{PIX_KEY}*\n\n"
            "Depois envie o comprovante aqui como foto (imagem)."
        )
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="voltar")]]
        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif package_key == "voltar":
        await start(update, context)

async def receber_comprovante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    package_key = user_orders.get(user_id)

    if not package_key:
        await update.message.reply_text("Por favor, selecione um pacote antes de enviar o comprovante usando /start.")
        return

    package = PACKAGES[package_key]
    caption = (
        f"📩 *Novo pedido recebido!*\n\n"
        f"👤 ID do cliente: `{user_id}`\n"
        f"📦 Pacote: *{package['name']}*\n"
        f"💰 Valor: *{package['price']}*\n\n"
        f"📸 Comprovante em anexo."
    )

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=file_id,
            caption=caption,
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Comprovante enviado! Aguarde a liberação manual.")
    else:
        await update.message.reply_text("Envie o comprovante como *imagem* (foto), por favor.", parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(pacote_callback))
    app.add_handler(MessageHandler(filters.PHOTO, receber_comprovante))
    print("🤖 Bot rodando...")
    app.run_polling()
