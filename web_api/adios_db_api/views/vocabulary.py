import logging

from cornice import Service
from pyramid.httpexceptions import HTTPNotFound

from adios_db.models.common.vocabulary import compounds, industry_properties
from adios_db_api.common.views import cors_policy


vocabulary_api = Service(name='vocabulary', path='/vocabulary/*category',
                         description=('Manage the vocabulary for compounds '
                                      'and industry properties.'),
                         cors_policy=cors_policy)

logger = logging.getLogger(__name__)

categories = {
    'compounds': compounds,
    'industry_properties': industry_properties
}


@vocabulary_api.get()
def get_vocabulary_words(request):
    """
    List the vocabulary words that match the incoming word fragment.
    """
    category = request.matchdict.get('category')
    if isinstance(category, tuple) and len(category) > 0:
        category = category[0]
    else:
        category = None

    logger.info(f'Our vocabulary category: "{category}"')

    if category in categories:
        word_fragment = request.GET.get('wf', '')

        return sorted(
            [w for w in categories[category]
             if word_fragment.lower() in w.lower()],
            key=lambda w: w.lower()
        )
    else:
        raise HTTPNotFound()
