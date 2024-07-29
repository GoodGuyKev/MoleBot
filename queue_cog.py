import discord
import random
import sqlite3
from discord import app_commands
from discord.ext import commands
from .views import QueueView, TeamSelectView, MatchView

queue = []
initial_queue = []
teams = []
teams_data = [
    ("JTEKT Stings", "<:JTEKT:1266599811327594568>"),
    ("Panasonic Panthers", "<:Panthers:1266599797994029127>"),
    ("JT Thunders Hiroshima", "<:Thunders:1266599787294232669>"),
    ("Toray Arrows", "<:Arrows:1266599777265778833>"),
    ("Wolfdogs Nagoya", "<:WolfDogs:1266599765571797032>"),
    ("Tokyo Great Bears", "<:Bears:1266599753932865619>"),
    ("Oita Miyoshi Weisse Adler", "<:Oita:1266599711503155301>"),
    ("VC Nagano Tridents", "<:Tridents:1266599699528552589>"),
    ("Suntory Sunbirds", "<:Sunbirds:1266599688887468062>"),
    ("Sakai Blazers", "<:Blazers:1266599648643256320>"),
    ("Vero Volley Monza", "<:VeroVolley:1266599633912860702>")
        ]
'''ranks_data = [
    ("Bronze", "<:Bronze:1266599640715642880>"),
    ("Bronze2", "<:Bronze:1266599640715642880>"),
    ("Bronze3", "<:Bronze:1266599640715642880>"),
    ("Silver", "<:Silver:1266599642832273408>"),
    ("Silver2", "<:Silver:1266599642832273408>"),
    ("Silver3", "<:Silver:1266599642832273408>"),
    ("Gold", "<:Gold:1266599644919191552>"),
    ("Gold2", "<:Gold:1266599644919191552>"),
    ("Gold3", "<:Gold:1266599644919191552>"),
    ("Platinum", "<:Platinum:1266599646989137921>"),
    ("Platinum2", "<:Platinum:1266599646989137921>"),
    ("Platinum3", "<:Platinum:1266599646989137921>"),
    ("Diamond", "<:Diamond:1266599648934860801>"),
    ("Diamond2", "<:Diamond:1266599648934860801>"),
    ("Diamond3", "<:Diamond:1266599648934860801>"),
    ("Elite", "<:Master:1266599651049441280>"),
    ("Champion", "<:Grandmaster:1266599653099290624>"),
    ("Unreal", "<:Challenger:1266599654978570240>"),
]'''

def create_connection():
    connection = None
    try:
        connection = sqlite3.connect("discord_bot.db")
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return connection

class QueueCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue_message = None
        self.mode = 'Full Court'
        self.team_names = []
        self.matchups = []
        self.match_messages = []
        self.conn = create_connection()

    @app_commands.command(name="queue", description="Manage the queue")
    async def queue(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Queue", description="Current players in queue:\n" + "\n".join(queue) if queue else "No players in queue.")
        await interaction.response.send_message(embed=embed, view=QueueView())
        self.queue_message = await interaction.original_response()

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["Heads", "Tails"])
        await interaction.response.send_message(f"The coin landed on: {result}")

    def add_player(self, user_id, username):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO players (user_id, username) VALUES (?, ?)", (user_id, username))
        self.conn.commit()

    def update_player_rank(self, user_id, new_rank):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE players SET rank = ? WHERE user_id = ?", (new_rank, user_id))
        self.conn.commit()

    def get_player_rank(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT rank FROM players WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def record_match(self, match_id, team1, team2, winner):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO matches (match_id, team1, team2, winner) VALUES (?, ?, ?, ?)", (match_id, team1, team2, winner))
        self.conn.commit()

    def fetch_match_history(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute("SELECT match_id, team1, team2, winner FROM matches ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return rows

    @app_commands.command(name="matchhistory", description="Displays the recent match history")
    async def match_history(self, interaction: discord.Interaction, limit: int = 10):
        match_history = self.fetch_match_history(limit)
        if not match_history:
            await interaction.response.send_message("No match history available.", ephemeral=True)
            return

        embed = discord.Embed(title="Recent Match History")
        for match in match_history:
            match_id, team1, team2, winner = match
            embed.add_field(name=f"Match {match_id}", value=f"**{team1}** vs **{team2}**\n**Winner:** {winner}", inline=False)

        await interaction.response.send_message(embed=embed)

    async def update_queue_message(self):
        if self.queue_message:
            embed = discord.Embed(title="Queue", description="Current players in queue:\n" + "\n".join(queue) if queue else "No players in queue.")
            await self.queue_message.edit(embed=embed, view=QueueView())

    async def join_queue(self, interaction: discord.Interaction):
        if interaction.user.display_name not in queue:
            queue.append(interaction.user.display_name)
            self.add_player(interaction.user.id, interaction.user.display_name)
            await self.update_queue_message()
            await interaction.response.send_message(f"{interaction.user.display_name} has joined the queue!", ephemeral=True)
        else:
            await interaction.response.send_message("You are already in the queue.", ephemeral=True)

    async def leave_queue(self, interaction: discord.Interaction):
        if interaction.user.display_name in queue:
            queue.remove(interaction.user.display_name)
            await self.update_queue_message()
            await interaction.response.send_message(f"{interaction.user.display_name} has left the queue!", ephemeral=True)
        else:
            await interaction.response.send_message("You are not in the queue.", ephemeral=True)

    async def start_queue(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to start the queue.", ephemeral=True)
            return

        if len(queue) < 6:
            await interaction.response.send_message("There must be at least 6 players to start the queue.", ephemeral=True)
            return

        global initial_queue
        initial_queue = queue.copy()

        await interaction.response.send_message("Select the number of teams:", view=TeamSelectView(self.bot, mode=self.mode), ephemeral=True)

    async def handle_team_selection(self, interaction: discord.Interaction, num_teams: int):
        global teams
        max_team_size = 6 if self.mode == 'Full Court' else 4
        teams = [initial_queue[i::num_teams] for i in range(num_teams)]
        for team in teams:
            if len(team) > max_team_size:
                await interaction.response.send_message(f"Cannot form teams. Too many players for {self.mode}.", ephemeral=True)
                return

        self.team_names = random.sample(teams_data, num_teams)

        team_embed = discord.Embed(title="Teams", description="Here are the randomly assigned teams:")
        for i, team in enumerate(teams):
            team_name, emote = self.team_names[i]
            team_embed.add_field(name=f"{team_name} {emote}", value="\n".join(team), inline=False)

        await interaction.response.send_message(embed=team_embed, view=TeamSelectView(self.bot, mode=self.mode, num_teams=num_teams))

    async def reshuffle_teams(self, interaction: discord.Interaction, num_teams: int):
        global teams
        max_team_size = 6 if self.mode == 'Full Court' else 4
        teams = [initial_queue[i::num_teams] for i in range(num_teams)]
        for team in teams:
            if len(team) > max_team_size:
                await interaction.response.send_message(f"Cannot form teams. Too many players for {self.mode}.", ephemeral=True)
                return

        self.team_names = random.sample(teams_data, num_teams)

        team_embed = discord.Embed(title="Teams", description="Teams reshuffled:")
        for i, team in enumerate(teams):
            team_name, emote = self.team_names[i]
            team_embed.add_field(name=f"{team_name} {emote}", value="\n".join(team), inline=False)

        await interaction.response.send_message(embed=team_embed, view=TeamSelectView(self.bot, mode=self.mode, num_teams=num_teams))

    async def matchmake(self, interaction: discord.Interaction):
        if not teams or len(teams) < 2:
            await interaction.response.send_message("Not enough teams to matchmake.", ephemeral=True)
            return

        random.shuffle(teams)
        self.matchups = [(self.team_names[i], self.team_names[i+1]) for i in range(0, len(self.team_names)-1, 2)]
        if len(self.team_names) % 2 == 1:
            self.matchups.append((self.team_names[-1], None))

        self.match_messages = []
        for i, (team1, team2) in enumerate(self.matchups):
            team1_name, team1_emote = team1
            team2_name, team2_emote = team2 if team2 else ("No opponent", "")
            match_embed = discord.Embed(title=f"Match {i+1}", description=f"{team1_name} {team1_emote} vs {team2_name} {team2_emote}")
            match_message = await interaction.channel.send(embed=match_embed, view=MatchView(self.bot, [(team1, team2)], match_index=i))
            self.match_messages.append(match_message)

    async def select_winner(self, interaction: discord.Interaction, match_index: int, winner_index: int):
        match = self.matchups[match_index]
        winner = match[winner_index][0]
        await interaction.response.send_message(f"The winner of match {match_index + 1} is {winner}!", ephemeral=True)
        await self.match_messages[match_index].delete()
        # Record the match in the database
        self.record_match(match_id=match_index, team1=match[0][0], team2=match[1][0], winner=winner)

    async def toggle_mode(self, interaction: discord.Interaction):
        self.mode = 'Short Court' if self.mode == 'Full Court' else 'Full Court'
        await interaction.response.send_message(f"Mode changed to {self.mode}.", ephemeral=True)
        await self.start_queue(interaction)

    async def add_bots(self, interaction: discord.Interaction):
        for i in range(1, 12):
            bot_name = f"Bot {i}"
            if bot_name not in queue:
                queue.append(bot_name)
        await self.update_queue_message()
        await interaction.response.send_message("Added 11 bots to the queue.", ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            if interaction.data["custom_id"] == "join_queue":
                await self.join_queue(interaction)
            elif interaction.data["custom_id"] == "leave_queue":
                await self.leave_queue(interaction)
            elif interaction.data["custom_id"] == "add_bots":
                await self.add_bots(interaction)
            elif interaction.data["custom_id"] == "start_queue":
                await self.start_queue(interaction)
            elif interaction.data["custom_id"].startswith("teams_"):
                num_teams = int(interaction.data["custom_id"].split("_")[1])
                await self.handle_team_selection(interaction, num_teams)
            elif interaction.data["custom_id"].startswith("reshuffle_"):
                num_teams = int(interaction.data["custom_id"].split("_")[1])
                await self.reshuffle_teams(interaction, num_teams)
            elif interaction.data["custom_id"] == "toggle_mode":
                await self.toggle_mode(interaction)
            elif interaction.data["custom_id"] == "matchmake":
                await self.matchmake(interaction)
            elif interaction.data["custom_id"].startswith("winner_"):
                parts = interaction.data["custom_id"].split("_")
                match_index = int(parts[1])
                winner_index = int(parts[2]) - 1
                await self.select_winner(interaction, match_index, winner_index)

async def setup(bot):
    await bot.add_cog(QueueCog(bot))

