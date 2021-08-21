======
Busker
======
Busker is a Django app for managing and redeeming codes that allow end-users to download digital assets
(Music, E-Books, High-resolution artwork, etc.)

Demo
====
You can test-drive the code redemption workflow by visiting `<https://magicians.band/download/>`_ and entering the code ``AM1FDEF``, or by going directly to `<https://magicians.band/download/redeem/AM1FDEF/>`_.

Pre-requisites
==============

* A Django 3 installation (Will probably work fine in 2.x but has not been tested)
* Python 3

Installation
============

pip
---
To install the latest release of Busker with pip, use::

  pip install git+https://github.com/tinpan-io/django-busker.git#egg=django_busker

To install a specific tag with pip, use the following format::

  pip install git+https://github.com/tinpan-io/django-busker.git@[tag]#egg=django_busker

...where ``[tag]`` is the version you want to use; for example, to install version 0.7.0::

  pip install git+https://github.com/tinpan-io/django-busker.git@0.7.0#egg=django_busker

  
Local
-----
To install from a checked out copy of the repository, ``cd`` into the top-level
directory and run::

  python setup.py install

  
Django Setup
=====
Edit your Django ``settings.py`` module and add three new items to the ``INSTALLED_APPS`` list::

  'imagekit',
  'markdownfield',
  'busker'

You will also need to make sure that ``'django.contrib.sessions.middleware.SessionMiddleware'`` is enabled in ``MIDDLEWARE`` (It's included by default in a new boilerplate Django project, so you probably won't need to change anything here.)

Next, add busker's URLs to your Django project's main ``urls.py`` module::

  path('busker/', include('busker.urls', namespace='busker')),

(The first argument to ``path()`` can be whatever you like, but make sure ``namespace`` is set to ``'busker'``.

For uploaded images to display correctly you also will need ``MEDIA_ROOT`` and ``MEDIA_URL`` configured in your ``settings.py`` module. (See <https://docs.djangoproject.com/en/3.1/howto/static-files/> for a way to tweak your project ``urls.py`` to serve media when developing locally.)

When deploying to production, you'll need to run the ``collectstatic`` admin command.

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

Represents an item that will be accessible to people with valid download codes; for example, a zip file containing an album of music. (Or, several zip files of the same album in different formats.)

File
----

One or more File objects can be linked to a DownloadableWork

Batch
-----

Batches automatically generate batches of unique codes for a given DownloadableWork. Note the 'export csv' option in the Batch admin view.

DownloadCode
------------

DownloadCode objects represent the actual codes users can use to access files. They're generally auto-created when a new Batch is saved. Note the 'export csv' option in the DownloadCode admin view.

Signals
=======
Busker provides the following signals which may be useful:

``busker.signals.code_post_redeem(sender, request, code)``
This signal is sent whenever a DownloadCode is redeemed, *after* its ``times_used`` and ``last_used_date`` fields have been updated but *before* the user is presented with the download page. It sends the `request` object and the `DownloadCode` object being redeemed. 

``busker.signals.file_pre_download(sender, request, file)``
This signal is sent whenever a user clicks on a link to download a file, *after* the File object has been loaded but *before* the file is actually sent to the client. It sends the `request` object and the `File` object being redeemed.
