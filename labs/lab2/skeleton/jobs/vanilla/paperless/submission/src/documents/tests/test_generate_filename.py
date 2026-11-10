import datetime
import uuid

from django.test import TestCase
from django.test import override_settings
from django.utils import timezone

from ..file_handling import generate_filename
from ..models import Document
from ..models import DocumentType
from ..models import Tag


def make_document(**kwargs):
    defaults = {
        "title": "title",
        "mime_type": "application/pdf",
        "checksum": str(uuid.uuid4()),
    }
    defaults.update(kwargs)
    return Document.objects.create(**defaults)


class TestGenerateFilename(TestCase):
    @override_settings(PAPERLESS_FILENAME_FORMAT="{document_type}")
    def test_document_type_placeholder(self):
        doc = make_document()
        self.assertEqual(generate_filename(doc), "none.pdf")

        doc.document_type = DocumentType.objects.create(name="invoice")
        self.assertEqual(generate_filename(doc), "invoice.pdf")

    @override_settings(PAPERLESS_FILENAME_FORMAT="{asn}")
    def test_asn_placeholder(self):
        doc = make_document()
        self.assertEqual(generate_filename(doc), "none.pdf")

        doc.archive_serial_number = 1234
        self.assertEqual(generate_filename(doc), "1234.pdf")

    @override_settings(PAPERLESS_FILENAME_FORMAT="{tags[foo]}")
    def test_tags_with_underscores(self):
        doc = make_document()
        tag = Tag.objects.create(name="foo_bar")
        doc.tags.add(tag)

        self.assertEqual(generate_filename(doc), "bar.pdf")

    @override_settings(PAPERLESS_FILENAME_FORMAT="{tags[foo]}")
    def test_tags_with_dashes(self):
        doc = make_document()
        tag = Tag.objects.create(name="foo-bar")
        doc.tags.add(tag)

        self.assertEqual(generate_filename(doc), "bar.pdf")

    @override_settings(PAPERLESS_FILENAME_FORMAT="{tags[foo]}")
    def test_tags_with_unrecognized_format(self):
        doc = make_document()
        tag = Tag.objects.create(name="foobar")
        doc.tags.add(tag)

        self.assertEqual(generate_filename(doc), "none.pdf")

    @override_settings(PAPERLESS_FILENAME_FORMAT="{tags[0]}")
    def test_tags_by_index(self):
        doc = make_document()
        tag = Tag.objects.create(name="foo_bar")
        doc.tags.add(tag)

        self.assertEqual(generate_filename(doc), "foo_bar.pdf")

    @override_settings(PAPERLESS_FILENAME_FORMAT="{tags[1]}")
    def test_tags_by_index_out_of_range(self):
        doc = make_document()
        tag = Tag.objects.create(name="foo_bar")
        doc.tags.add(tag)

        self.assertEqual(generate_filename(doc), "none.pdf")

    @override_settings(PAPERLESS_FILENAME_FORMAT="{tag_list}")
    def test_tag_list_placeholder(self):
        doc = make_document()
        tag1 = Tag.objects.create(name="b")
        tag2 = Tag.objects.create(name="a")
        doc.tags.add(tag1, tag2)

        self.assertEqual(generate_filename(doc), "a,b.pdf")

    @override_settings(PAPERLESS_FILENAME_FORMAT="/{title}")
    def test_leading_path_separator(self):
        doc = make_document(title="mytitle")

        self.assertEqual(generate_filename(doc), "mytitle.pdf")

    @override_settings(
        PAPERLESS_FILENAME_FORMAT="{created_year}-{created_month}-{created_day}",
    )
    def test_created_year_month_day(self):
        doc = make_document(
            created=timezone.make_aware(datetime.datetime(2020, 5, 21, 7, 36, 51)),
        )

        self.assertEqual(generate_filename(doc), "2020-05-21.pdf")
