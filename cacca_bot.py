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
intents.members = True          # necessario per leggere i membri

bot = commands.Bot(command_prefix="!", intents=intents)

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
    try:
        synced = await bot.tree.sync()
        print(f"Comandi slash sincronizzati: {len(synced)}")
    except Exception as e:
        print(e)

# ----------------------
# Comandi Slash
# ----------------------
@bot.tree.command(name="cacca", description="Aggiungi una cacca al tuo record!")
async def cacca(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    today = today_str()

    if user_id not in data:
        data[user_id] = {}

    if today not in data[user_id]:
        data[user_id][today] = 0

    data[user_id][today] += 1
    save_data()
    await interaction.response.send_message(f"💩 {interaction.user.mention} ha fatto la cacca! Totale oggi: {data[user_id][today]}")

@bot.tree.command(name="recordcacca", description="Mostra il tuo record giornaliero di cacca!")
async def recordcacca(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    today = today_str()
    count = data.get(user_id, {}).get(today, 0)
    await interaction.response.send_message(f"📊 {interaction.user.mention}, oggi hai fatto la cacca {count} volte!")

@bot.tree.command(name="cagate", description="Mostra chi fa più cacca!")
async def cagate(interaction: discord.Interaction):
    leaderboard = []

    for user_id, days in data.items():
        total = sum(days.values())
        leaderboard.append((user_id, total))

    leaderboard.sort(key=lambda x: x[1], reverse=True)

    if not leaderboard:
        await interaction.response.send_message("Nessuna cacca registrata 😅")
        return

    message = "🏆 **Classifica delle Cagate** 🏆\n"
    for i, (user_id, total) in enumerate(leaderboard[:10], start=1):
        message += f"{i}. <@{user_id}>: {total} 💩\n"

    await interaction.response.send_message(message)

# ----------------------
# Avvio bot
# ----------------------
bot.run(os.getenv("DISCORD_TOKEN"))
