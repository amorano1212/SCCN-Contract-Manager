import os
import discord
from discord.ext import commands
import asyncio
import logging
from bot.commands import setup_commands

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EliteDangerousBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        # Remove privileged intents to avoid permission issues
        # intents.message_content = True  # This is a privileged intent
        super().__init__(command_prefix='!', intents=intents)
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        await setup_commands(self)
        logger.info("Bot setup completed")
        
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

async def main():
    """Main function to run the bot"""
    # Get Discord token from environment variables
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set!")
        return
    
    bot = EliteDangerousBot()
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot shutting down...")
        await bot.close()
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
