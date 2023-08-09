import configparser
import os
import twitchio
from twitchio.ext import commands
from db import DB
from datetime import datetime
from configparser import ConfigParser
from twitchio.ext.commands.errors import MissingRequiredArgument
from pathlib import Path


class Bot(commands.Bot):
    def __init__(self, config):
        self.twitch_token = config.twitch_token
        self.twitch_prefix = config.twitch_prefix
        self.twitch_initial_channels = config.twitch_initial_channels
        self.welcome_cooldown = config.welcome_cooldown
        # Initialise our Bot with our access token, prefix, and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=self.twitch_token, prefix=self.twitch_prefix, initial_channels=self.twitch_initial_channels)

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        print(message.content, message.author.id)

        await self.handle_commands(message)

        # Checking if user is in db
        await self.welcome_message(message.author.name, message)

    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            # await ctx.send("Command not recognized. Please use valid commands.")
            pass
        else:
            # Handle other exceptions here if needed
            print(f"An error occurred: {error}")

    @commands.command()
    async def welcome(self, ctx, command, name=None, *, custom_message=None):
        user = ctx.author.is_mod
        if user == True:

            try:
                if command.lower() == "remove":
                    result = db.remove_user(name)
                    if result == True:
                        # print(result)
                        await ctx.send(f"{name} is successfully removed")
                    else:
                        await ctx.send(f"{name} is not recognised or added to welcome list")
                    return

                if not name or not custom_message or not command:
                    raise MissingRequiredArgument("name and custom_message")

                if command.lower() == "add":

                    if name.startswith('@'):
                        name = name[1:]
                    try:
                        result = db.add_user(name)
                        if result == False:
                            await ctx.send("User already exist")
                            return
                        db.set_custommessage(custom_message, name)
                        if result == True:
                            await ctx.send(f"{name} added to the welcome list")
                    except:
                        pass
                        # print("already added")
                    # print(custom_message)

                elif command.lower() == "edit":
                    # print(custom_message, name)
                    result = db.set_custommessage(custom_message, name)
                    if result == False:
                        await ctx.send(f"{name} is not recognised or added to welcome list")
                    if result == True:
                        await ctx.send(f"{name} new custom message is {custom_message}")

                else:
                    await ctx.send(
                        'Command not recognized, please use: !welcome add/edit/remove <username> <custom_message>')
                    # print(command)

            except MissingRequiredArgument as e:
                await ctx.send(
                    "Command not recognized, please use: !welcome add/edit/remove <username> <custom_message>")

    def check_time_difference(self, message_author):
        timestamp_str = db.check_lastmessage(message_author)
        timestamp = datetime.fromisoformat(timestamp_str)
        current_time = datetime.now()

        time_difference_seconds = (current_time - timestamp).total_seconds()
        time_difference_minutes = time_difference_seconds / 60
        if time_difference_minutes > self.welcome_cooldown:
            # print(f"Time is more than 2 minutes in difference: {time_difference_minutes} minutes")
            return True
        else:
            # print(f"Time is less than or equal to 2 minutes in difference: {time_difference_minutes} minutes")
            return False

    async def welcome_message(self, name, message):

        if db.check_user(name):

            # Checking if sufficient time has passed
            if self.check_time_difference(name):

                # Setting new chatting time
                db.set_lastmessage(name)

                # Checking if user has a custom message, if not will use default message
                if db.check_custommessage(name) != False:
                    welcome_message = db.check_custommessage(name)
                    await message.channel.send(welcome_message)
            else:
                print("Not long enough")
                return


class Config():
    def __init__(self, cp):
        self.config_file = Path('config.ini')
        self.configparser = cp
        self.twitch_token = ''
        self.twitch_prefix = ''
        self.twitch_initial_channels = []
        self.welcome_cooldown = 60

    def read_config_file(self):

        if not self.config_file.is_file:
            print("No file")
            self.make_config_file()
            self.write_config_file()

        self.configparser.read(self.config_file)

        # Read the Twitch settings
        self.twitch_token = self.configparser.get('Twitch', 'token')
        self.twitch_prefix = self.configparser.get('Twitch', 'prefix')
        self.twitch_initial_channels.append(self.configparser.get('Twitch', 'initial_channels'))
        try:
            self.welcome_cooldown = float(self.configparser.get('Twitch', 'welcome_cooldown'))
        except:
            self.welcome_cooldown = 60

    def make_config_file(self):
        # Create a ConfigParser object
        make_config = self.configparser

        # Add the structure to the file we will create
        make_config.add_section('Twitch')
        make_config.set('Twitch', 'token', '')
        make_config.set('Twitch', 'prefix', '')
        make_config.set('Twitch', 'initial_channels', '')
        make_config.set('Twitch', 'welcome_cooldown', '')
        # Write the new structure to the new file
        with open(r"config.ini", 'w') as configfile:
            make_config.write(configfile)

    def write_config_file(self):
        # Create a ConfigParser object
        write_config = self.configparser

        # Add the structure to the file we will create
        token = input("Please input Twitch Token:")
        write_config.set('Twitch', 'token', token)

        prefix = input("Please input Twitch Prefix:")
        write_config.set('Twitch', 'prefix', prefix)

        channel = input("Please input which channel you want the bot in:")
        write_config.set('Twitch', 'initial_channels', channel)

        cooldown = input("Please input your wished cooldown on welcome:")
        write_config.set('Twitch', 'welcome_cooldown', cooldown)

        # Write the new structure to the new file
        with open(r"config.ini", 'w') as configfile:
            write_config.write(configfile)


if __name__ == "__main__":
    try:
        config = Config(configparser.ConfigParser())
        config.read_config_file()
        db = DB()
        bot = Bot(config)
        bot.run()
    except Exception as e:
        print(e)
        input("Press enter to close...")
