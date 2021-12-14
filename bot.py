import discord
import os
import threading
import time

mcHost = discord.Client()
token = ""
running=False

def server():
    global running
    os.system(r"")
    time.sleep(1)
    running=False
    print ("Server stopped. ")

@mcHost.event
async def on_ready():
    print("Logged in as {0.user}".format(mcHost))
    await mcHost.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="if someone wants to play"))

@mcHost.event
async def on_message(message):
    global running
    msg = message.content
    if msg.startswith("!start"):
        if running==False:
            await message.channel.send("Starting Skoolkraft SMP. ")
            server_thread=threading.Thread(target=server)
            server_thread.daemon = True
            server_thread.start()
            running=True
            print("Server started")
        else:
            await message.channel.send("Server is already running! ")
    if msg.startswith("!check"):
        await message.channel.send("Server running: "+str(running))

mcHost.run(token)
