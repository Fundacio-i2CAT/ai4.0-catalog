from enum import Enum


class Status(Enum):
    CREATED = 0
    SAVED = 1
    PENDING = 2
    CONFIRMED = 3
    PROVISIONED = 4
    RUNNING = 5
    DEPLOYED = 6
    FAILED = 7
    DISABLED = 8
    UNKNOWN = 9

state_dict = {
    "CREATED": Status.CREATED.value,
    "SAVED": Status.SAVED.value,
    "PENDING": Status.PENDING.value,
    "CONFIRMED": Status.CONFIRMED.value,
    "PROVISIONED": Status.PROVISIONED.value,
    "RUNNING": Status.RUNNING.value,
    "DEPLOYED": Status.DEPLOYED.value,
    "FAILED": Status.FAILED.value,
    "DISABLED": Status.DISABLED.value,
    "UNKNOWN": Status.UNKNOWN.value,
}


def get_state_enum_value(state):
    print '111111111111111'
    print state
    return state_dict[state]