import os

GUILD_IDS = [
    # BETA
    1167228972443123772,
] if os.environ.get("BETA") is not None else [
    # PROD
    730196305124655176,
]
"""Guild IDs the bot will allow slash commands for."""

GLOBAL_COMMANDS = ["poll", "role", "vclog"]
"""Names of commands that can be used in any channel.

By default, commands will be denied if not executed in #dababy.
"""
