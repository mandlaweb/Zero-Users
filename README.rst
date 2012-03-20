===========
Zero Common
===========

Another simple app to manage profiles in django.

1. To install run the following command in this directory:

    python setup.py install

2. Add the app in the INSTALLED_APPS on your settings:

    INSTALLED_APPS = (
        ...,
        'users',
        ....,
    )

3. Add to your urls.py:
    
    ...

    urlpatters += patterns('',
        url(r'^users/', include('users.urls')),
    )
    ...

4. Add in you settings.py

   AUTH_PROFILE_MODULE = 'users.Profile'
   LOGIN_URL = '/users/login'
   LOGIN_REDIRECT_URL = '/' # You can use here another path too.





