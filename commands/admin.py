import asyncio
from aiogram import Router, Bot
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command
from aiogram.enums import ParseMode

router = Router()

ALLOWED_GROUP = -1003414533097
OWNER_ID = 6957681631

# Global pause flag — when True, bot ignores all commands except /startbot
bot_paused = False


def is_bot_paused() -> bool:
    """Check if the bot is currently paused."""
    return bot_paused


def is_owner(msg: Message) -> bool:
    """Check if the user is the bot owner."""
    return msg.from_user and msg.from_user.id == OWNER_ID


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /stopbot — Pause the bot (ignore cmds)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("stopbot"))
async def stopbot_handler(msg: Message, bot: Bot):
    global bot_paused

    if not is_owner(msg):
        await msg.answer(
            "<blockquote><code>𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗢𝘄𝗻𝗲𝗿 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    if bot_paused:
        await msg.answer(
            "<blockquote><code>⏸ 𝗕𝗼𝘁 𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗣𝗮𝘂𝘀𝗲𝗱</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗨𝘀𝗲 <code>/startbot</code> 𝘁𝗼 𝗿𝗲𝘀𝘂𝗺𝗲</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    bot_paused = True

    await msg.answer(
        "<blockquote><code>⏸ 𝗕𝗼𝘁 𝗣𝗮𝘂𝘀𝗲𝗱 ✅</code></blockquote>\n\n"
        "<blockquote>「❃」 𝗕𝗼𝘁 𝘄𝗶𝗹𝗹 𝗶𝗴𝗻𝗼𝗿𝗲 𝗮𝗹𝗹 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀\n"
        "「❃」 𝗨𝘀𝗲 <code>/startbot</code> 𝘁𝗼 𝗿𝗲𝗮𝗰𝘁𝗶𝘃𝗮𝘁𝗲</blockquote>",
        parse_mode=ParseMode.HTML
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /startbot — Resume the bot
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("startbot"))
async def startbot_handler(msg: Message, bot: Bot):
    global bot_paused

    if not is_owner(msg):
        await msg.answer(
            "<blockquote><code>𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗢𝘄𝗻𝗲𝗿 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    if not bot_paused:
        await msg.answer(
            "<blockquote><code>▶️ 𝗕𝗼𝘁 𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗔𝗰𝘁𝗶𝘃𝗲</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗕𝗼𝘁 𝗶𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗿𝘂𝗻𝗻𝗶𝗻𝗴</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    bot_paused = False

    await msg.answer(
        "<blockquote><code>▶️ 𝗕𝗼𝘁 𝗔𝗰𝘁𝗶𝘃𝗮𝘁𝗲𝗱 ✅</code></blockquote>\n\n"
        "<blockquote>「❃」 𝗕𝗼𝘁 𝗶𝘀 𝗻𝗼𝘄 𝗮𝗰𝘁𝗶𝘃𝗲 𝗮𝗻𝗱 𝗿𝗲𝗮𝗱𝘆\n"
        "「❃」 𝗔𝗹𝗹 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗮𝗿𝗲 𝗻𝗼𝘄 𝗲𝗻𝗮𝗯𝗹𝗲𝗱</blockquote>",
        parse_mode=ParseMode.HTML
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /purge — Delete all messages in group
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("purge"))
async def purge_handler(msg: Message, bot: Bot):
    if not is_owner(msg):
        await msg.answer(
            "<blockquote><code>𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗢𝘄𝗻𝗲𝗿 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    if bot_paused:
        await msg.answer(
            "<blockquote><code>⏸ 𝗕𝗼𝘁 𝗣𝗮𝘂𝘀𝗲𝗱</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗨𝘀𝗲 <code>/startbot</code> 𝘁𝗼 𝗿𝗲𝘀𝘂𝗺𝗲</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    if msg.chat.type == "private":
        await msg.answer(
            "<blockquote><code>⚠️ 𝗚𝗿𝗼𝘂𝗽 𝗢𝗻𝗹𝘆</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗧𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝗼𝗻𝗹𝘆 𝘄𝗼𝗿𝗸𝘀 𝗶𝗻 𝗴𝗿𝗼𝘂𝗽𝘀</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    status_msg = await msg.answer(
        "<blockquote><code>🗑 𝗣𝘂𝗿𝗴𝗶𝗻𝗴...</code></blockquote>\n\n"
        "<blockquote>「❃」 𝗗𝗲𝗹𝗲𝘁𝗶𝗻𝗴 𝗮𝗹𝗹 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀...</blockquote>",
        parse_mode=ParseMode.HTML
    )

    chat_id = msg.chat.id
    current_msg_id = msg.message_id
    deleted = 0
    failed = 0
    batch_size = 100  # Telegram deleteMessages max per call

    # Delete in batches going backward from current message
    msg_id = current_msg_id
    while msg_id > 0:
        # Build batch of message IDs
        batch_ids = list(range(max(msg_id - batch_size + 1, 1), msg_id + 1))

        try:
            # Try bulk delete first (faster, works for messages < 48h old)
            result = await bot.delete_messages(chat_id=chat_id, message_ids=batch_ids)
            if result:
                deleted += len(batch_ids)
        except Exception:
            # Fallback: delete one by one
            for mid in reversed(batch_ids):
                try:
                    await bot.delete_message(chat_id=chat_id, message_id=mid)
                    deleted += 1
                except Exception:
                    failed += 1

                # Small delay to avoid rate limits
                if deleted % 50 == 0:
                    await asyncio.sleep(0.5)

        msg_id -= batch_size

        # Update progress every 500 messages
        if deleted % 500 == 0 and deleted > 0:
            try:
                await status_msg.edit_text(
                    f"<blockquote><code>🗑 𝗣𝘂𝗿𝗴𝗶𝗻𝗴...</code></blockquote>\n\n"
                    f"<blockquote>「❃」 𝗗𝗲𝗹𝗲𝘁𝗲𝗱: <code>{deleted}</code> 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀</blockquote>",
                    parse_mode=ParseMode.HTML
                )
            except Exception:
                pass

    # Final status
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=(
                f"<blockquote><code>🗑 𝗣𝘂𝗿𝗴𝗲 𝗖𝗼𝗺𝗽𝗹𝗲𝘁𝗲 ✅</code></blockquote>\n\n"
                f"<blockquote>「❃」 𝗗𝗲𝗹𝗲𝘁𝗲𝗱: <code>{deleted}</code> 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀\n"
                f"「❃」 𝗙𝗮𝗶𝗹𝗲𝗱: <code>{failed}</code></blockquote>"
            ),
            parse_mode=ParseMode.HTML
        )
    except Exception:
        pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /lock — Lock group (restrict messages)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("lock"))
async def lock_handler(msg: Message, bot: Bot):
    if not is_owner(msg):
        await msg.answer(
            "<blockquote><code>𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗢𝘄𝗻𝗲𝗿 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    if bot_paused:
        await msg.answer(
            "<blockquote><code>⏸ 𝗕𝗼𝘁 𝗣𝗮𝘂𝘀𝗲𝗱</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗨𝘀𝗲 <code>/startbot</code> 𝘁𝗼 𝗿𝗲𝘀𝘂𝗺𝗲</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    if msg.chat.type == "private":
        await msg.answer(
            "<blockquote><code>⚠️ 𝗚𝗿𝗼𝘂𝗽 𝗢𝗻𝗹𝘆</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗧𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝗼𝗻𝗹𝘆 𝘄𝗼𝗿𝗸𝘀 𝗶𝗻 𝗴𝗿𝗼𝘂𝗽𝘀</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    try:
        locked_permissions = ChatPermissions(
            can_send_messages=False,
            can_send_audios=False,
            can_send_documents=False,
            can_send_photos=False,
            can_send_videos=False,
            can_send_video_notes=False,
            can_send_voice_notes=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_change_info=False,
            can_invite_users=True,
            can_pin_messages=False,
            can_manage_topics=False,
        )

        await bot.set_chat_permissions(
            chat_id=msg.chat.id,
            permissions=locked_permissions
        )

        await msg.answer(
            "<blockquote><code>🔒 𝗚𝗿𝗼𝘂𝗽 𝗟𝗼𝗰𝗸𝗲𝗱 ✅</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗠𝗲𝗺𝗯𝗲𝗿𝘀 𝗰𝗮𝗻 𝗻𝗼 𝗹𝗼𝗻𝗴𝗲𝗿 𝘀𝗲𝗻𝗱 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀\n"
            "「❃」 𝗨𝘀𝗲 <code>/unlock</code> 𝘁𝗼 𝗿𝗲𝘀𝘁𝗼𝗿𝗲</blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await msg.answer(
            f"<blockquote><code>❌ 𝗟𝗼𝗰𝗸 𝗙𝗮𝗶𝗹𝗲𝗱</code></blockquote>\n\n"
            f"<blockquote>「❃」 𝗘𝗿𝗿𝗼𝗿: <code>{str(e)[:100]}</code>\n"
            f"「❃」 𝗠𝗮𝗸𝗲 𝘀𝘂𝗿𝗲 𝗯𝗼𝘁 𝗶𝘀 𝗮𝗱𝗺𝗶𝗻 𝘄𝗶𝘁𝗵 '𝗥𝗲𝘀𝘁𝗿𝗶𝗰𝘁 𝗠𝗲𝗺𝗯𝗲𝗿𝘀'</blockquote>",
            parse_mode=ParseMode.HTML
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /unlock — Unlock group (restore perms)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("unlock"))
async def unlock_handler(msg: Message, bot: Bot):
    if not is_owner(msg):
        await msg.answer(
            "<blockquote><code>𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗢𝘄𝗻𝗲𝗿 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    if bot_paused:
        await msg.answer(
            "<blockquote><code>⏸ 𝗕𝗼𝘁 𝗣𝗮𝘂𝘀𝗲𝗱</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗨𝘀𝗲 <code>/startbot</code> 𝘁𝗼 𝗿𝗲𝘀𝘂𝗺𝗲</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    if msg.chat.type == "private":
        await msg.answer(
            "<blockquote><code>⚠️ 𝗚𝗿𝗼𝘂𝗽 𝗢𝗻𝗹𝘆</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗧𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝗼𝗻𝗹𝘆 𝘄𝗼𝗿𝗸𝘀 𝗶𝗻 𝗴𝗿𝗼𝘂𝗽𝘀</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    try:
        unlocked_permissions = ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_manage_topics=False,
        )

        await bot.set_chat_permissions(
            chat_id=msg.chat.id,
            permissions=unlocked_permissions
        )

        await msg.answer(
            "<blockquote><code>🔓 𝗚𝗿𝗼𝘂𝗽 𝗨𝗻𝗹𝗼𝗰𝗸𝗲𝗱 ✅</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗠𝗲𝗺𝗯𝗲𝗿𝘀 𝗰𝗮𝗻 𝗻𝗼𝘄 𝘀𝗲𝗻𝗱 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗮𝗴𝗮𝗶𝗻</blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await msg.answer(
            f"<blockquote><code>❌ 𝗨𝗻𝗹𝗼𝗰𝗸 𝗙𝗮𝗶𝗹𝗲𝗱</code></blockquote>\n\n"
            f"<blockquote>「❃」 𝗘𝗿𝗿𝗼𝗿: <code>{str(e)[:100]}</code>\n"
            f"「❃」 𝗠𝗮𝗸𝗲 𝘀𝘂𝗿𝗲 𝗯𝗼𝘁 𝗶𝘀 𝗮𝗱𝗺𝗶𝗻 𝘄𝗶𝘁𝗵 '𝗥𝗲𝘀𝘁𝗿𝗶𝗰𝘁 𝗠𝗲𝗺𝗯𝗲𝗿𝘀'</blockquote>",
            parse_mode=ParseMode.HTML
        )
