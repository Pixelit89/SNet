from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.views.generic import DetailView, FormView, TemplateView
from .forms import LoginForm, RegistrationForm, EditForm
from .models import ExtendedUser
import json
# Create your views here.


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


class IndexView(LoginRequiredMixin, DetailView):
    template_name = "index.html"
    model = ExtendedUser
    login_url = '/login'
    redirect_field_name = ''

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['current_page_id'] = self.kwargs['pk']
        friend = ExtendedUser.objects.get(id=int(self.kwargs['pk']))
        user = ExtendedUser.objects.get(id=self.request.session['id'])
        context['avatar'] = friend.avatar
        context['friends'] = friend.friends.all()
        try:
            context['is_friend'] = user.friends.get(id=friend.id)
        except ExtendedUser.DoesNotExist:
            context['is_friend'] = None
        return context


class LoginView(FormView):
    template_name = "login.html"
    form_class = LoginForm


class RegistrationView(FormView):
    template_name = "registration.html"
    form_class = RegistrationForm


class EditProfileView(LoginRequiredMixin, FormView):
    login_url = "/login"
    redirect_field_name = ''
    template_name = 'edit_profile.html'
    form_class = EditForm


def update_profile(request):
    user = ExtendedUser.objects.get(id=request.session['id'])
    user.avatar = request.FILES['avatar']
    user.save()
    return HttpResponseRedirect(reverse_lazy('index', kwargs={'current_page_id': request.session['id']}))


def add_friend(request, current_page_id):
    user = ExtendedUser.objects.get(id=request.session['id'])
    print(current_page_id)
    friend = ExtendedUser.objects.get(id=int(current_page_id))
    user.friends.add(friend)
    return HttpResponseRedirect(reverse_lazy('index', kwargs={'pk': current_page_id}))


def remove_friend(request, current_page_id):
    user = ExtendedUser.objects.get(id=request.session['id'])
    print(current_page_id)
    friend = ExtendedUser.objects.get(id=current_page_id)
    user.friends.remove(friend)
    return HttpResponseRedirect(reverse_lazy('index', kwargs={'pk': current_page_id}))


class FriendsView(LoginRequiredMixin, TemplateView):
    login_url = "/login"
    redirect_field_name = ''
    template_name = 'friends_list.html'

    def get_context_data(self, **kwargs):
        context = super(FriendsView, self).get_context_data(**kwargs)
        user = ExtendedUser.objects.get(id=self.request.session['id'])
        context['friends'] = user.friends.all()
        print(context)
        return context


def index(request):
    return render(request, 'chat/index.html', {})


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })
