import abc

from voter_validation.models import RegStatus


class Serializer(object):
    """
    Base serializer to allow a central point of entry and data interface.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def serialize(self, debug=False):
        """
        Should return a dict of data represented by this serializer.
        :param debug: if True, include additional info in each object
        """
        raise NotImplemented()


class VoterSerializer(Serializer):
    """
    Used to create a serialized dict of a voter. The details here will be
    visible to logged-in users.
    """
    def __init__(self, voter, *args, **kwargs):
        super(VoterSerializer, self).__init__(*args, **kwargs)
        self.voter = voter

    def serialize(self, debug=False, campaign_id=None):
        # If campaign_id is specified, check if the ValidationRecord set for
        # this Voter contains that ID, to see if they're validated.
        is_validated = False
        if campaign_id:
            is_validated = self.voter.validationrecord_set.filter(
                campaign_pk=campaign_id).count() != 0 \
                and self.voter.reg_status == RegStatus.ACTIVE.value
        return {
            'id': self.voter.voter_id,
            'name': self.voter.get_full_name(),
            'res_addr': self.voter.res_addr,
            'gender': self.voter.gender,
            'party': self.voter.party,
            'language': self.voter.language,
            'curr_reg_date': self.voter.curr_reg_date,
            'orig_reg_date': self.voter.orig_reg_date,
            'reg_status': self.voter.reg_status,
            'reg_status_reason': self.voter.reg_status_reason,
            'is_validated': is_validated,
            'type': 'Voter',
        }
