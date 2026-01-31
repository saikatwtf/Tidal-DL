import time
import asyncio
import datetime
from bot import CMD
from pyrogram import Client, filters
from bot.helpers.utils.auth_check import check_id
from bot.helpers.database.mongo_impl import broadcast_db

@Client.on_message(filters.command(CMD.BROADCAST) & filters.reply)
async def broadcast_handler(bot, message):
    if not await check_id(message.from_user.id, restricted=True):
        return
    
    b_msg = message.reply_to_message
    sts = await message.reply_text('Broadcasting your message...')
    
    start_time = time.time()
    total_users = broadcast_db.total_users_count()
    done = 0
    success = 0
    blocked = 0
    deleted = 0
    failed = 0
    
    async for user in broadcast_db.get_all_users():
        user_id = int(user['user_id'])
        try:
            await b_msg.copy(chat_id=user_id)
            success += 1
        except Exception as e:
            if "blocked" in str(e).lower():
                blocked += 1
            elif "deleted" in str(e).lower():
                deleted += 1
            else:
                failed += 1
        
        done += 1
        if done % 20 == 0:
            try:
                await sts.edit(
                    f"Broadcast in progress:\n\n"
                    f"Total Users: {total_users}\n"
                    f"Completed: {done} / {total_users}\n"
                    f"Success: {success}\n"
                    f"Blocked: {blocked}\n"
                    f"Deleted: {deleted}\n"
                    f"Failed: {failed}"
                )
            except:
                pass
        await asyncio.sleep(0.1)
    
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(
        f"Broadcast Completed:\n"
        f"Completed in {time_taken}\n\n"
        f"Total Users: {total_users}\n"
        f"Completed: {done} / {total_users}\n"
        f"Success: {success}\n"
        f"Blocked: {blocked}\n"
        f"Deleted: {deleted}\n"
        f"Failed: {failed}"
    )
