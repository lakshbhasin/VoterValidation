"""
URLs for the voter_validation app. Currently, these URLs are rooted at the root
directory of the website (see backend/urls.py).
"""
from django.conf.urls import url

from voter_validation import views

app_name = 'voter_validation'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^logout/$', views.logout, name='logout'),

    # Private APIs
    url(r'^validate/(?P<campaign_id>[\w]+)/$', views.validate, name='validate'),
]
