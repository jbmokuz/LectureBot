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
EXCLUDE_LIST = []

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
# Starts a lecute.
# Basically gives some one (The Lecturer) the abilty to unmute some one and mutes everyone
async def start_lecture(ctx, lecturer=None):
    """
    Starts a lecture (admin only)
    Args:
        lecturer: an @ of the lecture ex: !startLecture @moku
    """
    global LECTURER
    player, chan = setup(ctx)
    try:
        LECTURER = int(lecturer[3:-1])
    except:
        await chan.send("Not a valid lecturer, please @ the lecturer in the argument")
        return
    await muteAll(True)

@bot.command()
@has_permissions(administrator=True)
# Gets unmutes everyone and gets rid of the Lecturer
async def end_lecture(ctx):
    """
    Ends a lecture (admin only)
    """
    global LECTURER
    player, chan = setup(ctx)
    if LECTURER == None:
        await chan.send("Lecture has not been started yet!")
        return
    await muteAll(False)

@bot.command()
# @TODO, should this add some one to a list or something?
async def hand(ctx):
    """
    Raise your hand?
    """
    global VOICE_CHAN
    player, chan = setup(ctx)
    await chan.send(f"{str(player)} raised hand!")

@bot.command()
# This allows a Lecturer to unmute some one
async def call(ctx, student):
    """
    Call on some one to talk (admin and lecturer only)
    Args:
        student: an @ of the member ex: !call @moku
    """    
    global VOICE_CHAN
    player, chan = setup(ctx)    
    if player.guild_permissions.administrator or player.bot or player.id == LECTURER:
        try:
            student = int(student[3:-1])
        except:
            await chan.send("Not a valid lecturer, please @ the lecturer in the argument")
            return
        for member in LECTURE_CHAN.members:
            if member.id == student and  member.id not in EXCLUDE_LIST:
                await member.edit(mute=False)
    else:
        await chan.send("I'm affraid you can't do that")
            
@bot.command()
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


@bot.command()
# Just to get an id to add someone to the EXCLUDE_LIST
async def get_ids(ctx):
    """
    Just for testing
    """
    for i in ctx.message.guild.members:
        print(i.id,i)


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
