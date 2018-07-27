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

    @Plugin.command('choose', '<options:str...>') 
    def choose_command(self, event, options):
        """= choose =
        Choose between two or more options
        usage    :: $choose
        aliases  :: None
        category :: Utilities
        """
        options = options.split('\\')
        bot_choice = random.choice(options)
        if len(options) > 1:
            event.msg.reply('I choose: {}'.format(bot_choice))
        
