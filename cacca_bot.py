import discord
from discord.ext import commands
import json
import os
from datetime import datetime

# ----------------------
# Impostazioni intents
# ----------------------
intents = discord.Intents.default()
intents.message_content = True  # necessario per leggere i messaggi
intents.members = True          # necessario se leggi membri

bot = commands.Bot(command_prefix="*", intents=intents)

# ----------------------
# Percorso file dati
# ----------------------
DATA_FILE = "cacca_data.json"

# Carica dati esistenti o crea struttura vuota
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {}

# ----------------------
# Funzioni di supporto
# ----------------------
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def today_str():
    return datetime.utcnow().strftime("%Y-%m-%d")

# ----------------------
# Eventi
# ----------------------
@bot.event
async def on_ready():
    print(f"✅ Bot connesso come {bot.user}")

# ----------------------
# Comandi con prefisso *
# ----------------------

@bot.command(name="cacca")
async def cacca(ctx):
    user_id = str(ctx.author.id)
    today = today_str()

    if user_id not in data:
        data[user_id] = {}

    if today not in data[user_id]:
        data[user_id][today] = 0

    data[user_id][today] += 1
    save_data()
    await ctx.send(f"💩 {ctx.author.mention} ha fatto la cacca! Totale oggi: {data[user_id][today]}")

@bot.command(name="recordcacca")
async def recordcacca(ctx):
    user_id = str(ctx.author.id)
    today = today_str()
    count = data.get(user_id, {}).get(today, 0)
    await ctx.send(f"📊 {ctx.author.mention}, oggi hai fatto la cacca {count} volte!")

@bot.command(name="cagate")
async def cagate(ctx):
    leaderboard = []

    for user_id, days in data.items():
        total = sum(days.values())
        leaderboard.append((user_id, total))

    leaderboard.sort(key=lambda x: x[1], reverse=True)

    if not leaderboard:
        await ctx.send("Nessuna cacca registrata 😅")
        return

    message = "🏆 **Classifica delle Cagate** 🏆\n"
    for i, (user_id, total) in enumerate(leaderboard[:10], start=1):
        message += f"{i}. <@{user_id}>: {total} 💩\n"

    await ctx.send(message)

# ----------------------
# Avvio bot
# ----------------------
bot.run(os.getenv("DISCORD_TOKEN"))
