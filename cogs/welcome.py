from twitchio.ext import commands
from twitchio.ext.commands import MissingRequiredArgument


class WelcomeMessageCog(commands.Cog):

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.command(name="welcome")
    async def welcome(self, ctx, command=None, username=None, *, custom_message=None):
        """
        Function to Remove/Add/Edit users to Welcome message system
        :param ctx: Context
        :param command: What command
        :param username: Username for the chosen user
        :param custom_message: Custom message for the user
        :return: None
        """
        user = ctx.author.is_mod
        if not user:
            return
        command_handlers = {
            "view": self.view_welcome_message,
            "remove": self.remove_user,
            "add": self.add_user,
            "edit": self.edit_user,
        }
        command = command.lower() if command else None
        handler = command_handlers.get(command)
        if handler:
            await handler(ctx, username, custom_message)
        else:
            await ctx.send("Command not recognized. Please use: !welcome add/edit/remove/view <username> <custom_message>.")

    async def view_welcome_message(self, ctx, username, custom_message):
        """
        View custom message for user
        :param ctx: Context
        :param username: Username of who you are going add
        :param custom_message: Not used but can not be removed
        :return: None
        """
        if not username:
            raise MissingRequiredArgument("username")

        result = self.db.check_custom_message(username)

        if result:
            await ctx.send(f"The current welcome message for {username} is {result}")
        else:
            await ctx.send(f"No custom message found for {username}")

    async def remove_user(self, ctx, username, custom_message):
        """
        Remove user from welcome list
        :param ctx: Context
        :param username: Username of who you are going add
        :param custom_message: Not used but can not be removed
        :return: None
        """
        if not username:
            raise MissingRequiredArgument("username")

        result = self.db.remove_user(username)
        if result:
            await ctx.send(f"{username} has been removed from the welcome list.")
        else:
            await ctx.send(f"{username} is not recognized or is not on the welcome list.")

    async def add_user(self, ctx, username, custom_message):
        """
        Add user to welcome list
        :param ctx: Context
        :param username: Username of who you are going add
        :param custom_message: Custom message you want to add to the user
        :return: None
        """
        if not username or not custom_message:
            raise MissingRequiredArgument("username and custom_message")

        username = username.lstrip('@')

        result = self.db.add_user(username)
        if result:
            self.db.set_custom_message(custom_message, username)
            await ctx.send(f"{username} has been added to the welcome list.")
        else:
            await ctx.send("User already exists in the welcome list.")

    async def edit_user(self, ctx, username, custom_message):
        """
        Edit custom message for user
        :param ctx: Context
        :param username: Username of who you want to change message on
        :param custom_message: New custom message
        :return: None
        """
        if not username or not custom_message:
            raise MissingRequiredArgument("username and custom_message")

        result = self.db.set_custom_message(custom_message, username)
        if result:
            await ctx.send(f"{username}'s custom message has been updated to: {custom_message}")
        else:
            await ctx.send(f"{username} is not recognized or is not on the welcome list.")
