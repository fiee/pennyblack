==========
pennyblack
==========

Pennyblack is a newsletter module based on the feincms.org_ CMS building
toolkit. E-mails can either be sent as mass mails (e.g. monthly newsletter) or
as part of a customised workflow (e.g. user clicks on a link and in response to
that your application sends out an e-mail).  Conditional data and variables can
be filled in to a newsletter using the django template language.

SPF (sender validation) and bounce management can be activated if desired.
Key data like bounce rate, opening rate and link clicks is tracked and presented
in the admin menu. Sending bulk e-mails is easy on memory. 20’000 and more
addresses wont crash your server. From the outset we developed Pennyblack to
easily integrate into existing web projects.

This is the fork by fiëé visuëlle, intended to work with latest Django (1.9)
and FeinCMS (1.11+). Based on the Django 1.7 branch of nickburlett’s fork.


Installation
------------

**Notice**: This installation guide is not complete.

1. Make sure you have a working django project setup.

2. Install Pennyblack over `pip`::

    pip install git+https://github.com/fiee/pennyblack.git

3. Make sure that the FeinCMS and Pennyblack Apps are added to your installed
   apps in your `settings.py`::

    'feincms',
    'feincms.module.medialibrary',
    'pennyblack',
    'pennyblack.module.subscriber',

4. Add a newsletter url to your `urls.py`::

    url(r'^newsletter/', include('pennyblack.urls'), name='pennyblack'),
    
5. Install dependencies (over `pip`):

    * pydns==2.3.4
    * pyspf==2.0.5
    * celery
    
6. Import Pennyblack and add a newsletter template to your `models.py`::

    from pennyblack.models.newsletter import Newsletter
    from pennyblack.content.richtext import (TextOnlyNewsletterContent,
                                             TextWithImageNewsletterContent)
   
    Newsletter.register_templates({
      'key': 'example',
      'title': 'Example Newsletter',
      'path': 'example_newsletter.html',
      'regions': (
          ('main', 'Main Region'),
          ),
      })

    Newsletter.create_content_type(TextOnlyNewsletterContent)
    Newsletter.create_content_type(TextWithImageNewsletterContent)
        
7. Migrate::

    ./manage.py makemigrations pennyblack subscriber
    ./manage.py migrate pennyblack subscriber
    

Dependencies
------------

*   Python

    *   django
    *   feincms incl. medialibrary
    *   pyspf
    *   pydns
    *   pil(low)
    *   celery
    
*   Project Settings

    *   TEMPLATE_CONTEXT_PROCESSORS
    
        *   `django.core.context_processors.request`
    *   FEINCMS_ADMIN_MEDIA
    

.. _feincms.org: http://feincms.org
