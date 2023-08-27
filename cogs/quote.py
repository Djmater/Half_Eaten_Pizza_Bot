import random

from twitchio.ext import commands
from twitchio.ext.commands import MissingRequiredArgument


class Quote(commands.Cog):
    """
    TODO: Quote Command handler
    TODO: Quote Add
    TODO: Quote Edit
    TODO: Quote Remove
    TODO: Quote INT
    TODO: Quote Random
    TODO: Quote Import
    TODO: Quote Export
    """

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.command()
    async def quote(self, ctx, command=None):
        """
        Command handler for Quote
        :param ctx: Context
        :param command: Command chosen
        :return: None
        """
        command_handlers = {
            "add": self.add_quote,
            "edit": self.edit_quote,
            "remove": self.remove_quote,
            int: self.specific_quote,
            None: self.random_quote
        }

        command = command.lower() if command else None
        handler = command_handlers.get(command)
        if handler:
            await handler(ctx)
        else:
            await ctx.send("Command not recognized.")

    async def add_quote(self, ctx):
        await ctx.send("Add Quote")

    async def edit_quote(self, ctx):
        pass

    async def remove_quote(self, ctx):
        pass

    async def specific_quote(self, ctx):
        pass

    @staticmethod
    async def random_quote(ctx, random_int):
        random.randint(1, 600)
        await ctx.send(f"{random_int}")
        return

