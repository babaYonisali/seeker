import discord
from discord.ext import commands
import os
from deepseek import DeepSeekAPI  # We'll create this in another file
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def seek(ctx, *, prompt):
    """
    Command to interact with DeepSeek API
    Usage: !seek <your prompt here>
    """
    try:
        # Send a "typing" indicator while processing
        async with ctx.typing():
            # Get response from DeepSeek
            deepseek_client = DeepSeekAPI(api_key=os.getenv('DEEPSEEK_API_KEY'))
            response = await deepseek_client.generate_response(prompt)
            
            # Send the response back to Discord
            await ctx.send(response)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN')) 