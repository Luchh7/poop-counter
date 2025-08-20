import discord
from discord.ext import commands
from collections import defaultdict
import datetime
import json
import os
import shutil

# Intents necessari
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

DATA_FILE = "cacca_data.json"
BACKUP_FOLDER = "backups"

# Variabili
cacca_oggi = defaultdict(int)
record_personale = defaultdict(int)
ultima_data = datetime.date.today()


# ---------- Gestione file ----------
def salva_dati():
    data = {
        "cacca_oggi": dict(cacca_oggi),
        "record_personale": dict(record_personale),
        "ultima_data": ultima_data.isoformat()
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def carica_dati():
    global cacca_oggi, record_personale, ultima_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        cacca_oggi = defaultdict(int, {int(k): v for k, v in data.get("cacca_oggi", {}).items()})
        record_personale = defaultdict(int, {int(k): v for k, v in data.get("record_personale", {}).items()})
        ultima_data = datetime.date.fromisoformat(data.get("ultima_data", str(datetime.date.today())))


def backup_locale():
    oggi = datetime.date.today().isoformat()
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
    shutil.copy(DATA_FILE, os.path.join(BACKUP_FOLDER, f"cacca_backup_{oggi}.json"))


def reset_giornaliero():
    global cacca_oggi, ultima_data
    oggi = datetime.date.today()
    if oggi != ultima_data:
        cacca_oggi = defaultdict(int)
        ultima_data = oggi
        salva_dati()
        backup_locale()


# ---------- Eventi e comandi ----------
@bot.event
async def on_ready():
    carica_dati()
    print(f"✅ Bot connesso come {bot.user}")


@bot.command()
async def cacca(ctx):
    """Segna che l'utente è andato in bagno"""
    reset_giornaliero()

    user = ctx.author
    cacca_oggi[user.id] += 1

    # aggiorna record personale
    if cacca_oggi[user.id] > record_personale[user.id]:
        record_personale[user.id] = cacca_oggi[user.id]

    salva_dati()
    await ctx.send(f"💩 {user.display_name} ha fatto cacca! Totale di oggi: {cacca_oggi[user.id]}")


@bot.command()
async def classifica(ctx):
    """Mostra la classifica delle cacche di oggi"""
    reset_giornaliero()

    if not cacca_oggi:
        await ctx.send("Nessuno ha ancora fatto cacca oggi 💩")
        return

    classifica = sorted(cacca_oggi.items(), key=lambda x: x[1], reverse=True)
    msg = "📊 Classifica cacche di oggi:\n"
    for i, (user_id, count) in enumerate(classifica, start=1):
        user = await bot.fetch_user(user_id)
        msg += f"{i}. {user.display_name} → {count}\n"

    await ctx.send(msg)


@bot.command()
async def record(ctx):
    """Mostra i record personali"""
    if not record_personale:
        await ctx.send("Nessun record ancora registrato 💩")
        return

    classifica = sorted(record_personale.items(), key=lambda x: x[1], reverse=True)
    msg = "🏆 Record personali:\n"
    for i, (user_id, record) in enumerate(classifica, start=1):
        user = await bot.fetch_user(user_id)
        msg += f"{i}. {user.display_name} → {record}\n"

    await ctx.send(msg)


# ---------- Avvio bot ----------
bot.run(os.getenv("DISCORD_TOKEN"))
