# -*- coding: utf-8 -*-
# Copyright 2012 Mandla Web Studio
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__author__ = 'Jose Maria Zambrana Arze'
__email__ = 'contact@josezambrana.com'
__version__ = '0.1'
__copyright__ = 'Copyright 2012, Mandla Web Studio'


import logging
import traceback

from django import template
from django.http import Http404
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as login_view
from django.contrib.auth.views import logout as logout_view

from django.contrib.auth.models import User

from django.contrib.auth.views import password_reset as django_reset
from django.contrib.auth.views import password_reset_done as django_reset_done
from django.contrib.auth.views import password_reset_confirm as django_reset_confirm
from django.contrib.auth.views import password_reset_complete as django_reset_complete

from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from django.views.generic.list import ListView

from common.views import UpdateView
from common.views import LoginRequiredMixin
from common.views import ListView
from common.views import DetailView
from common.views import OwnerRequiredMixin

from users.forms import PasswordResetForm
from users.forms import RegisterForm
from users.forms import UserForm
from users.forms import ProfileForm
from users.forms import DesignForm

from users.utils import get_dict_by_ids
from users.models import Profile


current_site = Site.objects.get_current()


def register(request, **kwargs):
    if request.user.is_authenticated():
        messages.error(request, 'Ya estas registrado')
        logging.error('Ya estas registrado: %s ' % request.user.username)
        return redirect(reverse('error'))
    
    form = RegisterForm()
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            messages.success(request, _("Bienvenido a %s" % current_site.name))

            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'])
            auth_login(request, user)

            return redirect(reverse('home'))
    
    context = {
        'form': form
    }

    c = template.RequestContext(request, context)
    return render_to_response('page.users.register.html', c)


# password reset
def password_reset(request):
    kwargs = {
        'template_name': 'page.password_reset.html',
        'post_reset_redirect': reverse('password_reset_done'),
        'password_reset_form': PasswordResetForm
    }
    return django_reset(request, **kwargs)


def password_reset_done(request):
    kwargs = {
        'template_name': 'page.password_reset.done.html'
    }
    return django_reset_done(request, **kwargs)


def password_reset_confirm(request, uidb36=None, token=None):
    kwargs = {
        'uidb36': uidb36, 
        'token': token,
        'template_name': 'page.password_reset.confirm.html',
        'post_reset_redirect': reverse('password_reset_complete')
    }
    return django_reset_confirm(request, **kwargs)


def password_reset_complete(request):
    kwargs = {
        'template_name': 'page.password_reset.complete.html'
    }
    return django_reset_complete(request, **kwargs)


class AttachActors(object):
    """
    Añade la lista de actores que intervienen en la vista al contexto
    """

    def get_actors_ids(self, context):
        """
        Retorna los ids de todos los actores que intervienen en esta vista.
        """

        raise NotImplementedError
        
    def get_context_data(self, **kwargs):
        """
        Retorna el contexto con el diccionario de usuarios y perfiles.
        """
        context = super(AttachActors, self).get_context_data(**kwargs)
        
        # Añadimos al contexto los perfiles de los actores en un diccionario.
        users_ids = self.get_actors_ids(context)
        context['users_dict'] = get_dict_by_ids(User, users_ids)
        context['profiles_dict'] = Profile.objects.profiles_dict(users_ids)
         
        return context


class UsersIndex(AttachActors, ListView):
    """
    Muestra los usuarios registrados en el sistema.
    """

    model = User
    view_name = 'users-index'
    app_name = 'users'
    
    templates = {
        'html': 'page.users.index.html'
    }

    def get_actors_ids(self, context):
        """
        Retorna los ids de los usuario de la vista.
        """
        
        return [user.id for user in context['object_list']]
        

class UsersUpdate(OwnerRequiredMixin, UpdateView):
    """
    Vista para actualizar los datos de la cuenta del usuario.
    """
    
    model = User
    form_class = UserForm
    
    view_name = 'users-account'
    app_name = 'users'
    templates = {
        'html': 'page.users.settings.html'
    }
    
    def get_object(self):
        return self.request.user

    def is_owner(self, user, current_user):
        return user.id == current_user.id

    def form_valid(self, form):
        user = form.save()
        
        self.success_message = _(u'Tu cuenta fue actualizada.')
        
        return super(UsersUpdate, self).form_valid(form)
    
    def get_success_redirect_url(self):
        return reverse('users_profile', args=[self.request.user.username])


class UsersUpdateProfile(OwnerRequiredMixin, UpdateView):
    """
    Vista para actualizar el perfil del usuario.
    """

    model = Profile
    form_class = ProfileForm
    
    view_name = 'users-personal'
    app_name = 'users'
    templates = {
        'html': 'page.users.settings.html'
    }
    
    def get_object(self):
        profile = self.request.user.get_profile()
        return profile
    
    def form_valid(self, form):
        profile = form.save()
        self.success_message = _(u'Tus datos fueron actualizados.')
        return super(UsersUpdateProfile, self).form_valid(form)
    
    def get_success_redirect_url(self):
        return reverse('users_profile', args=[self.request.user.username])


class UsersUpdateDesign(UsersUpdateProfile):
    """
    Vista para actualizar el diseño del perfil del usuario.
    """
    form_class = DesignForm

    view_name = 'users-design'
    
    def form_valid(self, form):
        """
        Procesa el formulario.
        """
        profile = form.save()
        self.success_message = _(u'El diseño fue actualizado correctamente')
        return super(UsersUpdateDesign, self).form_valid(form)


def profile(request, username=None):
    """
    Redirecciona la página de usuario con el subdominio: http://<username>.<domain>
    """
    
    if username is None:
        user = request.user
    else:
        user = get_object_or_404(User, username=username)
    
    user_url = 'http://%s.%s' % (user.username, current_site.domain)
    
    return redirect(user_url)


class UsersProfile(DetailView):
    """
    Muestra el perfil del usuario.
    """
    
    model = User
    
    view_name = 'users-profile'
    app_name = 'users'
    
    templates = {
        'html': 'page.users.profile.html'
    }

    def get_object(self):
        username = self.kwargs.get('username', self.request.user.username)
        return get_object_or_404(User, username=username)

    def get_context_data(self, **kwargs):
        context = super(UsersProfile, self).get_context_data(**kwargs)
        context['user_profile'] = context['object'].get_profile()
        return context


