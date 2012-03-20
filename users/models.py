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


import os
import uuid
import logging

from time import time

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

from django.utils.translation import ugettext_lazy as _

from common.fields import DictField
from common.fields import ColorField
from thumbnails.models import ThumbnailMixin

from users.managers import ProfileManager


current_site = Site.objects.get_current()


class Profile(ThumbnailMixin):
    """
    Modelo para manejar información adicional sobre el perfil del usuario.
    """
    
    #: usuario al que pertence el perfil
    user = models.ForeignKey(User, related_name='profile')

    #: Nombre de usuario
    username = models.CharField(_(u'Nombre de usuario'), max_length=255, 
                                                         blank=True,
                                                         null=True)

    # Fecha de la última publicación realizada.
    last_published = models.DateTimeField(_(u'Última publicación'), auto_now_add=True)
    
    #: descripción del usuario.
    description = models.TextField(_(u'Descripción'), blank=True, default='')
    
    #: Website del usuario.
    url = models.URLField(_(u'Website'), blank=True, default='')
    
    #: Campo para almacenar información adicional
    extras = DictField(_('Extras'), null=False, blank=True, default={})

    #: Imagen de fondo del perfil.
    background = models.ImageField(_(u'Imagen de fondo'), blank=True, null=True, upload_to='backgrounds')
    
    #: Color de fondo del perfil.
    background_color = ColorField(_(u'Color de fondo'), blank=True, null=True)
    
    #: Color de los enlaces.
    links_color = ColorField(_(u'Color de los enlaces'), blank=True, null=True)
    
    #: Color del fondo de los botones
    button_background = ColorField(_(u'Fondo botones'), blank=True, null=True)

    #: Color del texto de los botones
    button_color = ColorField(_(u'Color texto botones'), blank=True, null=True)


    objects = ProfileManager()
    
    #: Los tamaños permitidos en los avatares
    sizes = {
        'u': (25, 25),
        's': (50, 50),
        'm': (80, 80),
        'l': (115, 115),
    }

    # directorio base para los avatares
    basepath = 'avatars'
    
    #: Avatares por defecto.
    defaults = {
        'u': 'avatar_u.png',
        's': 'avatar_s.png',
        'm': 'avatar_m.png',
        'l': 'avatar_l.png',
    }

    def thumbnail_name(self, size):
        """
        Retorna el nombre del thumbnail del tamaño *size*
        """
        
        thumb_name = '%s_%s.jpg' % (self.user.username, str(size))
        return os.path.join(self.thumbnail_basepath(), thumb_name)
    
    def get_absolute_url(self):
        """
        Retorna el path absoluto del perfil.
        """
        
        return "http://%s.%s" % (self.username, current_site.domain)
