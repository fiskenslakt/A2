import random

from disco.bot import Plugin


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
        Randomly choose between two or more options
        usage    :: $choose <options...>
        aliases  :: None
        category :: Utilities
        == Arguments
        options  :: A list of options from which one will be chosen
        == Examples
        $choose windows\macOS\linux 'I choose: macOS'
        $choose boil em\mash em\stick em in a stew 'I choose: boil em'
        $choose a\ \c 'I choose: c'
        """
        options = options.split('\\')
        options = [i for i in options if i.strip() != '']
        bot_choice = random.choice(options)
        if len(options) > 1:
            event.msg.reply('I choose: {}'.format(bot_choice))
        print(options)

