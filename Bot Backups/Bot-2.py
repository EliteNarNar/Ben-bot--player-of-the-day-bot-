###Ben-Bot.py


#############IMPORTS##############
import json
import os
import re
import asyncio
import configparser
from datetime import datetime
from datetime import timedelta
import discord
from discord import Embed
import random
from dotenv import load_dotenv
from discord.ext import commands, tasks

#####################SETUP#########################
intents = discord.Intents.default()  # required to work with server members
intents.members = True

# Its nice to keep your alterable variables in a config file so users can edit the bot to their need without having to alter the code.
config = configparser.ConfigParser()
config.read("resources/config.ini")
load_dotenv()
# We store the TOKEN in a .env file since it is secret and if anyone gains access to it they can control the bot (.env files are usually ignored in most code sharing services
TOKEN = os.getenv("DISCORD_TOKEN")
# the object bot represents our connection to discord
bot = commands.Bot(command_prefix=".", intents=intents)


###############MAIN BOT PROGRAM######################
print("Ben-bot starting...")
botSettings = {}  # Will be a dictionary of server settings
print("Loading server settings")
# reading the setting.json file to get settings
with open("settings.json", "r") as file:
    botSettings = json.load(file)


print("Server settings loaded")
#############SETTINGS#############
defaultSettings = {  # defines the default settings
    "dadJoke": True,
    "potd": False,
    "potdHour": 17,
    "potdRole": None,  # None variables will have no value
    "potdMinRole": None,
    "potdAnnouncementChannel": None,
    "potdCustomMessage": None,
    "lastPotd": None,
}


##############BOT EVENTS##########################


@bot.event
async def on_ready():  # This is what the bot will do when its ready

    print(f"{bot.user.name} has connected to Discord!")


@bot.event
async def on_member_join(member):
    await member.dm_channel.send(f"Hi {member.name}, welcome to {member.guild.name}!")


@bot.event
async def on_message(message):
    sentence = message.content.lower()
    if len(sentence) > 0:
        if sentence[0] == ".":
            await bot.process_commands(message)
            return
        else:
            sentence = message.content.lower()  # So that we can work with one case
            if message.content == "raise-exception":
                raise discord.DiscordException

            # checks if the message is not the bot so it doesnt process its own message.
            if message.author.bot:
                return

            if message.content == "oh? so you're approaching me?":
                await message.channel.send(
                    "I can't beat the shit out of you without getting closer."
                )
                return

            # This function splits sentences into list like so > ["this", "is", "a,", "sentence"]
            words = sentence.split()
            prankOp = False
            for x in range(len(words)):
                # this combs through the list looking for the words "Im" or "I'm" and identifies where it is in the sentence
                if words[x] == "i'm" or words[x] == "im":
                    pointer = x
                    prankOp = True
                    break
                elif words[x] == "i" and words[x + 1] == "am":
                    # this does the same thing but looks for the words "I" and "am" in consecutive positions
                    pointer = x + 1
                    prankOp = True
                    break

            if not message.guild.id in botSettings:
                botSettings[message.guild.id] = {}
                for k, v in defaultSettings.items():
                    botSettings[message.guild.id][k] = v

            if prankOp and botSettings[message.guild.id]["dadJoke"]:
                del words[0 : pointer + 1]

                # If there are more than 5 words after "I am" or "im" we just ignore the rest since the joke wouldnt work if there is a whole paragraph after I am
                if len(words) <= 5:
                    reply = " "
                    for y in range(len(words)):
                        if y != len(words) - 1:
                            # Adding the words after "I am" or "im" into an empty string with the " " as a space.
                            reply += words[y] + " "
                        else:
                            reply += words[y]

                    await message.channel.send("Hi{}, I'm Dad :)".format(reply))


@bot.command()
async def repeat(ctx, *, message):
    """Repeats a message"""

    boolean = False
    words = message.split()
    for word in words:
        # this combs through the list looking for the words "Im" or "I'm"
        if word == "i'm" or word == "im" or word == "i":
            await ctx.channel.send("Lmao we know")
            return

    await ctx.channel.send(message)
    print(message)


@bot.command()
async def ping(ctx):
    """"Mainly a development feature that tests if the bot is running"""
    await ctx.channel.send("Pong")


@bot.command()
@commands.has_role("admin")
async def settings(ctx, setting=None, value=None):
    if not ctx.guild.id in botSettings:
        botSettings[ctx.guild.id] = {}
        for k, v in defaultSettings.items():
            botSettings[ctx.guild.id][k] = v

    if setting is None:
        await ctx.channel.send(
            "\nSettings:\nPlayer of the day: **{0}**\nDad joker: **{1}**\n".format(
                botSettings[ctx.guild.id]["dadJoke"], botSettings[ctx.guild.id]["potd"]
            )
        )
        return

    if not setting in defaultSettings:
        return

    if value is None:
        print(botSettings)
        onOrOff = "on" if botSettings[ctx.guild.id][setting] else "off"

        await ctx.channel.send(f"{setting} is currently {onOrOff}")
        return

    value = value.lower()
    newSetting = True if value == "on" else False

    if botSettings[ctx.guild.id][setting] == newSetting:
        await ctx.channel.send(f"{setting} was already {value}")
        return
    else:
        if setting.lower() == "potd":
            if (
                botSettings[ctx.guild.id]["potdAnnouncementChannel"] is None
                or botSettings[ctx.guild.id]["potdMinRole"] is None
                or botSettings[ctx.guild.id]["potdRole"] is None
            ):
                await ctx.channel.send(
                    "You still havent setup all your settings! To set up potd settings do `.potd`"
                )
                return

        botSettings[ctx.guild.id][setting] = newSetting
        await ctx.channel.send(f"{setting} is now {value}")


@bot.command()
@commands.has_role("admin")
async def potd(ctx, setting=None, *, value=None):
    if not ctx.guild.id in botSettings:
        botSettings[ctx.guild.id] = {}
        for k, v in defaultSettings.items():
            botSettings[ctx.guild.id][k] = v

    minRole = ctx.guild.get_role(botSettings[ctx.guild.id]["potdMinRole"])
    winnerRole = ctx.guild.get_role(botSettings[ctx.guild.id]["potdRole"])
    announceChannel = ctx.guild.get_channel(
        botSettings[ctx.guild.id]["potdAnnouncementChannel"]
    )
    announceHour = botSettings[ctx.guild.id]["potdHour"]

    if setting is None:
        print(botSettings[ctx.guild.id])
        await ctx.channel.send(
            "__Current potd settings__: \n**Announcement time**: {0}:00\n**Announcement Channel**: {1}\n**Winner's role: {2}**\n**Minimum winner role: {3}**".format(
                botSettings[ctx.guild.id]["potdHour"],
                announceChannel.mention,
                winnerRole.mention,
                minRole.mention,
            )
        )

    if (
        minRole is None
        or winnerRole is None
        or announceChannel is None
        or announceChannel is None
    ):
        print(botSettings[ctx.guild.id])
        await ctx.channel.send(
            "You still have some settings missing, to set these use: \n`.potd time <hour 0-24> \n.potd channel <channel> \n.potd minimum-role <role\n.potd winner-role <role>`"
        )

        if setting is None:
            return

    setting = setting.lower()
    if not setting in defaultSettings:
        return

    if value is None:
        if botSettings[ctx.guild.id][setting] is None:
            if setting == "custom-message":
                await ctx.channel.send(
                    "There is currently no custom announcement. To set one do `.potd custom-message <message>` you can use \{winnername\} to add the users name and \{winnermention\} to mention them"
                )
            else:
                await ctx.channel.send(
                    "The {} has not been set yet - to set it do `.potd {} <value>`".format(
                        setting
                    )
                )
        else:
            currentValue = botSettings[ctx.guild.id][setting]
            if (
                setting is "channel"
                or setting is "minimum-role"
                or setting is "winner-role"
            ):
                currentValue = currentValue.mention
            await ctx.channel.send(
                "The current {0} is {1} - to change it do `.potd {0} <value>`".format(
                    setting, currentValue
                )
            )
        return
    else:
        if setting == "channel":
            channelMatch = re.match("<#(\d+)>", value)
            if channelMatch:
                try:
                    chanGuild = ctx.guild.get_channel(int(channelMatch.group(1)))
                    botSettings[ctx.guild.id]["potdAnnouncementChannel"] = int(
                        channelMatch.group(1)
                    )
                    await ctx.channel.send(
                        "The channel has been successfully set to {}!".format(
                            chanGuild.mention
                        )
                    )
                    aChannel = ctx.guild.get_channel(
                        botSettings[ctx.guild.id]["potdAnnouncementChannel"]
                    )
                except:
                    await ctx.channel.send("That channel doesn't exist in this server!")

            else:
                await ctx.channel.send("Please enter a valid channel.")

        elif setting == "minimum-role":
            roleMatch = re.match("<@&(\d+)>", value)
            if roleMatch:
                try:
                    guildRole = ctx.guild.get_role(int(roleMatch.group(1)))
                    botSettings[ctx.guild.id]["potdMinRole"] = int(roleMatch.group(1))
                    await ctx.channel.send(
                        "The minimum role has been successfully set to {}!".format(
                            guildRole.mention
                        )
                    )
                    mRole = ctx.guild.get_role(botSettings[ctx.guild.id]["potdMinRole"])
                except:
                    await ctx.channel.send("That role doesn't exist in this server!")
            else:
                await ctx.channel.send("Please enter a valid role.")

        elif setting == "winner-role":
            roleMatch = re.match("<@&(\d+)>", value)
            if roleMatch:
                try:
                    guildRole = ctx.guild.get_role(int(roleMatch.group(1)))
                    botSettings[ctx.guild.id]["potdRole"] = int(roleMatch.group(1))
                    await ctx.channel.send(
                        "The role given to winners has been successfully set to {}!".format(
                            guildRole.mention
                        )
                    )
                except:
                    await ctx.channel.send("That role doesn't exist in this server!")
            else:
                await ctx.channel.send("Please enter a valid channel.")

        elif setting == "time":
            try:
                value = int(value)
                if value >= 0 and value <= 23:
                    botSettings[ctx.guild.id]["potdHour"] = value
                    await ctx.channel.send(
                        "Succesfully set announcement time to {}:00!".format(value)
                    )
                else:
                    await ctx.channel.send("Must be a number between 0 and 23!")
            except:
                await ctx.channel.send("Must be a number between 0 and 23!")
        elif setting == "custom-message":
            botSettings[ctx.guild.id]["potdCustomMessage"] = value
            await ctx.channel.send(
                "The custom announcement has been set to:\n{}".format(value)
            )


#################TASKS###################
@tasks.loop(seconds=20)
async def backUp():

    with open("settings.json", "w") as f:
        json.dump(botSettings, f)

    pass


@tasks.loop(hours=1)
async def postPotd():
    for guildId, guildSettings in botSettings.items():
        now = datetime.utcnow()
        now = datetime(now.year, now.month, now.day, 17, 0, 0, 0)
        if guildSettings["potdHour"] == now.hour:
            print("Choosing player of the day")

            await chooseThePotd(guildId)


@postPotd.before_loop
async def before_postPotd():
    await bot.wait_until_ready()
    now = datetime.utcnow()
    now = datetime(now.year, now.month, now.day, 16, 59, 15, 0)
    future = datetime(now.year, now.month, now.day, 17, 0, 0, 0)
    # if now.minute >= 0:
    # future += timedelta(hours = 1)
    await asyncio.sleep((future - now).seconds)


async def chooseThePotd(guildId):
    # if not botSettings[guildId]["potd"]:
    #   return

    # else:
    chosen = False
    guild = bot.get_guild(guildId)
    minRole = guild.get_role(botSettings[guildId]["potdMinRole"])
    annChannel = guild.get_channel(botSettings[guildId]["potdAnnouncementChannel"])
    winRole = guild.get_role(botSettings[guildId]["potdRole"])
    lastWinner = guild.get_member(botSettings[guildId]["lastPotd"])
    print(guild.name)
    print(guild.members)
    while not chosen:
        contender = random.choice(guild.members)
        if contender.top_role >= minRole and not contender.bot:
            print("is not a bot")
            if contender.id != botSettings[guildId]["lastPotd"]:
                chosen = True
                break
        else:
            continue

    await contender.add_roles(winRole)
    if lastWinner is None:
        pass
    else:
        lastWinner.remove_roles(winRole)
        if botSettings[guildId]["potdCustomMessage"] is None:
            await annChannel.send(
                "Todays player of the day goes to {0}".format(contender.mention)
            )

        else:
            announcement = botSettings[guildId]["potdCustomMessage"]
            announcement.replace("{winnermention}", contender.mention)
            announcement.replace("{winnername}", contender.name)
            await annChannel.send(announcement)


#####Initialising the Bot###########
backUp.start()
postPotd.start()

# runs the bot is designed to run forever so never put anything after it. ANYTHING (trust me i know)
bot.run(TOKEN)
