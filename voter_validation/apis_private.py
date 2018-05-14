"""
Private APIs (as linked to by urls.py)
"""

from .common import create_json_response
from .search import generic_search


def search_generic(request):
    """
    Searches for voters and returns both ValidationRecords (if voter has already
    been validated)
    :param request: contains:
    - "name": full name of voter
    - "street_address": street (residential) address of voter
    - "zip": ZIP code
    :return: {"users": user_results, "teams": team_results}
    """
    if request.method != "GET":
        return
    query = request.GET.get("q", None)
    is_typeahead = request.GET.get("typeahead", "false").lower() == "true"
    return create_json_response(generic_search(query, is_typeahead))
