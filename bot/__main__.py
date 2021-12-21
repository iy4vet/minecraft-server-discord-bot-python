from dotenv import load_dotenv
import os
import threading
import time

import disnake
from mcrcon import MCRcon

running = False
mcHost = disnake.Client()

load_dotenv(dotenv_path=f"{os.getcwd()}/.env")
token = os.getenv('BOT_TOKEN')
rcon_ip = os.getenv('RCON_IP')
rcon_pass = os.getenv('RCON_PASS')

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
    await mcHost.change_presence(status=disnake.Status.dnd, activity=disnake.Activity(type=disnake.ActivityType.watching, name="if someone wants to play"))

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
    if msg.startswith("$ip"):
        server_ip = os.getenv('SERVER_IP')
        await message.channel.send("Server IP: "+server_ip)
    if msg.startswith("$help"):
        await message.channel.send("`$start` starts the server. `$stop` stops it. `$check` checks if the server is running. `$ip` will give you the server IP. ")

mcHost.run(token)
