from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/chat/listener/$', consumers.ListenerConsumer),
    url(r'^ws/chat/(?P<group>[^/]+)/$', consumers.ChatConsumer),
]
