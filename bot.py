import disnake
import dotenv
import os
import threading
import time
from dotenv import load_dotenv
from mcrcon import MCRcon

running = False
mcHost = disnake.Client()
load_dotenv(dotenv_path=f"{os.getcwd()}/bot.env")
load_dotenv(dotenv_path=f"{os.getcwd()}/server.properties")

if os.getenv("enable-rcon") != "true":
    dotenv.set_key("server.properties", "enable-rcon", 'true')
    print("Rcon was not enabled in your server.properties file. I have enabled it now. ")
if os.getenv("rcon.port") != "25575":
    dotenv.set_key("server.properties", "rcon.port", "25575")
    print("Rcon port was not set to 25575 in your server.properties file. I have changed it now. ")
    print("If you have any port forward rules for the Rcon port, please change them accordingly. ")
#todo: fix '25575', 'true' apostrophes when overwriting

def server():
    global running
    running = True
    print("Server started. ")
    os.system(os.getenv("start-script"))
    running = False
    time.sleep(1)
    print("Server stopped. ")

def rcon(cmd):
    mcr = MCRcon(os.getenv("server-ip"),os.getenv("rcon.password"))
    mcr.connect()
    return mcr.command(cmd)
    mcr.disconnect()

def shutdown():
    time.sleep(300)
    print("Auto shutdown thread started. ")
    while running:
        print("Attempting auto shutdown... ")
        rcon("execute unless entity @a run stop")
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
            start_thread = threading.Thread(target=server)
            stop_thread = threading.Thread(target=shutdown)
            start_thread.start()
            stop_thread.start()
    if msg.startswith("$stop"):
        if running:
            await message.channel.send("Attempting server shutdown. ")
            print("Attempting manual shutdown... ")
            await message.channel.send(rcon("execute unless entity @a run stop"))
        else:
            await message.channel.send("Server is already down. ")
    if msg.startswith("$check"):
        await message.channel.send("Server running: "+str(running))
    if msg.startswith("$ip"):
        await message.channel.send("Server IP: "+os.getenv('server-address'))
    if msg.startswith("$list"):
        if running:
            await message.channel.send(rcon("list"))
        else:
            await message.channel.send("Server is down. No players online. ")
    if msg.startswith("$rcon "):
        if message.author.id == int(os.getenv('rcon-op')):
            if running:
                await message.channel.send("Rcon Response: "+rcon(msg[6:]))
            else:
                await message.channel.send("Server is down. Please start the server to execute the command. ")
    if msg.startswith("$help"):
        await message.channel.send("`$start` starts the server. `$stop` stops it. `$check` checks if the server is running. `$ip` will give you the server IP. `$list` will list online players. ")
#todo: merge $check, $ip, $list into $info embed

mcHost.run(os.getenv("bot-token"))
