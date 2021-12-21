# Contributing to the bot

If you would like to contribute to the bot please follow these instructions to set a local development environment up

*Prerequisities: Install [Python](https://www.python.org/) on your local system*

## Setting up the Minecraft server
If you haven't already, set up your Minecraft server on your machine. Open the "server.properties" file. Change the parameters as shown below:
1. `rcon.port=25575`
2. `enable-rcon=true`
3. `rcon.password=<password>`, where \<password> is the password you wish to use. If you don't see these parameters, simply add them at the bottom of the file. 
Rename your launch script to "run.bat". 


## Running the bot

#### Setting up the Discord bot
Do this ONLY IF you are setting this up for the first time!
Go to https://discord.com/developers, and create a new application. Now go to the "Bot" section and build a bot. Head over to the "OAuth2" section, and under it, the "URL Generator" section. Under "Scopes", check the "bot" option. Under "Bot Permissions", select the permissions "Send Messages", "Read Message History". At the very bottom, there will be a "Generated URL". Copy it and paste it in your browser. Add the bot to your server. 

#### Step-by-step Instructions
1. Install `poetry`, a python package manager, with pip:
```shell
pip install -U poetry
```

2. Install the necessary dependencies for this project in the root directory with:
```shell
poetry install
```

3. Create a `.env` and update the [settings](#settings)
```shell
cp .env.example .env
```

4. Make sure the bot program, the env file, your launch script, and server.properties files are in the same folder.

5. Run the discord bot in development with:
```shell
poetry run task bot
```

#### Settings
BOT_TOKEN - The discord bot token

SERVER_IP - Server address that other players would connect to

RCON_IP - The internal server IP

RCON_PASS - Same value as the one in your `server.properties` file
