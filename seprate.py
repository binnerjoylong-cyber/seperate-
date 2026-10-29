import re
import json
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType

API_ID = 39727110
API_HASH = "cb8629e4ee38ddd7a62d53f4e4555e7d"
STRING_SESSION = ""

app = Client(
    "user_extractor",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

@app.on_message(filters.me & filters.command("link", prefixes="."))
async def get_hidden_link(client: Client, message: Message):
    target = message.reply_to_message
    if not target:
        await message.edit_text("❌ Dir reply 3la el message li fih el preview w kteb `.link`")
        return

    extracted_links = set()

    # 1. Tjbed web_page preview link direct
    if target.web_page:
        if target.web_page.url:
            extracted_links.add(target.web_page.url)
        if target.web_page.display_url:
            extracted_links.add(target.web_page.display_url)

    # 2. Text links w entities
    entities = (target.entities or []) + (target.caption_entities or [])
    raw_text = target.text or target.caption or ""
    for ent in entities:
        if ent.type == MessageEntityType.TEXT_LINK and ent.url:
            extracted_links.add(ent.url)
        elif ent.type == MessageEntityType.URL:
            extracted_links.add(raw_text[ent.offset : ent.offset + ent.length])

    # 3. Deep regex search f raw data
    raw_dump = str(target)
    found_urls = re.findall(r'(https?://[^\s",]+|t\.me/(?:\+|joinchat/)?[a-zA-Z0-9_\-]+)', raw_dump)
    for u in found_urls:
        clean_url = u.replace('\\/', '/')
        extracted_links.add(clean_url)

    # Natija
    if extracted_links:
        res = "✅ **Extracted Hidden Links:**\n\n"
        for l in extracted_links:
            res += f"🔗 `{l}`\n"
        await message.edit_text(res)
    else:
        # Ila malqash link, ykhtar dump file bach tchouf raw data
        await message.edit_text("⚠️ Malqash link f preview. Ha raw JSON:")
        with open("raw_message.json", "w", encoding="utf-8") as f:
            f.write(raw_dump)
        await client.send_document(message.chat.id, "raw_message.json")

app.run()
