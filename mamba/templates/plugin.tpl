from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet

from mamba.utils import config
from ${application} import MambaApplicationFactory

settings = config.Application('config/${file}')


class Options(usage.Options):
    optParameters = [
        ['port', 'p', settings.port, 'The port number to listen on']
    ]


class MambaServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = settings.name
    description = settings.description
    options = Options

    def makeService(self, options):
        """Construct a TCPServer from a factory defined in ${application}
        """
        factory, application = MambaApplicationFactory(settings)
        httpserver = internet.TCPServer(int(options['port']), factory)
        httpserver.setName('{} Application'.format(settings.name))
        httpserver.setServiceParent(application)

        return httpserver


# Now construct an object which *provides* the relevant interfaces
# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker

mamba_service_maker = MambaServiceMaker()
