import re
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType

# Apne credentials yahan dalein
API_ID =  26950458
API_HASH = "d818b8d530e4a9b209509815ab1b9c7c"
BOT_TOKEN = ""

app = Client("link_extractor_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    await message.reply_text(
        "👋 Mujhe koi bhi message forward ya send karo. Main uske hidden link, web_page preview link, user ID, aur text sab alag-alag extract kar dunga!"
    )

@app.on_message(filters.private & ~filters.command(["start"]))
async def extract_handler(client: Client, message: Message):
    extracted_links = set()
    extracted_user_ids = set()
    
    # 1. Web Page Preview link check (Jo Telegram embed mein hota hai par text mein nahi dikhta)
    if message.web_page and message.web_page.url:
        extracted_links.add(message.web_page.url)

    # 2. Forwarded message se user ID check
    if message.forward_from:
        extracted_user_ids.add(f"Forwarded User ID: `{message.forward_from.id}` (@{message.forward_from.username or 'No Username'})")
    elif message.forward_from_chat:
        extracted_user_ids.add(f"Forwarded Channel/Chat ID: `{message.forward_from_chat.id}`")

    # 3. Message entities (Hidden hyperlinks, Text mentions, raw URLs)
    raw_text = message.text or message.caption or ""
    entities = message.entities or message.caption_entities or []

    for ent in entities:
        if ent.type == MessageEntityType.TEXT_LINK:
            # Hyperlinked text ke peeche ka hidden link
            extracted_links.add(ent.url)
        elif ent.type == MessageEntityType.URL:
            # Text mein likha hua normal link
            link = raw_text[ent.offset : ent.offset + ent.length]
            extracted_links.add(link)
        elif ent.type == MessageEntityType.TEXT_MENTION:
            # Inline mention ki User ID
            if ent.user:
                extracted_user_ids.add(f"Mentioned User ID: `{ent.user.id}`")

    # 4. Regex se phone numbers aur baaki URLs nikalna
    regex_urls = re.findall(r'(https?://[^\s]+|t\.me/[^\s]+)', raw_text)
    for u in regex_urls:
        extracted_links.add(u)

    phone_numbers = re.findall(r'\b(?:\+?\d{1,3}[- ]?)?\d{10}\b', raw_text)

    # Output formatting
    output = ["**🔍 Extracted Details:**\n"]

    if extracted_links:
        output.append("🔗 **Links / Preview URLs:**")
        for link in extracted_links:
            output.append(f"• `{link}`")
        output.append("")

    if extracted_user_ids:
        output.append("👤 **User / Chat IDs:**")
        for uid in extracted_user_ids:
            output.append(f"• {uid}")
        output.append("")

    if phone_numbers:
        output.append("📞 **Phone / Numbers Found:**")
        for num in set(phone_numbers):
            output.append(f"• `{num}`")
        output.append("")

    if raw_text:
        output.append(f"📝 **Clean Text:**\n`{raw_text}`\n")

    result_text = "\n".join(output)

    # Agar photo attached hai toh use alag se bhejega
    if message.photo:
        await message.reply_photo(
            photo=message.photo.file_id,
            caption=result_text
        )
    else:
        await message.reply_text(result_text)

if __name__ == "__main__":
    app.run()
