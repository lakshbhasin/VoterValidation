"""
Search-related functions and variables
"""
import re

from django.contrib.postgres.search import SearchVector, SearchRank, \
    SearchQuery, \
    TrigramSimilarity
from django.db.models import Q

from .models import UserProfile
from .serializers import VoterSerializer

# Fields used in computing trigram similarity
USER_TRIGRAM_SIM_FIELDS = ['user__username', 'user__first_name',
                           'user__last_name', 'description']
TEAM_TRIGRAM_SIM_FIELDS = ['name', 'description']

# Search vectors for user and team search. Used for ranking in non-typeahead
# search. Some features from trigram similarity are left off to save
# computation.
USER_SEARCH_VECTOR = SearchVector('user__username', weight='A') \
                     + SearchVector('description', weight='B')

TEAM_SEARCH_VECTOR = SearchVector('name', weight='A') \
                     + SearchVector('description', weight='B')

ALPHANUMERIC_REGEX = re.compile(r'\W+', re.UNICODE)


def normalize_query(query):
    """
    Make the query lower-case and remove non-alphanumeric characters.
    :param query:
    :return:
    """
    query = query.lower()
    query = ' '.join(ALPHANUMERIC_REGEX.split(query))
    return query


def construct_similarity_metric(fields, query):
    """
    Constructs a TrigramSimilarity metric with the given fields and query.
    This is used for "candidate generation" for search.
    :param fields: list of strings corresponding to model fields
    :param query: string search query
    :return: TrigramSimilarity
    """
    similarity = None
    for sim_field in fields:
        if similarity is None:
            similarity = TrigramSimilarity(sim_field, query)
        else:
            similarity += TrigramSimilarity(sim_field, query)
    return similarity


def user_search(query, is_typeahead, debug=False, normalize=True, limit=30):
    """
    Returns user search results for typeahead and non-typeahead queries.

    Typeahead just involves trigram similarity, so that "adm" matches a user
    called "admin" (for example). Typeahead results are ranked by trigram
    similarity.

    Non-typeahead search involves trigram similarity as well during
    filtering, so we can catch "typos". However, final ranking is by
    SearchRank, i.e. stemmed token match, with similarity only used for
    tie-breaking.
    :param query: string search query
    :param is_typeahead: if True, apply typeahead logic.
    :param debug: if True, additional info about the scoring is included
    with the serialized results.
    :param normalize: if True, normalize the query
    :param limit: if > 0, return the top "limit" results.
    :return: list of JSON-serialized UserProfiles
    """
    if normalize:
        query = normalize_query(query)

    # Return all profiles for null or empty query
    if query == '' or query is None:
        profiles = UserProfile.objects.all()
    else:
        similarity = construct_similarity_metric(USER_TRIGRAM_SIM_FIELDS, query)
        search_query = SearchQuery(query)
        corpus = UserProfile.objects.select_related('user')

        if is_typeahead:
            # Lower threshold for trigram similarity than in non-typeahead.
            profiles = corpus.annotate(search_similarity=similarity)\
                .filter(Q(search_similarity__gte=0.1))\
                .order_by('-search_similarity')
        else:
            profiles = corpus.annotate(
                    search_rank=SearchRank(USER_SEARCH_VECTOR, search_query),
                    search_similarity=similarity)\
                .filter(
                    Q(search_rank__gte=0.3) | Q(search_similarity__gte=0.15))\
                .order_by('-search_rank', '-search_similarity')

    if limit > 0:
        profiles = profiles[:limit]

    results = [VoterSerializer(p).serialize(debug) for p in profiles]
    return results


def generic_search(query, is_typeahead, debug=False, normalize=True,
                   limit=30):
    """
    Synchronously carries out team and user search, and then returns the
    results in a dict. This is apparently faster than using Celery and doing
    the searches asynchronously, or using multiprocessing.
    :return: dict of the form {"users": user_results, "teams": team_results}
    """
    if normalize:
        query = normalize_query(query)

    results = {
        # Normalization is already taken care of
        "users": user_search(query, is_typeahead, debug=debug, normalize=False,
                             limit=limit),
    }
    return results
