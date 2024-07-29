import sqlite3
import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

def create_connection():
    connection = None
    try:
        connection = sqlite3.connect("discord_bot.db")
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return connection

def create_tables(connection):
    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                rank INTEGER DEFAULT 1000
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY,
                match_id TEXT NOT NULL,
                team1 TEXT NOT NULL,
                team2 TEXT NOT NULL,
                winner TEXT
            );
        ''')
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")

# Initialize the database and tables
conn = create_connection()
if conn:
    create_tables(conn)

async def load_cogs():
    await bot.load_extension('cogs.queue_cog')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')

async def main():
    async with bot:
        await load_cogs()
        await bot.start('bot token placeholder')  

asyncio.run(main())

