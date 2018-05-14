"""
backend URL Configuration
See the voter_validation folder for more details.
"""
import backend.settings as settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^private/admin/', include(admin.site.urls)),
    url(r'^', include('voter_validation.urls')),

    url(r'^favicon.ico$', RedirectView.as_view(
            url=settings.STATIC_URL + "favicon.ico",
            permanent=False),
        name="favicon"),

    # Keep robots away from herokuapp website.
    url(r'^robots\.txt', include('hide_herokuapp.urls')),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
