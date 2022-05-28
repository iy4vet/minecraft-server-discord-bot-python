import os
from pkg_resources import require
from random import randint

requirements = ["pyyaml==6.0","python-dotenv==0.19.2"]
for requirement in requirements:
    try:
        require(requirement)
    except:
        os.system(f"pip install {requirement}")

import yaml
from dotenv import load_dotenv


def below3p0(server):
    print("Loading bot.env")
    load_dotenv(dotenv_path=f"{os.getcwd()}/bot.env")

    print("Moving server files")
    try:
        os.mkdir(f"{os.getcwd()}/{server}")
    except:
        below3p0(f"{server}{randint(0,9)}")
        input("Press enter to exit...")
        exit(code=0)
    rmfiles = {"bot.py","upgrade.py","bot.env",f"{server}"}
    movefiles = set(os.listdir(os.getcwd())) - rmfiles
    for file in movefiles:
        os.replace(f"{os.getcwd()}/{file}",f"{os.getcwd()}/{server}/{file}")

    print("Reading bot.env")
    config = dict()

    config['bot_token'] = os.getenv("bot-token")
    config['server_address'] = os.getenv("server-address").split(":")[0]

    try: config['server_port'] = int(os.getenv("server-address").split(":")[1])
    except: config['server_port'] = 25565

    config['minecraft'] = dict()
    config['minecraft'][f'{server}'] = dict()
    config['minecraft'][f'{server}']['start_script'] = os.getenv("start-script")

    config['bot_op'] = [int(i) for i in os.getenv("server-op").split(",")]
    config['discord'] = [int(i) for i in os.getenv("chat-channel-id").split(",")]

    config['bungeecord'] = 0
    config['mc_url'] = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/i/977e8c4f-1c99-46cd-b070-10cd97086c08/d36qrs5-017c3744-8c94-4d47-9633-d85b991bf2f7.png"
    config['server_max_concurrent'] = -1
    config['server_title'] = "A Minecraft Server"
    config['version'] = "v3.0"

    print("Creating bot.yaml")
    with open(f"{os.getcwd()}/bot.yaml", 'w') as file:
        yaml.dump(config, file)

    print("Deleting bot.env")
    os.remove("bot.env")
    
    print("Done!")


if os.path.exists(f"{os.getcwd()}/bot.yaml"):
    with open(f"{os.getcwd()}/bot.yaml") as file:
        config = yaml.load(file,Loader=yaml.FullLoader)
        try:
            currentversion = config['version']
        except KeyError:
            print("A YAML exists, but it appears to be missing the version number. Check your bot.yaml against the example provided on the GitHub page. ")
    if currentversion in ["v3.0"]:
        print("You are on the latest version. ")
else:
    currentversion = str(input("Enter currently installed version (example: v2.2): "))
    if currentversion in ["v2.1","v2.2"]:
        below3p0("Server")
    else:
        print("This version is either missing key features for upgradation or is nonexistent. Please update to v2.1 or later and try again. ")

input("Press enter to exit...")
