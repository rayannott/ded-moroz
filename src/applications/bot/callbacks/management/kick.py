from loguru import logger

from src.applications.bot.callbacks.management.base import ManagementCallback
from src.applications.bot.utils import get_keyboard, remove_keyboard, text
from src.models.room import Room
from src.models.user import User
from src.shared.exceptions import NotInRoom, UserNotFound


class KickCallback(ManagementCallback):
    def process_management(self, user: User, room: Room):
        logger.info(f"Kick action chosen by {user} in {room}")

        if not (players := self.moroz.get_users_in_room(room.id)):
            self.bot.send_message(
                user.id,
                "There are no players in the room to kick.",
                reply_markup=remove_keyboard(),
            )
            logger.debug(f"No players to kick in {room} for {user}")
            return

        player_repr_to_id = {
            player.formal_display_name: player.id for player in players
        }
        keyboard = get_keyboard(
            list(player_repr_to_id.keys()) + ["Cancel"],
            row_width=2,
        )  # TODO dynamic row width?

        msg = self.bot.send_message(
            user.id,
            "Select a player to kick:",
            reply_markup=keyboard,
        )

        self.bot.register_next_step_handler(
            msg,
            self._handle_player_selected,
            user=user,
            room=room,
            player_repr_to_id=player_repr_to_id,
        )

    def _handle_player_selected(
        self,
        message,
        user: User,
        room: Room,
        player_repr_to_id: dict[str, int],
    ):
        if (chosen_text := text(message)) == "Cancel":
            self.bot.send_message(
                user.id,
                "Kick action cancelled.",
                reply_markup=remove_keyboard(),
            )
            logger.debug(f"Kick action cancelled by {user}")
            return

        if chosen_text not in player_repr_to_id:
            self.bot.send_message(
                user.id,
                "Invalid selection. Please try the kick command again.",
                reply_markup=remove_keyboard(),
            )
            logger.debug(f"Invalid player selection by {user}: {chosen_text!r}")
            return

        try:
            player_id_to_kick = player_repr_to_id[chosen_text]
            player_to_kick = self.moroz.get_user(player_id_to_kick)
            room = self.moroz.leave_room(user_id=player_to_kick.id)
        except (KeyError, UserNotFound):
            logger.opt(exception=True).critical(f"Player {chosen_text=} not found")
            self.bot.send_message(
                user.id,
                "Internal error.",
                reply_markup=remove_keyboard(),
            )
            return
        except NotInRoom:
            logger.warning(f"Player {chosen_text=} was not in room (why?)")
            self.bot.send_message(
                user.id,
                f"Player {chosen_text} is already not in the room. "
                "Perhaps they left while you were choosing?",
                reply_markup=remove_keyboard(),
            )
            return

        logger.debug(f"User manager {user} kicking {player_to_kick=} from {room=}")

        self.bot.send_message(
            user.id,
            f"Player {player_to_kick.formal_display_name} has been kicked from the room {room.display_short_code}.",
            reply_markup=remove_keyboard(),
        )

        self._notify_kicked_player(player_to_kick, room, user)

    def _notify_kicked_player(
        self,
        kicked_user: User,
        room: Room,
        manager_user: User,
    ):
        logger.info(
            f"Notifying kicked user {kicked_user} about being kicked from {room}"
        )
        self.bot.send_message(
            kicked_user.id,
            f"You have been kicked from the room {room.display_short_code} by its manager {manager_user.formal_display_name}.",
        )
