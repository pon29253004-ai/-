import os
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- 24時間稼働用のWebサーバー ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Discord Bot 本体 ---
intents = discord.Intents.default()
intents.members = True

class PokeNameBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced!")

bot = PokeNameBot()

@bot.tree.command(name="pokename", description="指定したフォーマットでニックネームを変更します")
@app_commands.describe(name="メインの名前", level="レベル・ランク", attribute="属性・ギルドなど")
async def pokename(interaction: discord.Interaction, name: str, level: str = "", attribute: str = ""):
    details = [x for x in [level, attribute] if x]
    formatted_name = f"{name} [{' / '.join(details)}]" if details else name

    if len(formatted_name) > 32:
        await interaction.response.send_message("エラー: 32文字を超えています。", ephemeral=True)
        return

    try:
        await interaction.user.edit(nick=formatted_name)
        await interaction.response.send_message(f"ニックネームを `{formatted_name}` に変更しました！", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("エラー: 権限不足です（Botのロール位置を確認してください）。", ephemeral=True)

keep_alive()
token = os.environ.get('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("エラー: DISCORD_TOKEN が設定されていません。")
