#pylint:disable=E1101
from disco.bot import Plugin
from disco.bot.command import CommandLevels
from disco.types.user import Game, GameType, Status


class CorePlugin(Plugin):
    @Plugin.listen('Ready')
    def on_ready(self, ctx):
        self.client.update_presence(Status.online, Game(type=GameType.listening, name='nothing because I don\'t work yet'))

    @Plugin.command('reload')
    def reload_command(self, event):
        user_level = self.bot.get_level(event.author)
        if user_level < CommandLevels.OWNER:
            event.msg.reply('**Only admins can do that**')
            return

        self.log.info('Reloading Plugins')
        reloaded_plugins = []
        for name, value in self.bot.plugins.copy().items():
            if 'Core' in name:
                continue

            self.log.info('reloading {}'.format(name))
            self.bot.reload_plugin(value.__class__)
            self.log.info('reloaded {}'.format(name))
            reloaded_plugins.append(name)

        event.msg.reply('Plugins reloaded:\n{}'.format('\n'.join(reloaded_plugins)))
