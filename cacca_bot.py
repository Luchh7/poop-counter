import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime

# --------------------
# CONFIG
# --------------------
BACKUP_FILE = "backup.json"
TOKEN = os.getenv("DISCORD_TOKEN")  # su Railway setti la variabile
PREFIX = "*"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# --------------------
# FUNZIONI UTILI
# --------------------
def load_data():
    if not os.path.exists(BACKUP_FILE):
        return {"users": {}, "daily": {}}
    try:
        with open(BACKUP_FILE, "r") as f:
            data = json.load(f)
        if "users" not in data:
            data["users"] = {}
        if "daily" not in data:
            data["daily"] = {}
        return data
    except (json.JSONDecodeError, KeyError):
        return {"users": {}, "daily": {}}

def save_data(data):
    with open(BACKUP_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --------------------
# EVENTI
# --------------------
@bot.event
async def on_ready():
    print(f"✅ Bot connesso come {bot.user}")
    auto_backup.start()

# --------------------
# COMANDI
# --------------------
@bot.command()
async def cacca(ctx):
    user_id = str(ctx.author.id)
    today = datetime.now().strftime("%Y-%m-%d")

    data = load_data()

    # totale
    if user_id not in data["users"]:
        data["users"][user_id] = 0
    data["users"][user_id] += 1

    # giornaliero
    if today not in data["daily"]:
        data["daily"][today] = {}
    if user_id not in data["daily"][today]:
        data["daily"][today][user_id] = 0
    data["daily"][today][user_id] += 1

    save_data(data)

    await ctx.send(f"💩 {ctx.author.mention} ha cagato! (Totale: {data['users'][user_id]})")

@bot.command()
async def classifica(ctx):
    data = load_data()
    if not data["users"]:
        await ctx.send("😢 Nessuno ha ancora cagato...")
        return

    sorted_users = sorted(data["users"].items(), key=lambda x: x[1], reverse=True)
    msg = "🏆 Classifica Cagate:\n"
    for i, (user_id, count) in enumerate(sorted_users[:10], 1):
        user = await bot.fetch_user(int(user_id))
        msg += f"{i}. {user.mention} — {count} cagate\n"

    await ctx.send(msg)

@bot.command()
async def recordcagate(ctx):
    data = load_data()
    if not data["daily"]:
        await ctx.send("📉 Nessun record ancora registrato.")
        return

    best_day = None
    best_user = None
    best_count = 0

    for day, users in data["daily"].items():
        for uid, count in users.items():
            if count > best_count:
                best_count = count
                best_day = day
                best_user = uid

    if best_user:
        user = await bot.fetch_user(int(best_user))
        await ctx.send(f"🔥 Record giornaliero: {user.mention} con {best_count} cagate in un giorno ({best_day})!")
    else:
        await ctx.send("📉 Nessun record trovato.")

@bot.command()
async def backup(ctx):
    data = load_data()
    save_data(data)
    await ctx.send("💾 Backup manuale completato!")

# --------------------
# BACKUP AUTOMATICO
# --------------------
@tasks.loop(hours=2)
async def auto_backup():
    data = load_data()
    save_data(data)
    print("💾 Backup automatico eseguito")

# --------------------
# START
# --------------------
bot.run(TOKEN)
