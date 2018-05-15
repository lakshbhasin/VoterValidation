"""
Private APIs (as linked to by urls.py)
"""
from django.views.decorators.csrf import csrf_exempt

from voter_validation.common import create_json_response, bad_request
from voter_validation.models import Campaign, Voter
from voter_validation.tasks import validate_voter


@csrf_exempt
def validation_api(request):
    """
    An API to validate/invaidate a Voter for a given Campaign. Only responds to
    POSTs. The request should contain the following parameters:
        * voter_id: the Voter to validate
        * campaign_id: the Campaign to validate
        * val: whether to validate ("true" or "false")

    All of the other context parameters are determined from cookies.
    """
    if request.method != 'POST':
        return bad_request("Invalid request: not POST.")

    if not request.user.is_authenticated():
        return bad_request("Invalid request: not authenticated.")

    voter_id = request.POST.get("voter_id")
    campaign_id = request.POST.get("campaign_id")
    if campaign_id is None or voter_id is None:
        return bad_request("Invalid request: required params not present.")

    if not request.user.userprofile.in_campaign(campaign_id):
        return bad_request(
            "Invalid request: user not authenticated for Campaign.")

    voter = Voter.objects.filter(voter_id=voter_id)
    if voter.count() == 0:
        return bad_request("Invalid request: invalid Voter ID specified.")
    voter = voter.get()

    # Asynchronously validate/invalidate voter.
    val = request.POST.get("val", "false").lower() == "true"
    campaign = Campaign.objects.get(pk=campaign_id)
    validate_voter.delay(voter=voter, campaign=campaign,
                         val=val, validator=request.user.userprofile)
    return create_json_response({
        "result": "success",
        "message": "Voter asynchronously saved",
    })
