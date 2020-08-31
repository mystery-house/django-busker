======
Busker
======
Busker is a Django app for managing and redeeming codes that allow end-users to download digital assets
(Music, E-Books, High-resolution artwork, etc.)

Pre-requisites
==============

* A Django 3 installation (Will probably work fine in 2.x but has not been tested)
* Python 3

Installation
============

From the top level of your checked-out copy of the busker repository, run::

  python setup.py install

Edit your Django ``settings.py`` module and add three new items to the ``INSTALLED_APPS`` list::

  'imagekit',
  'markdownfield',
  'busker'

You will also need to make sure that ``'django.contrib.sessions.middleware.SessionMiddleware'`` is enabled in ``MIDDLEWARE`` (It's included by default in a new boilerplate Django project, so you probably won't need to change anything here.)

Next, add busker's URLs to your Django project's main ``urls.py`` module::

  path('busker/', include('busker.urls', namespace='busker')),

(The first argument to ``path()`` can be whatever you like, but make sure ``namespace`` is set to ``'busker'``.

Finally, in the terminal, run busker's migrations from the top level of the Django project::

  python manage.my migrate busker

If you log into the Admin UI you should now see several new models.

Models
======

These are the models defined by busker, in the order you'll probably want to create them:

Artist
------

Represents an artist/creator.

DownloadableWork
----------------

Represents an item that will be accessible to people with valid download codes; for example, an music album or EP.

File
----

One or more File objects can be linked to a DownloadableWork

Batch
-----

Batches automatically generate batches unique codes for a given DownloadableWork. Note the 'export csv' option in the Batch admin view.

DownloadCode
------------

DownloadCode objects represent the actual codes users can use to access files. They're generally auto-created when a new Batch is saved. Note the 'export csv' option in the DownloadCode admin view.
