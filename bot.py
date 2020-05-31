import discord, os
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from functions import *
import requests, sys, re
import xml.etree.ElementTree as ET
import copy
import urllib

TOKEN = os.environ["DISCORD_LECTURE_TOKEN"]
bot = commands.Bot("!")
gi = GameInstance()

# What chan the lecture is taking place in
VOICE_CHAN_NAME = "General"
# Handel to the Lecture chan
LECTURE_CHAN = None
# Handel to the Lecture chan's voice
VOICE_CHAN = None
# A Member object that is the Lecturer
LECTURER = None
# An id list of people to not mute or unmute
# @TODO this should not be hardcoded
EXCLUDE_LIST = [279677842504286210]

# This finds the voice channel tht the lecture is taking place in
# It also gets the person who calls the bot function (I call a player as I mostly dev bots for games)
def setup(ctx):
    global LECTURE_CHAN
    global VOICE_CHAN
    if LECTURE_CHAN == None:
        LECTURE_CHAN = discord.utils.get(ctx.message.guild.channels, name=VOICE_CHAN_NAME, type=discord.ChannelType.voice)
    player = ctx.author     # Who called the function
    chan = ctx.channel      # The chan the called it in
    return [player,chan]


# If b is true, it mutes everyone else it unmutes everyone
# Does nothing to admins, bots, the lecturer or someone in the exclude list
async def muteAll(b):
    global LECTURER
    global LECTURE_CHAN
    global EXCLUDE_LIST
    for member in LECTURE_CHAN.members:
        if not (member.guild_permissions.administrator or member.bot or member.id == LECTURER or member.id in EXCLUDE_LIST):
            await member.edit(mute=b)


@bot.command()
@has_permissions(administrator=True)
async def mute_all(ctx):
    """
    Mutes everyone except admins and the lecturer (admin and lecture only)
    """
    global VOICE_CHAN
    player, chan = setup(ctx)

    if player.guild_permissions.administrator or player.bot or player.id == LECTURER:
        await muteAll(True)
    else:
        await chan.send("I'm affraid you can't do that")


@bot.command()
@has_permissions(administrator=True)
async def unmute_all(ctx):
    """
    Unmutes everyone except admins and the lecturer (admin only)
    """
    global VOICE_CHAN
    player, chan = setup(ctx)
    await muteAll(False)


##########################
### Hand rasing things ###
##########################

@bot.command(aliases=['oi'])
async def join(ctx):
    """
    Join the list of who wants to be called on!
    """

    player = ctx.author
    chan = ctx.channel
        
    ret = gi.addWaiting(player)
    if ret != 0:
        await chan.send(gi.lastError)
        return
    await chan.send(f"{player} wants to be called on!")


@bot.command(aliases=['rm','remove','rme'])
async def leave(ctx):
    """
    Leave the list of who wants to be called on!
    """

    player = ctx.author
    chan = ctx.channel

    ret = gi.removeWaiting(player)
    if ret != 0:
        await chan.send(gi.lastError)
        return
    await chan.send(f"{player} no longer wants to be called on!")


@bot.command()
async def pick(ctx):
    """
    Pick a random person who wants to be called on!
    """

    player = ctx.author
    chan = ctx.channel

    await chan.send(f"You are called on {gi.pickRandom().mention}")


@bot.command(aliases=['clearlist'])
@has_permissions(administrator=True)
async def clear(ctx):
    """
    Clear the list of who wants to be called on
    """
    
    player = ctx.author
    chan = ctx.channel

    gi.reset()
    await chan.send(f"Cleared!")
    

@bot.command(aliases=["showlist"])
async def list(ctx):
    """
    Show who wants to be called on!
    """

    player = ctx.author
    chan = ctx.channel

    ret = ""

    async for message in chan.history(limit=10):
        if message.author.id == player.id:
            await message.delete()
            break
    
    if gi.waiting == []:
        await chan.send("Currently no one is waiting to be called on")
    else:
        for p in gi.waiting:
            ret += str(p) + "\n"
        await chan.send(ret)


@bot.command(aliases=['p'])
async def ping(ctx):
    """
    Ping! and get lecutre state
    """
    player = ctx.author
    chan = ctx.channel
    await chan.send(f"pong Lecutre:{LECTURER!=None}")

@bot.event
# If someone leaves the voice chan (After lecture has started) we unmute them
# If some one comes into the lecture voice chan (After a lecture has started) we mute them
# @TODO this will not unmute some one if they dissconnect (How do we do that?)
async def on_voice_state_update(member, before, after):
    if LECTURER != None:
        if str(before.channel) == VOICE_CHAN_NAME and str(after.channel) != VOICE_CHAN_NAME:
            if not (member.guild_permissions.administrator or member.bot or member.id == LECTURER or member.id in EXCLUDE_LIST):
                await member.edit(mute=False)
        if str(before.channel) != VOICE_CHAN_NAME and str(after.channel) == VOICE_CHAN_NAME:
            if not (member.guild_permissions.administrator or member.bot or member.id == LECTURER or member.id in EXCLUDE_LIST):
                await member.edit(mute=True)
            
@bot.event
async def on_ready():
    print("Time to Lecture!")
    print("Logged in as: {}".format(bot.user.name))

@bot.event
async def on_error(event, *args, **kwargs):
    print("ERROR!")
    print("Error from:", event)
    print("Error context:", args, kwargs)

    from sys import exc_info

    exc_type, value, traceback = exc_info()
    print("Exception type:", exc_type)
    print("Exception value:", value)
    print("Exception traceback object:", traceback)

    
bot.run(TOKEN)
