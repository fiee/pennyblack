from __future__ import absolute_import
from __future__ import unicode_literals
from django.core import files
from django.db import models
from django import forms
try:
    from django.forms.utils import ErrorList  # django >= 1.8
except ImportError:
    from django.forms.util import ErrorList   # django < 1.8
from django.template import Context, Template, TemplateSyntaxError
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from pennyblack import settings
from pennyblack.models.link import check_if_redirect_url, is_link

from feincms.contents import RichTextContent
from feincms.module.medialibrary.models import MediaFile
from feincms.admin.item_editor import ItemEditorForm
from feincms.utils import get_object

import re
import os
try:
    import Image
except:
    from PIL import Image
import exceptions

HREF_RE = re.compile(r'href\="((\{\{[^}]+\}\}|[^"><])+)"')


# copied from old version of FeinCMS:
# https://github.com/feincms/feincms/blob/b4c36b6e3f1f67f271dab83f3382783ec0a48ed3/feincms/content/richtext/models.py
class RichTextContentAdminForm(ItemEditorForm):
    #: If FEINCMS_TIDY_ALLOW_WARNINGS_OVERRIDE allows, we'll convert this into
    # a checkbox so the user can choose whether to ignore HTML validation
    # warnings instead of fixing them:
    seen_tidy_warnings = forms.BooleanField(
        required=False,
        label=_("HTML Tidy"),
        help_text=_("Ignore the HTML validation warnings"),
        widget=forms.HiddenInput
    )

    def clean(self):
        """
        TODO: Tidy was included in old releases of FeinCMS
        """
        cleaned_data = super(RichTextContentAdminForm, self).clean()

        if settings.TIDY_HTML:
            text, errors, warnings = get_object(
                settings.TIDY_FUNCTION)(cleaned_data['text'])

            # Ick, but we need to be able to update text and seen_tidy_warnings
            self.data = self.data.copy()

            # We always replace the HTML with the tidied version:
            cleaned_data['text'] = text
            self.data['%s-text' % self.prefix] = text

            if settings.TIDY_SHOW_WARNINGS and (errors or warnings):
                if settings.TIDY_ALLOW_WARNINGS_OVERRIDE:
                    # Convert the ignore input from hidden to Checkbox so the
                    # user can change it:
                    self.fields['seen_tidy_warnings'].widget =\
                        forms.CheckboxInput()

                if errors or not (
                        settings.TIDY_ALLOW_WARNINGS_OVERRIDE and
                        cleaned_data['seen_tidy_warnings']):
                    self._errors["text"] = self.error_class([mark_safe(
                        _(
                            "HTML validation produced %(count)d warnings."
                            " Please review the updated content below before"
                            " continuing: %(messages)s"
                        ) % {
                            "count": len(warnings) + len(errors),
                            "messages": '<ul><li>%s</li></ul>' % (
                                "</li><li>".join(
                                    map(escape, errors + warnings))),
                        }
                    )])

                # If we're allowed to ignore warnings and we don't have any
                # errors we'll set our hidden form field to allow the user to
                # ignore warnings on the next submit:
                if (not errors and
                        settings.TIDY_ALLOW_WARNINGS_OVERRIDE):
                    self.data["%s-seen_tidy_warnings" % self.prefix] = True

        return cleaned_data


class NewsletterSectionAdminForm(RichTextContentAdminForm):
    def clean(self):
        cleaned_data = super(NewsletterSectionAdminForm, self).clean()
        try:
            Template("{%%load pennyblack_tags %%}%s" % cleaned_data['text'])
        except TemplateSyntaxError, e:
            self._errors["text"] = ErrorList([e])
        except exceptions.KeyError:
            pass
        try:
            Template("{%%load pennyblack_tags %%}%s" % cleaned_data['title'])
        except TemplateSyntaxError, e:
            self._errors["title"] = ErrorList([e])
        except exceptions.KeyError:
            pass
        return cleaned_data

    class Meta:
        exclude = ('image_thumb', 'image_width', 'image_height', 'image_url_replaced')

    def __init__(self, *args, **kwargs):
        super(NewsletterSectionAdminForm, self).__init__(*args, **kwargs)
        self._meta.fields.insert(0, 'title')


class TextOnlyNewsletterContent(RichTextContent):
    """
    Has a title and a text wich both can contain template code.
    """
    title = models.CharField(
        verbose_name=_('Title'),
        max_length=500)
    form = NewsletterSectionAdminForm
    feincms_item_editor_form = NewsletterSectionAdminForm

    feincms_item_editor_includes = {
        'head': [settings.TINYMCE_CONFIG_URL],
    }

    baselayout = "content/text_only/section.html"

    class Meta:
        abstract = True
        verbose_name = _('text only content')
        verbose_name_plural = _('text only contents')

    def __repr__(self):
        return super(TextOnlyNewsletterContent, self).__repr__() + "'''%r'''"%(self.text,)

    def replace_links(self, job):
        """
        Replaces all links and inserts pingback links
        """
        offset = 0
        for match in HREF_RE.finditer(self.text):
            link = match.group(1)
            if check_if_redirect_url(link):
                continue
            # don't replace links to proxy view
            if u'link_url' in link:
                continue
            replacelink = job.add_link(link)
            self.text = ''.join((self.text[:match.start(1) + offset],
                                 replacelink,
                                 self.text[match.end(1) + offset:]))
            offset += len(replacelink) - len(match.group(1))

    def prepare_to_send(self, save=True):
        """
        insert link_style into all a tags
        """
        self.text = re.sub(
            r"<a ",
            "<a style=\"{% get_newsletterstyle request link_style %}\"",
            self.text)
        if save:
            self.save()

    def get_template(self):
        """
        Creates a template
        """
        return Template("""{%% extends "%s" %%}
        {%% load pennyblack_tags %%}
        {%% block title %%}%s{%% endblock %%}
        {%% block text %%}%s{%% endblock %%}
        """ % (self.baselayout, self.title, self.text,))

    def render(self, request, **kwargs):
        context = request.content_context
        context['request'] = request
        context.update({
            'content': self,
            'content_width': settings.NEWSLETTER_CONTENT_WIDTH})
        if hasattr(self, 'get_extra_context'):
            context.update(self.get_extra_context())
        return self.get_template().render(Context(context))


class TextWithImageNewsletterContent(TextOnlyNewsletterContent):
    """
    Like a TextOnlyNewsletterContent but with extra image field
    """
    image_original = models.ForeignKey(
        MediaFile,
        verbose_name=_('Image Original'))
    image_thumb = models.ImageField(
        verbose_name=_('Image Thumbnail'),
        upload_to='newsletter/images', blank=True,
        width_field='image_width', height_field='image_height')
    image_width = models.IntegerField(
        verbose_name=_('Image Width'),
        default=0)
    image_height = models.IntegerField(
        verbose_name=_('Image Height'),
        default=0)
    image_url = models.CharField(
        verbose_name=_('Image URL'),
        max_length=250, blank=True)
    image_url_replaced = models.CharField(
        verbose_name=_('Replaced Image URL'),
        max_length=250, default='')
    position = models.CharField(
        verbose_name=_('Position'),
        max_length=10,
        choices=settings.TEXT_AND_IMAGE_CONTENT_POSITIONS)

    baselayout = "content/text_and_image/section.html"

    class Meta:
        abstract = True
        verbose_name = _('text and image content')
        verbose_name_plural = _('text and image contents')

    def get_extra_context(self):
        text_width = settings.NEWSLETTER_CONTENT_WIDTH \
            if self.position == 'top' \
            else (settings.NEWSLETTER_CONTENT_WIDTH - 20 - settings.TEXT_AND_IMAGE_CONTENT_IMAGE_WIDTH_SIDE)
        return {
            'image_width': self.image_width,
            'image_height': self.image_height,
            'text_width': text_width,
        }

    def get_image_url(self, context=None):
        """
        Gives the repalced url back, if no mail is present it gives instead
        the original url.
        """
        if context is None:
            return self.image_url
        template = Template(self.image_url_replaced)
        return template.render(context)

    def replace_links(self, job):
        super(TextWithImageNewsletterContent, self).replace_links(job)
        if not is_link(self.image_url, self.image_url_replaced):
            self.image_url_replaced = job.add_link(self.image_url)
            self.save()

    def save(self, *args, **kwargs):
        image_width = settings.NEWSLETTER_CONTENT_WIDTH \
            if self.position == 'top' \
            else settings.TEXT_AND_IMAGE_CONTENT_IMAGE_WIDTH_SIDE
        im = Image.open(self.image_original.file.path)
        im.thumbnail((image_width, 1000), Image.ANTIALIAS)
        img_temp = files.temp.NamedTemporaryFile()
        im.convert('RGB').save(
            img_temp, 'jpeg', quality=settings.JPEG_QUALITY, optimize=True)
        img_temp.flush()
        self.image_thumb.save(
            os.path.split(self.image_original.file.name)[1],
            files.File(img_temp), save=False)
        super(TextWithImageNewsletterContent, self).save(*args, **kwargs)
