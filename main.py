# -*- coding: utf-8 -*-
"""
Importing packages needed for the bot to function,
"""
from configparser import ConfigParser
from datetime import datetime
from typing import Optional, List

from twitchio import User
from twitchio.ext import commands

from cogs.autoso import AutoShoutOut
from cogs.welcome import WelcomeMessageCog
from config import Config
from db import DB


class Bot(commands.Bot):
    """
    The core of the bot where it handles messages, Exceptions.

    TODO:
        Write better documentation.
    """

    def __init__(self, twitch_config):

        self.twitch_token = twitch_config.twitch_token
        self.twitch_prefix = twitch_config.twitch_prefix
        self.twitch_initial_channels = twitch_config.twitch_initial_channels
        self.welcome_cooldown = twitch_config.welcome_cooldown
        # Initialise our Bot with our access token, prefix, and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=self.twitch_token, prefix=self.twitch_prefix,
                         initial_channels=self.twitch_initial_channels)

    async def event_ready(self):
        """
        Notifying that bot is ready and prints command and welcome list
        """
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        print("""
Command list:
welcome
    View
    Delete
    Add
    Edit

eg: !welcome view djmater

autoSo
    View
    Toggle
    
eg: !autoSo view djmater
        """)
        print("""
Welcome List
        """)
        for i in db.fetch_names():
            custom_message = db.check_custom_message(i)
            final_string = f"{i} - {custom_message}"
            print(final_string)

    async def event_message(self, message):
        """
        Reading chat messages and sending events if commands are found
        :param message:
        :return:
        """
        # Messages with echo set to True are messages sent by the bot...
        # For now, we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        print(message.content, message.author.id)

        await self.handle_commands(message)

        # Checking if user is in db
        await self.welcome_message(message.author.name, message)
        await self.shoutout_message(message.author.name, message)

    async def event_command_error(self, ctx, error):
        """
        Handler for command errors
        :param ctx: Context
        :param error: What error is raised
        :return: Nothing
        """
        if isinstance(error, commands.CommandNotFound):
            # await ctx.send("Command not recognized. Please use valid commands.")
            pass
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Command not recognized, Please use valid commands.")
        else:
            pass
            # Handle other exceptions here if needed
            # print(f"An error occurred: {error}")

    async def fetch_users(
            self,
            names: List[str] = None,
            ids: List[int] = None,
            token: str = None,
            force=False,
    ) -> List[User]:
        """
        Fetch user info on twitch, so we have the Twitch ID
        :param names:
        :param ids:
        :param token:
        :param force:
        :return:
        """
        data = await self._http.get_users(ids, names, token=token)
        return data

    async def fetch_channels(self, broadcaster_ids, token: Optional[str] = None):
        """
        Fetch Channel information, so we get the game_name
        :param broadcaster_ids: The twitch id of who you want to search for
        :param token:
        :return: Returning a list of data that's in a dictionary

        content_classification_labels
        delay
        game_id
        game_name
        is_branded_content
        language
        tags
        title
        user
        """
        data = await self._http.get_channels_new(broadcaster_ids=broadcaster_ids, token=token)
        return data

    def check_time_difference(self, message_author, time_difference_type):
        """
        Checking if the user has waited long enough for Welcome message to be sent
        :param time_difference_type: what type of type check, if its shoutout or welcome
        :param message_author: username of the user we are checking
        :return: True if it's true
        """
        timestamp_str = ''
        if time_difference_type == "welcome":
            timestamp_str = db.check_last_message(message_author)
        elif time_difference_type == "shoutout":
            timestamp_str = db.check_last_shoutout(message_author)
        timestamp = datetime.fromisoformat(timestamp_str)
        current_time = datetime.now()

        time_difference_seconds = (current_time - timestamp).total_seconds()
        time_difference_minutes = time_difference_seconds / 60
        if time_difference_minutes > self.welcome_cooldown:
            # print(f"Time is more than 2 minutes in difference: {time_difference_minutes} minutes")
            return True

    async def shoutout_message(self, message_author, message):
        """
        Auto shoutout that will shoutout anyone that fulfills the criteria.
        :param message_author: Who wrote in the chat
        :param message: Just passing message function into to be able to send message
        :return: None
        """
        if db.check_shoutout_user(username=message_author):
            if db.check_shoutout(username=message_author)[0]:
                if self.check_time_difference(message_author=message_author, time_difference_type="shoutout"):
                    db.set_last_shoutout(username=message_author)
                    result = await self.fetch_users([message_author], token=self.twitch_token)
                    game_name = await self.fetch_channels([result[0]['id']])
                    game_name = game_name[0]['game_name']
                    await message.channel.send(
                        f"Checkout {message_author} they were last playing {game_name} you should deff give them a follow https://twitch.tv/{message_author}")

    async def welcome_message(self, message_author, message):
        """
        Here we process if the user is in DB, then if the time difference is big enough then send welcome message
        :param message_author:  Name of the user
        :param message: To send the message in the chat
        :return: None
        """
        if db.check_user(message_author):

            # Checking if sufficient time has passed
            if self.check_time_difference(message_author, time_difference_type="welcome"):

                # Setting new chatting time
                db.set_last_message(message_author)

                # Checking if user has a custom message, if not will use default message
                if db.check_custom_message(message_author):
                    welcome_message = db.check_custom_message(message_author)
                    await message.channel.send(welcome_message)
            else:
                # print("Not long enough")
                return


if __name__ == "__main__":
    try:
        config = Config(ConfigParser())
        config.read_config_file()
        db = DB()
        bot = Bot(config)
        bot.add_cog(WelcomeMessageCog(bot, db))
        bot.add_cog(AutoShoutOut(bot, db))
        bot.run()
    except Exception as e:
        print(e)
        input("Press enter to close...")
