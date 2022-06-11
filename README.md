This document is for v3.0 [Download here](https://github.com/MinecraftServerDiscordBot/minecraft-server-discord-bot-python/releases/tag/v3.0)

# Overview
Have you ever wanted a Discord Bot to start and manage your own Minecraft servers? If so, this program is for you! 

# Features
This bot can start your Minecraft servers from a Discord command and will shut them down automatically when inactive. Users can get information about the server such as its address and online players. They can also make the bot try to update the server address automatically. This bot also integrates your Minecraft and Discord chats without even modding your Minecraft server, and is capable of handling multiple servers along with [BungeeCord](https://www.spigotmc.org/wiki/bungeecord) support if you wish to use it. 

# Commands
### There are 5 commands that can be used by anyone: 
1. `/start <server> <delay>` will start the specified server if it's not already running. If provided, `delay` will delay the automatic inactive shutdown by the value given in seconds. 
2. `/info` will list all servers and provide information about each of them. Additionally, it also states if Bungeecord is enabled and what it means for the average user. 
3. `/stop` will attempt to shut down all Minecraft servers. **This is only useful if the maximum concurrent server limit has been reached.** 
4. `/checkaddress <server>` will check the server address given in `/info`. The bot will try to update the server address on its own if the address doesn't work. **Note: The `server` parameter becomes meaningless when using BungeeCord, but must be provided nonetheless.** 
5. `/help` will provide help with all commands
### These commands can be used only by the user(s) set in `server-op`: 
1. `/cmd <command> <server>` will execute a Minecraft command on the specified server. 
2. `/setaddress <address> <port> <server>` will take a new server address and check it. If it's valid, the bot will start using that address moving forward. **Note: The `server` parameter becomes meaningless when using BungeeCord, but must be provided nonetheless.** 

# Installation
If you are upgrading from an old version, follow [these instructions](#upgrading-from-old-versions). <br />If you are running this for the first time, follow [these instructions](#first-time-installation). 
## Upgrading from old versions
### Upgrading from v2.0 or earlier
You need to upgrade to v2.1 at least in order to use the new upgrading system. 
### Upgrading from v2.1 or v2.2
You do not need change anything for the base functionality. Simply copy `upgrader.py` and the new `bot.py` to the same folder that you were using earlier. Make a backup of your `bot.env`, and run `upgrader.py` and enter your version when prompted. If all goes well, you should be left with a new file called `bot.yaml`, and all your server files moved to a newly created folder. You can now run the new `bot.py` and it will work fine. To get a sense of how the bot works and how you can customise it, refer [this section](#about-`bot.yaml`). 
## First time installation
### Setting up the Discord bot
Go to the [Discord Developer site](https://discord.com/developers/), and create a new application. Now go to the "Bot" section and build a bot. <br />
Head over to the "OAuth2" section, and under it, the "URL Generator" section. Under "Scopes", check `bot` and `applications.commands`. <br />
Under "Bot Permissions", select the permission "Administrator". At the very bottom, there will be a "Generated URL". <br />
Copy it and paste it in your browser. This will allow you to invite your bot to your server. <br />

### Setting up a Minecraft server
If you haven't already, set up your Minecraft server on your machine as normal. Now go to your `server.properties` file. <br />
Change the following values: 
- `enable-rcon=true` 
- `rcon.password=<password>`, where `password` is the password you wish to use for Rcon. <br />
Now, go to the folder your `bot.py` is in and make a new folder. This folder will be your server name. **Note: `logs`,`bungeecord` are reserved names. They are case insensitive, meaning `LoGs` is still an illegal name.** Move the server files in this folder. 
 
### Setting up the Bot variables
It is recommended that you read through [this section](#about-`bot.yaml`) to get an understanding of how the YAML works first, and then follow these instructions, however it isn't strictly required. <br />
(WIP)

### Setting up your Discord server
Open `bot.yaml`, and go the `discord` section. <br />
*You may repeat the following steps as many times as you need to. <br />*
Create a new channel for the Discord-Minecraft chat integration in any Discord server you wish and copy its ID. Make a new line under `discord` and paste the ID. Refer [this section](#about-`bot.yaml`) to understand what it should look like. 

# About `bot.yaml`
(WIP)

# Important notes
- The Minecraft -> Discord integration works off the fact that messages sent by players show up as `<player> message` in the console. Therefore, any mods that change the chat format are very likely to break this feature. However, it is definitely worth trying such mods since there is a chance that some of them may work normally. 
