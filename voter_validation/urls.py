"""
URLs for the voter_validation app. Currently, these URLs are rooted at the root
directory of the website (see backend/urls.py).
"""
from django.conf.urls import url

from voter_validation import views, apis_private

app_name = 'voter_validation'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^logout/$', views.logout, name='logout'),

    # Validation links
    url(r'^api/private/validate_voter/$',
        apis_private.validation_api, name='validate_voter'),
    url(r'^validate/(?P<campaign_id>[\w]+)/$', views.validate, name='validate'),
]
