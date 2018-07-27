from disco.bot import Plugin

import random


class UtilitiesPlugin(Plugin):
    @Plugin.command('ping')
    def ping_command(self, event):
        """= ping =
        Latency of bot and discord (not very accurate)
        usage    :: $ping
        aliases  :: None
        category :: Utilities
        """
        user_ping = event.msg.timestamp
        bot = event.msg.reply('Pong!')
        bot_ping = bot.timestamp

        user_bot_latency = (bot_ping - user_ping).total_seconds() * 1000.0

        bot.edit('Latency of you to bot: ~{:.2f}ms'.format(user_bot_latency))

    @Plugin.command('choose', '<message:str...>') 
    def choose_command(self, event, message):
        """= choose =
        Choose between two or more choices
        usage    :: $choose
        aliases  :: None
        category :: Utilities
        """
        choices = message.split('\\')
        bot_choice = random.choice(choices)
        if len(choices) > 1:
            event.msg.reply('I choose: {}'.format(bot_choice))
        
