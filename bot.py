import discord
from discord.ext import commands
import re
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

token = os.getenv("token")

def identify_urls(text):
    # Finds and returns all URLs in a given text.
    url_pattern = re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
    return re.findall(url_pattern, text)

# Define intents (permissions your bot needs)
intents = discord.Intents.default()
intents.message_content = True  # Necessary for reading message content
intents.members = True #Allows for sending DM's of the receipt for the message

# Create bot instance with command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)  # You can change the prefix

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print('------')
    await bot.change_presence(activity=discord.Activity(name="Make sure to give feedback!")) # Sets status as "Make sure to give feedback"
    
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    feedback_channel_id = 123456789012345678  # Replace with the actual channel ID
    # message.channel.id == feedback_channel_id and message.channel.type == discord.ChannelType.text:
    if message.channel.id == feedback_channel_id and message.channel.type == discord.ChannelType.text:
        if not message.reference and not message.mentions:  # Check for both conditions at once
            if any(url in message.content for url in identify_urls(message.content)) or message.attachments:
                async for previous_message in message.channel.history(limit=2, before=message):  # Check the 2 previous messages
                    if previous_message.mentions and previous_message.author == message.author:
                        return
                try:  # Wrap in a try-except to handle potential errors
                    await message.author.send("Here is a copy of your message for convenience. Make sure to give proper feedback first before requesting feedback of your own so that everyone can benefit :D\n\n" + message.content)
                    if message.attachments:
                        for attachment in message.attachments:
                            file = await attachment.to_file()
                            await message.author.send(file=file)

                except discord.HTTPException:
                    await message.reply("Make sure to give feedback first!")
                    
                await message.delete() #Remove the no feedback request
                return

    
    await bot.process_commands(message)

# Example command
@bot.command()  # Creates a command called !hello
async def hello(ctx):  # ctx is the context (information about the command invocation)
    await ctx.send()


# Example error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found.")
    else:  # For more complex error handling, log the error and send a generic message
        print(f"An error occurred: {error}")
        await ctx.send("An error occurred while processing your command.")





# Run the bot
bot.run(token)


