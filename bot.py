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
if os.getenv("rcon.password") == "":
    dotenv.set_key("server.properties", "rcon.password", "adefaultpassword")
    print("No password was set for Rcon. I have set a default password, though you are free to change it to something else. ")
#todo: fix apostrophes when overwriting

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
            print("Attempting manual shutdown... ")
            resp=rcon("execute unless entity @a run stop")
            if resp != "":
                await message.channel.send(resp)
            else:
                await message.channel.send("There are players on the server, so I cannot stop it. ")
        else:
            await message.channel.send("Server is already down. ")
    if msg.startswith("$check") or msg.startswith("$ip") or msg.startswith("$list"):
        await message.channel.send("This command is deprecated. Please use `$info` for server information. ")#you may delete this command if you wish
    if msg.startswith("$info"):
        online = ""
        if running:
            online=rcon("list")
        await message.channel.send("Server address: `"+os.getenv("server-address")+"`. \nServer running: "+str(running)+". \n"+online)
    if msg.startswith("$rcon ") and str(message.author.id) == os.getenv("rcon-op"):
        if running:
            await message.channel.send("Rcon: "+rcon(msg[6:]))
        else:
            await message.channel.send("Please start the server to execute this command. ")
    if msg.startswith("$help"):
        await message.channel.send("There are 3 commands that are available to use. \nTo start the server, use `$start`. \nTo get server information, use `$info`. \nTo manually stop the server, use `$stop`. This will only stop the server if no players are online. ")
#todo: $info embed

mcHost.run(os.getenv("bot-token"))
