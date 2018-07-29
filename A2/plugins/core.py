"""Core functionality of the bot.

Handles bot initialisation, configuration, and 'lower-level' operations.
"""
from disco.bot import Plugin
from disco.bot.command import CommandLevels
from disco.types.user import Game, GameType, Status


class CorePlugin(Plugin):
    @Plugin.listen('Ready')
    def on_ready(self, ctx):
        game = Game(
            type=GameType.listening,
            name='nothing because I don\'t work yet')
        self.client.update_presence(Status.online, game)

    @Plugin.command('reload')
    def reload_command(self, event):
        """= reload =
        Reloads all plugins except Core.
        usage    :: $reload
        aliases  :: None
        category :: Core
        """
        user_level = self.bot.get_level(event.author)

        if user_level < CommandLevels.OWNER:
            event.msg.reply('**Only admins can do that!**')
            return

        self.log.info('Reloading Plugins')
        reloaded_plugins = []

        for name, instance in self.bot.plugins.copy().items():
            # Don't reload Core.
            if instance == self:
                continue

            self.log.info('Reloading {}.'.format(name))
            self.bot.reload_plugin(instance.__class__)
            self.log.info('Reloaded {}.'.format(name))
            reloaded_plugins.append(name)

        reloaded_plugins = '\n'.join(reloaded_plugins)
        event.msg.reply('Plugins reloaded:\n```{}```'.format(reloaded_plugins))
