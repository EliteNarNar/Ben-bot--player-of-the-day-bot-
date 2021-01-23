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
    "potdHour": 16,
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
    await member.create_dm()  # Sends a DM message to a user
    await member.dm_channel.send(
        # will send anyone who joins a dm
        f"Hi {member.name}, welcome to {member.guild.name}!"
    )


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
            if message.author == bot.user:
                return
            if message.content == "oh? so you're approaching me?":
                await message.channel.send(
                    "I can't beat the shit out of you without getting closer."
                )
                return

            # This function splits sentences into list like so > ["this", "is", "a,", "sentence"]
            thisList = sentence.split()
            prankOp = False
            for x in range(len(thisList)):
                # this combs through the list looking for the words "Im" or "I'm" and identifies where it is in the sentence
                if thisList[x] == "i'm" or thisList[x] == "im":
                    pointer = x
                    prankOp = True
                # this does the same thing but looks for the words "I" and "am" in consecutive positions
                elif thisList[x] == "i" and thisList[x + 1] == "am":
                    pointer = x + 1
                    prankOp = True
            if not message.guild.id in botSettings:
                botSettings[str(message.guild.id)] = {}
                for k, v in defaultSettings.items():
                    botSettings[str(message.guild.id)][k] = v
            if prankOp == True and botSettings[message.guild.id]["dadJoke"] == True:
                del thisList[0 : pointer + 1]
                if (
                    len(thisList) > 5
                ):  # If there are more than 5 words after "I am" or "im" we just ignore the rest since the joke wouldnt work if there is a whole paragraph after I am
                    pass
                else:
                    themessage = " "
                    for y in range(len(thisList)):

                        if y != len(thisList) - 1:
                            # Adding the words after "I am" or "im" into an empty string with the " " as a space.
                            themessage += thisList[y] + " "
                        else:
                            themessage += thisList[y]

                    await message.channel.send("Hi{}, I'm Dad :)".format(themessage))

        await bot.process_commands(message)


# @bot.event
##async def on_error(event, *args, **kwargs):
##   with open('err.log', 'a') as f:
##      if event == 'on_message':
##          f.write(f'Unhandled message: {args[0]}\n')
##       else:
##           raise


# @bot.event
# async def on_command_error(ctx, error):
#  if isinstance(error, commands.CheckFaliure):
#    await ctx.send("You do not have the correct role for this command")
#  if isinstance(error, commands.MissingRequiredArgument):
#     if ctx.command.qualified_name == 'repeat':  # Check if the command being invoked is 'tag list'
#        await ctx.send('``` Syntax: .repeat <message>```')

################BOT COMMANDS####################


@bot.command(name="repeat", help="Repeats a message!")
async def repeatCommand(ctx, *, message):
    boolean = False
    aList = message.split()
    for x in range(len(aList)):
        # this combs through the list looking for the words "Im" or "I'm"
        if aList[x] == "i'm" or aList[x] == "im" or aList[x] == "i":
            boolean = True
    if boolean == True:
        await ctx.channel.send("Lmao we know")
    if boolean == False:
        await ctx.channel.send(message)
        print(message)


###################################################################


@bot.command(
    name="ping", help=("Mainly a development feature that tests if the bot is running")
)
async def pingCommand(ctx):
    await ctx.channel.send("Pong")


###################################################################


@bot.command(name="settings", help=("Bot settings"))
@commands.has_role("admin")
async def settings(ctx, setting=None, value=None):

    if not str(ctx.guild.id) in botSettings:
        botSettings[str(ctx.guild.id)] = {}
        for k, v in defaultSettings.items():
            botSettings[str(ctx.guild.id)][k] = v

    if setting is None:
        if botSettings[str(ctx.guild.id)]["potd"]:
            option = "On"
        else:
            option = "Off"
        if botSettings[str(ctx.guild.id)]["dadJoke"]:
            otheroption = "On"
        else:
            otheroption = "Off"
        embed = discord.Embed(
            title="Bot settings",
            description="These are the settings currently set for this server",
            colour=0x339931,
        )
        embed.add_field(
            name="Player of the day",
            value="**{}**".format(option),
            inline=False,
        )
        embed.add_field(
            name="Dad joker",
            value="**{}**".format(otheroption),
            inline=False,
        )
        await ctx.channel.send(embed=embed)

        return

    if value is None:
        setting = setting.lower()
        print(botSettings)
        if setting == "dadjoke":
            if botSettings[str(ctx.guild.id)]["dadJoke"]:
                await ctx.channel.send("Dad Joker is currently on")
            else:
                await ctx.channel.send("Dad Joker is currently off")
        elif setting == "potd":
            if botSettings[str(ctx.guild.id)]["potd"]:
                await ctx.channel.send("Player of the day is currently on")
            else:
                await ctx.channel.send("Player of the day is currently off")
        return

    if setting == "dadjoke":
        setting = setting.lower()
        value = value.lower()
        if value == "on":
            if botSettings[str(ctx.guild.id)]["dadJoke"]:
                await ctx.channel.send("Dad Joker was already on.")
            else:
                botSettings[str(ctx.guild.id)]["dadJoke"] = True
                await ctx.channel.send("Dad Joker is now **On**")

        if value == "off":
            if not botSettings[str(ctx.guild.id)]["dadJoke"]:
                await ctx.channel.send("Dad joker was already off!")
            else:
                botSettings[str(ctx.guild.id)]["dadJoke"] = False
                await ctx.channel.send("Dad Joker is now **Off**")
    if setting == "potd":
        if value == "on":
            if botSettings[str(ctx.guild.id)]["potd"]:
                await ctx.channel.send("Player of the day was already on!")
            else:
                if (
                    botSettings[str(ctx.guild.id)]["potdAnnouncementChannel"] is None
                    or botSettings[str(ctx.guild.id)]["potdMinRole"] is None
                    or botSettings[str(ctx.guild.id)]["potdRole"] is None
                ):

                    await ctx.channel.send(
                        "You still havent setup all your settings! To set up potd settings do `.potd`"
                    )
                    return
                botSettings[str(ctx.guild.id)]["potd"] = True
                await ctx.channel.send("Player of the day is now **On**")

        if value == "off":
            if not botSettings[str(ctx.guild.id)]["potd"]:
                await ctx.channel.send("Player of the day was already off!")
            else:
                botSettings[str(ctx.guild.id)]["potd"] = False
                await ctx.channel.send("Player of the day is now **Off**")


###########################################################################


@bot.command(name="potd", help=("Potd settings"))
@commands.has_role("admin")
async def potdSettings(ctx, setting=None, *, value=None):
    if not str(ctx.guild.id) in botSettings:
        botSettings[str(ctx.guild.id)] = {}
        for k, v in defaultSettings.items():
            botSettings[str(ctx.guild.id)][k] = v

    if (
        ctx.guild.get_role(botSettings[str(ctx.guild.id)]["potdMinRole"])
        in ctx.guild.roles
    ):
        mRole = ctx.guild.get_role(botSettings[str(ctx.guild.id)]["potdMinRole"])
    else:
        mRole = None
    if (
        ctx.guild.get_role(botSettings[str(ctx.guild.id)]["potdRole"])
        in ctx.guild.roles
    ):
        wRole = ctx.guild.get_role(botSettings[str(ctx.guild.id)]["potdRole"])
    else:
        wRole = None
    if (
        ctx.guild.get_channel(botSettings[str(ctx.guild.id)]["potdAnnouncementChannel"])
        in ctx.guild.channels
    ):
        aChannel = ctx.guild.get_channel(
            botSettings[str(ctx.guild.id)]["potdAnnouncementChannel"]
        )
    else:
        aChannel = None

    if setting is None:
        if (
            botSettings[str(ctx.guild.id)]["potdHour"] is None
            or wRole is None
            or mRole is None
            or aChannel is None
        ):

            embed = discord.Embed(
                title="Bot settings",
                description="To continue please set the following settings",
                colour=0x339931,
            )

            if wRole is None:
                embed.add_field(
                    name="Announcement channel",
                    value="`.potd channel <channel>`",
                    inline=False,
                )
            if mRole is None:
                embed.add_field(
                    name="Minimum role",
                    value="`.potd minimum-role <role>`",
                    inline=False,
                )

            if wRole is None:
                embed.add_field(
                    name="Winner role",
                    value="`.potd winner-role <role>`",
                    inline=False,
                )
            await ctx.channel.send(embed=embed)

            print(botSettings[str(ctx.guild.id)])
            return
        else:
            embed = discord.Embed(
                title="Player of the day settings",
                description="These are the settings currently set for this server",
                colour=0x339931,
            )
            embed.add_field(
                name="Announcement time",
                value="The announcement time is set to {}:00".format(
                    botSettings[str(ctx.guild.id)]["potdHour"]
                ),
                inline=False,
            )
            embed.add_field(
                name="Announcement channel",
                value="The announcement channel is {}".format(aChannel.mention),
                inline=False,
            )
            embed.add_field(
                name="Winner's role",
                value="The winner is given {}".format(wRole.mention),
                inline=False,
            )
            embed.add_field(
                name="Minimum role",
                value="The minimum role to win is {}".format(mRole.mention),
                inline=False,
            )
            if botSettings[str(ctx.guild.id)]["potdCustomMessage"] is not None:
                cm = "None"
            else:
                cm = botSettings[str(ctx.guild.id)]["potdCustomMessage"]
            embed.add_field(
                name="Custom message",
                value=cm,
                inline=False,
            )
            await ctx.channel.send(embed=embed)

            print(botSettings[str(ctx.guild.id)])
    elif value is None:
        if setting == "channel":
            if aChannel is not None:
                await ctx.channel.send(
                    "The current announcement channel is {} to change it do `.potd channel <channel>`".format(
                        aChannel.mention
                    )
                )
            else:
                await ctx.channel.send(
                    "The announcement channel has not been set yet. To set it do `.potd channel <channel>`"
                )
        elif setting == "minimum-role":
            if mRole is not None:
                await ctx.channel.send(
                    "The current minimum role to get player of the day is {} to change it do `.potd minimum-role <role>".format(
                        mRole.mention
                    )
                )
            else:
                await ctx.channel.send(
                    "The minimum role to get player of the day has currently not been set. To set it do `.potd minimum-role <role>`"
                )

        elif setting == "winner-role":
            if wRole is not None:
                await ctx.channel.send(
                    "The current winning role that is given to player of the day is {} to change it do `.potd winner-role <role>`".format(
                        wRole.mention
                    )
                )
            else:
                await ctx.channel.send(
                    "The role that is given to the player of the day has not been set. To set it do `.potd winner-role <role>`"
                )
        elif setting == "time":
            await ctx.channel.send(
                "The current time the winners are announced is {}:00 to change it do `potd time <hour(0-23)>`".format(
                    botSettings[str(ctx.guild.id)]["potdHour"]
                )
            )
        elif setting == "custom-message":
            if botSettings[str(ctx.guild.id)]["potdCustomMessage"] is None:
                await ctx.channel.send(
                    "There is currently no custom announcement. To set one do `.potd custom-message <message>` you can use {winnername} to add the users name and {winnermention} to mention them"
                )
            else:
                await ctx.channel.send(
                    "This is the current announcement message:\n{}\nTo change it do `.potd custom-message <message>`".format(
                        botSettings[str(ctx.guild.id)]["potdCustomMessage"]
                    )
                )
    else:
        setting = setting.lower()
        if setting == "channel":
            channelMatch = re.match("<#(\d+)>", value)
            if channelMatch:
                try:
                    chanGuild = ctx.guild.get_channel(int(channelMatch.group(1)))
                    botSettings[str(ctx.guild.id)]["potdAnnouncementChannel"] = int(
                        channelMatch.group(1)
                    )
                    await ctx.channel.send(
                        "The channel has been successfully set to {}!".format(
                            chanGuild.mention
                        )
                    )
                    aChannel = ctx.guild.get_channel(
                        botSettings[str(ctx.guild.id)]["potdAnnouncementChannel"]
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
                    botSettings[str(ctx.guild.id)]["potdMinRole"] = int(
                        roleMatch.group(1)
                    )
                    await ctx.channel.send(
                        "The minimum role has been successfully set to {}!".format(
                            guildRole.mention
                        )
                    )
                    mRole = ctx.guild.get_role(
                        botSettings[str(ctx.guild.id)]["potdMinRole"]
                    )
                except:
                    await ctx.channel.send("That role doesn't exist in this server!")
            else:
                await ctx.channel.send("Please enter a valid role.")

        elif setting == "winner-role":
            roleMatch = re.match("<@&(\d+)>", value)
            if roleMatch:
                try:
                    guildRole = ctx.guild.get_role(int(roleMatch.group(1)))
                    botSettings[str(ctx.guild.id)]["potdRole"] = int(roleMatch.group(1))
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
                    botSettings[str(ctx.guild.id)]["potdHour"] = value
                    await ctx.channel.send(
                        "Succesfully set announcement time to {}:00!".format(value)
                    )
                else:
                    await ctx.channel.send("Must be a number between 0 and 23!")
            except:
                await ctx.channel.send("Must be a number between 0 and 23!")
        elif setting == "custom-message":
            botSettings[str(ctx.guild.id)]["potdCustomMessage"] = value
            await ctx.channel.send(
                "The custom announcement has been set to:\n{}".format(value)
            )


#################TASKS###################


@tasks.loop(seconds=5)
async def backUp():

    with open("settings.json", "w") as f:
        json.dump(botSettings, f)
    now = datetime.utcnow()
    future = datetime(now.year, now.month, now.day, now.hour + 1, 0, 0, 0)
    secondsLeft = (future - now).seconds

    pass


@tasks.loop(hours=1)
async def postPotd():
    await asyncio.sleep(2)
    now = datetime.utcnow()
    print("checking if time to activate")
    for guildId, guildSettings in botSettings.items():
        if guildSettings["potdHour"] == now.hour:
            print("Choosing player of the day")

            await chooseThePotd(guildId)


@postPotd.before_loop
async def before_postPotd():
    await bot.wait_until_ready()
    now = datetime.utcnow()
    future = datetime(now.year, now.month, now.day, now.hour + 1, 0, 0, 0)
    print("Sleeping for {} seconds".format((future - now).seconds))
    await asyncio.sleep((future - now).seconds)


async def chooseThePotd(guildId):
    if not botSettings[str(guildId)]["potd"]:
        return

    else:

        chosen = False
        guild = bot.get_guild(int(guildId))
        minRole = guild.get_role(botSettings[str(guildId)]["potdMinRole"])
        annChannel = guild.get_channel(
            botSettings[str(guildId)]["potdAnnouncementChannel"]
        )
        winRole = guild.get_role(botSettings[str(guildId)]["potdRole"])
        lastWinner = guild.get_member(botSettings[str(guildId)]["lastPotd"])
        while not chosen:
            contender = random.choice(guild.members)
            print("Contender is '{0}''".format(contender.name))
            if contender.top_role >= minRole and not contender.bot:
                if contender.id != botSettings[str(guildId)]["lastPotd"]:
                    chosen = True
                    print(contender.name, " has been selected")
                    break
                else:
                    print(
                        "Person was player of the day last time! Choosing someone else"
                    )
                    continue
            else:
                print("Person is either a bot or not high enough ranked")
                continue

        await contender.add_roles(winRole)
        botSettings[str(guildId)]["lastPotd"] = contender.id
        if lastWinner is not None:
            await lastWinner.remove_roles(winRole)
        if botSettings[str(guildId)]["potdCustomMessage"] is None:
            embed = discord.Embed(
                title="Player of the day",
                description="Today's player of the day goes to {0}".format(
                    contender.mention
                ),
                colour=0x339931,
            )
            await annChannel.send(embed=embed)

        else:

            announcement = botSettings[guildId]["potdCustomMessage"]
            announcement = announcement.replace("{winnermention}", contender.mention)
            announcement = announcement.replace("{winnername}", contender.name)
            embed = discord.Embed(
                title="Player of the day",
                description=announcement,
                colour=0x339931,
            )
            await annChannel.send(embed=embed)


#####Initialising the Bot###########

backUp.start()
postPotd.start()
# keep_alive()
# runs the bot is designed to run forever so never put anything after it. ANYTHING (trust me i know)
bot.run(TOKEN)
