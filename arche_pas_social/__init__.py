from logging import getLogger

from pyramid.i18n import TranslationStringFactory


logger = getLogger(__name__)
_ = TranslationStringFactory('arche_pas_social')


def includeme(config):
    pass
