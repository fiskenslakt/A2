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
