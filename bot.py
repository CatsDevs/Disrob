import os
import asyncio
import unicodedata
from aiohttp import web
import discord

TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.getenv("PORT", "10000"))

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable is not set")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
client = discord.Client(intents=intents)

STYLES = {
    "Smile": "flag", "Flag": "flag", "Bold": "bold", "Italic": "italic",
    "Gothic": "gothic", "Bubble": "bubble", "Double": "double",
    "Small": "small", "Wide": "wide", "Mono": "mono",
    "Strike": "strike", "Underline": "underline", "Glitch": "glitch",
    "Zalgo": "zalgo", "Upside": "upside",
}

MAPS = {
    "bold": ("𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭", "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"),
    "italic": ("𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡", "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻"),
    "gothic": ("𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ", "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷"),
    "bubble": ("ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ", "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ"),
    "double": ("𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ", "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫"),
    "small": ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"),
    "wide": ("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ", "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"),
    "mono": ("𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉", "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣"),
}

def translate(text, style):
    upper, lower = MAPS[style]
    out = []
    for ch in text:
        if "A" <= ch <= "Z": out.append(upper[ord(ch)-65])
        elif "a" <= ch <= "z": out.append(lower[ord(ch)-97])
        else: out.append(ch)
    return "".join(out)

def flag_text(text):
    return " ".join(chr(0x1F1E6 + ord(ch.upper()) - 65) if ch.isascii() and ch.isalpha() else ch for ch in text)

def decorate(text, style):
    if style in MAPS: return translate(text, style)
    if style == "flag": return flag_text(text)
    if style == "strike": return "".join(ch + "\u0336" if not ch.isspace() else ch for ch in text)
    if style == "underline": return "".join(ch + "\u0332" if not ch.isspace() else ch for ch in text)
    if style == "upside":
        table = str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!?.,", "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz∀ᗺƆᗡƎℲƓHIſʞ⅃WNOԀΌᴚS┴∩ΛMX⅄Z¡¿˙'")
        return text.translate(table)[::-1]
    if style in ("glitch", "zalgo"):
        marks = ["\u0300","\u0301","\u0302","\u0303","\u0304","\u0307","\u0308","\u0310","\u0311","\u0312","\u0322","\u0323","\u0324","\u0325","\u0326","\u0327","\u0328","\u0332","\u0336","\u0338"]
        amount = 2 if style == "glitch" else 5
        return unicodedata.normalize("NFC", "".join(ch if ch.isspace() else ch + "".join(marks[(i*7+j*11)%len(marks)] for j in range(amount)) for i,ch in enumerate(text)))
    return None

async def health(request):
    return web.Response(text="Disrob is running")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()

@client.event
async def on_ready():
    print(f"Disrob logged in as {client.user} ({client.user.id})")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    content = message.content.strip()
    if content.lower() == "/styles":
        await message.delete()
        await message.channel.send("**Disrob styles:** " + ", ".join(STYLES.keys()))
        return
    if not content.lower().startswith("/text "):
        return
    payload = content[6:].strip()
    if "=" not in payload:
        await message.reply("Использование: /text Smile = Hello", mention_author=False)
        return
    style_name, text = payload.split("=", 1)
    style_name, text = style_name.strip(), text.strip()
    style = STYLES.get(style_name)
    if not style or not text:
        await message.reply(f"❌ Стиль {style_name} не найден. Используй /styles.", mention_author=False)
        return
    result = decorate(text, style)
    try:
        await message.delete()
    except discord.Forbidden:
        pass
    await message.channel.send(result)

async def main():
    await start_web_server()
    await client.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
