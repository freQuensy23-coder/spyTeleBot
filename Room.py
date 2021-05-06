import time
from random import randint, choice
from logging import getLogger
from aiogram.types import User, Message
from Exceptions import *

log = getLogger("Room")
rooms = []
locations = ["a", "b", "c", "d"]
location_text = "".join([f"* {location}\n" for location in locations])

class Room:
    def __init__(self, admin):
        self.created_at = time.time()
        self.admin: User = admin
        self.users: list[User] = [admin]
        self.status: int = 0  # Waiting = 0, In Game = 1
        self.spy: User = None
        self.location = None
        self.id: int = -1
        self.generate_room_id()
        rooms.append(self)

    def generate_room_id(self):
        id_is_used = True
        while id_is_used:
            id_is_used = False
            room_id = randint(1000, 9999)
            log.debug(f"Room id = {room_id}")
            for room in rooms:
                if room.id == room_id:
                    id_is_used = True
                    break
            if not id_is_used:
                log.debug(f"Created room id {room_id}")
                self.id = room_id
                return True

    def add_new_user(self, user) -> bool:
        """Add user to room. If he can enter returns True else return False"""
        log.debug(f"User {user.id} trying to room {self.id}")
        if self.can_user_enter(user) and user not in self.users:
            self.users.append(user)
            return True
        else:
            return False

    def __del__(self):
        log.debug(f"Room {self.id} deleted.")
        if self.id != -1:
            for i, room in rooms:
                if room.id == self.id:
                    del rooms[i]
    def __hash__(self):
        return self.id

    def start_game(self):
        if len(self.users) >= 3: # TODO 3 Debug
            if self.status == 1:
                raise GameAlreadyStartedError
            self.location = generate_location()
            self.spy = choice(self.users)
            self.status = 1
        else:
            raise NotEnoughPlayersError

    def can_user_enter(self, user: User) -> bool:
        """Can user user connect ot this room"""
        if self.status == 0:
            return True
        else:
            return False  # If game have already started

    def stop_game(self):
        self.spy = None
        self.location = None
        self.status = 0

    def del_user(self, user_to_del):
        if self.status == 0:
            self.users.remove(user_to_del)
        if self.status == 1:
            self.stop_game()
            self.users.remove(user_to_del)

# TODO Waste cleaner - clean rooms that crated a long time ago


def generate_location():
    global locations
    return choice(locations) # TODO create location func


def add_user_to_room(room_id: int, user: User) -> Room:
    room_found = False
    if not rooms:
        # If there are no created rooms
        raise NoSuchRoomError
    for room in rooms:
        if room.id == room_id:
            room_found = True
            break
    if not room_found:
        raise NoSuchRoomError
    if not room.add_new_user(user):
        raise CanNotEnterRoomError
    return room


def del_user(user: User):
    if rooms:
        for room in rooms:
            try:
                room.users.remove(user)
            except ValueError:
                pass  # If such user not fount in this room


def get_room_by_user(user: User) -> Room:
    """Get the room the user is in"""
    if rooms:
        for room in rooms:
            if user in room.users:
                return room
        raise NoSuchRoomError
    else:
        raise NoSuchRoomError
