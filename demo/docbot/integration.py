# Using a connection from the OpenSearch connection builder
# to see an example of using the opensearch connection builder
# check out tests/test_util.py

# Here we will create classes for connecting into services like Discord
# We should use the discord python client here
import discord, sys
import dotenv
from os import getenv
dotenv.load_dotenv()
DISCORD_TOKEN= getenv("DISCORD_TOKEN")


sys.path.append('./demo/')
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Successfully logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!docbot'):
        msg = message.content
        await message.channel.send('This is what you sent: ' + msg)
client.run(DISCORD_TOKEN)
