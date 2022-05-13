# Written by Inukaasith for DaisyX

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.error import BadRequest
from telegram.ext import CallbackQueryHandler, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from DaisyX import dispatcher
from DaisyX.modules.disable import DisableAbleCommandHandler
from DaisyX.modules.helper_funcs.alternate import typing_action
from DaisyX.modules.helper_funcs.chat_status import bot_admin, user_admin
from DaisyX.modules.helper_funcs.extraction import extract_user_and_text


@run_async
@bot_admin
@user_admin
@typing_action
def addtag(update, context):
    chat = update.effective_chat
    update.effective_user
    message = update.effective_message
    args = context.args
    user_id, reason = extract_user_and_text(message, args)
    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("I can't seem to find this user")
        return
    if user_id == context.bot.id:
        message.reply_text("how I supposed to tag myself")
        return

    chat_id = str(chat.id)[1:]
    tagall_list = list(REDIS.sunion(f"tagall2_{chat_id}"))
    match_user = mention_html(member.user.id, member.user.first_name)
    if match_user in tagall_list:
        message.reply_text(
            f"{mention_html(member.user.id, member.user.first_name)} is already exist in {chat.title}'s tag list.",
            parse_mode=ParseMode.HTML,
        )

        return
    message.reply_text(
        f"{mention_html(member.user.id, member.user.first_name)} accept this, if you want to add yourself into {chat.title}'s tag list! or just simply decline this.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Accept", callback_data=f"tagall_accept={user_id}"
                    ),
                    InlineKeyboardButton(
                        text="Decline",
                        callback_data=f"tagall_dicline={user_id}",
                    ),
                ]
            ]
        ),
        parse_mode=ParseMode.HTML,
    )


@run_async
@bot_admin
@user_admin
@typing_action
def removetag(update, context):
    chat = update.effective_chat
    update.effective_user
    message = update.effective_message
    args = context.args
    user_id, reason = extract_user_and_text(message, args)
    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("I can't seem to find this user")
        return
    if user_id == context.bot.id:
        message.reply_text("how I supposed to tag or untag myself")
        return
    chat_id = str(chat.id)[1:]
    tagall_list = list(REDIS.sunion(f"tagall2_{chat_id}"))
    match_user = mention_html(member.user.id, member.user.first_name)
    if match_user not in tagall_list:
        message.reply_text(
            f"{mention_html(member.user.id, member.user.first_name)} is doesn't exist in {chat.title}'s list!",
            parse_mode=ParseMode.HTML,
        )

        return
    member = chat.get_member(int(user_id))
    chat_id = str(chat.id)[1:]
    REDIS.srem(
        f"tagall2_{chat_id}", mention_html(member.user.id, member.user.first_name)
    )
    message.reply_text(
        f"{mention_html(member.user.id, member.user.first_name)} is successfully removed from {chat.title}'s list.",
        parse_mode=ParseMode.HTML,
    )


@run_async
def tagg_all_button(update, context):
    query = update.callback_query
    chat = update.effective_chat
    splitter = query.data.split("=")
    query_match = splitter[0]
    user_id = splitter[1]
    if query_match == "tagall_accept" and query.from_user.id == int(user_id):
        member = chat.get_member(int(user_id))
        chat_id = str(chat.id)[1:]
        REDIS.sadd(
            f"tagall2_{chat_id}",
            mention_html(member.user.id, member.user.first_name),
        )
        query.message.edit_text(
            f"{mention_html(member.user.id, member.user.first_name)} is accepted! to add yourself {chat.title}'s tag list.",
            parse_mode=ParseMode.HTML,
        )


    elif (
        query_match == "tagall_accept"
        or query_match == "tagall_dicline"
        and query.from_user.id != int(user_id)
    ):
        context.bot.answer_callback_query(
            query.id, text="You're not the user being added in tag list!"
        )
    elif query_match == "tagall_dicline":
        member = chat.get_member(int(user_id))
        query.message.edit_text(
            f"{mention_html(member.user.id, member.user.first_name)} is deslined! to add yourself {chat.title}'s tag list.",
            parse_mode=ParseMode.HTML,
        )


@run_async
@typing_action
def untagme(update, context):
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    chat_id = str(chat.id)[1:]
    tagall_list = list(REDIS.sunion(f"tagall2_{chat_id}"))
    match_user = mention_html(user.id, user.first_name)
    if match_user not in tagall_list:
        message.reply_text(f"You're already doesn't exist in {chat.title}'s tag list!")
        return
    REDIS.srem(f"tagall2_{chat_id}", mention_html(user.id, user.first_name))
    message.reply_text(
        f"{mention_html(user.id, user.first_name)} has been removed from {chat.title}'s tag list.",
        parse_mode=ParseMode.HTML,
    )


@run_async
@typing_action
def tagme(update, context):
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    chat_id = str(chat.id)[1:]
    tagall_list = list(REDIS.sunion(f"tagall2_{chat_id}"))
    match_user = mention_html(user.id, user.first_name)
    if match_user in tagall_list:
        message.reply_text(f"You're Already Exist In {chat.title}'s Tag List!")
        return
    REDIS.sadd(f"tagall2_{chat_id}", mention_html(user.id, user.first_name))
    message.reply_text(
        f"{mention_html(user.id, user.first_name)} has been successfully added in {chat.title}'s tag list.",
        parse_mode=ParseMode.HTML,
    )


@run_async
@bot_admin
@user_admin
@typing_action
def tagall(update, context):
    chat = update.effective_chat
    update.effective_user
    message = update.effective_message
    args = context.args
    query = " ".join(args)
    if not query:
        message.reply_text("Please give a reason why are you want to tag all!")
        return
    chat_id = str(chat.id)[1:]
    tagall = sorted(REDIS.sunion(f"tagall2_{chat_id}"))
    if tagall := ", ".join(tagall):
        tagall_reason = query
        if message.reply_to_message:
            message.reply_to_message.reply_text(
                "{}"
                "\n\n<b>• Tagged Reason : </b>"
                "\n{}".format(tagall, tagall_reason),
                parse_mode=ParseMode.HTML,
            )
        else:
            message.reply_text(
                "{}"
                "\n\n<b>• Tagged Reason : </b>"
                "\n{}".format(tagall, tagall_reason),
                parse_mode=ParseMode.HTML,
            )
    else:
        message.reply_text("Tagall list is empty!")


@run_async
@bot_admin
@user_admin
@typing_action
def untagall(update, context):
    chat = update.effective_chat
    update.effective_user
    message = update.effective_message
    chat_id = str(chat.id)[1:]
    tagall_list = list(REDIS.sunion(f"tagall2_{chat_id}"))
    for tag_user in tagall_list:
        REDIS.srem(f"tagall2_{chat_id}", tag_user)
    message.reply_text(
        f"Successully removed all users from {chat.title}'s tag list."
    )


__mod_name__ = "Tagger 🖇"

__help__ = """ 
Tagger is an essential feature to mention all subscribed members in the group. Any chat members can subscribe to tagger.

- /tagme: registers to the chat tag list.
- /untagme: unsubscribes from the chat tag list.

*Admin only:*
- /tagall: mention all subscribed members.
- /untagall: clears all subscribed members. 
- /addtag <userhandle>: add a user to chat tag list. (via handle, or reply)
- /removetag <userhandle>: remove a user to chat tag list. (via handle, or reply)
"""

TAG_ALL_HANDLER = DisableAbleCommandHandler("tagall", tagall, filters=Filters.group)
UNTAG_ALL_HANDLER = DisableAbleCommandHandler(
    "untagall", untagall, filters=Filters.group
)
UNTAG_ME_HANDLER = CommandHandler("untagme", untagme, filters=Filters.group)
TAG_ME_HANDLER = CommandHandler("tagme", tagme, filters=Filters.group)
ADD_TAG_HANDLER = DisableAbleCommandHandler(
    "addtag", addtag, pass_args=True, filters=Filters.group
)
REMOVE_TAG_HANDLER = DisableAbleCommandHandler(
    "removetag", removetag, pass_args=True, filters=Filters.group
)
TAGALL_CALLBACK_HANDLER = CallbackQueryHandler(tagg_all_button, pattern=r"tagall_")


dispatcher.add_handler(TAG_ALL_HANDLER)
dispatcher.add_handler(UNTAG_ALL_HANDLER)
dispatcher.add_handler(UNTAG_ME_HANDLER)
dispatcher.add_handler(TAG_ME_HANDLER)
dispatcher.add_handler(ADD_TAG_HANDLER)
dispatcher.add_handler(REMOVE_TAG_HANDLER)
dispatcher.add_handler(TAGALL_CALLBACK_HANDLER)
