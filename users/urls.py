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


from django.conf.urls.defaults import *
from django.contrib.auth.models import User

from django.contrib.auth.views import login, logout

from users.views import UsersIndex
from users.views import UsersProfile
from users.views import UsersUpdate
from users.views import UsersUpdateProfile
from users.views import UsersUpdateDesign


login_kwargs = {
    'template_name': 'page.users.login.html',
    'current_app': 'users'
}
logout_kwargs = {
    'next_page': '/'
}


urlpatterns = patterns('',
    # usuarios
    url(r'^$', UsersIndex.as_view(), name='users_index'),
    url(r'^login$', login, login_kwargs, name='users_login'),
    url(r'^logout$', logout, logout_kwargs, name='users_logout'),
)

urlpatterns += patterns('users.views',
    # password reset
    url(r'^password/$', 'password_reset', name='password_reset'),
    url(r'^password/completo$', 'password_reset_done', name='password_reset_done'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'password_reset_confirm', name='password_reset_confirm'),
    url(r'^reset/completo/$', 'password_reset_complete', name='password_reset_complete'),
    
    # User
    url(r'^register$', 'register', name='users_register'),
    url(r'^cuenta$', UsersUpdate.as_view(), name='users_account'),
    url(r'^personal$', UsersUpdateProfile.as_view(), name='users_personal'),
    url(r'^diseno$', UsersUpdateDesign.as_view(), name='users_design'),
    url(r'^profile$', 'profile', name='users_profile'),
    url(r'^(?P<username>[\w\-]+)', 'profile', name='users_profile')
)

