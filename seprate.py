import json
import re
from pyrogram import Client, filters
from pyrogram.types import Message

# Aapke credentials
API_ID = 26950458
API_HASH = "d818b8d530e4a9b209509815ab1b9c7c"

# Isme bot token nahi, apna Telegram account login hoga
app = Client("my_account", api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.me & filters.command("link", prefixes="."))
async def extract_link_user(client: Client, message: Message):
    # Reply kiye huye message ko target karein
    target = message.reply_to_message
    if not target:
        await message.edit_text("❌ Kisi bhi preview waale message ko **reply** karke `.link` likho.")
        return

    extracted_links = set()

    # 1. Web Page Preview URL
    if target.web_page:
        if target.web_page.url:
            extracted_links.add(target.web_page.url)
        if target.web_page.display_url:
            extracted_links.add(target.web_page.display_url)

    # 2. Raw JSON string me se deep regex search
    raw_json = str(target)
    found_urls = re.findall(r'(https?://[^\s",]+|t\.me/(?:\+|joinchat/)?[a-zA-Z0-9_\-]+)', raw_json)
    for u in found_urls:
        extracted_links.add(u.replace('\\/', '/'))

    # Result show karega
    if extracted_links:
        res = "✅ **Extracted Group / Hidden Link:**\n\n"
        for l in extracted_links:
            res += f"🔗 `{l}`\n"
        await message.edit_text(res)
    else:
        await message.edit_text("❌ Koi web_page preview link nahi mila.")

app.run()
