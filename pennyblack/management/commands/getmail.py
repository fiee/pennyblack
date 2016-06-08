from django.utils.translation import ugettext_lazy as _
from django.core.management.base import BaseCommand
from pennyblack.models import Sender


class Command(BaseCommand):
    args = ''
    help = _('Gets all Bounce emails')

    def handle(self, *args, **options):
        senders = Sender.objects.filter(get_bounce_emails=True)
        for sender in senders:
            sender.get_mail()
