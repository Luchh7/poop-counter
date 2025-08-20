import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime

# Prefisso dei comandi
bot = commands.Bot(command_prefix="*", intents=discord.Intents.all())

DATA_FILE = "cagate.json"
BACKUP_FILE = "backup.json"

# Funzione per caricare dati
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    elif os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, "r") as f:
            return json.load(f)
    else:
        return {"users": {}, "daily": {}}

# Funzione per salvare dati
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Funzione per backup
def backup_data():
    with open(BACKUP_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Carica dati
data = load_data()

@bot.event
async def on_ready():
    print(f"✅ Bot connesso come {bot.user}")
    auto_backup.start()

# Comando per aggiungere cacca
@bot.command()
async def cacca(ctx):
    user_id = str(ctx.author.id)
    today = datetime.now().strftime("%Y-%m-%d")

    if user_id not in data["users"]:
        data["users"][user_id] = 0
    if today not in data["daily"]:
        data["daily"][today] = {}

    if user_id not in data["daily"][today]:
        data["daily"][today][user_id] = 0

    data["users"][user_id] += 1
    data["daily"][today][user_id] += 1
    save_data()

    await ctx.send(f"💩 {ctx.author.mention} ha fatto una cacca! Totale: {data['users'][user_id]}")

# Comando classifica
@bot.command()
async def cagate(ctx):
    if not data["users"]:
        await ctx.send("Nessuno ha ancora cagato 💨")
        return

    classifica = sorted(data["users"].items(), key=lambda x: x[1], reverse=True)
    testo = "🏆 Classifica cacate 🏆\n"
    for i, (user_id, count) in enumerate(classifica, start=1):
        user = await bot.fetch_user(int(user_id))
        testo += f"{i}. {user.mention} → {count} cacate\n"

    await ctx.send(testo)

# Comando record giornaliero
@bot.command()
async def recordcagate(ctx):
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in data["daily"] or not data["daily"][today]:
        await ctx.send("Oggi nessuno ha cagato 💨")
        return

    top_user_id, top_count = max(data["daily"][today].items(), key=lambda x: x[1])
    user = await bot.fetch_user(int(top_user_id))
    await ctx.send(f"📅 Oggi il campione di cacate è {user.mention} con {top_count} 💩!")

# Comando manuale backup
@bot.command()
async def backup(ctx):
    backup_data()
    await ctx.send("💾 Backup manuale completato!")

# Backup automatico ogni 2 ore
@tasks.loop(hours=2)
async def auto_backup():
    backup_data()
    print("💾 Backup automatico eseguito")

# Avvia il bot
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
