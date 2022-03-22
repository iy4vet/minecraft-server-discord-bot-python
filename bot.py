#https://github.com/therectifier
#https://github.com/MinecraftServerDiscordBot/

import asyncio
import disnake
import os
import socket
import time
import urllib.request
import yaml
from disnake.ext import commands
from jproperties import Properties
from mcrcon import MCRcon

mcBot = commands.Bot(sync_commands_debug=True)
configs = Properties()
running = dict()
serverip = dict()
rconpassword = dict()
rconport = dict()

with open(f"{os.getcwd()}/bot.yaml") as file:
    config = yaml.load(file,Loader=yaml.FullLoader)
for directory in list(config['minecraft'].keys()):
    running[directory] = False
    with open(f"{os.getcwd()}/{directory}/server.properties", 'rb') as config_file:
        configs.load(config_file)
        serverip[directory] = configs.get("server-ip").data
        rconpassword[directory] = configs.get("rcon.password").data
        rconport[directory] = int(configs.get("rcon.port").data)
        if configs.get("enable-rcon").data != "true":
            print(f"enable-rcon was not set to true in {os.getcwd()}/{directory}/server.properties")
            print("please set this value to \"true\"")
            time.sleep(5)
            exit(code=0)

def rcon(server,cmd):
    if not running[server]:
        print("Rcon unsuccessful: Server down. ")
        return 
    mcr = MCRcon(serverip[server],rconpassword[server],port=rconport[server])
    try:
        mcr.connect()
        resp = mcr.command(cmd)
        mcr.disconnect()
        return resp
    except ConnectionRefusedError:
        print("Rcon unsuccessful: Server in start/stop state. ")
        return ("The server is either starting up, or shutting down. Please wait a bit, and then try again. ")

def ping(server,ip,port):
    if not running[server]:
        print("Ping failed: Server down. ")
        return -1
    if not rcon(server,"list").startswith("There are"):
        print("Ping failed: Server in start/stop state. ")
        return -2
    try:
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex((ip,port))
    except socket.gaierror:
        print("Ping failed: Address unresolvable. ")
        return -3

def update_yml():
    with open(f"{os.getcwd()}/bot.yaml", 'w') as file:
        yaml.dump(config, file)

async def autocomp_servers(inter: disnake.ApplicationCommandInteraction, user_input: str):
    return [lang for lang in list(config['minecraft'].keys()) if user_input.lower() in lang.lower()]

async def server_thread(server):
    global running
    running[server] = True
    print("Server started. ")
    origWD = os.getcwd()
    os.chdir(os.path.join(os.getcwd(),server))
    proc = await asyncio.create_subprocess_shell(config['minecraft'][server]['start_script'], stdout=asyncio.subprocess.PIPE)
    os.chdir(origWD)
    while True: 
        data = await proc.stdout.readline()
        if not data:
            break
        line = data.decode("latin1").rstrip()   
        print(line)
        asyncio.create_task(on_line(server,line))
    running[server] = False
    print("Server stopped. ")

async def shutdown_thread(server):
    while True:
        try:
            if rcon(server,"list").startswith("There are"):
                break
            else:
                await asyncio.sleep(5)
        except AttributeError:
            return
    print("Auto shutdown thread started. ") 
    await asyncio.sleep(300)
    while running[server]:
        print("Attempting auto shutdown... ")
        rcon(server,"execute unless entity @a run stop")
        await asyncio.sleep(180)

async def webhook_send(server,content,uname,avatar):
    for channelid in list(config['discord'].keys()):
        channel = mcBot.get_channel(channelid)
        thrd = channel.get_thread(config['discord'][channelid][server])
        exist = False
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.name == "MCBotChat":
                exist = True
        if not exist:
            await channel.create_webhook(name="MCBotChat")
        for webhook in webhooks:
            try:
                await webhook.send(str(content),username=uname,avatar_url=avatar,thread=thrd)
            except disnake.errors.InvalidArgument:
                pass
            except disnake.errors.HTTPException:
                pass

async def on_line(server,line):
    try:
        split = line.split("<",1)[1].split("> ",1)
        await webhook_send(server,split[1],split[0],"https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/i/977e8c4f-1c99-46cd-b070-10cd97086c08/d36qrs5-017c3744-8c94-4d47-9633-d85b991bf2f7.png")
    except IndexError:
        return  

@mcBot.event
async def on_ready():
    print(f"Logged in as {mcBot.user}")
    await mcBot.change_presence(activity=disnake.Game("/help for help"))
    for channelid in list(config['discord'].keys()):
        for server in list(config['minecraft'].keys()):
            try:
                config['discord'][channelid][server]
            except TypeError:
                channel = mcBot.get_channel(channelid)
                msg = await channel.send("Creating threads for chat integration. Each thread is named after the server it is tied to. ")
                thread = await channel.create_thread(name=server,reason="Auto Thread Creation. ",message=msg)
                config['discord'][channelid] = dict()
                config['discord'][channelid][server] = thread.id
            except KeyError:
                channel = mcBot.get_channel(channelid)
                msg = await channel.send("Creating threads for chat integration. Each thread is named after the server it is tied to. ")
                thread = await channel.create_thread(name=server,reason="Auto Thread Creation. ",message=msg)
                config['discord'][channelid][server] = thread.id
    update_yml()


@mcBot.slash_command(description="Starts the Minecraft server")
async def start(inter,server:str = commands.Param(autocomplete=autocomp_servers),delay:int = None):
    """
    Starts the Minecraft server

    Parameters
    ----------
    server: The server this is for
    delay: The amount of time in seconds to delay the shutdown thread. Must be between 1 and 300
    """
    await inter.response.defer()
    if running[server]:
        await inter.edit_original_message(content="Server is already running! ")
    else:
        if delay:
            if delay>300 or delay<1:
                await inter.edit_original_message(content=f"A value between 1 and 300 must be provided for delay. You entered {delay}. Please try again. ")
                await asyncio.sleep(5)
            else:
                asyncio.create_task(server_thread(server))
                await inter.edit_original_message(content=f"Starting {server}. Delaying automatic shutdown by an additional {delay} second(s). Remember that the automatic shutdown starts 5 minutes after the server is joinable without this delay. ")
                await asyncio.sleep(delay)
        else:
            asyncio.create_task(server_thread(server))
            await inter.edit_original_message(content=f"Starting {server}. ")
        asyncio.create_task(shutdown_thread(server))

@mcBot.slash_command(description="Attempts to stop the server")
async def stop(inter,server:str = commands.Param(autocomplete=autocomp_servers)):
    """
    Attempts to stop the server

    Parameters
    ----------
    server: The server this is for
    """
    await inter.response.defer()
    if running[server]:
        print("Attempting manual shutdown... ")
        try:
            await inter.edit_original_message(content=rcon(server,"execute unless entity @a run stop"))
            while running[server]:
                await asyncio.sleep(5)
            await inter.edit_original_message(content="Stopped the server. ")
        except disnake.errors.HTTPException:
            await inter.edit_original_message(content="Could not stop the server. ")
    else:
        await inter.edit_original_message(content="Server is already down. ")

@mcBot.slash_command(description="Attempts to stop all servers")
async def stopall(inter):
    await inter.response.defer()
    resp = ""
    for server in list(config['minecraft'].keys()):
        resp = f"{resp}\n{server}:{rcon(server,'execute unless entity @a run stop')}"
    await inter.edit_original_message(content=resp)

@mcBot.slash_command(description="Gets server information")
async def info(inter,server:str = commands.Param(autocomplete=autocomp_servers)):
    """
    Gets server information

    Parameters
    ----------
    server: The server this is for
    """
    await inter.response.defer()
    try:
        address=config['minecraft'][server]['server_address']
    except KeyError:
        address=config['server_address']
    try:
        port=config['minecraft'][server]['server_port']
    except KeyError:
        port=config['server_port']
    online = rcon(server,'list')
    if online:
        await inter.edit_original_message(content=f"Server address: `{address}:{port}`. \nServer running: {running[server]}. \n{online}")
    else:
        await inter.edit_original_message(content=f"Server address: `{address}:{port}`. \nServer running: {running[server]}. ")

@mcBot.slash_command(description="Checks server address")
async def checkaddress(inter,server:str = commands.Param(autocomplete=autocomp_servers)):
    """
    Checks server address

    Parameters
    ----------
    server: The server this is for
    """
    await inter.response.defer()
    await inter.edit_original_message(content="Pinging current address...")
    try:
        address=config['minecraft'][server]['server_address']
    except KeyError:
        address=config['server_address']
    try:
        port=config['minecraft'][server]['server_port']
    except KeyError:
        port=config['server_port']
    connectcode = ping(server,address,port)
    if connectcode == 0:
        await inter.edit_original_message(content=f"I am able to ping the server at `{address}:{port}`. \nCheck that the address you set in Minecraft matches this. If it's correct, check your network connection and firewall settings. ")
    elif connectcode == -1:
        await inter.edit_original_message(content="The server is not running[server]. Please start the server to check the address. ")
    elif connectcode == -2:
        await inter.edit_original_message(content="The server is either starting up, or shutting down. Please wait a bit, and then try again. ")
    else:
        await inter.edit_original_message(content="The current address is incorrect. Fetching new address...")
        extip = urllib.request.urlopen("https://ident.me").read().decode("utf8")
        await inter.edit_original_message(content="Fetched new address. Pinging...")
        connectcode = ping(server,extip,port)
        if connectcode == 0:
            config['minecraft'][server]['server_address'] = extip
            await inter.edit_original_message(content=f"Found new address! New address: `{config['minecraft'][server]['server_address']}:{port}`")
        else:
            opping = ""
            for i in config['bot_op']:
                opping = f"{opping}<@{i}> "
            await inter.edit_original_message(content=f"I was unable to get a new working address for the server. Please ask the bot host to update the `server-address` field and restart the bot. \nAlternatively, ask {opping}to use the /setaddress command to update the server address. \nHowever, you may try this address: `{extip}`. ")
    update_yml()

@mcBot.slash_command(description="Sends a message in the Minecraft server")
async def say(inter,message:str,server:str = commands.Param(autocomplete=autocomp_servers)):
    """
    Sends a message in the Minecraft server

    Parameters
    ----------
    message: The message to be sent
    server: The server this is for
    """
    await inter.response.defer(ephemeral=True)
    if not rcon(server,"list").startswith("There are"):
        await inter.edit_original_message(content="Server is not running[server]. ")
        return
    try:
        await inter.edit_original_message(content=rcon(server,'tellraw @a ["{'+str(await mcBot.fetch_user(inter.author.id))+'} '+message+'"]'))
        return
    except disnake.errors.HTTPException:
        pass
    await webhook_send(server,message,inter.author.name,inter.author.avatar)
    await inter.edit_original_message(content="Sent! ")

@mcBot.slash_command(description="Get help on all commands")
async def help(inter):
    await inter.response.send_message("There are 5 commands that are available to use. \nTo start the server, use `/start`. \nTo get server information, use `/info`. \nTo manually stop the server, use `/stop`. This will only stop the server if no players are online. \nTo send a message in the server, use `/say <message>`. \nIf the address given in `/info` does not work, you can do `/ipcheck`. This will update the server address if the current one does not work. ")

@mcBot.slash_command(description="Sets a new address for the Minecraft server")
async def setaddress(inter,address:str,port:int,server:str = commands.Param(autocomplete=autocomp_servers)):
    """
    Sets a new address for the Minecraft server

    Parameters
    ----------
    address: The new server address
    port: The new server port
    server: The server this is for
    """
    if inter.author.id not in config['bot_op']:
        await inter.response.send_message(content="You don't have access to this command! ",ephemeral=True)
        return
    await inter.response.defer()
    connectcode = ping(server,address,port)
    if connectcode == 0:
        await inter.edit_original_message(content="This address works. I will update it now. ")
        config['minecraft'][server]['server_address'] = address
        config['minecraft'][server]['server_address'] = port
    elif connectcode == -1:
        await inter.edit_original_message(content="The server is not running[server]. Please start the server so I can check that this address works. ")
    elif connectcode == -2:
        await inter.edit_original_message(content="The server is either starting up, or shutting down. Please wait a bit, and then try again. ")
    elif connectcode == -3:
        await inter.edit_original_message(content="This address couldn't be resolved. This is probably because the URL/IP doesn't exist. ")
    elif connectcode == 10060:
        await inter.edit_original_message(content="This address timed out when pinged. This is probably due to the port not being forwarded. ")
    else:
        await inter.edit_original_message(content=f"This address doesn't work. While pinging, I ran into the code {connectcode}. Try looking up `sockets code {connectcode}`. ")
    update_yml()

@mcBot.slash_command(description="Executes a Minecraft command on the Minecraft server")
async def cmd(inter,command:str,server:str = commands.Param(autocomplete=autocomp_servers)):
    """
    Executes a Minecraft command on the Minecraft server

    Parameters
    ----------
    command: The command to be executed
    server: The server this is for
    """
    if inter.author.id not in config['bot_op']:
        await inter.response.send_message(content="You don't have access to this command! ",ephemeral=True)
        return
    await inter.response.defer()
    if running[server]:
        await inter.edit_original_message(content=f"Rcon: {rcon(server,command)}")
    else:
        await inter.edit_original_message(content="Please start the server to execute this command. ")

@mcBot.event
async def on_message(message):
    if message.author.bot:
        return  
    valid = False
    for channel in list(config['discord'].keys()):
        try:
            if config['discord'][channel][message.channel.name] == message.channel.id:
                valid = True
        except KeyError:
            return
    if not valid:
            return
    server = message.channel.name
    await message.delete()
    if not running[server]:
        msg = await message.channel.send("Server is down. ")
        await asyncio.sleep(5)
        await msg.delete()
        return
    if not rcon(server,"list").startswith("There are"):
        msg = await message.channel.send("Server is not running[server]. ")
        await asyncio.sleep(5)
        await msg.delete()
        return
    try:
        msg = await message.channel.send(rcon(server,'tellraw @a [\"{'+str(await mcBot.fetch_user(message.author.id))+'} '+message.clean_content+'\"]'))
        await asyncio.sleep(5)
        await msg.delete()
        return
    except disnake.errors.HTTPException:
        pass
    await webhook_send(server,message.content,message.author.name,message.author.avatar)

mcBot.run(config['bot_token'])
