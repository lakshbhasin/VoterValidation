"""
Search-related functions and variables
"""
import re

from django.contrib.postgres.search import SearchVector, SearchRank, \
    SearchQuery, TrigramSimilarity
from django.db.models import Q, F

from .models import UserProfile, Voter, RegStatus
from .serializers import VoterSerializer

ALPHANUMERIC_REGEX = re.compile(r'\W+', re.UNICODE)

# Fields used in computing trigram similarity for Voter searches (fuzzy search)
FULL_NAME_TRIGRAM_SIM_FIELDS = ['full_name']  # is a combination of all names
RES_ADDR_TRIGRAM_SIM_FIELDS = ['res_addr']
FULL_NAME_WEIGHT = 2
RES_ADDR_WEIGHT = 1


def normalize_query(query):
    """
    Make the query lower-case and remove non-alphanumeric characters.
    """
    if query is None:
        return query
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


def voter_search(name, address, res_zip, campaign_id=None,
                 debug=False, normalize=True, limit=30):
    """
    Searches for the given Voter and returns a list of matching Active results.
    :param name: string full name of Voter
    :param address: string full residential address of Voter (or part thereof)
    :param res_zip: string ZIP of Voter
    :param campaign_id: if set, this is used to determine if a Voter has already
    been validated.
    :param debug: if True, add debug information to JSON about search.
    :param normalize: if True, normalize the query parameters
    :param limit: if > 0, return the top "limit" results.
    :return: list of JSON-serialized Voters ranked in order
    """
    if normalize:
        name = normalize_query(name)
        address = normalize_query(address)
        res_zip = normalize_query(res_zip)

    # Filter by ZIP exactly, if present
    corpus = Voter.objects
    if res_zip is not None:
        corpus = corpus.filter(res_addr_zip=res_zip)

    # Ignore non-Active registration status
    corpus = corpus.filter(reg_status=RegStatus.ACTIVE.value)

    # Use full name and address for trigram similarity computation.
    addr_similarity = construct_similarity_metric(
        RES_ADDR_TRIGRAM_SIM_FIELDS, address)
    name_similarity = construct_similarity_metric(
        FULL_NAME_TRIGRAM_SIM_FIELDS, name)

    # Use weighted sum of trigram similarity for match.
    voters = corpus.annotate(
            name_similarity=name_similarity,
            addr_similarity=addr_similarity)\
        .filter(Q(name_similarity__gte=0.005) & Q(addr_similarity__gte=0.005))\
        .annotate(search_score=FULL_NAME_WEIGHT * F('name_similarity')
                  + RES_ADDR_WEIGHT * F('addr_similarity'))\
        .order_by('-search_score')

    if limit > 0:
        voters = voters[:limit]

    voters = voters.prefetch_related('validationrecord_set')
    results = [VoterSerializer(v).serialize(
        debug=debug, campaign_id=campaign_id) for v in voters]
    return results
