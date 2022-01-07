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
mcHost = disnake.Client()
load_dotenv(dotenv_path=f"{os.getcwd()}/bot.env")
load_dotenv(dotenv_path=f"{os.getcwd()}/server.properties")

if os.getenv("enable-rcon") != "true":
    print("Rcon is not enabled in your server.properties file. Please change enable-rcon to true. ")
if os.getenv("rcon.port") != "25575":
    print("Rcon port is not set to 25575 in your server.properties file. Please change rcon.port to 25575. ")
    print("If you have any port forward rules for the Rcon port, please change them accordingly. ")
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
        return mcr.command(cmd)
        mcr.disconnect()
        print("Rcon successful. ")
    except ConnectionRefusedError:
        return ("The server is either starting up, or shutting down. Please wait a bit. ")
        print("Rcon unsuccessful. ConnectionRefusedError")

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
        await ctx.send("This command is deprecated. Please use `$info` for server information. ")#you may delete this command if you wish
    if msg == "$info":
        online = ""
        if running:
            online=rcon("list")
        await ctx.send("Server address: `"+os.getenv("server-address")+"`. \nServer running: "+str(running)+". \n"+online)
    if msg == "$rcon " and str(message.author.id) == os.getenv("server-op"):
        if running:
            await ctx.send("Rcon: "+rcon(msg[6:]))
        else:
            await ctx.send("Please start the server to execute this command. ")
    if msg == "$ip-check":
        if running:
            reallyrunning = True
            mct = MCRcon(os.getenv("server-ip"),os.getenv("rcon.password"))
            try:
                mct.connect()
                mct.disconnect()
                print("Test Rcon successful. ")
            except:
                reallyrunning = False
                print("Test Rcon unsuccessful. ")
            if reallyrunning:
                await ctx.send("Checking server address. ")
                try:
                    connectcode = socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex((os.getenv("server-address"),25565))
                except:
                    connectcode = 1984
                if connectcode == 0:
                    await ctx.send("I am able to ping the server at `"+os.getenv("server-address")+"`. Please check your network connection and firewall settings. ")
                    print("Ping successful. ")
                else:
                    await ctx.send("The server address is incorrect. I will attempt to refresh it now. ")
                    print("Ping unsuccessful. ")
                    print("Getting external IP... ")
                    extip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
                    print("External IP found: "+extip)
                    try:
                        connectcode = socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex((extip,25565))
                    except:
                        pass
                    if connectcode == 0:
                        print("New IP successful. ")
                        await ctx.send("New IP: "+extip)
                        os.environ["server-address"] = extip
                    else:
                        print("New IP unsuccessful. ")
                        await ctx.send("I was unable to get a new working IP for the server. Please ask <@"+os.getenv("server-op")+"> or the bot host to update the `server-address` field and restart the bot. ")
            else:
                await ctx.send("The server is either starting up, or shutting down. ")
        else:
            await ctx.send("The server is not running. ")
    if msg == "$help":
        await ctx.send("There are 4 commands that are available to use. \nTo start the server, use `$start`. \nTo get server information, use `$info`. \nTo manually stop the server, use `$stop`. This will only stop the server if no players are online. \nIf the address given in `$info` does not work, you can do `$ip-check`. This will update the server address if the current one does not work. ")

mcHost.run(os.getenv("bot-token"))
