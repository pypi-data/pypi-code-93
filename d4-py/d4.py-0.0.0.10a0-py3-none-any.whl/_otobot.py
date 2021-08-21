import __init__ as d4

client = d4.Client(prefix="!", print_log=False)


@client.EventListener
async def ready():
    print("Bot is ready!")


@client.EventListener
async def interaction_create(interaction):
    if interaction.data.custom_id:
        await interaction.reply(f"The custom id for this button is {interaction.data.custom_id}.")


@client.cmd(name="ping")
async def ping(msg):
    await msg.get_channel().send("pong!")


@client.cmd()
async def time(msg):
    import time
    await msg.channel.send(time.strftime("%Y-%m-%d"))


@client.cmd()
async def me(msg):
    await msg.channel.send(f"Name: {msg.author.username}\nID: {msg.author.id}")


@client.cmd(name="createButton", aliases=["button", "create", "buttons"])
async def buttons_(msg):
    myButton = d4.Button(type=1, text="Test Button", customId="simpleId")
    await myButton.send(msg)

client.login("ODYzNjc2NTIwODA2NDgxOTIx.YOqXcA.170WwW7xjC8UOUZ8KcxPp9N3_k" + "k")
