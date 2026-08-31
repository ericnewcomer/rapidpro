import re
from gettext import gettext as _

from markdown import markdown

from django.db import models
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe

# matches links and images in rendered markdown which use unsafe URL protocols
UNSAFE_PROTOCOL_RE = re.compile(r'(href|src)="\s*(?:javascript|data|vbscript):[^"]*"', re.IGNORECASE)


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
        # escaping the description prevents raw HTML injection but markdown link syntax can still generate anchors
        # with unsafe protocols, so neutralize those in the rendered output
        html = markdown(escape(self.description or ""))
        return mark_safe(UNSAFE_PROTOCOL_RE.sub(r'\1="#"', html))

    class Meta:
        unique_together = ("apk_type", "version", "pack")
