from typing import List

import discord
from lib.events.cap import CapEvent
from lib.events.event import Event
from lib.events.maxisonline import MaxIsOnlineEvent
from lib.events.pingchallenge import PingChallengeEvent
from lib.events.stolenletter import StolenLetterEvent


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

