import re
from gettext import gettext as _

from markdown import markdown

from django.db import models
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe

# link and image targets which would execute script if we let them through - markdown escapes ampersands and trims
# leading whitespace before it writes these attributes, so matching on the literal scheme is enough
UNSAFE_URL_SCHEME = re.compile(r'(href|src)="\s*(?:javascript|data|vbscript):[^"]*"', re.IGNORECASE)


class Apk(models.Model):
    DOWNLOAD_EXPIRES = 60 * 60 * 24  # Up to 24 hours

    TYPE_RELAYER = "R"
    TYPE_MESSAGE_PACK = "M"

    TYPE_CHOICES = (
        (TYPE_RELAYER, _("Relayer Application APK")),
        (TYPE_MESSAGE_PACK, _("Message Pack Application APK")),
    )

    apk_type = models.CharField(choices=TYPE_CHOICES, max_length=1)

    apk_file = models.FileField(upload_to="apks")

    version = models.TextField(null=False, help_text="Our version, ex: 1.9.8")

    pack = models.IntegerField(
        null=True, blank=True, help_text="Our pack number if this is a message pack (otherwise blank)"
    )

    description = models.TextField(
        null=True, blank=True, default="", help_text="Changelog for this version, markdown supported"
    )

    created_on = models.DateTimeField(default=timezone.now)

    def markdown_description(self):
        # descriptions are entered by staff but are rendered to any user claiming an Android channel, so escape any
        # embedded HTML and neutralize script bearing link targets before marking the result as safe
        html = markdown(escape(self.description))

        return mark_safe(UNSAFE_URL_SCHEME.sub(r'\1="#"', html))

    class Meta:
        unique_together = ("apk_type", "version", "pack")
