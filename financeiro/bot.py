# bot.py
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)
from database import tabela_ganhos, tabela_gastos, tabela_reserva, resumo_financeiro
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN não encontrado no .env!")

# Estados
ESCOLHA, VALOR, DESCRICAO, DATA, MES_RESUMO = range(5)

ANO_ATUAL = datetime.now().year

# -------- TECLADO --------

def teclado_menu():
    botoes = [
        ["💰 Adicionar Ganho",  "💸 Adicionar Gasto"],
        ["🏦 Adicionar Reserva", "📊 Ver Resumo"],
    ]
    return ReplyKeyboardMarkup(botoes, resize_keyboard=True)

def teclado_meses():
    botoes = [
        ["01 - Janeiro",  "02 - Fevereiro", "03 - Março"],
        ["04 - Abril",    "05 - Maio",       "06 - Junho"],
        ["07 - Julho",    "08 - Agosto",     "09 - Setembro"],
        ["10 - Outubro",  "11 - Novembro",   "12 - Dezembro"],
    ]
    return ReplyKeyboardMarkup(botoes, resize_keyboard=True)

# -------- INÍCIO --------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(
        "👋 Olá! Bem-vindo ao seu Financeiro Pessoal!\n"
        "Escolha uma opção abaixo:",
        reply_markup=teclado_menu()
    )
    return ESCOLHA

# -------- GANHO --------

async def iniciar_ganho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    context.user_data["acao"] = "ganho"
    await update.message.reply_text(
        "💰 Qual o valor do ganho?\nEx: 1500.00",
        reply_markup=ReplyKeyboardRemove()
    )
    return VALOR

# -------- GASTO --------

async def iniciar_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    context.user_data["acao"] = "gasto"
    await update.message.reply_text(
        "💸 Qual o valor do gasto?\nEx: 200.00",
        reply_markup=ReplyKeyboardRemove()
    )
    return VALOR

# -------- RESERVA --------

async def iniciar_reserva(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    context.user_data["acao"] = "reserva"
    await update.message.reply_text(
        "🏦 Qual o valor da reserva?\nEx: 500.00",
        reply_markup=ReplyKeyboardRemove()
    )
    return VALOR

# -------- RECEBE VALOR --------

async def receber_valor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    try:
        valor = float(update.message.text.replace(",", "."))
        context.user_data["valor"] = valor
    except ValueError:
        await update.message.reply_text("❌ Valor inválido! Digite apenas números. Ex: 1500.00")
        return VALOR

    if context.user_data["acao"] == "gasto":
        await update.message.reply_text("📝 Qual a descrição do gasto?")
        return DESCRICAO

    await update.message.reply_text("📅 Qual a data? (AAAA-MM-DD)\nEx: 2026-05-01")
    return DATA

# -------- RECEBE DESCRIÇÃO --------

async def receber_descricao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    context.user_data["descricao"] = update.message.text
    await update.message.reply_text("📅 Qual a data? (AAAA-MM-DD)\nEx: 2026-05-01")
    return DATA

# -------- RECEBE DATA E SALVA --------

async def receber_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    data  = update.message.text
    acao  = context.user_data["acao"]
    valor = context.user_data["valor"]

    try:
        if acao == "ganho":
            with tabela_ganhos() as db:
                db.inserir(valor, data)
            await update.message.reply_text(
                f"✅ Ganho de R$ {valor:.2f} salvo!",
                reply_markup=teclado_menu()
            )
        elif acao == "gasto":
            descricao = context.user_data["descricao"]
            with tabela_gastos() as db:
                db.inserir(valor, descricao, data)
            await update.message.reply_text(
                f"✅ Gasto de R$ {valor:.2f} ({descricao}) salvo!",
                reply_markup=teclado_menu()
            )
        elif acao == "reserva":
            with tabela_reserva() as db:
                db.inserir(valor, data)
            await update.message.reply_text(
                f"✅ Reserva de R$ {valor:.2f} salva!",
                reply_markup=teclado_menu()
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao salvar: {e}")

    return ESCOLHA

# -------- RESUMO - ESCOLHE MÊS --------

async def ver_resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(
        f"📅 Escolha o mês de {ANO_ATUAL}:",
        reply_markup=teclado_meses()
    )
    return MES_RESUMO

async def receber_mes_resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    try:
        # pega só os 2 primeiros caracteres "05 - Maio" → "05" → 5
        mes = int(update.message.text.strip()[:2])
        if mes < 1 or mes > 12:
            raise ValueError

        with resumo_financeiro() as db:
            r = db.obter_resumo(ANO_ATUAL, mes)

        nomes_mes = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março",
            4: "Abril",   5: "Maio",      6: "Junho",
            7: "Julho",   8: "Agosto",    9: "Setembro",
            10: "Outubro",11: "Novembro", 12: "Dezembro"
        }

        await update.message.reply_text(
            f"📊 *Resumo de {nomes_mes[mes]}/{ANO_ATUAL}*\n\n"
            f"💰 Ganhos:  R$ {r['total_ganhos']:.2f}\n"
            f"💸 Gastos:  R$ {r['total_gastos']:.2f}\n"
            f"🏦 Reserva: R$ {r['total_reserva']:.2f}\n"
            f"─────────────────\n"
            f"🏁 Saldo:   R$ {r['saldo']:.2f}",
            parse_mode="Markdown",
            reply_markup=teclado_menu()
        )
        return ESCOLHA

    except ValueError:
        await update.message.reply_text("❌ Mês inválido! Escolha uma opção do teclado.")
        return MES_RESUMO

# -------- CANCELAR --------

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(
        "❌ Operação cancelada.",
        reply_markup=teclado_menu()
    )
    return ESCOLHA

# -------- MAIN --------

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    conversa = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ESCOLHA: [
                MessageHandler(filters.Regex("💰 Adicionar Ganho"),   iniciar_ganho),
                MessageHandler(filters.Regex("💸 Adicionar Gasto"),   iniciar_gasto),
                MessageHandler(filters.Regex("🏦 Adicionar Reserva"), iniciar_reserva),
                MessageHandler(filters.Regex("📊 Ver Resumo"),        ver_resumo),
            ],
            VALOR:      [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_valor)],
            DESCRICAO:  [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_descricao)],
            DATA:       [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data)],
            MES_RESUMO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_mes_resumo)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conversa)
    print("🤖 Bot rodando...")
    app.run_polling()