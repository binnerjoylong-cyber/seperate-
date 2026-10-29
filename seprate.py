import json
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType

API_ID = 26950458
API_HASH = "d818b8d530e4a9b209509815ab1b9c7c"
BOT_TOKEN = ""  
app = Client("link_extractor_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def extract_all_links_from_json(data):
    links = set()
    raw_str = json.dumps(data)
    found_urls = re.findall(r'(https?://[^\s",]+|t\.me/(?:\+|joinchat/)?[a-zA-Z0-9_\-]+)', raw_str)
    for u in found_urls:
        links.add(u.replace('\\/', '/'))
    return links

@app.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    await message.reply_text("Forward ya send karo, main JSON dump aur hidden preview links dono nikaal dunga!")

@app.on_message(filters.private & ~filters.command(["start"]))
async def extract_handler(client: Client, message: Message):
    raw_dict = json.loads(str(message))
    all_links = extract_all_links_from_json(raw_dict)
    
    if message.web_page and message.web_page.url:
        all_links.add(message.web_page.url)

    entities = (message.entities or []) + (message.caption_entities or [])
    for ent in entities:
        if ent.type == MessageEntityType.TEXT_LINK and ent.url:
            all_links.add(ent.url)
        elif ent.type == MessageEntityType.URL:
            text = message.text or message.caption or ""
            all_links.add(text[ent.offset : ent.offset + ent.length])

    raw_text = message.text or message.caption or ""
    phone_numbers = re.findall(r'\b(?:\+?\d{1,3}[- ]?)?\d{10}\b', raw_text)

    response = []
    
    if all_links:
        response.append("🔗 **Extracted Hidden Links:**")
        for l in all_links:
            response.append(f"• `{l}`")
        response.append("")
    else:
        response.append("⚠️ **Link preview Telegram Bot API ne strip kar diya hai.**\n(Telegram forwards me kabhi-kabhi web_page preview bot ko pass nahi hota).")
        response.append("")

    if phone_numbers:
        response.append("📞 **Phone Numbers:**")
        for num in set(phone_numbers):
            response.append(f"• `{num}`")
        response.append("")

    if message.forward_from_chat:
        response.append(f"📢 **Forwarded From Chat ID:** `{message.forward_from_chat.id}`\n")
    if message.forward_from:
        response.append(f"👤 **Forwarded From User ID:** `{message.forward_from.id}`\n")

    response_text = "\n".join(response)
    await message.reply_text(response_text)

    if not all_links:
        with open("dump.json", "w", encoding="utf-8") as f:
            json.dump(raw_dict, f, indent=4, ensure_ascii=False)
        await message.reply_document("dump.json", caption="📄 Message ka complete Raw JSON Dump")

if __name__ == "__main__":
    app.run()
