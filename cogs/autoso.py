from twitchio.ext import commands
from twitchio.ext.commands import MissingRequiredArgument


class AutoShoutOut(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.command(aliases=("autoso",))
    async def autoSo(self, ctx, command=None, username=None):
        """
        Command for setting up or viewing auto shoutout
        :param ctx: Context
        :param command: The chosen command of View/Toggle
        :param username: Username of the chosen user
        """
        user = ctx.author.is_mod
        if not user:
            return
        command_handlers = {
            "view": self.view_shoutout,
            "toggle": self.toggle,
        }
        command = command.lower() if command else None
        handler = command_handlers.get(command)
        if handler:
            await handler(ctx, username)
        else:
            await ctx.send("Command not recognized. Please use valid commands.")

    async def view_shoutout(self, ctx, username):
        """
        View status
        :param ctx: Context
        :param username: Username of who you want to look up
        :return: None
        """
        if not username:
            raise MissingRequiredArgument("username")

        result = self.db.check_shoutout(username)
        if result:
            status = "On"
        else:
            status = "Off"
        await ctx.send(f"Auto shoutout for {username} is currently {status}")

    async def toggle(self, ctx, username):
        if not username:
            raise MissingRequiredArgument("username")

        username = username.lstrip('@')
        result, flag = self.db.toggle_shoutout(username)

        if result == 3:
            await ctx.send(f"{username} is added to the auto shoutout list")
        else:
            status = "On" if flag else "Off"
            await ctx.send(f"Auto shoutout is set to {status} on {username}")
