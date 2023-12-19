# Using a connection from the OpenSearch connection builder
# to see an example of using the opensearch connection builder
# check out tests/test_util.py

# Here we will create classes for connecting into services like Discord
# We should use the discord python client here
import discord, sys
import dotenv
from os import getenv
from docbot import DocBot
dotenv.load_dotenv()
DISCORD_TOKEN= getenv("DISCORD_TOKEN")


sys.path.append('./demo/')
intents = discord.Intents.default()
intents.message_content = True


client = discord.Client(intents=intents)
docbot = DocBot()

@client.event
async def on_ready():
    print(f'Successfully logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!docbot'):
        msg = message.content
        response = docbot.handle_message(msg)
        await message.channel.send(response)

client.run(DISCORD_TOKEN)
