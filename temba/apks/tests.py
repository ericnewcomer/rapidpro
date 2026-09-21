from unittest.mock import MagicMock

from django.core.files import File
from django.urls import reverse

from temba.tests import CRUDLTestMixin, TembaTest

from .models import Apk


class ApkCRUDLTest(CRUDLTestMixin, TembaTest):
    def setUp(self):
        super().setUp()
        apk_file_mock = MagicMock(spec=File)
        apk_file_mock.name = "relayer.apk"

        self.apk = Apk.objects.create(
            apk_type="R", version="1.0", description="* has new things", apk_file=apk_file_mock
        )

    def tearDown(self):
        self.clear_storage()

    def test_claim_android(self):
        self.login(self.admin)
        response = self.client.get(reverse("channels.types.android.claim"))
        self.assertContains(response, "<li>has new things</li>")

    def test_markdown_description(self):
        def as_markdown(description):
            self.apk.description = description
            return self.apk.markdown_description()

        # markdown is still rendered as markdown
        self.assertEqual("<ul>\n<li>has new things</li>\n</ul>", as_markdown("* has new things"))
        self.assertEqual("<p><strong>bold</strong></p>", as_markdown("**bold**"))
        self.assertEqual('<p><a href="https://example.com/p">ok</a></p>', as_markdown("[ok](https://example.com/p)"))

        # embedded HTML is escaped rather than passed through
        self.assertEqual("<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>", as_markdown("<script>alert(1)</script>"))
        self.assertEqual("<p>&lt;img src=x onerror=alert(1)&gt;</p>", as_markdown("<img src=x onerror=alert(1)>"))

        # link and image targets which would execute script are neutralized
        self.assertEqual('<p><a href="#">x</a></p>', as_markdown("[x](javascript:alert(1))"))
        self.assertEqual('<p><a href="#">x</a></p>', as_markdown("[x](JaVaScRiPt:alert(1))"))
        self.assertEqual('<p><a href="#">x</a></p>', as_markdown("[x](vbscript:msgbox)"))
        self.assertEqual('<p><a href="#">x</a></p>', as_markdown("[x](data:text/html;base64,PHN2Zz4=)"))
        self.assertEqual('<p><img alt="i" src="#" /></p>', as_markdown("![i](javascript:alert(1))"))

    def test_list(self):
        list_url = reverse("apks.apk_list")

        response = self.assertStaffOnly(list_url)

        self.assertContains(response, "Relayer Application APK")

    def test_create(self):
        create_url = reverse("apks.apk_create")

        self.assertStaffOnly(create_url)

    def test_update(self):
        update_url = reverse("apks.apk_update", args=[self.apk.id])

        response = self.assertStaffOnly(update_url)

        self.assertContains(response, "Relayer Application APK")
