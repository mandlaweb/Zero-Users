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


def get_dict_by_related(query, related):
    """
    Retorna un diccionario con los ids de los objetos de query como claves y 
    como valores a sus respectivos objetos que estan nombrados como *related*.
    
    Por ejemplo dado una lista de posts que cada uno tiene un atributo llamado 
    'user' que referencia a un objeto Usuario, retorna un diccionario con los
    ids de los posts como claves y sus respectivos usuarios como valores::

        {
            <id_post>: <user>
            ...
        }

    """

    object_dict = {}

    for obj in query:
        field = getattr(obj, related)
        key = str(field)
        object_dict[key] = obj

    return object_dict

def get_dict_by_ids(model, ids):
    """
    Retorna un diccionario con los *ids* pasados como parametro y los objetos
    que pertenecen al modelo *model* y que tienen sus id dentro de *ids*
    """

    objects_dict = {}

    query = model.objects.filter(pk__in=ids)

    for obj in query:
        key = str(obj.id)
        objects_dict[key] = obj

    return objects_dict
