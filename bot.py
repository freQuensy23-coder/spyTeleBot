from aiogram import *
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


async def notify(room: Room, event: str):
    """Send notification msg to everybody in room when game stopped or started
    :param event start or stop
    """
    if event == "stop":
        for user in room.users:
            log.info("Send notification msgs to user [ID: user.id].")
            await bot.send_message(user.id,
                                   text=f"Game stopped.\n * Location: {room.location}.\n * Spy: {room.spy.full_name}")
    if event == "start":
        for user in room.users:
            if user == room.spy:
                await bot.send_message(user.id,
                                       "You are spy in this game. You guess location. Use /location")
            else:
                await bot.send_message(user.id, f"Lacation is {room.location}. You should find spy.")

    if event == "leave":
        for user in room.users:
            await bot.send_message(user.id, text="Somebode leave your room. If it was admin, room will be closed. Use "
                                                 "/info.")


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
        room_id = int(message.get_args().strip())
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
                f"Room not found")
            await message.reply("Room not found")
    except ValueError:
        log.info(f"User [ID: {message.from_user.id}] tried to join room but he does not send room id.")
        await message.reply("Use /join {room id} to join room or /create (/c) to create it")
    except Exception as e:
        log.info(f"Smth wrong with user [ID: {message.from_user.id}]. Exception {e}. Message {message.text}")


@dp.message_handler(commands=["stop"])
async def stop_game_handler(message: Message):
    log.info(f"User [ID: {message.from_user.id}] tried to stop game.")
    try:
        room = get_room_by_user(user=message.from_user)
        if room.status != 1:
            log.info(f"User [ID: {message.from_user.id}] tried to stop room [ID: {room.id}] but it is already stopped")
            await message.reply("Game has not started yet. Use /begin to start")
        if room.admin == message.from_user:
            log.info(f"User [ID: {message.from_user.id}] successfully stopped room [ID : {room.id}]")
            await notify(room, "stop")
            room.stop_game()
            await message.reply(
                f"Game ended successfully! You can play again now  (/b) or invite friends,\n /j {room.id}")
        else:
            log.info(f"User [ID: {message.from_user.id}] tried to delete room [ID: {room.id}], but he is not admin.")
            await message.reply(f"You are not admin. Ask {room.admin.full_name} do this.")
    except NoSuchRoomError:
        log.info(f"User [ID: {message.from_user.id}] tried to delete room, but he does not in any.")
        await message.reply("You are not in room.")


@dp.message_handler(commands=["create", "c"])
async def create_room(message: Message):
    log.info(f"User [ID: {message.from_user.id}] tried to create room")
    del_user(user=message.from_user)
    room = Room(admin=message.from_user)
    await message.reply(f"Room created successfully. To join it use: \n /j {room.id} (send this code to your "
                        f"friends). To start game use /begin (/b)")
    logging.info(f"Room [ID: {room.id}] created by user [ID: {message.from_user.id}]")


@dp.message_handler(commands=["begin", "b"])
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
                await message.reply("You can't start game because there are not enough players")
                await send_room_info(message)
        else:
            log.info(f"User [ID: {message.from_user.id}] unsuccessfully tried to begin room [ID: {room.id}. He is not "
                     f"admin")
            await message.reply(f"You are not admin. Ask {room.admin.full_name} do this.")
    except NoSuchRoomError:
        log.info(f"User [ID: {message.from_user.id}] unsuccessfully tried to begin game. Room not found")
        await message.reply("Room not found. Create it using /c or join /j")


@dp.message_handler(commands=["room", "roominfo", "info"])
async def send_room_info(message: Message):
    log.info(f"User [ID: {message.from_user.id}] wants to get room info")
    try:
        room = get_room_by_user(message.from_user)
        info = get_room_info(room)
        log.info(f"User [ID: {message.from_user.id}] get info about room [ID: {room.id}]")
        log.debug(info)
        await message.reply(text=info)
    except NoSuchRoomError:
        log.info(f"User [ID: {message.from_user.id}] unsuccessfully tried to get room info. No such room.")
        await message.reply("Room not found. Create it using /c or join /j")


def get_room_info(room: Room) -> str:
    """Get info about room """
    info = ""
    if room.status == 0:
        info += f"Waiting for host ({room.admin.full_name}) to start. Players in room: \n"
    elif room.status == 1:
        info += f"Game is started by ({room.admin.full_name}). Players in room: \n"
    for i, user in enumerate(room.users):
        if user == room.admin:
            info += "*"
        info += f"{i + 1}. {user.full_name} \n"

    return info


@dp.message_handler(commands=["l", "leave"])
async def leave_handler(message: Message):
    log.info(f"User [ID: {message.from_user.id}] tried to leave his room")
    try:
        room = get_room_by_user(message.from_user)
        if room.admin == message.from_user:
            log.info(f"User [ID: {message.from_user.id}] delete his room [ID: {room.id}]")
            await notify(room, "deleted")
            del room
        else:
            room.del_user(user_to_del=message.from_user)
    except NoSuchRoomError:
        log.info(f"User [ID: {message.from_user.id}] unsuccessfully tried to leave room but he is not in room.")
        await message.reply("You can't leave room. You have not entered it.")


@dp.message_handler(commands=["/loc", "/locations"])
async def send_locations(message: Message):
    # TODO add logging
    try:
        room = get_room_by_user(user=message.from_user)
        if room.status == 0:
            await message.reply(f"Available locations: \n {location_text}")
        else:
            if message.from_user == room.spy:
                await message.reply(f"You are spy in this game. Available locations: {location_text}.")
            else:
                await message.reply(f"Current location is {room.location}. Available locations: {location_text}.")
    except NoSuchRoomError:
        await message.reply(f"Available locations: \n {location_text}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
