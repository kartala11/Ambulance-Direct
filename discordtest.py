import discord
from discord.ext import commands

# Initialize the bot with your token
TOKEN = 'MTI4NTU0NzgyMjEwNzg1Njg5Ng.GlDLrh.eLjUj9JdBFXNPrH_zK9AaHH8EdzC_FYuojpQio'

intents = discord.Intents.default()
intents.members = True  # Allows the bot to access member details in the server
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    # The username of the user to whom you want to send the DM
    target_username = 'vani_80802'  # Replace with the actual username

    # The message you want to send
    message_to_send = "Hello! This is an automated message"

    # Find the user and send the message
    for guild in bot.guilds:
        for member in guild.members:
            print(member)
            if member.name == target_username:
                await member.send(message_to_send)
                print(f'Message sent to {member.name}')
                return

    print(f'User {target_username} not found.')

# Run the bot
bot.run(TOKEN)
