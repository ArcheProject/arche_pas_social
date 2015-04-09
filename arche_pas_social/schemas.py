import colander
import deform
from pyramid.httpexceptions import HTTPForbidden
from pyramid.traversal import find_root

from arche_pas_social import _
from arche_pas_social.interfaces import IProviderMapper


class ConfirmTrueValidator(object):
    def __call__(self, node, value):
        if value != True:
            raise colander.Invalid(node, _("You must confirm to use this."))


@colander.deferred
def confirm_pas_attach_title(node, kw):
    view = kw['view']
    request = kw['request']
    msg = _("confirm_attach_pas_title",
            default = "You're logged in as '${userid}' - do you wish to be able to login with your current account using ${title}?",
            mapping = {'userid': request.authenticated_userid, 'title': request.localizer.translate(view.method.title)})
    return msg
    

class AttachPASProviderSchema(colander.Schema):
    confirm_pas_attach = colander.SchemaNode(colander.Bool(),
                                             validator = ConfirmTrueValidator(),
                                             title = confirm_pas_attach_title,)


class ExactValidatorForHidden(object):

    def __init__(self, should_be, msg = ""):
        self.should_be = should_be
        self.msg = msg

    def __call__(self, node, value):
        if not self.should_be or self.should_be != value:
            raise HTTPForbidden(self.msg)


@colander.deferred
def currently_attached_widget(node, kw):
    request = kw['request']
    context = kw['context']
    request.authenticated_userid
    root = find_root(context)
    mapper = IProviderMapper(root)
    values = []
    services = mapper.get_services(request.authenticated_userid)
    if services:
        for (provider, identifier) in services:
            values.append((provider, provider))    
    return deform.widget.CheckboxChoiceWidget(values = values)

class RemovePASProvidersSchema(colander.Schema):
    currently_attached = colander.SchemaNode(colander.Set(),
                                             title = _("Currently active"),
                                             description = _("remove_pas_description",
                                                             default = "Check any you wish to remove from your account. "
                                                             "You won't be able to login with them again."),
                                             widget = currently_attached_widget)
