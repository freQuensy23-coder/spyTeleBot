import aiogram
from aiogram import *
from aiogram.types import Message, User
from Room import *
from os import getenv
import logging

API_TOKEN = getenv("telegram_bot_token")
logging.basicConfig(level=logging.INFO)

# TODO Use safe mesgs sender
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


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
async def create_room(message: Message):
    try:
        room_id = int(message.get_args()[-1].strip())
        try:
            room = add_user_to_room(room_id, user=message.from_user)  # TODO  Delete this user from all other rooms
            log.debug(f"User [ID: {message.from_user.id}] successfully entered room [ID: {room_id}")
            users_msg = ""
            for i, user in enumerate(room.users):
                users_msg += f"{i}. {user.full_name} \n"
            await message.reply(f"You have entered room. There are: \n {users_msg} there.")
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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
