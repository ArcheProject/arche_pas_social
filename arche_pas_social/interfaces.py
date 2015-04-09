from zope.interface import Attribute
from zope.interface import Interface
from pyramid.interfaces import IDict
from arche.interfaces import IContextAdapter

class IProviderData(IDict, IContextAdapter):
    """ Adapts an IUser object and stores information from authentication
        providers.
    """


class IProviderMapper(IContextAdapter):
    pass


class ISocialAuth(Interface):
    name = Attribute("Name of the provider.")
    title = Attribute("Translation string, ment for users.")

    def login(identifier):
        """ Return the userid that should be logged in, if the identifier
            is associated with anything.
        """

    def get_identifier(data):
        """ Fetch what we should use as identifier from some data that this provider uses.
        """

    def get_data(request):
        """ Return some kind of valid data that both the method get_appstruct and get_identifier will use.
        """

    def get_appstruct(data):
        """ Get something that the registration schema can use as an appstruct from
            a providers data. Usually just translating one dicts keys to anothers'.
        """
