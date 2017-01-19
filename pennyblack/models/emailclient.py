"""
http://user-agent-string.info/
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _

import datetime
try:
    from django.utils import timezone
except ImportError:
    now = datetime.datetime.now
else:
    now = timezone.now


class EmailClient(models.Model):
    """
    Stores some information about the used email client and about the user
    """
    mail = models.ForeignKey(
        'pennyblack.Mail',
        verbose_name=_('Mail message'),
        related_name='clients')
    user_agent = models.CharField(
        verbose_name=_('User Agent'),
        max_length=1024,
        db_index=True)
    referer = models.CharField(
        verbose_name=_('Referer'),
        max_length=2048, blank=True)
    ip_address = models.GenericIPAddressField(
        verbose_name=_('IP address'))
    visited = models.DateTimeField(
        verbose_name=_('Visited'),
        default=now)
    contact_type = models.CharField(
        verbose_name=_('Contact type'),
        max_length=15, default='')

    class Meta:
        verbose_name = _('email client')
        verbose_name_plural = _('email clients')
        app_label = 'pennyblack'

    def __unicode__(self):
        return self.user_agent
