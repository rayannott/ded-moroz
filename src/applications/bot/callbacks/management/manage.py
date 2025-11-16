from enum import StrEnum

from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.applications.bot.callbacks.management.complete import CompleteCallback
from src.applications.bot.callbacks.management.delete import DeleteCallback
from src.applications.bot.callbacks.management.info import InfoCallback
from src.applications.bot.callbacks.management.kick import KickCallback
from src.applications.bot.callbacks.management.play import PlayCallback
from src.applications.bot.utils import get_keyboard, remove_keyboard, text
from src.models.room import Room
from src.models.user import User


class ManageActions(StrEnum):
    CANCEL = "cancel"
    INFO = "about room"
    COMPLETE = "complete"
    DELETE = "delete room"
    KICK_PLAYER = "kick player"
    START = "start game"


class ManageCallback(Callback):
    @staticmethod
    def get_available_actions(room: Room) -> list[str]:
        # all except complete if not started and not completed
        actions = []
        if not room.game_started and not room.game_completed:
            actions.extend(
                [
                    ManageActions.DELETE.value,
                    ManageActions.START.value,
                    ManageActions.KICK_PLAYER.value,
                ]
            )
        # can only complete if started and not completed
        elif room.game_started:
            actions.extend([ManageActions.COMPLETE.value])
        else:
            logger.error("Should not be possible to manage a completed room")
        # no actions if completed
        actions.extend([ManageActions.INFO.value, ManageActions.CANCEL.value])
        return actions

    def process(self, user: User, *, message: types.Message):
        logger.info(f"/manage from {user}")

        managed_rooms = self.moroz.get_rooms_managed_by_user(user)
        active_managed_rooms = [room for room in managed_rooms if room.is_active()]

        if not active_managed_rooms:
            past_games_info = (
                f" However, you have managed {len(managed_rooms)} rooms in the past. Use /history to see them."
                if managed_rooms
                else ""
            )
            self.bot.send_message(
                user.id,
                f"You are not managing any active rooms currently.{past_games_info}",
            )
            return

        code_to_room = {room.short_code: room for room in active_managed_rooms}

        answer = self.bot.send_message(
            user.id,
            "Please select a room to manage:",
            reply_markup=get_keyboard(
                [f"{room.display_short_code}" for room in active_managed_rooms]
                + [ManageActions.CANCEL.value]
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
        if chosen_text == ManageActions.CANCEL.value:
            self.bot.send_message(
                user.id,
                "Room management cancelled.",
                reply_markup=remove_keyboard(),
            )
            logger.debug(f"Room management cancelled by {user}")
            return
        room_short_code = int(chosen_text)
        logger.debug(f"Room to manage chosen: {room_short_code} by {user}")

        room = code_to_room.get(room_short_code)
        if room is None:
            logger.critical(f"Room {room_short_code=} not found; {user=}")
            self.bot.send_message(
                user.id, "Internal error.", reply_markup=remove_keyboard()
            )
            return

        actions_kb = get_keyboard(self.get_available_actions(room), row_width=2)

        answer = self.bot.send_message(
            user.id,
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
            logger.debug(f"Invalid action chosen: {chosen_text} by {user}")
            self.bot.send_message(
                user.id,
                "Invalid action selected. (How did you do that, huh?)",
                reply_markup=remove_keyboard(),
            )
            return
        if chosen_text == ManageActions.CANCEL.value:
            self.bot.send_message(
                user.id,
                "Room management cancelled.",
                reply_markup=remove_keyboard(),
            )
            logger.debug(f"Room management cancelled by {user}")
        elif chosen_text == ManageActions.INFO.value:
            InfoCallback(bot=self.bot, moroz=self.moroz).process_management(
                room=room, user=user
            )
        elif chosen_text == ManageActions.DELETE.value:
            DeleteCallback(bot=self.bot, moroz=self.moroz).process_management(
                room=room, user=user
            )
        elif chosen_text == ManageActions.KICK_PLAYER.value:
            KickCallback(bot=self.bot, moroz=self.moroz).process_management(
                room=room, user=user
            )
        elif chosen_text == ManageActions.START.value:
            PlayCallback(bot=self.bot, moroz=self.moroz).process_management(
                room=room, user=user
            )
        elif chosen_text == ManageActions.COMPLETE.value:
            CompleteCallback(bot=self.bot, moroz=self.moroz).process_management(
                room=room, user=user
            )
        else:
            logger.debug(f"Unknown action chosen: {chosen_text} by {user}")
            self.bot.send_message(
                user.id,
                "Unknown action selected.",
                reply_markup=remove_keyboard(),
            )
