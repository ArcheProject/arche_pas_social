from BTrees.OOBTree import OOBTree
from arche.interfaces import IObjectWillBeRemovedEvent
from arche.interfaces import IRoot
from arche.interfaces import IUser
from pyramid.traversal import find_root
from zope.component import adapter
from zope.interface import implementer

from arche_pas_social.interfaces import ISocialAuth
from arche_pas_social.interfaces import IProviderMapper
from persistent.list import PersistentList


@implementer(IProviderMapper)
@adapter(IRoot)
class ProviderMapper(object):

    def __init__(self, context):
        self.context = context

    @property
    def service_identifier_to_userid(self):
        try:
            si_userid = self.context._service_identifier_to_userid
        except AttributeError:
            si_userid = self.context._service_identifier_to_userid = OOBTree()
        return si_userid

    @property
    def userid_to_services(self):
        try:
            userid_si = self.context._userid_to_services
        except AttributeError:
            userid_si = self.context._userid_to_services = OOBTree()
        return userid_si

    def add(self, userid, service_name, identifier):
        if userid not in self.userid_to_services:
            self.userid_to_services[userid] = PersistentList()
        if (service_name, identifier) not in self.userid_to_services[userid]:
            self.userid_to_services[userid].append((service_name, identifier))
        self.service_identifier_to_userid[(service_name, identifier)] = userid

    def remove(self, userid, service_name, identifier = None):
        if identifier is None:
            identifier = self.find_identifier_for(userid, service_name)
        try:
            self.userid_to_services[userid].remove((service_name, identifier))
        except (KeyError, ValueError):
            pass
        try:
            del self.service_identifier_to_userid[(service_name, identifier)]
        except KeyError:
            pass

    def find_identifier_for(self, userid, service_name):
        for (name, identifier) in self.get_services(userid, ()):
            if name == service_name:
                return identifier

    def get_userid(self, service_name, identifier, default = None):
        return self.service_identifier_to_userid.get((service_name, identifier), default)

    def get_services(self, userid, default = None):
        return self.userid_to_services.get(userid, default)

    def remove_userid(self, userid):
        for name_id in self.userid_to_services.get(userid, ()):
            del self.service_identifier_to_userid[name_id]
        del self.userid_to_services[userid]


@implementer(ISocialAuth)
@adapter(IRoot)
class SocialAuth(object):
    name = "None"
    title = ""

    def __init__(self, context):
        self.context = context

    def login(self, identifier):
        mapper = IProviderMapper(self.context)
        userid = mapper.get_userid(self.name, identifier)
        if userid:
            return userid

    def get_identifier(self, data): #pragma : no coverage
        raise NotImplementedError()

    def get_data(self, request): #pragma : no coverage
        raise NotImplementedError()

    def get_appstruct(self, data): #pragma : no coverage
        raise NotImplementedError()
        

def remove_user_when_deleted(obj, event):
    root = find_root(obj)
    provider_mapper = IProviderMapper(root)
    provider_mapper.remove_userid(obj.userid)

def includeme(config):
    config.add_subscriber(remove_user_when_deleted, [IUser, IObjectWillBeRemovedEvent])
    config.registry.registerAdapter(ProviderMapper)
