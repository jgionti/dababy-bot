from typing import List

import discord
from src.events.cap import CapEvent
from src.events.event import Event
from src.events.maxisonline import MaxIsOnlineEvent
from src.events.pingchallenge import PingChallengeEvent
from src.events.stolenletter import StolenLetterEvent


def get_events(bot: discord.Bot) -> List[Event]:
    """Instantiate the list of server events.

    Returns a list of objects corresponding to each Event.
    """

    events = []

    events.append(PingChallengeEvent(bot))
    events.append(StolenLetterEvent(bot))
    events.append(MaxIsOnlineEvent(bot))
    events.append(CapEvent(bot))

    return events

