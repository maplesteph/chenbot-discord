from enum import Enum

class MessageEvent(Enum):
    on_message = 1
    on_raw_message_delete = 2
    on_raw_message_edit = 3
    on_raw_reaction_add = 4