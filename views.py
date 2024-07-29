import discord

class QueueView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="Join Queue", style=discord.ButtonStyle.primary, custom_id="join_queue"))
        self.add_item(discord.ui.Button(label="Leave Queue", style=discord.ButtonStyle.danger, custom_id="leave_queue"))
        self.add_item(discord.ui.Button(label="Add Bots", style=discord.ButtonStyle.secondary, custom_id="add_bots"))
        self.add_item(discord.ui.Button(label="Start Queue", style=discord.ButtonStyle.success, custom_id="start_queue"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.guild is not None

class TeamSelectView(discord.ui.View):
    def __init__(self, bot, mode='Full Court', num_teams=None):
        super().__init__()
        self.bot = bot
        self.mode = mode
        self.num_teams = num_teams
        if num_teams is None:
            for i in range(1, 7):
                self.add_item(discord.ui.Button(label=f"{i} Teams", style=discord.ButtonStyle.secondary, custom_id=f"teams_{i}"))
        else:
            self.add_item(discord.ui.Button(label="Reshuffle Teams", style=discord.ButtonStyle.primary, custom_id=f"reshuffle_{num_teams}"))
            self.add_item(discord.ui.Button(label="Matchmake", style=discord.ButtonStyle.success, custom_id="matchmake"))

        self.add_item(discord.ui.Button(label=f"Mode: {mode}", style=discord.ButtonStyle.primary, custom_id="toggle_mode"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.guild is not None

class MatchView(discord.ui.View):
    def __init__(self, bot, matchups, match_index):
        super().__init__()
        self.bot = bot
        self.matchups = matchups
        self.match_index = match_index
        team1, team2 = matchups[0]
        if team2:
            self.add_item(discord.ui.Button(label=f"Winner: {team1[0]}", style=discord.ButtonStyle.primary, custom_id=f"winner_{match_index}_1"))
            self.add_item(discord.ui.Button(label=f"Winner: {team2[0]}", style=discord.ButtonStyle.primary, custom_id=f"winner_{match_index}_2"))
        else:
            self.add_item(discord.ui.Button(label=f"Winner: {team1[0]}", style=discord.ButtonStyle.primary, custom_id=f"winner_{match_index}_1"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.guild is not None
