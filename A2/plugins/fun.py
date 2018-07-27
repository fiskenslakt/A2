from disco.bot import Plugin


class FunPlugin(Plugin): 
    @Plugin.command('echo', '<message:str...>') 
    def echo_command(self, event, message):
        """= echo =
        Echoes a user's message
        usage    :: $echo <message>
        aliases  :: None
        category :: Fun
        """
        self.log.info('{} echoed "{}"'.format(event.author, message))
        event.msg.delete()
        event.msg.reply(message)
