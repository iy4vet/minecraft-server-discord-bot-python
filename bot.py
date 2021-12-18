import configparser
import discord
import os
import threading
import time
from mcrcon import MCRcon

running = False
mcHost = discord.Client()
config = configparser.ConfigParser()
config.read('env.b')
token = config['BOT']['BOT_TOKEN']
rcon_ip = config['RCON']['RCON_IP']
rcon_pass = config['RCON']['RCON_PASS']

def server():
    global running
    running = True
    os.system(r"run.bat")
    running = False
    time.sleep(1)
    print("Server stopped. ")

def rcon_stop():
    mcr = MCRcon(rcon_ip, rcon_pass)
    mcr.connect()
    mcr.command("execute unless entity @a run stop")
    mcr.disconnect()

def shutdown():
    time.sleep(120)
    print("Auto shutdown started. ")
    while running:
        print("Attempting auto shutdown... ")
        rcon_stop()
        time.sleep(180)

@mcHost.event
async def on_ready():
    print("Logged in as {0.user}".format(mcHost))
    await mcHost.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="if someone wants to play"))

@mcHost.event
async def on_message(message):
    msg = message.content
    if msg.startswith("$start"):
        if running:
            await message.channel.send("Server is already running! ")
        else:
            await message.channel.send("Starting server. ")
            print("Server started. ")
            start_thread = threading.Thread(target=server)
            stop_thread = threading.Thread(target=shutdown)
            start_thread.start()
            stop_thread.start()
    if msg.startswith("$stop"):
        if running:
            await message.channel.send("Stopping server. ")
            print("Attempting manual shutdown... ")
            rcon_stop()
        else:
            await message.channel.send("Server is already down. ")
    if msg.startswith("$check"):
        await message.channel.send("Server running: "+str(running))
    if msg.startswith("$help"):
        await message.channel.send("Use $start to start the server, and $stop to stop it. ")
        await message.channel.send("Use $check to check the server status. ")

mcHost.run(token)
