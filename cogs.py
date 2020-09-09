import discord
import os
from dotenv import load_dotenv
from difflib import SequenceMatcher
from discord.ext import commands

class Quiz(commands.Cog):
    def __init__(self, bot, buzz_id):
        self.bot = bot
        self.tu_count = 1

        self.tossup = False
        self.bonus = 0
        self.bonusteam = None

        self.buzz_id = buzz_id

        self.moderator = None
        self.packet = False

        # teams
        self.team1 = []
        self.team2 = []
        self.teams = {1:0, 2:0}
        self.individuals = {}

        # lockout
        self.team1locked = False
        self.team2locked = False

        self.last_bonus = None
        self.last_buzz = None
        self.last_buzz_scoring = None


    def similar(self, a, b):
        return (SequenceMatcher(None, a, b).ratio() > 0.4)

    @commands.command(name='packet', help="Tell Quizbot a packet is about to be played, so it can listen for buzzes.")
    async def packet(self, ctx):
        if self.packet:
            page=discord.Embed(
                title="Oops!",
                description="A packet is already in progress! The moderator can end the current packet with !end if you wish to restart.",
                colour=discord.Colour.orange()
            )
        else:
            self.tu_count = 1
            self.moderator = None
            self.packet = True
            self.team1 = []
            self.team2 = []
            self.teams = {1:0, 2:0}
            self.individuals = {}

            # lockout
            self.team1locked = False
            self.team2locked = False

            self.last_bonus = None
            self.last_buzz = None
            self.last_buzz_scoring = None
            page=discord.Embed(
                title="Time for quiz!",
                description="Let's quiz! Moderator, declare yourself by typing !mod.",
                colour=discord.Colour.orange()
            )

        await self.buzz_channel.send(embed=page)

    @commands.command(name='end', help='Ends the current packet')
    async def end(self, ctx):
        if ctx.author.id == self.moderator.id:
            if self.packet:
                out = "Team 1: " + str(self.teams[1]) + " vs. Team 2: " + str(self.teams[2]) + "\n"
                out += "Individual player scores:\n"
                for player, score in self.individuals.items():
                    out += "\t " + player + " scored " + str(score) + " points!\n"
                self.packet = False
                self.moderator = None
                page=discord.Embed(
                    title="Final Scores",
                    description=out+"Thanks for a great game everyone. If you want to start a new packet, just type !packet into the chat and follow the instructions.",
                    colour=discord.Colour.orange()
                )
            else:
                page=discord.Embed(
                    title="Oops!",
                    description="There's no packet here to end! Type !packet into the chat to get one started.",
                    colour=discord.Colour.orange()
                )
        else:
            page=discord.Embed(
                title="Oops!",
                description="Only the moderator can end a game. If your moderator has disappeared, you can reset moderator priviliges by typing !unmod into the chat.",
                colour=discord.Colour.orange()
            )

        await self.buzz_channel.send(embed=page)


    @commands.command(name='mod', help="Register the moderator for a game of quiz")
    async def mod(self, ctx):
        if self.moderator is None:
            self.moderator = ctx.author
            page=discord.Embed(
                title="Moderator",
                description=f"Hello {self.moderator.name}, you're now the moderator. Type !tu between each tossup, and follow the scoring instructions as they appear!",
                colour=discord.Colour.orange()
            )
        else:
            page=discord.Embed(
                title="Moderator",
                description=f"{self.moderator.name} is already the moderator. If this is wrong, you can type !unmod to remove moderator privileges and allow a new moderator to be set.",
                colour=discord.Colour.orange()
            )

        await self.buzz_channel.send(embed=page)

    @commands.command(name='unmod', help="Unregister the current moderator, allowing a new moderator to be registered")
    async def unmod(self, ctx):
        if self.moderator is not None:
            self.moderator = None
            page=discord.Embed(
                title="Unregister moderator",
                description=f"Moderator privileges have been deallocated. Please assign a new moderator before proceeding with the game.",
                colour=discord.Colour.orange()
            )

            await self.buzz_channel.send(embed=page)

        else:
            page=discord.Embed(
                title="Unregister moderator",
                description=f"No moderator currently exists. Please assign a new moderator by typing !mod before proceeding with the game.",
                colour=discord.Colour.orange()
            )

            await self.buzz_channel.send(embed=page)


    @commands.command(name='tu', help="Signal the next tossup")
    async def tossup(self, ctx):
        if ctx.author.id == self.moderator.id:
            if self.bonus > 0:
                await self.buzz_channel.send("Oops, you haven't scored all of the last set of bonuses yet")
            else:
                await self.buzz_channel.send("Tossup " + str(self.tu_count))
                self.tu_count += 1
                self.tossup = True
        else:
            await self.buzz_channel.send(f"Oops! Only moderator ({self.moderator.name}) can signal a new tossup")

    @commands.command(name='team1', help='Assigns a player to Team 1')
    async def team1(self, ctx):
        if ctx.author.id in self.team1:
            page=discord.Embed(
                title="Oops!",
                description=f"{ctx.author.name}, you're already in Team 1. If you want to switch, type !team2",
                colour=discord.Colour.orange()
            )
        else:
            if self.nonteambuzz == ctx.author.id:
                self.bonusteam = 1
                self.nonteambuzz = None
            self.team1.append(ctx.author.id)
            if self.individuals.get(ctx.author.name) is None:
                self.individuals[ctx.author.name] = 0
            else:
                self.teams[1] += self.individuals[ctx.author.name]
            page=discord.Embed(
                title="New player",
                description=f"{ctx.author.name}just joined Team 1.",
                colour=discord.Colour.orange()
            )
        await self.buzz_channel.send(embed=page)

    @commands.command(name='team2', help='Assigns a player to Team 2')
    async def team2(self, ctx):
        if ctx.author.id in self.team2:
            page=discord.Embed(
                title="Oops!",
                description=f"{ctx.author.name}, you're already in Team 2. If you want to switch, type !team1",
                colour=discord.Colour.orange()
            )
        else:
            if self.nonteambuzz == ctx.author.id:
                self.bonusteam = 2
                self.nonteambuzz = None
            self.team2.append(ctx.author.id)
            if self.individuals.get(ctx.author.name) is None:
                self.individuals[ctx.author.name] = 0
            else:
                self.teams[2] += self.individuals[ctx.author.name]
            page=discord.Embed(
                title="New player",
                description=f"{ctx.author.name}just joined Team 2.",
                colour=discord.Colour.orange()
            )
        await self.buzz_channel.send(embed=page)

    @commands.Cog.listener()
    async def on_ready(self):
        self.buzz_channel = self.bot.get_channel(self.buzz_id)
        print(f'{self.bot.user.name} has connected to Discord!')

        page=discord.Embed(
            title="Quizbot",
            description="Hi, I'm Quizbot. Type !packet when you're ready to start reading a packet.",
            colour=discord.Colour.orange()
        )

        await self.buzz_channel.send(embed=page)

    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.channel.id == self.buzz_channel.id) and self.tossup:
            if self.bot.user.id != message.author.id:
                if (message.author.id in self.team1) and self.team1locked:
                    pass
                elif (message.author.id in self.team2) and self.team2locked:
                    pass
                else:
                    if self.similar('buzz', message.content):
                        buzz_page=discord.Embed(
                            title='Buzz!',
                            description=str(message.author.name) + ' buzzed in first! Gwan, my son!',
                            colour=discord.Colour.orange()
                        )
                    else:
                        buzz_page=discord.Embed(
                            title='Buzz?',
                            description='Possible banter detected. Moderator discretion required.',
                            colour=discord.Colour.orange()
                        )
                    await self.buzz_channel.send(embed=buzz_page)
                    self.tossup = False
                    self.last_buzz = message

                    page1=discord.Embed(
                        title='Scoring',
                        description=' Moderator, hit 👍 for a correct buzz, 👎 for an incorrect buzz at the end of the tossup, hit 🌩 for power, or 😭 for a neg. You can also hit 🤔 to reset the tossup if the buzz was made in error, or if someone\'s just bantering at an inopportune moment',
                        colour=discord.Colour.orange()
                    )

                    message1=await self.buzz_channel.send(embed=page1)

                    await message1.add_reaction('🌩')
                    await message1.add_reaction('👍')
                    await message1.add_reaction('👎')
                    await message1.add_reaction('😭')
                    await message1.add_reaction('🤔')

                    self.last_buzz_scoring = message1.id

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        def add_score(emoji, player, team):
            if self.individuals.get(player) == None:
                self.individuals[player] = 0
            if emoji == '🌩':
                self.bonus = 1
                self.individuals[player] += 15
                if team is not None:
                    self.bonusteam = team
                    self.teams[team] += 15
            elif emoji == '👍':
                self.bonus = 1
                self.individuals[player] += 10
                if team is not None:
                    self.bonusteam = team
                    self.teams[team] += 10
            elif emoji == '👎':
                if team == 1:
                    self.team1locked = True
                elif team == 2:
                    self.team2locked = True
                self.tossup = True
            elif emoji == '😭':
                self.individuals[player] -= 5
                if team is not None:
                    self.teams[team] -= 5
                if team == 1:
                    self.team1locked = True
                elif team == 2:
                    self.team2locked = True
                self.tossup = True
            elif emoji == '🤔':
                # TODO: erroneous buzz handling
                self.tossup = True
            if self.team1locked and self.team2locked:
                self.bonus = 0
                self.tossup = False
                self.team1locked=False
                self.team2locked=False

        if user.id ==self.moderator.id:
            if reaction.message.id == self.last_buzz_scoring:
                player_id = self.last_buzz.author.id
                player = self.last_buzz.author.name
                if player_id in self.team1:
                    team = 1
                elif player_id in self.team2:
                    team = 2
                else:
                    await self.buzz_channel.send(f"By the way, I noticed {player} isn't on a team yet. Type !team1 or !team2 to join a team, and I'll add your score to that team.")
                    self.nonteambuzz = player_id
                    team = None
                add_score(reaction.emoji, player, team)
                if self.bonus == 1:
                    page1=discord.Embed(
                        title='Scoring: Bonus 1',
                        description=' Moderator, hit 👍 if the bonus was answered correctly, and 👎 if not.',
                        colour=discord.Colour.orange()
                    )
                    self.last_bonus = await self.buzz_channel.send(embed=page1)

                    await self.last_bonus.add_reaction('👍')
                    await self.last_bonus.add_reaction('👎')

            elif reaction.message.id == self.last_bonus.id:
                if self.bonusteam is not None:
                    if self.bonus == 1:
                        if reaction.emoji == '👍':
                            self.teams[self.bonusteam] += 10

                        self.bonus += 1
                        page1=discord.Embed(
                            title='Scoring: Bonus 2',
                            description=' Moderator, hit 👍 if the bonus was answered correctly, and 👎 if not.',
                            colour=discord.Colour.orange()
                        )
                        self.last_bonus = await self.buzz_channel.send(embed=page1)

                        await self.last_bonus.add_reaction('👍')
                        await self.last_bonus.add_reaction('👎')
                    elif self.bonus == 2:
                        if reaction.emoji == '👍':
                            self.teams[self.bonusteam] += 10

                        self.bonus += 1
                        page1=discord.Embed(
                            title='Scoring: Bonus 3',
                            description=' Moderator, hit 👍 if the bonus was answered correctly, and 👎 if not.',
                            colour=discord.Colour.orange()
                        )
                        self.last_bonus = await self.buzz_channel.send(embed=page1)

                        await self.last_bonus.add_reaction('👍')
                        await self.last_bonus.add_reaction('👎')
                    elif self.bonus == 3:
                        if reaction.emoji == '👍':
                            self.teams[self.bonusteam] += 10

                        self.bonus = 0
                        self.bonusteam = None
                else:
                    await self.buzz_channel.send("You're trying to proceed with bonuses, but the player that buzzed correctly is not assigned to a team. Please rectify this before proceeding by typing !team1 or !team2 into the chat. Once you have done so, if the mod presses the same reaction again, the scores will be corrected.")

        else:
            pass




    @commands.command(name='shutdown', help='Shuts the current quizbot down.')
    async def shutdown(self,ctx):
        if ( ctx.message.author.id == 689895662082719810) or (ctx.message.author.id == self.moderator.id):
            await ctx.send("Bleep bloop! I was just learning to love...")
            print("shutdown")
            try:
                await self.bot.logout()
            except:
                print("EnvironmentError")
                self.bot.clear()
        else:
            await ctx.send("Only the moderator (or Dan) can shut Quizbot down!")
