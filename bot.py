#https://github.com/therectifier
#https://github.com/MinecraftServerDiscordBot/

import asyncio
import os
import socket
from datetime import datetime
from io import BytesIO
from pkg_resources import require
from urllib.request import urlopen

requirements = ["disnake==2.2.2","pyyaml==6.0","jproperties==2.1.1","mcrcon==0.7.0"]
for requirement in requirements:
    try:
        require(requirement)
    except:
        os.system(f"pip install {requirement}")

import disnake
import yaml
from disnake.ext import commands
from jproperties import Properties
from mcrcon import MCRcon

mcBot = commands.Bot(sync_commands_debug=True)
configs = Properties()
origwd = os.getcwd()
running,serverip,rconpassword,rconport = dict(),dict(),dict(),dict()
nrunning = 0
error = False
bungee_running = False

with open(f"{os.getcwd()}/bot.yaml") as file:
    config = yaml.load(file,Loader=yaml.FullLoader)
for directory in config['minecraft'].keys():
    if directory.lower() == "logs":
        print(f"It appears you have a server named '{directory}'! NO! NO! This bot needs its own folder for logging! Please rename your server and restart the bot! Keep in mind that folder names are case insensitive. ")
        error = True
        break
    if directory.lower() == "bungeecord":
        print(f"It appears you have a server named '{directory}'! NO! NO! If you're using BungeeCord, the bot uses the global default ! Please rename your server and restart the bot! Keep in mind that folder names are case insensitive. ")
        error = True
        break
    running[directory] = False
    with open(f"{os.getcwd()}/{directory}/server.properties", 'rb') as config_file:
        configs.load(config_file)
        serverip[directory] = configs.get("server-ip").data
        rconpassword[directory] = configs.get("rcon.password").data
        rconport[directory] = int(configs.get("rcon.port").data)
        if configs.get("enable-rcon").data != "true":
            print(f"You have not set 'enable-rcon' to 'true' in {os.getcwd()}/{directory}/server.properties! You need this enabled for the bot to communicate with the server! Please set this value to 'true' and restart the bot!")
            error = True
if error:
    input("Press enter to exit... ")
    exit(code=0)

async def logprint(text):
    print(f"[{datetime.now()}]: {text}")
    path = f"{os.getcwd()}/logs/console"
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f"{path}/{str(datetime.now())[:10]}.txt", 'a',encoding="utf-8") as log_file:
        print(f"[{datetime.now()}]: {text}",file=log_file)

async def logchat(server,message,author,discraft):
    if discraft: 
        source = "MC"
    else: 
        source = "DC"
    path = f"{os.getcwd()}/logs/chat/{server}"
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f"{path}/{str(datetime.now())[:10]}.txt", 'a',encoding="utf-8") as log_file:
        print(f"[{datetime.now()}]: [{source}] {author}: {message}",file=log_file)

async def loginter(cmd,user,params):
    path = f"{os.getcwd()}/logs/inter"
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f"{path}/{str(datetime.now())[:10]}.txt", 'a',encoding="utf-8") as log_file:
        print(f"[{datetime.now()}]: User {user} issued command {cmd} with parameters {params}",file=log_file)

def update_yml():
    with open(f"{origwd}/bot.yaml", 'w') as file:
        yaml.dump(config, file)

def rcon(server,cmd):
    if not running[server]:
        return "Server is not running. "
    mcr = MCRcon(serverip[server],rconpassword[server],port=rconport[server])
    try:
        mcr.connect()
        resp = mcr.command(cmd)
        mcr.disconnect()
        return resp
    except ConnectionRefusedError:
        return "The server is either starting up, or shutting down. Please wait a bit, and then try again. "

def ping(server,ip,port):
    if config['bungeecord'] == 1:
        pass
    elif not running[server]:
        return -1
    elif not rcon(server,"list").startswith("There are"):
        return -2
    try:
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex((ip,port))
    except socket.gaierror:
        return -3

def fetch_address(server):
    try:
        address=config['minecraft'][server]['server_address']
    except KeyError:
        address=config['server_address']
    if config['bungeecord'] == 1:
        port = config['server_port']
    else:
        try:
            port=config['minecraft'][server]['server_port']
        except KeyError:
            port=config['server_port']
    return (address,port)

async def autocomp_servers(inter: disnake.ApplicationCommandInteraction, user_input: str):
    return [lang for lang in config['minecraft'].keys() if user_input.lower() in lang.lower()]

async def server_thread(server,user):
    global running
    global nrunning
    asyncio.create_task(logprint(f"{server} started. "))
    running[server] = True
    nrunning += 1
    startembed = disnake.Embed(title=config['server_title'],description=f"🖥️ **{server}** started by {user.mention}",color=disnake.Colour.green(),timestamp=datetime.now())
    startembed.set_author(name=user,icon_url=user.avatar)
    await webhook_send(server,"","MC Bot",mcBot.user.avatar,embed=startembed)
    os.chdir(f"{origwd}/{server}")
    proc = await asyncio.create_subprocess_shell(config['minecraft'][server]['start_script'], stdout=asyncio.subprocess.PIPE)
    os.chdir(origwd)
    while True:
        data = await proc.stdout.readline()
        if not data:
            break
        line = data.decode("latin1").rstrip()
        asyncio.create_task(logprint(f"{server}: {line}"))
        asyncio.create_task(on_line(server,line))
    running[server] = False
    nrunning -=1
    stopembed = disnake.Embed(title=config['server_title'],description=f"🖥️ **{server}** stopped",color=disnake.Colour.red(),timestamp=datetime.now())
    await webhook_send(server,"","MC Bot",mcBot.user.avatar,embed=stopembed)
    asyncio.create_task(logprint(f"{server} stopped. "))

async def bungee_server():
    global bungee_running
    bungee_running = True
    os.chdir(f"{origwd}/BungeeCord")
    proc = await asyncio.create_subprocess_shell("run.bat", stdout=asyncio.subprocess.PIPE)
    os.chdir(origwd)
    asyncio.create_task(logprint(f"BungeeCord: BungeeCord started. "))
    while True: 
        data = await proc.stdout.readline()
        if not data:
            break
        print(data.decode("utf-8").rstrip())
    asyncio.create_task(logprint(f"BungeeCord: BungeeCord stopped. "))
    bungee_running = False

async def on_line(server,line):
    try:
        split = line.split("<",1)[1].split("> ",1)
        await webhook_send(server,split[1],split[0],config['mc_url'])
    except IndexError:
        pass

async def shutdown_thread(server):
    while True:
        rconresponse = rcon(server,"list")
        if rconresponse.startswith("There are"):
            break
        elif rconresponse == "Server is not running. ":
            return
        else:
            await asyncio.sleep(5)
    await asyncio.sleep(300)
    while running[server]:
        rcon(server,"execute unless entity @a run stop")
        await asyncio.sleep(180)

async def webhook_send(server,content,username,avatar,embed=None,fileprops=None):
    if not embed:
        asyncio.create_task(logchat(server,content,username,avatar == config['mc_url']))
    for channelid in config['discord'].keys():
        files = list()
        try:
            for fileprop in fileprops:
                fp = BytesIO(fileprop[0])
                fp.seek(0)
                files.append(disnake.File(fp=fp,filename=fileprop[1],spoiler=fileprop[2]))
        except TypeError:
            pass
        channel = await mcBot.fetch_channel(channelid)
        webhooks = await channel.webhooks()
        thread = channel.get_thread(config['discord'][channelid]['channels'][server]) or await channel.guild.fetch_channel(config['discord'][channelid]['channels'][server])
        if thread.archived:
            await thread.edit(archived=False)
        for webhook in webhooks:
            if webhook.token:
                try:
                    await webhook.send(str(content),username=username,avatar_url=avatar,thread=thread,embed=embed,files=files)
                except disnake.errors.HTTPException:
                    pass
                break

@mcBot.event
async def on_ready():
    asyncio.create_task(logprint(f"Logged in as {mcBot.user}"))
    await mcBot.change_presence(activity=disnake.Game("/help for help"))
    for channelid in config['discord'].keys():
        exist = False
        channel = await mcBot.fetch_channel(channelid)
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.token:
                exist = True
        if not exist:
            await channel.create_webhook(name="MCBotChat")
        for server in config['minecraft'].keys():
            try:
                thread = channel.get_thread(config['discord'][channelid]['channels'][server]) or await channel.guild.fetch_channel(config['discord'][channelid]['channels'][server])
                if thread.archived:
                    await thread.edit(archived=False)
            except (TypeError,KeyError,AttributeError,disnake.errors.NotFound) as e:
                if isinstance(e,TypeError):
                    config['discord'][channelid] = dict()
                msg = await channel.send(f"Creating thread for {server} chat integration. ")
                thread = await channel.create_thread(name=server,reason=f"Creating thread for {server} chat integration. ",message=msg)
                config['discord'][channelid]['channels'][server] = thread.id
    update_yml()
    if config['bungeecord'] == 1 and not bungee_running:
        await asyncio.create_task(bungee_server())

@mcBot.slash_command(description="Starts the Minecraft server")
async def start(inter,server:str = commands.Param(autocomplete=autocomp_servers),delay:int = None):
    """
    Starts the Minecraft server

    Parameters
    ----------
    server: The server this is for
    delay: The amount of time in seconds to delay the shutdown thread. Must be between 1 and 300
    """
    asyncio.create_task(loginter("start",inter.author,{"server":server,"delay":delay}))
    if config['bungeecord'] == 1 and not bungee_running:
        await asyncio.create_task(bungee_server())
    if server not in config['minecraft'].keys():
        await inter.response.send_message(content="Invalid server name given. Use /infoall to get a list of all servers. Remember that names are case sensitive. ",ephemeral=True)
        return
    await inter.response.defer()
    if running[server]:
        await inter.edit_original_message(content=f"{server} is already running! ")
    elif nrunning >= config['server_max_concurrent'] and config['server_max_concurrent'] != -1:
        await inter.edit_original_message(content=f"Maximum concurrent server limit ({config['server_max_concurrent']}) reached. Try `/stopall` to free up some slots. ")
    else:
        if delay:
            if delay>300 or delay<1:
                await inter.edit_original_message(content=f"A value between 1 and 300 must be provided for delay. You entered {delay}. Please try again. ",ephemeral=True)
                return
            else:
                asyncio.create_task(server_thread(server,inter.author))
                await inter.edit_original_message(content=f"Starting {server}. Delaying automatic shutdown by an additional {delay} second(s). Remember that the automatic shutdown starts 5 minutes after the server is joinable without this delay. ")
                await asyncio.sleep(delay)
        else:
            asyncio.create_task(server_thread(server,inter.author))
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
    asyncio.create_task(loginter("stop",inter.author,{"server":server}))
    if server not in config['minecraft'].keys():
        await inter.response.send_message(content="Invalid server name given. Use /infoall to get a list of all servers. Remember that names are case sensitive. ",ephemeral=True)
        return
    await inter.response.defer()
    try:
        await inter.edit_original_message(content=rcon(server,"execute unless entity @a run stop"))
        while running[server]:
            await asyncio.sleep(5)
        await inter.edit_original_message(content="Stopped the server. ")
    except disnake.errors.HTTPException:
        await inter.edit_original_message(content=f"Could not stop the server: {rcon(server,'list')}")

@mcBot.slash_command(description="Attempts to stop all servers")
async def stopall(inter):
    asyncio.create_task(loginter("stopall",inter.author,{}))
    await inter.response.defer()
    resp = ""
    for server in config['minecraft'].keys():
        res = rcon(server,'execute unless entity @a run stop')
        if not res:
            res = f"Could not stop the server: {rcon(server,'list')}"
        resp = f"{resp}\n{server}: `{res}`"
    await inter.edit_original_message(content=resp)

@mcBot.slash_command(description="Gets server information")
async def info(inter,server:str = commands.Param(autocomplete=autocomp_servers)):
    """
    Gets server information

    Parameters
    ----------
    server: The server this is for
    """
    asyncio.create_task(loginter("info",inter.author,{"server":server}))
    if server not in config['minecraft'].keys():
        await inter.response.send_message(content="Invalid server name given. Use /infoall to get a list of all servers. Remember that names are case sensitive. ",ephemeral=True)
        return
    await inter.response.defer()
    address,port = fetch_address(server)
    await inter.edit_original_message(content=f"Server address: `{address}:{port}`. \n{rcon(server,'list')}")

@mcBot.slash_command(description="Gets all servers' information")
async def infoall(inter):
    asyncio.create_task(loginter("infoall",inter.author,{}))
    await inter.response.defer()
    resp = ""
    for server in config['minecraft'].keys():
        address,port = fetch_address(server)
        resp = f"{resp}\n**{server}:**\n    Server address: `{address}:{port}`. \n    {rcon(server,'list')}"
    if config['bungeecord'] == 1:
        resp = f"{resp}\n\n_BungeeCord is enabled. This means you can connect to all servers using the same address and navigate between servers using `/server [server name]` in Minecraft._"
    await inter.edit_original_message(content=resp)

@mcBot.slash_command(description="Checks server address")
async def checkaddress(inter,server:str = commands.Param(autocomplete=autocomp_servers)):
    """
    Checks server address

    Parameters
    ----------
    server: The server this is for
    """
    asyncio.create_task(loginter("checkaddress",inter.author,{"server":server}))
    if config['bungeecord'] == 1 and not bungee_running:
        await asyncio.create_task(bungee_server())
    if server not in config['minecraft'].keys():
        await inter.response.send_message(content="Invalid server name given. Use /infoall to get a list of all servers. Remember that names are case sensitive. ",ephemeral=True)
        return
    await inter.response.defer()
    await inter.edit_original_message(content="Pinging current address...")
    address,port = fetch_address(server)
    connectcode = ping(server,address,port)
    if connectcode == 0:
        await inter.edit_original_message(content=f"I am able to ping the server at `{address}:{port}`. \nCheck that the address you set in Minecraft matches this. If it's correct, check your network connection and firewall settings. ")
    elif connectcode == -1:
        await inter.edit_original_message(content="The server is not running. Please start the server to check the address. ")
    elif connectcode == -2:
        await inter.edit_original_message(content="The server is either starting up, or shutting down. Please wait a bit, and then try again. ")
    else:
        await inter.edit_original_message(content="The current address is incorrect. Fetching new address...")
        extip = urlopen("https://ident.me").read().decode("utf8")
        await inter.edit_original_message(content="Fetched new address. Pinging...")
        connectcode = ping(server,extip,port)
        if connectcode == 0:
            if config['bungeecord'] == 1:
                config['server_address'] = extip
            else:
                config['minecraft'][server]['server_address'] = extip
            await inter.edit_original_message(content=f"Found new address! New address: `{extip}:{port}`")
        else:
            opping = ""
            for i in config['bot_op']:
                opping = f"{opping}<@{i}> "
            await inter.edit_original_message(content=f"I was unable to get a new working address for the server. Please ask the bot host to update the `server-address` field and restart the bot. \nAlternatively, ask {opping}to use the /setaddress command to update the server address. \nHowever, you may try this address: `{extip}`. ")
    update_yml()

@mcBot.slash_command(description="Get help on all commands")
async def help(inter):
    asyncio.create_task(loginter("help",inter.author,{}))
    await inter.response.send_message("There are 6 commands that are available to use. \n`/start`: Starts a server. \n`/info`: Gets server information. \n`/stop`: Stops a server. Only useful if you want to free up server slots. \n`/checkaddress`: Checks whether the given server address works. \n`/infoall`: List all servers and provide information about each of them. \n`/stopall`: Stops all servers. Only useful if you want to free up as many server slots as possible. ")

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
    asyncio.create_task(loginter("setaddress",inter.author,{"address":address,"port":port,"server":server}))
    if config['bungeecord'] == 1 and not bungee_running:
        await asyncio.create_task(bungee_server())
    if inter.author.id not in config['bot_op']:
        await inter.response.send_message(content="You don't have access to this command! ",ephemeral=True)
        return
    if server not in config['minecraft'].keys():
        await inter.response.send_message(content="Invalid server name given. Use /infoall to get a list of all servers. Remember that names are case sensitive. ",ephemeral=True)
        return
    await inter.response.defer()
    connectcode = ping(server,address,port)
    if connectcode == 0:
        await inter.edit_original_message(content="This address works. I will update it now. ")
        if config['bungeecord'] == 1:
            config['server_address'] = address
            config['server_port'] = port
        else:
            config['minecraft'][server]['server_address'] = address
            config['minecraft'][server]['server_port'] = port
    elif connectcode == -1:
        await inter.edit_original_message(content="The server is not running. Please start the server so I can check that this address works. ")
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
    asyncio.create_task(loginter("cmd",inter.author,{"server":server}))
    if inter.author.id not in config['bot_op']:
        await inter.response.send_message(content="You don't have access to this command! ",ephemeral=True)
        return
    if server not in config['minecraft'].keys():
        await inter.response.send_message(content="Invalid server name given. Use /infoall to get a list of all servers. Remember that names are case sensitive. ",ephemeral=True)
        return
    await inter.response.defer()
    await inter.edit_original_message(content=f"Rcon: {rcon(server,command)}")

@mcBot.event
async def on_message(message):
    if message.author.bot:
        return  
    for channel in config['discord'].keys():
        try:
            if config['discord'][channel]['channels'][message.channel.name] == message.channel.id:
                valid = True
        except (KeyError,AttributeError):
            return
    if not valid:
            return
    fileprops = list()
    valid = False
    cleanmsg = message.clean_content.split('"')
    cleanedmsg = ""
    for i in cleanmsg:
        cleanedmsg = f'{cleanedmsg}{i}\\"'
    cleanedmsg = cleanedmsg[:len(cleanedmsg)-2]
    resp = rcon(message.channel.name,'tellraw @a "{'+str(message.author)+'} '+cleanedmsg+'"]')
    if resp:
        msg = await message.channel.send(resp)
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except disnake.errors.HTTPException:
            pass
        try:
            await message.delete()
        except disnake.errors.HTTPException:
            pass
        return
    for attachment in message.attachments:
        if attachment.size >= 8388608:
            await message.channel.send(f"File `{attachment.filename}` was skipped! Bots cannot send files greater than 8 MB regardless of server boosting. This file was `{attachment.size}` bytes. ")
        else:
            fileprops.append([await attachment.read(),attachment.filename,attachment.is_spoiler()])
    try: 
        await message.delete()
    except disnake.errors.NotFound:
        pass
    await webhook_send(message.channel.name,message.content,message.author.name,message.author.avatar,fileprops=fileprops)

mcBot.run(config['bot_token'])
