from pyramid.renderers import render

from arche.portlets import PortletType
from betahaus.viewcomponent import render_view_group

from arche_pas_social import _
from zope.interface.interfaces import ComponentLookupError
from arche_pas_social import logger


class PASPortlet(PortletType):
    name = u"pas_social_portlet"
    title = _(u"Social auth")

    def render(self, context, request, view, **kwargs):
        try:
            contents = render_view_group(request.root, request, 'arche_pas_social', as_type = 'generator')
        except ComponentLookupError:
            logger.warn("Can't render PASPortlet - arche_pas_social is empty.")
            return
        return render("arche_pas_social:templates/portlet.pt",
                      {'title': self.title,
                       'portlet': self.portlet,
                       'contents': contents},
                      request = request)


def includeme(config):
    config.add_portlet(PASPortlet)
