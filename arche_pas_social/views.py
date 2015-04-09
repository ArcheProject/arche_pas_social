from arche.interfaces import IRoot
from arche.security import NO_PERMISSION_REQUIRED
from arche.security import PERM_REGISTER
from arche.views.auth import RegisterForm
from arche.views.base import BaseView
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
from pyramid.security import remember
import colander
import deform
from pyramid.response import Response
from arche.views.base import BaseForm
from arche.views.base import DefaultEditForm
from arche.interfaces import IUser

from arche_pas_social import _
from arche_pas_social.interfaces import ISocialAuth
from arche_pas_social.interfaces import IProviderMapper
from arche_pas_social.schemas import ExactValidatorForHidden
from arche_pas_social.schemas import AttachPASProviderSchema
from arche_pas_social.schemas import RemovePASProvidersSchema


class HelperMixin(object):

    @reify
    def method(self):
        """ First subpath of current view - name of the provider. """
        try:
            method_name = self.request.subpath[0]
        except IndexError:
            raise HTTPForbidden("Invalid request")
        social_auth = self.request.registry.queryAdapter(self.context, ISocialAuth, name = method_name)
        if social_auth is None:
            raise HTTPForbidden("No method called %r" % method_name)
        return social_auth

    @reify
    def identifier(self):
        """ Second subpath of current view - the identifier when process has already started. """
        try:
            return self.request.subpath[1]
        except IndexError:
            raise HTTPForbidden("Authentication with service %r didn't work" % self.method.name)

    def add_pas_info_to_schema(self, schema):
        schema.add(colander.SchemaNode(colander.String(),
                                       name = "__pas_identifier__",
                                       validator = ExactValidatorForHidden(self.identifier),
                                       widget = deform.widget.HiddenWidget()))
        schema.add(colander.SchemaNode(colander.String(),
                                       name = "__pas_provider__",
                                       validator = ExactValidatorForHidden(self.method.name),
                                       widget = deform.widget.HiddenWidget()))


class HandlePASView(BaseView, HelperMixin):

    def __call__(self):
        #FIXME: Split this up and refactor. This structure is error-prone
        data = self.method.get_data(self.request)
        identifier = self.method.get_identifier(data)
        root_url = self.request.resource_url(self.context)
        if identifier:
            print "identifier: ", identifier
            userid = self.method.login(identifier)
            if userid:
                print "userid: ", userid
                if not self.request.authenticated_userid:
                    print "Will login user and redirect"
                    headers = remember(self.request, userid)
                    return self.relocate_response(root_url, headers = headers)
                else:
                    print "Already logged in, user exists, nothing to do right?"
                    return Response()
            else:
                if not self.request.authenticated_userid:
                    #Register
                    url = self.request.resource_url(self.context, '__pas_registration__', self.method.name, identifier)
                    self.request.session[identifier] = data
                    return self.relocate_response(url)
                else:
                    #Attach profile
                    url = self.request.resource_url(self.context, '__attach_pas_provider__', self.method.name, identifier)
                    return self.relocate_response(url)
        if self.request.is_xhr:
            return Response()
        return self.relocate_response(root_url)


class HandlePASRegistrationForm(RegisterForm, HelperMixin):

    def appstruct(self):
        appstruct = {'__pas_identifier__': self.identifier,
                     '__pas_provider__': self.method.name}
        appstruct.update(self.method.get_appstruct(self.request.session.get(self.identifier, {})))
        return appstruct

    def get_schema(self):
        """ Fetch a combined schema if email validation should be skipped.
        """
        schema = self.get_schema_factory(self.type_name, 'register_skip_validation')
        schema = schema()
        self.add_pas_info_to_schema(schema)
        if 'password' in schema:
            del schema['password']
        return schema

    def register_success(self, appstruct):
        self.flash_messages.add(_("Welcome, you're now registered!"), type="success")
        factory = self.get_content_factory('User')
        userid = appstruct.pop('userid')
        #FIXME: What decide if email is validated or not here? Google has a setting for validated email for instance
        #if not self.root.skip_email_validation:
        #    appstruct['email_validated'] = True
        appstruct.pop('__pas_identifier__', None)
        appstruct.pop('__pas_provider__', None)
        mapper = IProviderMapper(self.context)
        mapper.add(userid, self.method.name, self.identifier)
        obj = factory(**appstruct)
        self.context['users'][userid] = obj
        headers = remember(self.request, obj.userid)
        return self.relocate_response(self.request.resource_url(self.root), headers = headers)


class AttachPASProviderForm(BaseForm, HelperMixin):
    

    def __call__(self):
        if not self.request.authenticated_userid:
            raise HTTPForbidden("Login to use this")
        return super(AttachPASProviderForm, self).__call__()

    def appstruct(self):
        return {'__pas_identifier__': self.identifier,
                '__pas_provider__': self.method.name}

    def get_schema(self):
        schema = AttachPASProviderSchema()
        self.add_pas_info_to_schema(schema)
        return schema

    def save_success(self, appstruct):
        self.flash_messages.add(self.default_success, type="success")
        mapper = IProviderMapper(self.context)
        mapper.add(self.request.authenticated_userid, self.method.name, self.identifier)
        msg = _("attachment_notice",
                default = "From now on you may login with ${method_name}.",
                mapping = {'method_name': self.request.localizer.translate(self.method.title)})
        self.flash_messages.add(msg)
        return self.relocate_response(self.request.resource_url(self.context))


class RemovePASProvidersForm(BaseForm):

    title = _("Remove providers?")

    @property
    def buttons(self):
        return (self.button_delete, self.button_cancel)

    def get_schema(self):
        return RemovePASProvidersSchema()

    def delete_success(self, appstruct):
        print appstruct
        return self.relocate_response(self.request.resource_url(self.context))


def includeme(config):
    config.add_view(HandlePASView,
                    context = IRoot,
                    name = "__pas_auth__",
                    permission = NO_PERMISSION_REQUIRED)
    config.add_view(HandlePASRegistrationForm,
                    context = IRoot,
                    name = "__pas_registration__",
                    renderer = "arche:templates/form.pt",
                    permission = PERM_REGISTER)
    config.add_view(AttachPASProviderForm,
                    context = IRoot,
                    name = "__attach_pas_provider__",
                    renderer = "arche:templates/form.pt",
                    permission = NO_PERMISSION_REQUIRED)
    config.add_view(RemovePASProvidersForm,
                    context = IUser,
                    name = "__remove_pas_provider__",
                    renderer = "arche:templates/form.pt",
                    permission = NO_PERMISSION_REQUIRED)
