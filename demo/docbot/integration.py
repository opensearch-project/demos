# Using a connection from the OpenSearch connection builder
# to see an example of using the opensearch connection builder
# check out tests/test_util.py

# Here we will create classes for connecting into services like Discord
# We should use the discord python client here
import discord, sys
import dotenv
from os import getenv

sys.path.append('./demo/')
print(sys.path)
from docbot.controller import Controller
from docbot.util import opensearch_connection_builder

dotenv.load_dotenv()
DISCORD_TOKEN = getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
docbot = Controller(opensearch_connection_builder())

conversation_history = {}


@client.event
async def on_ready():
  print(f'Successfully logged in as {client.user}')


@client.event
async def on_message(message):
  global conversation_history
  if message.author == client.user:
    return
  # WIP
  if message.content.startswith('!docbot'):
    response = docbot.handle_message(message)
    await message.channel.send("History so far: " + str(conversation_history) + " Response: " +
                               response)
    await message.channel.send("Channel: " + message.channel.name + " Author: " +
                               message.author.name + " Message: " + message.content[7:])
  else:
    conversation_history.update({
      message.id: {
        "channel": message.channel.name,
        "author": message.author.name,
        "content": message.content
      }
    })


client.run(DISCORD_TOKEN)
