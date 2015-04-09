from logging import getLogger

from pyramid.i18n import TranslationStringFactory


logger = getLogger(__name__)
_ = TranslationStringFactory('arche_pas_social')


def includeme(config):
    try:
        config.include('.portlet')
    except (ImportError, AttributeError):
        logger.warn("Can't enable portlet - Arche is probably not installed or included.")
    config.include('.views')
    config.include('.models')
