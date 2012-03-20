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
from os import path

from django.conf import settings
from django.core import mail
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from common.tests import TestBase
from thumbnails.tests import IMAGE_TEST
from users.models import Profile


class TestUsersViews(TestBase):
    fixtures = ['users'] 
    
    def setUp(self):
        TestBase.setUp(self)
        self.data = {
            "first_name": "Test",
            "last_name": "Fake",
            "username": "testfake",
            "password1": "fakepass",
            "password2": "fakepass",
            "email": "test@fake.com",
        }
        
        self.model = User
        self.object = self.model.objects.get(pk=1)

    def test_users_login(self):
        """
        Como usuario debo ser capaz de ver el formulario de identificación
        """
        response = self.client_get('users_login')
        assert response.status_code == 200

    def test_valid_login(self):
        """
        Como usuario debo ser capaz de identificarme en el sitio.
        """

        response = self.client_post('users_login', data={'username': 'testaccount', 'password': 'fakepass'})
        assert response.status_code == 302

    def test_users_logout(self):
        """
        Como usuario debo ser capaz de salir de sitio.
        """
        self._login()
        response = self.client_get('users_logout')
        self.assertRedirects(response, reverse('home'), host=self.server_name)
        
    def test_users_register(self):
        """
        Como visitante debo ser capaz de ver la página de registro del sitio.
        """

        response = self.client_get('users_register')
        assert response.status_code == 200

    def test_create_user(self):
        """
        Como visitante debo ser capaz de registrarme en el sitio.
        """
        
        mail_count = len(mail.outbox)
        
        # Enviamos la petición para crear un usuario.
        response = self.client_post('users_register', data=self.data)
        assert response.status_code == 302
        
        # Verificamos que se envió un mail de bienvenida.
        assert (mail_count + 1) == len(mail.outbox)

        # Verificamos que se crea un perfil
        p = Profile.objects.get(user__username=self.data['username'])
        assert p.username == self.data['username']
    
    def test_invalid_username(self):
        """
        El sistema debe validar el nombre de usuario antes de crear el usuario.
        """
        self.invalid_usernames = ['', '!@#$%^username', 'my_username', 'my@username.com']
        
        for username in self.invalid_usernames:
            self.data['username'] = username
            response = self.client_post('users_register', data=self.data)
            assert response.status_code != 302

    def test_invalid_email(self):
        """
        El sistema debe validar el email antes de crear el usuario.
        """
        
        self.invalid_emails = ['', 'invalidmail', 'invalid@mail']
        
        for email in self.invalid_emails:
            self.data['email'] = email
            response = self.client_post('users_register', data=self.data)
            assert response.status_code != 302

    def test_invalid_firstname(self):
        """
        El sistema debe ser capaz de validar el primer nombre antes de 
        registrar el usuario
        """

        self.data['first_name'] = ''
        response = self.client_post('users_register', data=self.data)
        assert response.status_code != 302
    
    def test_valid_usernames(self):
        """
        El sistema debe permitir registrar solo nombre usuario que contengan
        caracteres alfanúmericos y el caracter -
        """

        self.validusernames = ['fakeuser', 'fake-user', 'fakeuser01']
        
        for username in self.validusernames:
            # Actualizamos los datos con el nombre de usuario valido
            self.data['username'] = username
            self.data['email'] = '%s@mail.com' % username
            
            # Enviamos la petición para registrar y verificamos
            response = self.client_post('users_register', data=self.data)
            assert response.status_code == 302
            
            # Sale del sistema para intentar con un nuevo nombre de usuario.
            self.logout()

    def test_profile_get(self):
        """
        Como usuario debo poder ingresar en los perfiles de los usuarios que se crean.
        """
        # Creamos los usuarios
        self.test_valid_usernames()
        
        #verificamos que todos se cargan correctamente.
        for username in self.validusernames:
            url = 'http://%s.%s' % (username, self.server_name)
            response = self.client_get(url)
            self.assertEquals(response.status_code, 200)

    def test_account(self):
        """
        El sistema debe ser capaz de mostrar el formulario para modificar los
        datos del usuario.
        """
        
        from django.contrib.auth import REDIRECT_FIELD_NAME

        # Verificamos que el usuario tienen que estar logueado
        response = self.client_get('users_account')
        expected_url = '%s?%s=%s' % (reverse('users_login'), 
                                     REDIRECT_FIELD_NAME,
                                     reverse('users_account'))
        self.assertRedirects(response, expected_url, host=self.server_name)
        
        # Verificamos con un usuario logueado.
        self._login()
        response = self.client_get('users_account')
        logging.info('status_code: %s ' % response.status_code)
        assert response.status_code == 200

        # Modificamos los valores
        data = {
            'first_name': 'new first name',
            'last_name': 'new second name',
            'email': 'new@email.com'
        }
        response = self.client_post('users_account', data=data)
        assert response.status_code == 302

        # Verificamos los valores cambiados
        user = self._update(self.user)
        assert user.first_name == data['first_name']
        assert user.last_name == data['last_name']
        assert user.email == data['email']

    def test_change_account_without_change_password(self):
        """
        Como usuario debo ser capaz de cambiar mis datos de perfil sin cambiar
        mi contraseña
        """
        data = self.data.copy()
        del data["username"]
        data['password1'] = ''
        data['password2'] = ''

        self.login("zero", "fakepass")
        self.object = User.objects.get(username='zero')
        
        response = self.client_post('users_account', data=data)
        assert response.status_code == 302
        
        self.client_get('users_logout')
        
        response = self.client_post('users_login', data={'username': 'zero', 'password': 'fakepass'})
        self.assertRedirects(response, reverse('home'), host=self.server_name)
    
    def test_avatar_upload(self):
        """
        Como usuario debo ser capaz de subir un avatar a mi perfil.
        """

        self._login()
        image = open(IMAGE_TEST)

        data = {
            'image': image
        }
        response = self.client_post('users_personal', data=data)
        assert response.status_code == 302

        profile = self.user.get_profile()
        for size in Profile.sizes.keys():
            assert profile.thumbnail_exists(size)

    def test_change_personal_data(self):
        """
        Como usuario debo ser capaz de añadir mi website y una descripción de
        mi cuenta.
        """

        self._login()

        # Verificamos que se muestra el formulario
        response = self.client_get('users_personal')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, '<form')

        data = {
            'description': 'soy una cuenta para hacer tests.',
            'url': 'http://tester.me/'
        }
        response = self.client_post('users_personal', data=data)
        assert response.status_code == 302
        
        profile = self.user.get_profile()
        assert profile.description == data['description']
        assert profile.url == data['url']
    
    def test_password_reset(self):
        """
        Como usuario debo ser capaz de solicitar cambiar mi password.
        """

        # verificamos que la pagina para resetear el password
        response = self.client_get('password_reset')
        assert response.status_code == 200
        
        # Verificamos la petición de cambiar el password y el envío de mail
        mail_count = len(mail.outbox)

        response = self.client_post('password_reset', data={'email': self.email})
        assert response.status_code == 302
        assert (mail_count + 1) == len(mail.outbox)

    def test_reset_confirm(self):
        """
        Como usuario debo ser capaz de cambiar mi contraseña a travez de un 
        código.
        """

        self.test_password_reset()
        url, path = self._read_signup_email(mail.outbox[0])
        
        # verificamos que la pagina se carga correctamente.
        response = self.client_get(path)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Please enter your new password" in response.content)
        
        # verificamos que se cambia de contraseña
        data = {
            'new_password1': 'nuevopass',
            'new_password2': 'nuevopass',
        }
        response = self.client_post(path, data=data)
        self.assertRedirects(response, reverse('password_reset_complete'), host=self.server_name)
        user = User.objects.get(username=self.username)
        self.assertTrue(user.check_password('nuevopass'))

    def test_set_design(self):
        """
        Como usuario debo ser capaz de cambiar el color de fondo y la imagen
        de mi perfil y el color de los enlaces.
        """
        
        self._login()
        user = self.get_user()
        profile = user.get_profile()
        
        # Verificamos que se muestre el formulario de diseño
        response = self.client_get('users_design')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, '<form')
        
        # Cambiamos el color de fondo y de los links
        data = {
            "background_color": "#fff",
            "links_color": "#888",
            "button_background": '#444',
            "button_color": '#aaa'
        }
        
        response = self.client_post('users_design', data=data)
        assert response.status_code == 302
        
        # Verificamos el cambio en el perfil.
        profile = self._update(profile)
        self.assertEquals(profile.background_color, data['background_color'])
        self.assertEquals(profile.links_color, data['links_color'])
        
        # Verificamos que solo permita colores válidos.
        invalids = ['#fff9', '#a', 'asdf', '123456']
        
        for field in data.keys():
            for invalid in invalids:
                data[field] = invalid
                response = self.client_post('users_design', data=data)
                assert response.status_code == 200

    def test_set_background(self):
        """
        Como usuario debo ser capaz de colocar una imagen de fondo en mi perfil
        """

        self._login()
        
        user = self.get_user()
        profile = user.get_profile()
        background_file = path.join(path.abspath(path.dirname(__file__)),
                                    'static', 'bg.jpg')
        assert not profile.background

        # Posteamos la imagen
        data = {
            "background": open(background_file)
        }
        response = self.client_post('users_design', data=data)
        self.assertEquals(response.status_code, 302)

        # Verificamos que se ha subido la imagen
        profile = self._update(profile)
        self.assertTrue(profile.background)
    
    def _read_signup_email(self, email):
        urlmatch = re.search(r"https?://[^/]*(/.*reset/\S*)", email.body)
        self.assertTrue(urlmatch is not None, "No URL found in sent email")
        return urlmatch.group(), urlmatch.groups()[0]
        
    
