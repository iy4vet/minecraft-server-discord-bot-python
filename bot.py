#https://github.com/nottherectifier

import disnake
import dotenv
import os
import random
import socket
import string
import threading
import time
import urllib.request
from dotenv import load_dotenv
from mcrcon import MCRcon

running = False
waitmsg = "The server is either starting up, or shutting down. Please wait a bit, and then try again. "
mcHost = disnake.Client()
load_dotenv(dotenv_path=f"{os.getcwd()}/bot.env")
load_dotenv(dotenv_path=f"{os.getcwd()}/server.properties")

if os.getenv("enable-rcon") != "true":
    print("Rcon is not enabled in your server.properties file. Please change enable-rcon to true. ")
    time.sleep(10)
    exit
if os.getenv("rcon.port") != "25575":
    print("Rcon port is not set to 25575 in your server.properties file. Please change rcon.port to 25575. ")
    print("If you have any port forward rules for the Rcon port, please change them accordingly. ")
    time.sleep(10)
    exit
if os.getenv("rcon.password") == "":
    dotenv.set_key("server.properties", "rcon.password", ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10)))
    print("No password was set for Rcon. I have set a random password, though you are free to change it to something else. ")

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
    try:
        mcr.connect()
        resp = mcr.command(cmd)
        mcr.disconnect()
        return resp
    except ConnectionRefusedError:
        return (waitmsg)

def ping(ip):
    if not running:
        return -1
    if not rcon("list").startswith("There are"):
        return -2
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex((ip,25565))

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
    ctx = message.channel
    if msg == "$start":
        if running:
            await ctx.send("Server is already running! ")
        else:
            await ctx.send("Starting server. ")
            start_thread = threading.Thread(target=server)
            stop_thread = threading.Thread(target=shutdown)
            start_thread.start()
            stop_thread.start()
    if msg == "$stop":
        if running:
            print("Attempting manual shutdown... ")
            await ctx.send("Attempting to stop the server. ")
            try:
                await ctx.send(rcon("execute unless entity @a run stop"))
            except:
                pass
        else:
            await ctx.send("Server is already down. ")
    if msg == "$check" or msg == "$ip" or msg == "$list":
        await ctx.send("This command is deprecated. Use `$info` for server information. ")
    if msg == "$info":
        online = ""
        if running:
            online=rcon("list")
        await ctx.send("Server address: `"+os.getenv("server-address")+"`. \nServer running: "+str(running)+". \n"+online)
    if msg == "$ip-check":
        connectcode = ping(os.getenv("server-address"))
        if connectcode == 0:
            await ctx.send("I am able to ping the server at `"+os.getenv("server-address")+"`. \nCheck that the address you set in Minecraft matches this. If it's correct, check your network connection and firewall settings. ")
        elif connectcode == -1:
            await ctx.send("The server is not running. Please start the server to check the address. ")
        elif connectcode == -2:
            await ctx.send(waitmsg)
        else:
            await ctx.send("The address is incorrect. I will attempt to refresh it now. ")
            extip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
            connectcode = ping(extip)
            if connectcode == 0:
                await ctx.send("New IP: "+extip)
                os.environ["server-address"] = extip
            else:
                await ctx.send("I was unable to get a new working address for the server. Please ask <@"+os.getenv("server-op")+"> or the bot host to update the `server-address` field and restart the bot, or use the `$ip-set` command. ")
                await ctx.send("However, you may try this address: `"+extip+"`. ")
    if msg == "$help":
        await ctx.send("There are 4 commands that are available to use. \nTo start the server, use `$start`. \nTo get server information, use `$info`. \nTo manually stop the server, use `$stop`. This will only stop the server if no players are online. \nIf the address given in `$info` does not work, you can do `$ip-check`. This will update the server address if the current one does not work. ")
    if msg.startswith("$ip-set ") and str(message.author.id) == os.getenv("server-op"):
        connectcode = ping(msg[8:])
        if connectcode == 0:
            await ctx.send("This address works. I will update it now. ")
            os.environ["server-address"] = msg[8:]
        elif connectcode == -1:
            await ctx.send("The server is not running. Please start the server so I can check that this address works. ")
        elif connectcode == -2:
            await ctx.send(waitmsg)
        else:
            await ctx.send("This address doesn't work. I will continue with the old one. ")
    if msg.startswith("$rcon ") and str(message.author.id) == os.getenv("server-op"):
        if running:
            await ctx.send("Rcon: "+rcon(msg[6:]))
        else:
            await ctx.send("Please start the server to execute this command. ")

mcHost.run(os.getenv("bot-token"))
