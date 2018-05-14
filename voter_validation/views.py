import logging

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods

from voter_validation.models import Campaign

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
    :param campaign_id: the campaign this UserProfile is validating for.
    """
    campaign = get_object_or_404(Campaign, campaign_id=int(campaign_id))

    query = request.GET.get("q", None)
    return render(request, "voter_validation/validation.html",
                  {"campaign_name": campaign.name,
                   "results": None})


