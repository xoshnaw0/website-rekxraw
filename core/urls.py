from django.urls import path
from . import views as v
urlpatterns = [path("", v.page("index")), path("about/", v.page("about")), path("programs/", v.page("programs")),
    path("impact/", v.page("impact")), path("contact/", v.contact), path("contact/send/", v.contact_send), path("join/send/", v.join_send),
    path("activities.js", v.activities_js, name="activities_js")]
