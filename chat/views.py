from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.views.generic import DetailView, FormView, TemplateView, ListView, RedirectView, UpdateView
from django.core.exceptions import ObjectDoesNotExist
from .forms import LoginForm, RegistrationForm, EditForm, UploadPicForm
from .models import ExtendedUser, ChatGroups, Gallery, FriendsRequest, Wall, ChatMessages

import json
# Create your views here.


class IndexView(LoginRequiredMixin, DetailView):
    template_name = "index.html"
    model = ExtendedUser
    login_url = '/login'
    redirect_field_name = ''

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        current_page_user = ExtendedUser.objects.get(id=int(self.kwargs['pk']))
        user = ExtendedUser.objects.get(id=self.request.session['id'])
        friends_requests = FriendsRequest.objects.filter(user_id=self.request.session['id'])
        gallery = Gallery.objects.filter(user_id=current_page_user.id)
        wall = Wall.objects.filter(wall_owner=current_page_user.id)
        context['user'] = user
        context['current_page_user'] = current_page_user
        context['groups'] = user.chatgroups_set.all()
        context['friends_requests'] = friends_requests
        context['friends_requests_users'] = []
        context['friends'] = context['current_page_user'].friends.all()
        context['gallery'] = gallery
        context['wall'] = wall.order_by('-pub_date')
        for i in friends_requests:
            context['friends_requests_users'].append(ExtendedUser.objects.get(id=i.friend_request))
        try:
            context['is_friend'] = user.friends.get(id=current_page_user.id)
        except ExtendedUser.DoesNotExist:
            context['is_friend'] = None
        return context


class EditProfileView(IndexView, FormView):
    template_name = 'edit_profile.html'
    form_class = EditForm


class FriendsView(IndexView):
    template_name = 'friends_list.html'


class GalleryView(IndexView):
    template_name = 'gallery.html'

    def get_context_data(self, **kwargs):
        context = super(GalleryView, self).get_context_data(**kwargs)
        context['form'] = UploadPicForm
        return context


class ConversationsList(IndexView):
    template_name = 'chat/messages.html'


class LoginView(FormView):
    template_name = "login.html"
    form_class = LoginForm


class RegistrationView(FormView):
    template_name = "registration.html"
    form_class = RegistrationForm


class Redirect(RedirectView):
    url = 'login'


def logging_in(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        request.session['id'] = user.id
        login(request, user)
        return HttpResponseRedirect(reverse_lazy('index', args=(user.id,)))
    else:
        return HttpResponseRedirect(reverse_lazy('login'))


def logging_out(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('login'))


def registration(request):
    if request.POST['password'] == request.POST['confirm_password']:
        new_user = ExtendedUser(
            username=request.POST['username'],
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
        )
        new_user.set_password(request.POST['password'])
        new_user.save()
        request.session['id'] = new_user.id
        return HttpResponseRedirect(reverse_lazy('index', args=(new_user.id,)))
    else:
        return HttpResponseRedirect(reverse_lazy('registration'))


def update_profile(request, pk):
    user = ExtendedUser.objects.get(id=request.session['id'])
    if not request.POST['username'] == '':
        user.username = request.POST['username']
    if not request.POST['first_name'] == '':
        user.first_name = request.POST['first_name']
    if not request.POST['last_name'] == '':
        user.last_name = request.POST['last_name']
    if not request.POST['email'] == '':
        user.email = request.POST['email']
    if not request.FILES['avatar'] == '':
        user.avatar = request.FILES['avatar']
    if not request.POST['password'] == '':
        if request.POST['password'] == request.POST['confirm_password']:
            user.set_password(request.POST['password'])
        else:
            return HttpResponseRedirect(reverse_lazy('edit_profile', args=(pk,)))
    user.save()
    return HttpResponseRedirect(reverse_lazy('edit_profile', args=(pk, )))


def friends_request(request, current_page_id):
    user = ExtendedUser.objects.get(id=request.session['id'])
    current_page_user = ExtendedUser.objects.get(id=current_page_id)

    try:
        FriendsRequest.objects.get(user_id=int(current_page_id),
                                                        friend_request=request.session['id'])
        return HttpResponseRedirect(reverse_lazy('index', kwargs={'pk': current_page_id}))
    except ObjectDoesNotExist:
        if current_page_user in user.friends.all():
            return HttpResponseRedirect(reverse_lazy('index', kwargs={'pk': current_page_id}))
        else:
            friends_request = FriendsRequest.objects.create(user_id=int(current_page_id),
                                                            friend_request=request.session['id'])
            friends_request.save()
            return HttpResponseRedirect(reverse_lazy('index', kwargs={'pk': current_page_id}))


def accept_friend(request, friend_request_id):
    friends_request = FriendsRequest.objects.get(friend_request=friend_request_id, user_id=request.session['id'])
    user = ExtendedUser.objects.get(id=request.session['id'])
    friend = ExtendedUser.objects.get(id=friend_request_id)
    user.friends.add(friend)
    friends_request.delete()
    return HttpResponseRedirect(reverse_lazy('friends', kwargs={'pk': user.id}))


def remove_friend(request, current_page_id):
    user = ExtendedUser.objects.get(id=request.session['id'])
    friend = ExtendedUser.objects.get(id=current_page_id)
    user.friends.remove(friend)
    return HttpResponseRedirect(reverse_lazy('index', kwargs={'pk': current_page_id}))


def upload_pic(request):
    user = ExtendedUser.objects.get(id=request.session['id'])
    gallery = Gallery.objects.create(pic=request.FILES['pic'], user_id=request.session['id'])
    gallery.save()
    return HttpResponseRedirect(reverse_lazy('gallery', kwargs={'pk': user.id}))


class RoomView(IndexView):
    template_name = 'chat/room.html'

    def get_context_data(self, **kwargs):
        context = super(RoomView, self).get_context_data(**kwargs)
        group = ChatGroups.objects.get(name=self.kwargs['group'])
        history = ChatMessages.objects.filter(chat_room=group).order_by('-pub_date')[:10]
        convers = group.users.exclude(id=context['user'].id)
        if len(convers) == 1:
            context['convers'] = convers[0]
        context['history'] = history
        context['group_json'] = mark_safe(json.dumps(group.name))
        return context


def room(request, group):
    request.encoding = 'utf-8'
    user = ExtendedUser.objects.get(id=request.session['id'])
    return render(request, 'chat/room.html', {
        'group_json': mark_safe(json.dumps(group)),
        'user': user,
        'current_page_user': user
    })


def add_wall_message(request, pk):
    new_message = Wall.objects.create(
        wall_owner=pk,
        message=request.POST['message'],
        author=ExtendedUser.objects.get(id=request.session['id'])
        )
    new_message.save()
    return HttpResponseRedirect(reverse_lazy('index', args=(pk, )))
