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
import re

from django import forms
from django.core.exceptions import MultipleObjectsReturned
from django.forms.widgets import Widget
from django.forms.fields import Field
from django.conf import settings
from django.forms import ModelForm

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.localflavor.es import forms as es_forms
from django.contrib.auth.tokens import default_token_generator

from django.contrib.sites.models import Site, get_current_site

from django.utils.translation import ugettext_lazy as _
from django.utils.http import int_to_base36
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode

from common.mail import Mailer

from thumbnails.templatetags.thumbnails_tags import thumbnail_url
from thumbnails.forms import ThumbnailField
from thumbnails.utils import validate_file_size

from users.models import Profile


UPPER_RE = re.compile('[A-Z]+')
USERNAME_RE = re.compile(r'^[a-z0-9\-]+$')


current_site = Site.objects.get_current()


class MixinClean(object):
    """
    Clase para encapsular las validaciones relacionadas con los campos
    de un usuario.
    """

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise forms.ValidationError(_(u'El email es obligatorio'))

        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(u'El email debe ser único.')

        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if not first_name:
            raise forms.ValidationError(_(u'El Nombre es obligatorio'))

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if not last_name:
            raise forms.ValidationError(_(u'Los Apellidos son obligatorios.'))

        return last_name
    
    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class RegisterForm(UserCreationForm, MixinClean):
    """
    Formulario para registrar un usuario en el sistema
    """
    
    class Meta:
        model = UserCreationForm.Meta.model
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        UserCreationForm.__init__(self, *args, **kwargs)
        self.fields.keyOrder = ["first_name", "last_name", "username",
                                "password1", "password2", "email"]
        self.fields['first_name'].label = _('Nombre')
        self.fields['last_name'].label = _('Apellidos')
        self.fields['email'].label = _('Email')
        self.fields['username'].help_text = ""
        self.fields['password2'].help_text = ""
        self.fields['email'].label = _('Email')

    def clean_username(self):
        """
        Valida el nombre de usuario.
        """

        username = self.cleaned_data.get('username')

        if not USERNAME_RE.match(username):
            raise forms.ValidationError(_(u"Solo se permiten caracteres alfanuméricos y el caracter -"))

        return username.lower()

    def save(self, *args, **kwargs):
        """
        Almacena en la base de datos el nuevo usuario y envia un mail de 
        bienvenida.
        """
        
        # Crea el usuario
        user = super(RegisterForm, self).save(*args, **kwargs)
        
        # Envia el mail de bienvenida.
        context = {
            'user': user,
        }
        subject = _(u'%(firstname)s Bienvenido a %(sitename)s') % ({
            'firstname': user.first_name, 
            'sitename': current_site.name
        })

        mail = Mailer(subject, 'mail.welcome.txt',
                               'mail.welcome.html', 
                               **context)
        mail.send(user.email)

        return user


class UserForm(forms.ModelForm, MixinClean):
    """
    Formulario para configurar los datos del usuario: nombres, apellidos, email
    contraseña.
    """
    
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput,
                                required=False)
    
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above,"
                                            " for verification."),
                                required=False)
    
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ["first_name", "last_name",
                                "password1", "password2", "email"]
        self.fields['first_name'].label = _('Nombre')
        self.fields['last_name'].label = _('Apellidos')
        self.fields['password2'].help_text = ""

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise forms.ValidationError(_(u'El email es obligatorio'))

        username = self.instance.username

        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(u'El email debe ser único.')
        
        return email

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        
        if self.cleaned_data["password1"]:
            user.set_password(self.cleaned_data["password1"])
        
        if commit:
            user.save()
        
        return user


class ProfileForm(forms.ModelForm):
    """
    Formulario para configurar el perfil del usuario.
    """
    
    image = ThumbnailField(label=_("Avatar"), required=False, help_text=u'Tamaño máximo 5Mb')
    
    class Meta:
        model = Profile
        fields = ('image', 'url', 'description')
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        if image is not None:
            validate_file_size(image)
            
        return image

    def save(self):
        image = self.cleaned_data.get('image')
        
        profile = super(ProfileForm, self).save(commit=True)
        
        if image is not None:
            profile.create_thumbnails()
        
        return profile


class DesignForm(forms.ModelForm):
    """
    Formulario para configurar el diseño del perfil de un usuario.
    """

    class Meta:
        model = Profile
        fields = ('background', 'background_color', 'links_color', 
                  'button_background', 'button_color')


class PasswordResetForm(PasswordResetForm): 
    def save(self, **kwargs):
        use_https = kwargs.pop('use_https', False)
        token_generator = kwargs.pop('token_generator', default_token_generator)
        request = kwargs.pop('request', None)
        from_email = kwargs.pop('from_email', None)
        
        for user in self.users_cache:
            site_name = current_site.name
            domain = current_site.domain
            
            subject = _("Password reset on %s") % site_name
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            
            mail = Mailer(subject, 'mail.password_instructions.txt',
                                   'mail.password_instructions.html', 
                                   **context)
            mail.send(user.email, from_email)

