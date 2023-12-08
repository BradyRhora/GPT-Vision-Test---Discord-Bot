
import io
import discord
import requests
import openai_chat
from openai import OpenAI
from discord.ext import commands, voice_recv

DISCORD_TOKEN = open('bottoken').read().strip()
OPEN_AI_TOKEN = open('openaitoken').read().strip()
COMMAND_PREFIX = '>'

discord.opus._load_default()
intents = discord.Intents.all()
intents.message_content = True
active_chat = None

openai_client = OpenAI(api_key=OPEN_AI_TOKEN)
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def dalle3(ctx, prompt):
    response = openai_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard"
    )

    url = response.data[0].url
    image_data = requests.get(url).content
    image_file = discord.File(io.BytesIO(image_data), filename="image.png")
    await ctx.send(file=image_file)


@bot.command()
async def chat(ctx, message):
    global active_chat
    if active_chat is None:
        active_chat = openai_chat.Chat(openai_client, ctx.channel.id)
        image_url = ctx.message.attachments[0].url if ctx.message.attachments else None
        response = active_chat.send_message(ctx.author.name, message, image_url)
        await ctx.send(response)
    elif message == 'end':
        active_chat = None
        await ctx.send('Chat ended.')
    else:
        await ctx.send('There is already an active chat.')

@bot.command()
async def join(ctx):
    def callback(user, data: voice_recv.VoiceData):
        print(f"Got packet from {user}")

        ## voice power level, how loud the user is speaking
        # ext_data = packet.extension_data.get(voice_recv.ExtensionID.audio_power)
        # value = int.from_bytes(ext_data, 'big')
        # power = 127-(value & 127)
        # print('#' * int(power * (79/128)))
        ## instead of 79 you can use shutil.get_terminal_size().columns-1

    if (ctx.author.voice is None):
        await ctx.send("You're not in a voice channel!")
        return
    
    vc = await ctx.author.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
    vc.listen(voice_recv.BasicSink(callback))

@bot.command()
async def leave(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)
    if len(message.content) > 0 and message.content[0] == COMMAND_PREFIX:
        return
    
    if active_chat is not None and active_chat.channel_id == message.channel.id:
        image_url = message.attachments[0].url if message.attachments else None
        response = active_chat.send_message(message.author.name, message.content, image_url)
        await message.channel.send(response)

bot.run(DISCORD_TOKEN)