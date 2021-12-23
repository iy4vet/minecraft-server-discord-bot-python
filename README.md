# Overview
Do you want a Discord Bot to start your Minecraft server? This program will help you do just that!

## Features
This script starts your Minecraft server and shuts it down too! It also shuts down the server when it's inactive. 

## Commands
There are 7 commands that can be used. 
1. `$start` will start the Minecraft server if it's not already running. 
2. `$stop` will shut down the Minecraft server if no players are online. It confirms the shutdown by sending "Stopping the server". 
3. `$check` will tell you whether the server is running. 
4. `$ip` will give you the server address. 
5. `$list` will list all online players. 
7. `$rcon` will execute the command given after the `$rcon` command. Only usable by the server operator (can be set to any one person). 
7. `$help` can be used to get information on these commands on Discord.

## Installation
Follow these steps: 
### Setting up the Discord bot
#### Do this part ONLY IF you are setting this up for the first time! 
Go to [the Discord Developer site](https://discord.com/developers/), and create a new application. Now go to the "Bot" section and build a bot. 
Head over to the "OAuth2" section, and under it, the "URL Generator" section. Under "Scopes", check the "bot" option.
Under "Bot Permissions", select the permissions "Send Messages", "Read Message History". At the very bottom, there will be a "Generated URL".
Copy it and paste it in your browser. This will allow you to invite your bot to your server. 

### Setting up the Minecraft server
If you haven't already, set up your Minecraft server on your machine as normal. 
If you wish to set your own password for Rcon, you are free to do so. However, the program will set a default password if you leave it blank. 
Please note that this program uses port 25575 for Rcon and will thus modify your `server.properties` file. 
If you have any port forward rules for Rcon, please set the ports accordingly. 

### Setting up the Bot variables
Open the file named `bot.env`. 
1. Paste your Discord bot token next to `bot-token`. 
2. Paste the server address that other players would use to connect next to `server-address`. 
3. Paste the server start script next to `start-script`. (For example, `start-script=java -Xmx2G -Xms512M -jar server.jar`)
4. Paste the user ID of the account that shall be allowed to execute commands through Rcon next to `rcon-op`. 
