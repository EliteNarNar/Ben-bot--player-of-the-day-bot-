###Ben-Bot.py



#############IMPORTS##############
import json
import os
import re
import asyncio
import configparser
from datetime import datetime
import discord
from discord import Embed 
import random
from dotenv import load_dotenv
from discord.ext import commands, tasks
#####################SETUP#########################
intents = discord.Intents.default() ## required to work with server members
intents.members = True

config = configparser.ConfigParser() ##Its nice to keep your alterable variables in a config file so users can edit the bot to their need without having to alter the code.
config.read('resources/config.ini') 
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')## We store the TOKEN in a .env file since it is secret and if anyone gains access to it they can control the bot (.env files are usually ignored in most code sharing services
bot = commands.Bot(command_prefix='.') ## the object bot represents our connection to discord


###############MAIN BOT PROGRAM######################
print("Ben-bot starting...")
botSettings = {} ### Will be a dictionary of server settings
print("Loading server settings")
with open('/resources/settings.json', 'r') as file: ## reading the setting.json file to get settings
  botSettings = json.load(file)
print("Server settings loaded")
#############SETTINGS#############
defaultSettings = {     # defines the default settings

"dadJoke": True,
"potd": False,
"potdHour": 17,
"potdRole": None, # None variables will have no value
"potdMinRole": None,
"potdAnnouncementChannel": None,
"potdCustomMessage": None
}





##############BOT EVENTS########################## 
@bot.event
async def on_ready(): ### This is what the bot will do when its ready
  
  print(
    f'{bot.user.name} has connected to Discord!'
    )
  
@bot.event
async def on_member_join(member):
    await member.create_dm() ## Sends a DM message to a user
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to {member.guild.name}!' #will send anyone who joins a dm
    )



@bot.event
async def on_message(message):
  sentence = message.content.lower()
  if len(sentence) > 0:
    if sentence[0] == ".":
      await bot.process_commands(message)
      return
    else:
      sentence = message.content.lower() # So that we can work with one case
      if message.content == "raise-exception":
        raise discord.DiscordException

      if message.author == bot.user: ## checks if the message is not the bot so it doesnt process its own message.
        return
      if message.content == "oh? so you're approaching me?":
        await message.channel.send("I can't beat the shit out of you without getting closer.")
        return
      
      
      thisList = sentence.split( ) ## This function splits sentences into list like so > ["this", "is", "a,", "sentence"]
      prankOp = False
      for x in range(len(thisList)):
        if thisList[x] == "i'm" or thisList[x] == "im": # this combs through the list looking for the words "Im" or "I'm" and identifies where it is in the sentence
          pointer = x
          prankOp = True
        elif thisList[x] == "i" and thisList[x+1] == "am": #this does the same thing but looks for the words "I" and "am" in consecutive positions
          pointer = x+1
          prankOp = True
      if not message.guild.id in botSettings:
        botSettings [message.guild.id] = {}
        for k, v in defaultSettings.items():
          botSettings[message.guild.id][k] = v
      if prankOp == True and botSettings[message.guild.id]["dadJoke"] == True:
        del thisList[0 : pointer+1]
        if len(thisList) > 5: # If there are more than 5 words after "I am" or "im" we just ignore the rest since the joke wouldnt work if there is a whole paragraph after I am
          pass
        else:
          themessage = " "
          for y in range(len(thisList)):
            
            if y != len(thisList)-1:
              themessage += thisList[y]+ " " ## Adding the words after "I am" or "im" into an empty string with the " " as a space.
            else:
              themessage += thisList[y]
    
          await message.channel.send("Hi{}, I'm Dad :)".format(themessage))
      
    await bot.process_commands(message)
#@bot.event
##async def on_error(event, *args, **kwargs):
##   with open('err.log', 'a') as f:
##      if event == 'on_message':
##          f.write(f'Unhandled message: {args[0]}\n')
##       else:
##           raise


print
#@bot.event
#async def on_command_error(ctx, error):
#  if isinstance(error, commands.CheckFaliure):
#    await ctx.send("You do not have the correct role for this command")
 #  if isinstance(error, commands.MissingRequiredArgument):
 #     if ctx.command.qualified_name == 'repeat':  # Check if the command being invoked is 'tag list'
  #        await ctx.send('``` Syntax: .repeat <message>```')

################BOT COMMANDS####################

@bot.command(name='repeat', help="Repeats a message!")
async def repeatCommand(ctx, *,message):
  boolean = False
  aList = message.split()
  for x in range(len(aList)):
    if aList[x] == "i'm" or aList[x] == "im" or aList[x] == "i": # this combs through the list looking for the words "Im" or "I'm" 
      boolean = True
  if boolean == True:
    await ctx.channel.send("Lmao we know")  
  if boolean == False:
    await ctx.channel.send(message)
    print(message)
###################################################################
@bot.command(name='ping', help=("Mainly a development feature that tests if the bot is running"))
async def pingCommand(ctx):
  await ctx.channel.send("Pong")
###################################################################
@bot.command(name='settings', help=("Bot settings"))
@commands.has_role('admin')
async def settings(ctx, setting=None, value=None):  
 
  if not ctx.guild.id in botSettings:
    botSettings[ctx.guild.id] = {}
    for k, v in defaultSettings.items():
      botSettings[ctx.guild.id][k] = v
 

  if setting is None:
    await ctx.channel.send("\nSettings:\nPlayer of the day: **{0}**\nDad joker: **{1}**\n".format(botSettings[ctx.guild.id]["dadJoke"], botSettings[ctx.guild.id]["potd"]))
    return

  if value is None:
    setting = setting.lower()
    print(botSettings)
    if setting == "dadjoke":
      if botSettings[ctx.guild.id]["dadJoke"]:
        await ctx.channel.send("Dad Joker is currently on")
      else:
        await ctx.channel.send("Dad Joker is currently off")
    elif setting == "potd":
      if botSettings[ctx.guild.id]["potd"]:
        await ctx.channel.send("Player of the day is currently on")
      else:
        await ctx.channel.send("Player of the day is currently off")     
    return
  
  if setting == "dadjoke":
    setting = setting.lower()
    value = value.lower()
    if value == "on":
      if botSettings[ctx.guild.id]["dadJoke"]:
        await ctx.channel.send("Dad Joker was already on.")
      else:
        botSettings[ctx.guild.id]["dadJoke"]= True
        await ctx.channel.send("Dad Joker is now **On**")

    if value == "off":
      if not botSettings[ctx.guild.id]["dadJoke"]:
        await ctx.channel.send("Dad joker was already off!")
      else:
        botSettings[ctx.guild.id]["dadJoke"] = False
        await ctx.channel.send("Dad Joker is now **Off**")
  if setting == "potd":
    if value == "on":
      if botSettings[ctx.guild.id]["potd"]:
        await ctx.channel.send("Player of the day was already on!")
      else:
        botSettings[ctx.guild.id]["potd"]= True
        await ctx.channel.send("Player of the day is now **On**")

    if value == "off":
      if not botSettings[ctx.guild.id]["potd"]:
        await ctx.channel.send("Player of the day was already off!")
      else:
        botSettings[ctx.guild.id]["potd"] = False
        await ctx.channel.send("Player of the day is now **Off**")

###########################################################################
@bot.command(name="potd", help=("Potd settings"))
@commands.has_role('admin')
async def potdSettings(ctx, setting=None, *,value=None):  
  if not ctx.guild.id in botSettings:
    botSettings[ctx.guild.id] = {}
    for k, v in defaultSettings.items():
      botSettings[ctx.guild.id][k] = v
      
  if ctx.guild.get_role(botSettings[ctx.guild.id]["potdMinRole"]) in ctx.guild.roles:
    mRole = ctx.guild.get_role(botSettings[ctx.guild.id]["potdMinRole"])
  else:
    mRole = None
  if ctx.guild.get_role(botSettings[ctx.guild.id]["potdRole"]) in ctx.guild.roles:
    wRole = ctx.guild.get_role(botSettings[ctx.guild.id]["potdRole"])
  else:
    wRole = None
  if ctx.guild.get_channel(botSettings[ctx.guild.id]["potdAnnouncementChannel"]) in ctx.guild.channels:
    aChannel = ctx.guild.get_channel(botSettings[ctx.guild.id]["potdAnnouncementChannel"])
  else:
    aChannel = None
  
  if setting is None:
    if botSettings[ctx.guild.id]["potdHour"] is None or wRole is None or mRole is None or aChannel is None:
      await ctx.channel.send("You still have some settings missing, to display potd settings set these settings. \n`.potd time <hour 0-24> \n.potd channel <channel> \n.potd minimum-role <role\n.potd winner-role <role>`")
      print(botSettings[ctx.guild.id])
      return
    else:
      await ctx.channel.send("__Current potd settings__: \n**Announcement time**: {0}:00\n**Announcement Channel**: {1}\n**Winner's role: {2}**\n**Minimum winner role: {3}**".format(\
      botSettings[ctx.guild.id]["potdHour"], aChannel.mention, wRole.mention, mRole.mention))
  elif value is None:
    if setting == "channel":
      if aChannel is not None:
        await ctx.channel.send("The current announcement channel is {} to change it do `.potd channel <channel>`".format(aChannel.mention))
      else:
        await ctx.channel.send("The announcement channel has not been set yet. To set it do `.potd channel <channel>`")
    elif setting == "minimum-role":
      if mRole is not None:
        await ctx.channel.send("The current minimum role to get player of the day is {} to change it do `.potd minimum-role <role>".format(mRole.mention))
      else:
        await ctx.channel.send("The minimum role to get player of the day has currently not been set. To set it do `.potd minimum-role <role>`")

    elif setting == "winner-role":
      if wRole is not None:
        await ctx.channel.send("The current winning role that is given to player of the day is {} to change it do `.potd winner-role <role>`".format(wRole.mention))
      else:
        await ctx.channel.send("The role that is given to the player of the day has not been set. To set it do `.potd winner-role <role>`")
    elif setting == "time":
      await ctx.channel.send("The current time the winners are announced is {}:00 to change it do `potd time <hour(0-23)>`".format(botSettings[ctx.guild.id]["potdHour"]))
    elif setting == "custom-message":
      if botSettings[ctx.guild.id]["potdCustomMessage"] is None:
        await ctx.channel.send("There is currently no custom announcement. To set one do `.potd custom-message <message>` you can use {winnername} to add the users name and {winnermention} to mention them")
      else:
       await ctx.channel.send("This is the current announcement message:\n{}\nTo change it do `.potd custom-message <message>`".format(botSettings[ctx.guild.id]["potdCustomMessage"]))
  else:
    setting = setting.lower()
    if setting == "channel":
      channelMatch = re.match("<#(\d+)>", value)
      if channelMatch:
        try:
          chanGuild = ctx.guild.get_channel(int(channelMatch.group(1)))
          botSettings[ctx.guild.id]["potdAnnouncementChannel"] = int(channelMatch.group(1))
          await ctx.channel.send("The channel has been successfully set to {}!".format(chanGuild.mention))
          aChannel = ctx.guild.get_channel(botSettings[ctx.guild.id]["potdAnnouncementChannel"])
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
          await ctx.channel.send("The minimum role has been successfully set to {}!".format(guildRole.mention))
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
          await ctx.channel.send("The role given to winners has been successfully set to {}!".format(guildRole.mention))
        except:
          await ctx.channel.send("That role doesn't exist in this server!")
      else:
        await ctx.channel.send("Please enter a valid channel.")

    elif setting == "time":
      try:
        value = int(value)
        if value >= 0 and value <= 23:
          botSettings[ctx.guild.id]["potdHour"] = value
          await ctx.channel.send("Succesfully set announcement time to {}:00!".format(value))
        else:
          await ctx.channel.send("Must be a number between 0 and 23!")
      except:
        await ctx.channel.send("Must be a number between 0 and 23!")
    elif setting =="custom-message":
      botSettings[ctx.guild.id]["potdCustomMessage"] = value
      await ctx.channel.send("The custom announcement has been set to:\n{}".format(value))
#################TASKS###################

@tasks.loop(seconds = 10)
async def backUp():
  print("Backing up....")
  with open('settings.json','w') as f:
    json.dump(botSettings, f) 
  print("Back up complete!")





@tasks.loop(hours = 1)
async def postPotd():
  print("activated")
  for guildId, guildSettings in botSettings.items():
    now = datetime.utcnow()
    if guildSettings["potdHour"] == now.hour:
      
      chooseThePotd(guildId)
@postPotd.before_loop
async def before_postPotd():
  await bot.wait_until_ready()
  now = datetime.utcnow()
  now = datetime(now.year, now.month, now.day, 16, 59, 50)
  future = datetime(now.year, now.month, now.day, targetHour, 0, 0, 0)
  if now.hour >= targetHour:
      future += timedelta(days = 1)
  print((future-now).seconds)
  await asyncio.sleep((future - now).seconds)

async def chooseThePotd(guildId):
  chosen = False
  guild = bot.get_guild(guildId)
  minRole = guild.get_role(botSettings[guildId]["potdMinRole"])
  annChannel = guild.get_channel(botSettings[guildId]["potdAnnouncementChannel"])
  winRole = bot.get_role(botSettings[guildId]["potdRole"])
  while not chosen:
    contender = random.choice(guild.members)
    if contender.top_role >= minRole:
      chosen = True
    else:
      continue
    await contender.add_roles(winRole)
    if botSettings[guildId]["potdCustomMessage"] is None:
      await annChannel.send("Todays player of the day goes to {0}".format(contender.mention))

    else:
      announcement = botSettings[guildId]["potdCustomMessage"]
      announcement.replace("{winnermention}",contender.mention)
      announcement.replace("{winnername}",contender.name)
      await annChanel.send(announcement)
    
  

#####Initialising the Bot###########
#if potd == True:
postPotd.start()
bot.run(TOKEN) ## runs the bot is designed to run forever so never put anything after it. ANYTHING (trust me i know)
