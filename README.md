# Overview
Do you want a Discord Bot to start your Minecraft server? This program will help you do just that!

## Features
This script starts your Minecraft server and shuts it down too! It also shuts down the server when it's inactive. 

## Commands
### There are 5 commands that can be used by anyone: 
1. `$start` will start the Minecraft server if it's not already running. 
2. `$stop` will shut down the Minecraft server if no players are online.  
3. `$info` will give you the server information. 
4. `$ip-check` will check the server address given in `$info`. The bot will try to update the server address on its own if the address doesn't work. 
5. `$help` can be used to get information on these commands on Discord.
### These commands can be used only by the user set in `server-op`: 
1. `$rcon` will execute the command given after the `$rcon ` command. Only usable by the server operator (can be set to any one person). 
2. `$ip-set` will take a new server address and check it. If it's valid, the bot will start using that address moving forward (will be reset after restarts). 

## Installation
Follow these steps: 
### Setting up the Discord bot
#### Do this part ONLY IF you are setting this up for the first time! 
Go to [the Discord Developer site](https://discord.com/developers/), and create a new application. Now go to the "Bot" section and build a bot. 
Head over to the "OAuth2" section, and under it, the "URL Generator" section. Under "Scopes", check the "bot" option.
Under "Bot Permissions", select the permissions "Send Messages", "Read Message History". At the very bottom, there will be a "Generated URL".
Copy it and paste it in your browser. This will allow you to invite your bot to your server. 

### Setting up the Minecraft server
If you haven't already, set up your Minecraft server on your machine as normal. Now go to your `server.properties` file. 
Change the following values:
- `rcon.port=25575`
- `enable-rcon=true`
- If you'd like, you can set your own Rcon password. The program will automatically set a password if you leave it blank. 

### Setting up the Bot variables
Open the file named `bot.env`. 
1. Paste your Discord bot token next to `bot-token`. 
2. Paste the server address that other players would use to connect next to `server-address`. 
3. Paste the server start script next to `start-script`. (For example, `start-script=java -Xmx2G -Xms512M -jar server.jar`)
4. Paste the user ID of the account that shall be allowed to execute commands through Rcon next to `server-op`. 

### Important notes
1. Given that Minecraft connects to port 25565 by default, this program also pings `server-address` on port 25565. If you forward any port OTHER than 25565, your address would look something like `xxx.xxx.xxx.xxx:port`. This CAN be set in `bot.env`, however it WILL NOT WORK with the `$ip-check` function! You may choose, then, to change the port you're forwarding, or remove the code for this function by deleting all code within `if msg == "$ip-check":`, including the if condition itself. 
2. The Rcon port must be set to 25575. If you had set a different value and were forwarding that port, you only need to change the internal port to 25575, and the external port will continue to work as it did before. Note that the Rcon port and server port are different things altogether. 
