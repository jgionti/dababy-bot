"""This test doesn't really work."""

# import asyncio
# import pytest
# import threading
# import time
# from src.dababy_bot import DaBabyBot

# pytest_plugins = ('pytest_asyncio',)
# START_TIMEOUT_SEC = 30

# bot = DaBabyBot()
# loop = asyncio.new_event_loop()

# def start_bot():
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(bot.run(bot.token))
#     loop.close()
# thread = threading.Thread(target=start_bot, args=())
# thread.start()

# class TestMain:
#     """Itegration tests for connecting to Discord.
    
#     Makes sure the bot compiles and can connect.
#     """

#     @pytest.fixture(scope="session", autouse=True)
#     def wait_for_start(self):
#         """Waits for bot to connect, then cleans it up."""
#         count = 0
#         while (bot.user is None 
#                 and thread.is_alive()
#                 and count <= START_TIMEOUT_SEC):
#             time.sleep(1)
#             count += 1
#         yield
#         asyncio.run_coroutine_threadsafe(bot.close(), loop)
#         thread.join()

#     @pytest.mark.asyncio
#     async def test_heartbeat(self):
#         """Tests whether client is connected."""
#         assert bot.user is not None

#     # If tests get stuck: taskkill /F /IM python.exe in command prompt
