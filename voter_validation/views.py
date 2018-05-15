import logging

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods

from voter_validation.models import Campaign
from voter_validation.search import voter_search

logger = logging.getLogger(__name__)


def index(request):
    """
    The index view, for the home page.
    :param request:
    """
    context = dict()
    return render(request, 'voter_validation/index.html', context)


def logout(request):
    """
    The logout view. Redirects to home page after.
    :param request:
    """
    if request.user.is_authenticated():
        auth_logout(request)
    return HttpResponseRedirect(reverse("voter_validation:index"))


@login_required(login_url='/')
@require_http_methods(["GET", "POST"])
def validate(request, campaign_id):
    """
    Shows validation UI for a given campaign, if this UserProfile is authorized
    to do data entry for the specified Campaign.

    This is also the endpoint for searching for Voters as part of validation. If
    doing a search, assume that a sufficient number of the specified fields is
    present (taken care of in front-end form validation).

    :param campaign_id: the campaign this UserProfile is validating for.
    :param request: may contain the following parameters for searching:
    - "search": true if doing a search
    - "name": full name of voter
    - "address": street (residential) address of voter
    - "zip": ZIP code
    """
    if not request.user.userprofile.in_campaign(campaign_id):
        return HttpResponseRedirect(reverse("voter_validation:index"))

    campaign_id = int(campaign_id)
    campaign = get_object_or_404(Campaign, id=campaign_id)
    context = {"campaign_name": campaign.name, "campaign_id": campaign_id}

    # Search if specified in POST
    search = request.POST.get("search", "false")
    if search.lower() == "true":
        name = request.POST.get("name", None)
        address = request.POST.get("address", None)
        res_zip = request.POST.get("zip", None)
        # Pass in campaign_id so we can check the Voter was previously validated
        voters = voter_search(name, address, res_zip, campaign_id=campaign_id)
        context.update({
            "name": name,
            "address": address,
            "zip": res_zip,
            "results": voters,
        })

    return render(request, "voter_validation/validation.html", context)


