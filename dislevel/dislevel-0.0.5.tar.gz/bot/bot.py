from discord.ext import commands
from dislevel import increase_xp


bot = commands.Bot(command_prefix="?")
bot.load_extension("jishaku")
bot.load_extension("dislevel")

@bot.event
async def on_message(message):
    if not message.author.bot:
        await bot.process_commands(message)
        await increase_xp(message, bot)

bot.run("ODU3OTAzMDg1NjY1NTE3NTg4.YNWWgg.CgD11dh0hRpLuMV3pT3QaUh0XAU")
