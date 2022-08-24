from django.test import TestCase

from mailreceiver import mail_parsing


class AmountExtraction(TestCase):
    def test_invoice_amount_extraction(self):
        test_strings = (
            "Test 123.40EUR",
            "EUR 123,40",
            "€123.40",
            "123,40      €",
            "123.4€",
            "asd 123.40   ",
        )
        for input_ in test_strings:
            amount = mail_parsing.extract_invoice_amount_candidates(input_)
            self.assertEqual(max(amount), 123.4)

    def test_invoice_amount_extraction_fails_on_bogous_amounts(self):
        test_strings = (
            "Test 123.4",
            "",
        )
        for input_ in test_strings:
            amount = mail_parsing.extract_invoice_amount_candidates(input_)
            self.assertEqual(len(amount), 0)

    def test_invoice_amount_extraction_returns_absolute_value(self):
        test_strings = ("Test -123.40€",)
        for input_ in test_strings:
            amount = mail_parsing.extract_invoice_amount_candidates(input_)
            self.assertEqual(len(amount), 1)
            self.assertEqual(amount[0], 123.4)


class SubjectParsing(TestCase):
    def test_removes_prefix(self):
        test_subject = {"Subject": "Fwd: Aw: Re: TestSubject"}
        stripped_subject = mail_parsing.get_subject_without_prefixes(test_subject)
        self.assertEqual(stripped_subject, "TestSubject")
