""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""

import io
import os
import re
import random
import shutil
import tempfile
import datetime
import asyncio
import contextlib
import filetype
import requests

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import Context

from yt_dlp import YoutubeDL

class Choice(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.value = None

    @discord.ui.button(label="Heads", style=discord.ButtonStyle.blurple)
    async def confirm(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        self.value = "heads"
        self.stop()

    @discord.ui.button(label="Tails", style=discord.ButtonStyle.blurple)
    async def cancel(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        self.value = "tails"
        self.stop()


class RockPaperScissors(discord.ui.Select):
    def __init__(self) -> None:
        options = [
            discord.SelectOption(
                label="Scissors", description="You choose scissors.", emoji="✂"
            ),
            discord.SelectOption(
                label="Rock", description="You choose rock.", emoji="🪨"
            ),
            discord.SelectOption(
                label="Paper", description="You choose paper.", emoji="🧻"
            ),
        ]
        super().__init__(
            placeholder="Choose...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        choices = {
            "rock": 0,
            "paper": 1,
            "scissors": 2,
        }
        user_choice = self.values[0].lower()
        user_choice_index = choices[user_choice]

        bot_choice = random.choice(list(choices.keys()))
        bot_choice_index = choices[bot_choice]

        result_embed = discord.Embed(color=0xBEBEFE)
        result_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )

        winner = (3 + user_choice_index - bot_choice_index) % 3
        if winner == 0:
            result_embed.description = f"**That's a draw!**\nYou've chosen {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = 0xF59E42
        elif winner == 1:
            result_embed.description = f"**You won!**\nYou've chosen {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = 0x57F287
        else:
            result_embed.description = f"**You lost!**\nYou've chosen {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = 0xE02B2B

        await interaction.response.edit_message(
            embed=result_embed, content=None, view=None
        )


class RockPaperScissorsView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.add_item(RockPaperScissors())


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.YOUTUBE_REGEX = re.compile(r"(?m)http(?:s?):\/\/(?:www\.)?(?:music\.)?youtu(?:be\.com\/(watch\?v=|shorts/|embed/)|\.be\/|)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?")
        self.TIME_REGEX = re.compile(r"[?&]t=([0-9]+)")

    @commands.hybrid_command(name="randomfact", description="Get a random fact.")
    async def randomfact(self, context: Context) -> None:
        """
        Get a random fact.

        :param context: The hybrid command context.
        """
        # This will prevent your bot from stopping everything when doing a web request - see: https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-make-a-web-request
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://uselessfacts.jsph.pl/random.json?language=en"
            ) as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(description=data["text"], color=0xD75BF4)
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=0xE02B2B,
                    )
                await context.send(embed=embed)

    @commands.hybrid_command(
        name="coinflip", description="Make a coin flip, but give your bet before."
    )
    async def coinflip(self, context: Context) -> None:
        """
        Make a coin flip, but give your bet before.

        :param context: The hybrid command context.
        """
        buttons = Choice()
        embed = discord.Embed(description="What is your bet?", color=0xBEBEFE)
        message = await context.send(embed=embed, view=buttons)
        await buttons.wait()  # We wait for the user to click a button.
        result = random.choice(["heads", "tails"])
        if buttons.value == result:
            embed = discord.Embed(
                description=f"Correct! You guessed `{buttons.value}` and I flipped the coin to `{result}`.",
                color=0xBEBEFE,
            )
        else:
            embed = discord.Embed(
                description=f"Woops! You guessed `{buttons.value}` and I flipped the coin to `{result}`, better luck next time!",
                color=0xE02B2B,
            )
        await message.edit(embed=embed, view=None, content=None)

    @commands.hybrid_command(
        name="rps", description="Play the rock paper scissors game against the bot."
    )
    async def rock_paper_scissors(self, context: Context) -> None:
        """
        Play the rock paper scissors game against the bot.

        :param context: The hybrid command context.
        """
        view = RockPaperScissorsView()
        await context.send("Please make your choice", view=view)

    @commands.hybrid_command(
        name="media", description="Get a video from YouTube"
    )
    async def download_video(self, context: Context) -> None:
        if context.message.reference and context.message.reference.resolved.content:
            url = context.message.reference.resolved.content
        elif len(context.message.content) > len(context.prefix) + len(context.command.name):
            url = context.message.content.split(None, 1)[1]
        else:
            await context.reply("__You want me to turn the wind down?__")
            return
        #Requests yt_dlp
        ydl = YoutubeDL({"noplaylist": True})
        
        rege = self.YOUTUBE_REGEX.match(url)
        t = self.TIME_REGEX.search(url)
        
        temp = t.group(1) if t else 0

        if not rege:
            yt = ydl.extract_info(f"ytsearch:{url}", download=False)
            try:
                yt = yt["entries"][0]
            except IndexError:
                return
        else:
            yt = ydl.extract_info(rege.group(), download=False)

        for f in yt["formats"]:
            with contextlib.suppress(KeyError):
                if f["format_id"] == "140":
                    afsize = f["filesize"] or 0
                if f["ext"] == "mp4" and f["filesize"] is not None:
                    vfsize = f["filesize"] or 0
                    vformat = f["format_id"]
        msg = await context.reply("**Downloading...**")
        with tempfile.TemporaryDirectory() as tempdir:
            path = os.path.join(tempdir, "ytdl")
        ydl = YoutubeDL(
            {
                "outtmpl": f"{path}/%(title)s-%(id)s.%(ext)s",
                "format": f"{vformat}+140",
                "max_filesize": 8000000,
                "noplaylist": True,
            }
        )
        await msg.delete()
        try:
            yt = ydl.extract_info(url, download=True)
        except BaseException as e:
            await context.reply("<b>Error:</b> <i>{}</i>".format(e))
            return
        msg = await context.reply("**Uploading...**")
        filename = ydl.prepare_filename(yt)
        thumb = io.BytesIO((requests.get(yt["thumbnail"])).content)
        thumb.name = "thumbnail.png"
        views = 0
        likes = 0
        if yt.get("view_count"):
            views += yt["view_count"]
        if yt.get("like_count"):
            likes += yt["like_count"]
        await msg.delete()
        try:
            await context.send(
                ("**❯ Title:** __{}__\n**❯ Duration:** __{}__\n**❯ Channel:** __{}__\n**❯ Views:** __{}__\n**❯ Likes:** __{}__").format(
                    yt["title"],
                    datetime.timedelta(seconds=yt["duration"]) or 0,
                    yt["channel"] or None,
                    views,
                    likes
                    ),
                    file=discord.File(filename, filename=yt["title"] + ".mp4"),
                    reference=context.message.reference,
                )
        except discord.errors.HTTPException as e:
            await context.send("Erro ao enviar o vídeo: {errmsg}".format(errmsg=e))

async def setup(bot) -> None:
    await bot.add_cog(Fun(bot))
