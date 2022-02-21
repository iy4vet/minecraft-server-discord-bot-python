This document is for v2.2. [Download here](https://github.com/MinecraftServerDiscordBot/minecraft-server-discord-bot-python/releases/tag/v2.2). 

# Overview
Do you want a Discord Bot to start and manage your Minecraft server? This program will help you do just that! 

## Features
This script can start your Minecraft server from a Discord command and will shut it down automatically when inactive! Users can get information about the server such as its address and online players. If the address changes, users can request a new address and the bot will get one automatically! It can also integrate your Discord and Minecraft servers' chats! <br /><br />
For the server host, this program works entirely using vanilla methods, meaning you don't have to add any mods to your Minecraft server! 

## Commands
### There are 6 commands that can be used by anyone: 
1. `/start` will start the Minecraft server if it's not already running. 
2. `/stop` will shut down the Minecraft server if no players are online.  
3. `/info` will give you the server information. 
4. `/ipcheck` will check the server address given in `/info`. The bot will try to update the server address on its own if the address doesn't work. 
5. `/say <message>` will send a message in the Minecraft server if it's running. The message will appear as `{username#0000} <message>`. **This command is still usable, but is discouraged in favour of a new and better feature.** 
6. `/help` can be used to get information on these commands on Discord. 
### These commands can be used only by the user(s) set in `server-op`: 
1. `/cmd <command>` will execute a Minecraft command. For example, `/cmd time set 0`. The bot will respond with the output, in this case `Rcon: Set the time to 0`. 
2. `/ipset <address> <port>` will take a new server address and check it. If it's valid, the bot will start using that address moving forward. Providing a new port is optional: the bot defaults to the current server port. This will be reset when the bot restarts. 

## Installation
Follow these steps: 
### Setting up the Discord bot
#### Do this part ONLY IF you are setting this up for the first time! v2.1 requires you to redo this section. 
Go to [the Discord Developer site](https://discord.com/developers/), and create a new application. Now go to the "Bot" section and build a bot. <br />
Head over to the "OAuth2" section, and under it, the "URL Generator" section. Under "Scopes", check `bot` and `applications.commands`. <br />
Under "Bot Permissions", select the permission "Administrator". At the very bottom, there will be a "Generated URL". <br />
Copy it and paste it in your browser. This will allow you to invite your bot to your server. <br />

### Setting up the Minecraft server
If you haven't already, set up your Minecraft server on your machine as normal. Now go to your `server.properties` file. <br />
Change the following values: 
- `enable-rcon=true` 
- `rcon.password=<password>`, where \<password\> is the password you wish to use for Rcon.  
 
### Setting up the Bot variables
Open the file named `bot.env`. 
1. Paste your Discord bot token next to `bot-token`. 
2. Paste the server address that other players would use to connect next to `server-address`. 
3. Paste the server start script next to `start-script`. (For example, `start-script=java -Xmx2G -Xms512M -jar server.jar`)
4. Paste the user ID of the account that shall be allowed to execute commands through Rcon next to `server-op`. If you want multiple users, separate each one with `,`. For example: `server-op=123,456,243,632`. Do not use spaces. 
5. For `chat-channel-id`, refer to the [Discord server setup section](#setting-up-your-discord-server). 

### Setting up your Discord server
Create a new channel for the Discord-Minecraft chat integration. <br />
 Copy its ID and paste it under `chat-channel-id`. <br />
 If you want multiple channels, simply separate each ID with `,`, similar to `server-op`. Do not use spaces. <br />
 
### Important notes
- Minecraft connects to port 25565 by default. If you forward any port other than 25565, your address would look something like `xxx.xxx.xxx.xxx:port` since the port must also be specified for Minecraft. This CAN be set in `bot.env`, in which case the program pings the server on `port`. However, if you use port 25565, you may leave the address as `xxx.xxx.xxx.xxx` and the program will use port 25565 automatically. 
- The Minecraft -> Discord integration works off the fact that messages sent by players show up as `<player> message` in the console. Therefore, any mods that change the chat format are very likely to break this feature. However, it is definitely worth trying such mods since there is a chance that some of them may work normally. 
