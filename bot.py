# (c) @LazyDeveloperr

import os
import asyncio
import traceback
lazy_pic = os.environ.get("LAZY_PIC","https://graph.org/file/2ae5861238c1dc4fd534e.jpg")
from binascii import (
    Error
)
from pyrogram import (
    Client,
    enums,
    filters
)
from pyrogram.errors import (
    UserNotParticipant,
    FloodWait,
    QueryIdInvalid
)
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message
)
from configs import Config
from configs import *
from handlers.database import db
from handlers.add_user_to_db import add_user_to_database
from handlers.check_user_status import handle_user_status
from handlers.force_sub_handler import (
    handle_force_sub,
    get_invite_link
)
import logging
import logging.config
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

from handlers.broadcast_handlers import main_broadcast_handler
from util.human_readable import humanbytes
from urllib.parse import quote_plus
from util.file_properties import get_name, get_hash, get_media_file_size
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import idle
from lazybot import Bot
from util.keepalive import ping_server
from lazybot.clients import initialize_clients
from aiohttp import web
from handlers import web_server
from pyrogram import Client, __version__
from pyrogram.enums import ParseMode
import sys

Bot.start()
loop = asyncio.get_event_loop()

PORT = "8080"

async def Lazy_start():
    print('\n')
    print(' Initalizing clients ')
    await initialize_clients()
    try:
        db_channel = await Bot.get_chat(Config.DB_CHANNEL)
        Bot.db_channel = db_channel
        test = await Bot.send_message(chat_id=db_channel.id, text="TEST")
        await test.delete()
        print("Bot is admin in db channel")

    except Exception as e:
        # Handle the exception, log it, and optionally take other actions
        print(e)  # Print the error for debugging
        print(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
        print("\nBot Stopped bYE")
        sys.exit()
    @Bot.on_message(filters.private)
    async def _(bot: Client, cmd: Message):
        await handle_user_status(bot, cmd)


    @Bot.on_message(filters.command("start") & filters.private)
    async def start(bot: Client, cmd: Message):

        if cmd.from_user.id in Config.BANNED_USERS:
            await cmd.reply_text("ꜱᴏʀʀʏ, ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ.")
            return
        if Config.UPDATES_CHANNEL is not None:
            back = await handle_force_sub(bot, cmd)
            if back == 400:
                return
        usr_cmd = cmd.text.split("_", 1)[-1]
        if usr_cmd == "/start":
            await add_user_to_database(bot, cmd)
            await cmd.reply_photo(photo=lazy_pic,
                caption=Config.LAZY_HOME_TEXT.format(cmd.from_user.first_name, cmd.from_user.id),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("🍿supp⊕r† gr⊕up", url="https://t.me/LazyDeveloperSupport"),
                            InlineKeyboardButton("🔊ß⊕†s chαηηεl", url="https://t.me/LazyDeveloper")
                        ],
                        [
                            InlineKeyboardButton("🤖Aß⊕ut ß⊕†", callback_data="aboutbot"),
                            InlineKeyboardButton("♥️Aß⊕ut Đ€V", callback_data="aboutdevs")
                        ],
                        [
                            InlineKeyboardButton("⎝⎝✧✧ ᴡᴀᴛᴄʜ ᴛᴜᴛᴏʀɪᴀʟ ✧✧⎠⎠", url="https://youtu.be/Rtjyz3lEZwE")
                        ]]))

            except Exception as err:
                print(err)
                await cmd.reply_text(f"ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ.!\n\n**Error:** `{err}`")

    @Bot.on_message(filters.private & filters.command("broadcast") & filters.user(Config.BOT_OWNER) & filters.reply)
    async def broadcast_handler_open(_, m: Message):
        await main_broadcast_handler(m, db)


    @Bot.on_message(filters.private & filters.command("stats") & filters.user(Config.BOT_OWNER))
    async def sts(_, m: Message):
        total_users = await db.total_users_count()
        await m.reply_text(
            text=f"**ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ ɪɴ ᴅʙ:** `{total_users}`",
            quote=True
        )


    @Bot.on_message(filters.private & filters.command("ban") & filters.user(Config.BOT_OWNER))
    async def ban(c: Client, m: Message):
        
        if len(m.command) == 1:
            await m.reply_text(
                f"ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ʙᴀɴ ᴀɴʏ ᴜꜱᴇʀ ꜰʀᴏᴍ ᴛʜᴇ ʙᴏᴛ.\n\n"
                f"Usage:\n\n"
                f"`/ban_user user_id ban_duration ban_reason`\n\n"
                f"Eg: `/ban_user 1234567 28 You misused me.`\n"
                f"This will ban user with id `1234567` for `28` days for the reason `You misused me`.",
                quote=True
            )
            return

        try:
            user_id = int(m.command[1])
            ban_duration = int(m.command[2])
            ban_reason = ' '.join(m.command[3:])
            ban_log_text = f"BΔnninǤ user {user_id} FФЯ {ban_duration} ᴅᴀʏꜱ ꜰᴏʀ ᴛʜᴇ ʀᴇᴀꜱᴏɴ {ban_reason}."
            try:
                await c.send_message(
                    user_id,
                    f"ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ ꜰᴏʀ **{ban_duration}** ᴅᴀʏ(ꜱ) ꜰᴏʀ ᴛʜᴇ ʀᴇᴀꜱᴏɴ __{ban_reason}__ \n\n"
                    f"**Message from the admin**"
                )
                ban_log_text += '\n\nᴜꜱᴇʀ ɴᴏᴛɪꜰɪᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!'
            except:
                traceback.print_exc()
                ban_log_text += f"\n\nᴜꜱᴇʀ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ ꜰᴀɪʟᴇᴅ! \n\n`{traceback.format_exc()}`"

            await db.ban_user(user_id, ban_duration, ban_reason)
            print(ban_log_text)
            await m.reply_text(
                ban_log_text,
                quote=True
            )
        except:
            traceback.print_exc()
            await m.reply_text(
                f"Error occoured! Traceback given below\n\n`{traceback.format_exc()}`",
                quote=True
            )

    @Bot.on_message(filters.private & filters.command("unban") & filters.user(Config.BOT_OWNER))
    async def unban(c: Client, m: Message):

        if len(m.command) == 1:
            await m.reply_text(
                f"ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴜɴʙᴀɴ ᴀɴʏ ᴜꜱᴇʀ.\n\n"
                f"Usage:\n\n`/unban_user user_id`\n\n"
                f"Eg: `/unban_user 1234567`\n"
                f"ᴛʜɪꜱ ᴡɪʟʟ ᴜɴʙᴀɴ ᴜꜱᴇʀ ᴡɪᴛʜ ɪᴅ `1234567`.",
                quote=True
            )
            return

        try:
            user_id = int(m.command[1])
            unban_log_text = f"ᴜɴʙᴀɴɴɪɴɢ ᴜꜱᴇʀ {user_id}"
            try:
                await c.send_message(
                    user_id,
                    f"ʏᴏᴜʀ ʙᴀɴ ᴡᴀꜱ ʟɪꜰᴛᴇᴅ!"
                )
                unban_log_text += '\n\nᴜꜱᴇʀ ɴᴏᴛɪꜰɪᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!'
            except:
                traceback.print_exc()
                unban_log_text += f"\n\nᴜꜱᴇʀ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ ꜰᴀɪʟᴇᴅ! \n\n`{traceback.format_exc()}`"
            await db.remove_ban(user_id)
            print(unban_log_text)
            await m.reply_text(
                unban_log_text,
                quote=True
            )
        except:
            traceback.print_exc()
            await m.reply_text(
                f"Error occurred! Traceback given below\n\n`{traceback.format_exc()}`",
                quote=True
            )


    @Bot.on_message(filters.private & filters.command("banned") & filters.user(Config.BOT_OWNER))
    async def _banned_users(_, m: Message):
        
        all_banned_users = await db.get_all_banned_users()
        banned_usr_count = 0
        text = ''

        async for banned_user in all_banned_users:
            user_id = banned_user['id']
            ban_duration = banned_user['ban_status']['ban_duration']
            banned_on = banned_user['ban_status']['banned_on']
            ban_reason = banned_user['ban_status']['ban_reason']
            banned_usr_count += 1
            text += f"> **user_id**: `{user_id}`, **Ban Duration**: `{ban_duration}`, " \
                    f"**Banned on**: `{banned_on}`, **Reason**: `{ban_reason}`\n\n"
        reply_text = f"Total banned user(s): `{banned_usr_count}`\n\n{text}"
        if len(reply_text) > 4096:
            with open('banned-users.txt', 'w') as f:
                f.write(reply_text)
            await m.reply_document('banned-users.txt', True)
            os.remove('banned-users.txt')
            return
        await m.reply_text(reply_text, True)

    @Bot.on_callback_query()
    async def button(bot: Client, cmd: CallbackQuery):

        cb_data = cmd.data
        if "aboutbot" in cb_data:
            await cmd.message.edit(
                Config.ABOUT_BOT_TEXT,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("⚡️SФUЯCΞ CФDΞS ФF ß⊕Γ",
                                                url="https://github.com/LazyDeveloperr/MissRozy")
                        ],
                        [
                            InlineKeyboardButton("GФ HФMΞ", callback_data="gotohome"),
                            InlineKeyboardButton("♥️Aß⊕ut Đ€V", callback_data="aboutdevs")
                        ]
                    ]
                )
            )

        elif "aboutdevs" in cb_data:
            await cmd.message.edit(
                Config.ABOUT_DEV_TEXT,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("⚡️SФUЯCΞ CФDΞS ФF ß⊕Γ",
                                                url="https://github.com/LazyDeveloperr/MissRozy")
                        ],
                        [
                            InlineKeyboardButton("🤖Aß⊕ut ß⊕t", callback_data="aboutbot"),
                            InlineKeyboardButton("🥷GФ HФMΞ", callback_data="gotohome")
                        ]
                    ]
                )
            )

        elif "gotohome" in cb_data:
            await cmd.message.edit(
                Config.LAZY_HOME_TEXT.format(cmd.message.chat.first_name, cmd.message.chat.id),
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("🍿supp⊕r† gr⊕up", url="https://t.me/LazyDeveloperSupport"),
                            InlineKeyboardButton("🔊ß⊕ts Channel", url="https://t.me/LazyDeveloper")
                        ],
                        [
                            InlineKeyboardButton("🤖Aß⊕ut ß⊕t", callback_data="aboutbot"),
                            InlineKeyboardButton("♥️Aß⊕ut Đ€V", callback_data="aboutdevs")
                        ],
                        [
                            InlineKeyboardButton("⎝⎝✧✧ ᴡᴀᴛᴄʜ ᴛᴜᴛᴏʀɪᴀʟ ✧✧⎠⎠", url="https://youtu.be/Rtjyz3lEZwE")
                        ]
                    ]
                )
            )

        elif "refreshForceSub" in cb_data:
            if Config.UPDATES_CHANNEL:
                if Config.UPDATES_CHANNEL.startswith("-100"):
                    channel_chat_id = int(Config.UPDATES_CHANNEL)
                else:
                    channel_chat_id = Config.UPDATES_CHANNEL
                try:
                    user = await bot.get_chat_member(channel_chat_id, cmd.message.chat.id)
                    if user.status == "kicked":
                        await cmd.message.edit(
                            text="ꜱᴏʀʀʏ ꜱɪʀ, ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ᴛᴏ ᴜꜱᴇ ᴍᴇ. ᴄᴏɴᴛᴀᴄᴛ ᴍʏ [Support Group](https://t.me/LazyDeveloperSupport).",
                            disable_web_page_preview=True
                        )
                        return
                except UserNotParticipant:
                    invite_link = await get_invite_link(channel_chat_id)
                    await cmd.message.edit(
                        text="**ʏᴏᴜ ꜱᴛɪʟʟ ᴅɪᴅɴ'ᴛ ᴊᴏɪɴ ☹️, ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ!**\n\n"
                            "ᴅᴜᴇ ᴛᴏ ᴏᴠᴇʀʟᴏᴀᴅ, ᴏɴʟʏ ᴄʜᴀɴɴᴇʟ ꜱᴜʙꜱᴄʀɪʙᴇʀꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ!",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton("▌│ 𝙅𝙤𝙞𝙣 𝙐𝙥𝙙𝙖𝙩𝙚𝙨 𝘾𝙝𝙖𝙣𝙣𝙚𝙡 ║║", url=invite_link.invite_link)
                                ],
                                [
                                    InlineKeyboardButton("🔄 Refresh 🔄", callback_data="refreshmeh")
                                ]
                            ]
                        )
                    )
                    return
                except Exception:
                    await cmd.message.edit(
                        text="ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ. ᴄᴏɴᴛᴀᴄᴛ ᴍʏ [Support Group](https://t.me/LazyDeveloperSupport).",
                        disable_web_page_preview=True
                    )
                    return
            await cmd.message.edit(
                Config.LAZY_HOME_TEXT.format(cmd.message.chat.first_name, cmd.message.chat.id),
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("🍿supp⊕r† gr⊕up", url="https://t.me/LazyDeveloperSupport"),
                            InlineKeyboardButton("🔊ß⊕ts Channel", url="https://t.me/LazyDeveloper")
                        ],
                        [
                            InlineKeyboardButton("🤖Aß⊕ut ß⊕t", callback_data="aboutbot"),
                            InlineKeyboardButton("♥️Aß⊕ut Đ€V", callback_data="aboutdevs")
                        ],
                        [
                            InlineKeyboardButton("⎝⎝✧✧ ᴡᴀᴛᴄʜ ᴛᴜᴛᴏʀɪᴀʟ ✧✧⎠⎠", url="https://youtu.be/Rtjyz3lEZwE")
                        ]
                    ]
                )
            )

        elif cb_data.startswith("ban_user_"):
            user_id = cb_data.split("_", 2)[-1]
            if Config.UPDATES_CHANNEL is None:
                await cmd.answer("ꜱᴏʀʀʏ ꜱɪʀ, ʏᴏᴜ ᴅɪᴅɴ'ᴛ ꜱᴇᴛ ᴀɴʏ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ!", show_alert=True)
                return
            if not int(cmd.from_user.id) == Config.BOT_OWNER:
                await cmd.answer("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴅᴏ ᴛʜᴀᴛ!", show_alert=True)
                return
            try:
                await bot.kick_chat_member(chat_id=int(Config.UPDATES_CHANNEL), user_id=int(user_id))
                await cmd.answer("USEƦ BANNED FƦOM UPDATES CHANNEL!", show_alert=True)
            except Exception as e:
                await cmd.answer(f"ᴄᴀɴ'ᴛ ʙᴀɴ ʜɪᴍ!\n\nError: {e}", show_alert=True)

        elif cb_data.startswith("generate_stream_link"):
            _, file_id = cb_data.split(":")
            try:
                user_id = cmd.from_user.id
                username =  cmd.from_user.mention

                lazy_file = await media_forward(bot, user_id=STREAM_LOGS, file_id=file_id)
 
                
                fileName = {quote_plus(get_name(lazy_file))}
                lazy_stream = f"{URL}watch/{str(lazy_file.id)}/{quote_plus(get_name(lazy_file))}?hash={get_hash(lazy_file)}"
                lazy_download = f"{URL}{str(lazy_file.id)}/{quote_plus(get_name(lazy_file))}?hash={get_hash(lazy_file)}"

                xo = await cmd.message.reply_text(f'🔐')
                await asyncio.sleep(1)
                await xo.delete()

                await lazy_file.reply_text(
                    text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}",
                    quote=True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("web Download", url=lazy_download),  # we download Link
                                                        InlineKeyboardButton('▶Stream online', url=lazy_stream)]])  # web stream Link
                )
                await cmd.message.edit(
                    text="•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ☠︎⚔",
                    quote=True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("web Download", url=lazy_download),  # we download Link
                                                        InlineKeyboardButton('▶Stream online', url=lazy_stream)]])  # web stream Link
                )
            except Exception as e:
                print(e)  # print the error message
                await cmd.answer(f"☣something went wrong sweetheart\n\n{e}", show_alert=True)
                return

        elif "closeMessage" in cb_data:
            await cmd.message.delete(True)

        try:
            await cmd.answer()
        except QueryIdInvalid: pass

    if ON_HEROKU:
        asyncio.create_task(ping_server())
    me = await Bot.get_me()
    Bot.username = '@' + me.username
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0" if ON_HEROKU else BIND_ADRESS
    await web.TCPSite(app, "0.0.0.0", PORT).start()
    await idle()


if __name__ == '__main__':
    try:
        loop.run_until_complete(Lazy_start())
    except KeyboardInterrupt:
        logging.info(' Service Stopped ')

