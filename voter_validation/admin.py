from django.contrib import admin
from .models import Voter, Campaign, UserProfile, ValidationRecord

admin.site.register(Voter)
admin.site.register(Campaign)
admin.site.register(UserProfile)
admin.site.register(ValidationRecord)
