from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.applications.bot.callbacks.management.complete import CompleteCallback
from src.applications.bot.callbacks.management.delete import DeleteCallback
from src.applications.bot.callbacks.management.kick import KickCallback
from src.applications.bot.callbacks.management.play import PlayCallback
from src.applications.bot.utils import get_keyboard, remove_keyboard, text
from src.models.room import Room
from src.models.user import User

_CANCEL_ACTION = "cancel"
_COMPLETE_ACTION = "complete"
_DELETE_ACTION = "delete room"
_KICK_PLAYER_ACTION = "kick player"
_START_GAME_ACTION = "start game"


class ManageCallback(Callback):
    @staticmethod
    def get_available_actions(room: Room) -> list[str]:
        # all except complete if not started and not completed
        actions = []
        if not room.game_started and not room.game_completed:
            actions.extend(
                [
                    _DELETE_ACTION,
                    _START_GAME_ACTION,
                    _KICK_PLAYER_ACTION,
                ]
            )
        # can only complete if started and not completed
        elif room.game_started:
            actions.extend([_COMPLETE_ACTION])
        # no actions if completed

        actions.append(_CANCEL_ACTION)
        return actions

    def process(self, message: types.Message, user: User):
        logger.info(f"/manage from {user}")

        managed_rooms = self.moroz.get_active_rooms_managed_by_user(user)

        if not managed_rooms:
            self.bot.send_message(
                message.chat.id,
                "You are not managing any active rooms currently.",
            )
            return

        code_to_room = {room.short_code: room for room in managed_rooms}

        answer = self.bot.send_message(
            message.chat.id,
            "Please select a room to manage:",
            reply_markup=get_keyboard(
                [f"{room.display_short_code}" for room in managed_rooms]
                + [_CANCEL_ACTION]
            ),
        )
        self.bot.register_next_step_handler(
            answer,
            self._handle_room_chosen,
            user=user,
            code_to_room=code_to_room,
        )

    def _handle_room_chosen(
        self,
        message: types.Message,
        user: User,
        code_to_room: dict[int, Room],
    ):
        chosen_text = text(message)
        if chosen_text == _CANCEL_ACTION:
            self.bot.send_message(
                message.chat.id,
                "Room management cancelled.",
                reply_markup=remove_keyboard(),
            )
            logger.info(f"Room management cancelled by {user}")
            return
        room_short_code = int(chosen_text)
        logger.info(f"Room to manage chosen: {room_short_code} by {user}")

        room = code_to_room.get(room_short_code)
        if room is None:
            logger.critical(f"Room {room_short_code=} not found; {user=}")
            self.bot.send_message(
                message.chat.id, "Internal error.", reply_markup=remove_keyboard()
            )
            return

        actions_kb = get_keyboard(self.get_available_actions(room))

        answer = self.bot.send_message(
            message.chat.id,
            f"You are managing room {room.display_short_code}. Please choose an action:",
            reply_markup=actions_kb,
        )

        self.bot.register_next_step_handler(
            answer,
            self._handle_action_chosen,
            user=user,
            room=room,
        )

    def _handle_action_chosen(
        self,
        message: types.Message,
        user: User,
        room: Room,
    ):
        chosen_text = text(message)
        if chosen_text not in self.get_available_actions(room):
            logger.info(f"Invalid action chosen: {chosen_text} by {user}")
            self.bot.send_message(
                message.chat.id,
                "Invalid action selected. (How did you do that, huh?)",
                reply_markup=remove_keyboard(),
            )
            return
        if chosen_text == _CANCEL_ACTION:
            self.bot.send_message(
                message.chat.id,
                "Room management cancelled.",
                reply_markup=remove_keyboard(),
            )
            logger.info(f"Room management cancelled by {user}")
        elif chosen_text == _DELETE_ACTION:
            DeleteCallback(bot=self.bot, moroz=self.moroz).process_management(
                message=message, room=room, user=user
            )
        elif chosen_text == _KICK_PLAYER_ACTION:
            KickCallback(bot=self.bot, moroz=self.moroz).process_management(
                message=message, room=room, user=user
            )
        elif chosen_text == _START_GAME_ACTION:
            PlayCallback(bot=self.bot, moroz=self.moroz).process_management(
                message=message, room=room, user=user
            )
        elif chosen_text == _COMPLETE_ACTION:
            CompleteCallback(bot=self.bot, moroz=self.moroz).process_management(
                message=message, room=room, user=user
            )
        else:
            logger.info(f"Unknown action chosen: {chosen_text} by {user}")
            self.bot.send_message(
                message.chat.id,
                "Unknown action selected.",
                reply_markup=remove_keyboard(),
            )
