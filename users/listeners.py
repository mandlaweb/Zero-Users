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

from django.db import transaction
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, using, *args, **kwargs):
    """
    Crea el perfil de usuario cuando se crea un usuario.
    """
    from users.models import Profile

    if created:
        try:
            sp_id = transaction.savepoint()
            profile = Profile(user=instance, username=instance.username)
            profile.save()
            transaction.savepoint_commit(sp_id)
        except Exception, e:
            logging.error('ERROR: %s ' % e)
            transaction.savepoint_rollback(sp_id)
    
