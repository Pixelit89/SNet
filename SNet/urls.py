"""SNet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from chat import views
from channels.routing import ProtocolTypeRouter

application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
})


urlpatterns = [
    re_path(r'^id_(?P<pk>[0-9])$', views.IndexView.as_view(), name='index'),
    re_path(r'^login$', views.LoginView.as_view(), name='login'),
    re_path(r'^logging_in$', views.logging_in, name='logging_in'),
    re_path(r'^logging_out$', views.logging_out, name='logging_out'),
    re_path(r'^registration$', views.RegistrationView.as_view(), name='registration'),
    re_path(r'^register$', views.registration, name='register'),
    re_path(r'^edit_profile_(?P<pk>[0-9])$', views.EditProfileView.as_view(), name='edit_profile'),
    re_path(r'^update_profile', views.update_profile, name='update_profile'),
    re_path(r'^add_friend_(?P<current_page_id>[0-9])', views.add_friend, name='add_friend'),
    re_path(r'^remove_friend_(?P<current_page_id>[0-9])', views.remove_friend, name='remove_friend'),
    re_path(r'^id_(?P<pk>[0-9])/friends$', views.FriendsView.as_view(), name='friends'),
    re_path(r'^chat$', views.index, name="messages"),
    re_path(r'^chat/(?P<room_name>[^/]+)$', views.room, name='room'),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
