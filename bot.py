import aiogram
from aiogram import *
from aiogram.types import Message, User
from Room import *
from os import getenv
import logging
from Exceptions import *

API_TOKEN = getenv("telegram_bot_token")
logging.basicConfig(level=logging.INFO) # TODO room info

# TODO Use safe mesgs sender
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def notify(room: Room, event: str):
    """Send notification msg to everybody in room when game stopped or started
    :param event start or stop
    """
    if event == "stop":
        for user in room.users:
            log.info("Send notification msgs to user [ID: user.id].")
            await bot.send_message(user.id, text=f"Game stopped.\n * Location: {room.location}.\n * Spy: {room.spy.full_name}")
    if event == "start":
        for user in room.users:
            if user == room.spy:
                await bot.send_message(user.id, "You are spy in this game. You guess location. Use /location") # TODO /location
            else:
                await bot.send_message(user.id, f"Lacation is {room.location}. You should find spy.")
        pass


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    log.info(f"User [ID: {message.from_user.id}] print start.")
    await message.reply("Nice to see you in game 'Spy'. More about rules - /rules . To join room use /join {room_id} "
                        "(/j) to create it /create (/c) ")


@dp.message_handler(commands=["rules", "r"])
async def send_rules(message: Message):
    log.info(f"User [ID: {message.from_user.id}] get rules.")
    await message.reply("Learn rules with wikipedia https://en.wikipedia.org/wiki/I_spy")


@dp.message_handler(commands=["join", "j"])
async def enter_room(message: Message):
    try:
        room_id = int(message.get_args().strip()) # TODO send msg if no room id
        try:
            del_user(message.from_user)  # Delete this user from all other rooms
            room = add_user_to_room(room_id, user=message.from_user)
            log.info(f"User [ID: {message.from_user.id}] successfully entered room [ID: {room_id}]")
            users_msg = ""
            for i, user in enumerate(room.users):
                users_msg += f"{i + 1}. {user.full_name} \n"
            await message.reply(f"You have entered room. There are: \n {users_msg} \n there.")
        except CanNotEnterRoomError:
            log.info(f"User [ID: {message.from_user.id}] unsuccessfully entered room [ID: {room_id}]. Game already "
                     f"started or user already here")
            await message.reply("Can't enter the room. Game already started or you are already in this room")
        except NoSuchRoomError:
            log.info(
                f"User [ID: {message.from_user.id}] unsuccessfully entered room [ID: {room_id}]. "
                f"Room not found") # TODO send msg that room not found

    except Exception as e:
        log.info(f"Smth wrong with user [ID: {message.from_user.id}]. Exception {e}. Message {message.text}")


@dp.message_handler(commands=["stop"])
async def stop_game_handler(message: Message):
    log.info(f"User [ID: {message.from_user.id}] tried to stop game.")
    try:
        room = get_room_by_user(user=message.from_user)
        if room.admin == message.from_user:
            log.info(f"User [ID: {message.from_user.id}] successfully stopped room [ID : {room.id}]")
            await notify(room, "stop") # TODO Check if game started
            room.stop_game()  # TODO Send room id to admin
            await message.reply(f"Game ended successfully! You can play again now  (/b) or invite friends,\n /j {room.id}")
        else:
            log.info(f"User [ID: {message.from_user.id}] tried to delete room [ID: {room.id}], but he is not admin.")
            await message.reply(f"You are not admin. Ask {room.admin.full_name} do this.")
    except NoSuchRoomError:
        log.info(f"User [ID: {message.from_user.id}] tried to delete room, but he does not in any.")
        await message.reply("You are not in room.")
    # TODO Send room info command


@dp.message_handler(commands=["create", "c"])
async def create_room(message: Message):
    log.info(f"User [ID: {message.from_user.id}] tried to create room")
    del_user(user=message.from_user)
    room = Room(admin=message.from_user)
    await message.reply(f"Room created succsessfully. To join it use: \n /j {room.id}")
    logging.info(f"Room [ID: {room.id}] created by user [ID: {message.from_user.id}]")


@dp.message_handler(commands=["begin", "b"]) # TODO say to admin how to start game
async def begin_game_handler(message: Message):
    log.info(f"User [ID: {message.from_user.id}]] tried to start game")
    try:
        room = get_room_by_user(user=message.from_user)
        if room.admin == message.from_user:
            try:
                log.info(f"User [ID: {message.from_user.id}] successfully started room [ID : {room.id}]")
                room.start_game()
                await notify(room, "start")
            except NotEnoughPlayersError:
                log.info(f"User [ID: {message.from_user.id}] unsuccessfully tried to begin game. Not enough players.")
                await message.reply("You can't start game because there are not enough players") # TODO send room info

        else:
            log.info(f"User [ID: {message.from_user.id}] unsuccessfully tried to begin room [ID: {room.id}. He is not "
                     f"admin")
            await message.reply(f"You are not admin. Ask {room.admin.full_name} do this.")
    except NoSuchRoomError:
        log.info(f"User [ID: {message.from_user.id}] unsuccessfully tried to begin game. Room not found")
        await message.reply("Room not found. Create it using /c or join /j")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
