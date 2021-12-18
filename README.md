# Overview
Do you want a Discord Bot to start your Minecraft server? This program will help you do just that!

# Features
This script starts your Minecraft server and shuts it down too! It also shuts down the server when it's inactive. 

# Commands
There are 4 commands that can be used. 
1. `$start` will start the Minecraft server if it's not already running. 
2. `$stop` can be used to manually shut down the Minecraft server. However, it only shuts down if no players are online. 
3. `$check` will tell you whether the server is running. 
4. `$help` can be used to get information on these commands on Discord.

# Installation
## Setting up the Discord bot
Do this ONLY IF you are setting this up for the first time!
Go to https://discord.com/developers, and create a new application. Now go to the "Bot" section and build a bot. Head over to the "OAuth2" section, and under it, the "URL Generator" section. Under "Scopes", check the "bot" option. Under "Bot Permissions", select the permissions "Send Messages", "Read Message History". At the very bottom, there will be a "Generated URL". Copy it and add it to your server.

## Setting up the Minecraft server
If you haven't already, set up your Minecraft server on your machine. Open the "server.properties" file. Change the parameters as shown below:
1. `rcon.port=25575`
2. `enable-rcon=true`
3. `rcon.password=<password>`, where <password> is the password you wish to use. If you don't see these parameters, simply add them at the bottom of the file. 
Rename your launch script to "run.bat". 

## Setting up the bot script
Open command prompt and run "pip install mcrcon". Open the env file and paste your Discord bot token, the RCON IP (same as the server ip), and your RCON password (as set in the server.properties file). Make sure the bot program, the env file, your launch script, and server.properties files are in the same folder. 
  
That's it! Now just run the bot program! 
