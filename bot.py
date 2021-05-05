import aiogram
from aiogram import *
from aiogram.types import Message, User
from Room import *
from os import getenv
import logging
from Exceptions import *

API_TOKEN = getenv("telegram_bot_token")
logging.basicConfig(level=logging.INFO)

# TODO Use safe mesgs sender
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def notify(room: Room):
    """Send notification msg to everybody in room when game stopped"""
    for user in room.users:
        log.debug("Send notification msgs to user [ID: user.id].")
        bot.send_message(user.id, text=f"Game stopped.\n * Location: {room.location}.\n * Spy: {room.spy.full_name}")


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    log.debug(f"User [ID: {message.from_user.id}] print start.")
    await message.reply("Nice to see you in game 'Spy'. More about rules - /rules . To join room use /join {room_id} "
                        "(/j) to create it /create (/c) ")


@dp.message_handler(commands=["rules", "r"])
async def send_rules(message: Message):
    log.debug(f"User [ID: {message.from_user.id}] get rules.")
    await message.reply("Learn rules with wikipedia https://en.wikipedia.org/wiki/I_spy")


@dp.message_handler(commands=["join", "j"])
async def enter_room(message: Message):
    try:
        room_id = int(message.get_args()[-1].strip())
        try:
            del_user(message.from_user)  # Delete this user from all other rooms
            room = add_user_to_room(room_id, user=message.from_user)  # TODO  Delete this user from all other rooms
            log.debug(f"User [ID: {message.from_user.id}] successfully entered room [ID: {room_id}")
            users_msg = ""
            for i, user in enumerate(room.users):
                users_msg += f"{i}. {user.full_name} \n"
            await message.reply(f"You have entered room. There are: \n {users_msg} \n there.")
        except CanNotEnterRoomError:
            log.info(f"User [ID: {message.from_user.id}] unsuccessfully entered room [ID: {room_id}]. Game already "
                     f"started or user already here")
            await message.reply("Can't enter the room. Game already started or you are already in this room")
        except NoSuchRoomError:
            log.info(
                f"User [ID: {message.from_user.id}] unsuccessfully entered room [ID: {room_id}]. "
                f"Room not found")

    except Exception as e:
        log.info(f"Smth wrong with user [ID: {message.from_user.id}]. Exception {e}. Message {message.text}")


@dp.message_handler(commands=["/stop"])
def stop_game_handler(message: Message):
    log.debug(f"User [ID: {message.from_user.id}] tried to stop game.")
    try:
        room = get_room_by_user(user=message.from_user)
        if room.admin == message.from_user:
            log.debug(f"User [ID: {message.from_user.id}] successfully stopped room [ID : {room.id}]")
            notify(room)
            room.stop_game()  # TODO Send room id to admin
            message.reply(f"Game closed successfully! Invite friends, /j {room.id}")
        else:
            log.debug(f"User [ID: {message.from_user.id}] tried to delete room [ID: {room.id}], but he is not admin.")
            message.reply(f"You are not admin. Ask {room.admin.full_name} do this.")
    except NoSuchRoomError:
        log.debug(f"User [ID: {message.from_user.id}] tried to delete room, but he does not in any.")
        message.reply("You are not in room.")
    # TODO Send room info command


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
