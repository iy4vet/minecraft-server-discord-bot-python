#https://github.com/therectifier

import asyncio
import disnake
import os
import socket
import threading
import time
import urllib.request
from disnake.ext import commands
from dotenv import load_dotenv
from mcrcon import MCRcon

load_dotenv(dotenv_path=f"{os.getcwd()}/bot.env")
load_dotenv(dotenv_path=f"{os.getcwd()}/server.properties")
waitmsg = "The server is either starting up, or shutting down. Please wait a bit, and then try again. "
running = False
error = False
try:
    serverport = os.getenv("server-address").split(":")[1]
except IndexError:
    serverport = 25565
if os.getenv("enable-rcon") != "true":
    print("Rcon is not enabled in your server.properties file. Please change enable-rcon to true. ")
    error = True
if os.getenv("rcon.password") == "":
    print("No password was set for Rcon. Please set a password for Rcon under rcon.password")
    error = True
if error:
    time.sleep(10)
    exit(code=0)

mcBot = commands.Bot(
    sync_commands_debug=True,
)

def server():
    global running
    running = True
    print("Server started. ")
    os.system(os.getenv("start-script"))
    running = False
    print("Server stopped. ")

def rcon(cmd):
    mcr = MCRcon(os.getenv("server-ip"),os.getenv("rcon.password"),port=int(os.getenv("rcon.port")))
    try:
        mcr.connect()
        resp = mcr.command(cmd)
        mcr.disconnect()
        print("Rcon successful! ")
        return resp
    except ConnectionRefusedError:
        print("Rcon unsuccessful: Server in start/stop state. ")
        return (waitmsg)

def ping(ip,port):
    if not running:
        print("Ping failed: Server down. ")
        return -1
    if not rcon("list").startswith("There are"):
        print("Ping failed: Server in start/stop state. ")
        return -2
    try:
        print("Pinging! ")
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex((ip,port))
    except:
        print("Ping failed: Sockets error. ")
        return -3

def shutdown():
    time.sleep(300)
    print("Auto shutdown thread started. ")
    while running:
        print("Attempting auto shutdown... ")
        rcon("execute unless entity @a run stop")
        time.sleep(180)

@mcBot.event
async def on_ready():
    print("Logged in as {0.user}".format(mcBot))
    await mcBot.change_presence(activity=disnake.Game("/help for help"))

@mcBot.slash_command(description="Starts the server")
async def start(inter):
    await inter.response.defer()
    if running:
        await inter.edit_original_message(content="Server is already running! ")
    else:
        threading.Thread(target=server).start()
        while (not rcon("list").startswith("There are")) and running:
            await asyncio.sleep(5)
        threading.Thread(target=shutdown).start()
        await inter.edit_original_message(content="Started server. ")

@mcBot.slash_command(description="Attempts to stop the server")
async def stop(inter):
    await inter.response.defer()
    if running:
        print("Attempting manual shutdown... ")
        try:
            await inter.edit_original_message(content=rcon("execute unless entity @a run stop"))
        except disnake.errors.HTTPException:
            await inter.edit_original_message(content="Could not stop the server. ")
    else:
        await inter.edit_original_message(content="Server is already down. ")

@mcBot.slash_command(description="Gets server information")
async def info(inter):
    await inter.response.defer()
    online = ""
    if running:
        online=rcon("list")
    await inter.edit_original_message(content="Server address: `"+os.getenv("server-address")+"`. \nServer running: "+str(running)+". \n"+online)

@mcBot.slash_command(description="Checks server address")
async def ipcheck(inter):
    await inter.response.defer()
    connectcode = ping(os.getenv("server-address").split(":")[0],serverport)
    if connectcode == 0:
        await inter.edit_original_message(content="I am able to ping the server at `"+os.getenv("server-address")+"`. \nCheck that the address you set in Minecraft matches this. If it's correct, check your network connection and firewall settings. ")
    elif connectcode == -1:
        await inter.edit_original_message(content="The server is not running. Please start the server to check the address. ")
    elif connectcode == -2:
        await inter.edit_original_message(waitmsg)
    else:
        extip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
        connectcode = ping(extip,serverport)
        if connectcode == 0:
            await inter.edit_original_message(content="New IP: "+extip)
            if serverport == 25565:
                os.environ["server-address"] = extip
            else:
                os.environ["server-address"] = extip + ":" + serverport
        else:
            opping = ""
            for i in os.getenv("server-op").split(','):
                opping = opping + str("<@"+i+"> ")
            await inter.edit_original_message(content="I was unable to get a new working address for the server. Please ask the bot host to update the `server-address` field and restart the bot. \nAlternatively, ask "+opping+"to use the $ip-set command to update the server address. \nHowever, you may try this address: `"+extip+"`. ")

@mcBot.slash_command(description="Sends a message in the Minecraft server")
async def say(inter,message:str):
    """
    Sends a message in the Minecraft server

    Parameters
    ----------
    message: The message to be sent
    """
    await inter.response.defer(ephemeral=True)
    try:
        await inter.edit_original_message(content=rcon('tellraw @a ["{'+str(await mcBot.fetch_user(inter.author.id))+'} '+message+'"]'))
    except disnake.errors.HTTPException: 
        await inter.edit_original_message(content="Sent! ")

@mcBot.slash_command(description="Get help on all commands")
async def help(inter):
    await inter.response.send_message("There are 5 commands that are available to use. \nTo start the server, use `/start`. \nTo get server information, use `/info`. \nTo manually stop the server, use `/stop`. This will only stop the server if no players are online. \nTo send a message in the server, use `/say <message>`. \nIf the address given in `/info` does not work, you can do `/ipcheck`. This will update the server address if the current one does not work. ")

@mcBot.slash_command(description="Sets a new address for the Minecraft server")
async def ipset(inter,address:str,port:int = serverport):
    """
    Sets a new address for the Minecraft server

    Parameters
    ----------
    address: The new server address
    port: The new server port (optional)
    """
    if str(inter.author.id) not in os.getenv("server-op").split(','):
        await inter.response.send_message(content="You don't have access to this command! ",ephemeral=True)
        return
    await inter.response.defer()
    connectcode = ping(address,port)
    if connectcode == 0:
        await inter.edit_original_message(content="This address works. I will update it now. ")
        if port == 25565:
            os.environ["server-address"] = address
        else:
            os.environ["server-address"] = address + ":" + port
            serverport = port
    elif connectcode == -1:
        await inter.edit_original_message(content="The server is not running. Please start the server so I can check that this address works. ")
    elif connectcode == -2:
        await inter.edit_original_message(content=waitmsg)
    else:
        await inter.edit_original_message(content="This address doesn't work. I will continue with the old one. ")

@mcBot.slash_command(description="Executes a Minecraft command on the Minecraft server")
async def cmd(inter,command:str):
    """
    Executes a Minecraft command on the Minecraft server

    Parameters
    ----------
    command: The command to be executed
    """
    if str(inter.author.id) not in os.getenv("server-op").split(','):
        await inter.response.send_message(content="You don't have access to this command! ",ephemeral=True)
        return
    await inter.response.defer()
    if running:
        await inter.edit_original_message(content="Rcon: "+rcon(command))
    else:
        await inter.edit_original_message(content="Please start the server to execute this command. ")

mcBot.run(os.getenv("bot-token"))
