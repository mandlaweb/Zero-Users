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


from django.contrib import admin

from users.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    """
    Configuración para el área de administración para el modelo Profile.
    """

    list_display = ('user', )
    readonly_fields = ('extras', )
    
    def has_add_permission(self, request):
        """
        Evita que el usuario agregue nuevos usuarios desde el administrador del
        perfil, ya que debe hacerse solo desde el administrador del usuario.
        """
        return False

admin.site.register(Profile, ProfileAdmin)

