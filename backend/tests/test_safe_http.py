import unittest

from tools.safe_http import (
    UnsafeOutboundRequestError,
    normalize_public_https_url,
    public_https_url_host,
    validate_public_https_url,
)


class PublicHttpsUrlValidationTests(unittest.TestCase):
    def test_normalizes_domain_input_to_https_url(self):
        self.assertEqual(
            normalize_public_https_url("Example.COM./jobs?role=backend"),
            "https://example.com/jobs?role=backend",
        )

    def test_empty_optional_url_stays_empty(self):
        self.assertEqual(normalize_public_https_url("   "), "")

    def test_extracts_normalized_public_host(self):
        self.assertEqual(
            public_https_url_host("https://www.Example.com/careers"),
            "www.example.com",
        )

    def test_accepts_default_https_port(self):
        self.assertEqual(
            validate_public_https_url("https://example.com:443/jobs"),
            "https://example.com:443/jobs",
        )

    def test_rejects_plain_http(self):
        with self.assertRaises(UnsafeOutboundRequestError):
            validate_public_https_url("http://example.com/jobs")

    def test_rejects_embedded_credentials(self):
        with self.assertRaises(UnsafeOutboundRequestError):
            validate_public_https_url("https://user:pass@example.com/jobs")

    def test_rejects_non_default_ports(self):
        with self.assertRaises(UnsafeOutboundRequestError):
            validate_public_https_url("https://example.com:8443/jobs")

    def test_rejects_localhost(self):
        with self.assertRaises(UnsafeOutboundRequestError):
            validate_public_https_url("https://localhost/jobs")

    def test_rejects_private_ipv4_literal(self):
        with self.assertRaises(UnsafeOutboundRequestError):
            validate_public_https_url("https://10.0.0.4/jobs")

    def test_rejects_loopback_ipv6_literal(self):
        with self.assertRaises(UnsafeOutboundRequestError):
            validate_public_https_url("https://[::1]/jobs")

    def test_rejects_cloud_metadata_ip(self):
        with self.assertRaises(UnsafeOutboundRequestError):
            validate_public_https_url("https://169.254.169.254/latest/meta-data")

    def test_rejects_reserved_internal_domains(self):
        for url in (
            "https://service.local/jobs",
            "https://metadata.google.internal/computeMetadata/v1",
            "https://example.test/jobs",
        ):
            with self.subTest(url=url):
                with self.assertRaises(UnsafeOutboundRequestError):
                    validate_public_https_url(url)


if __name__ == "__main__":
    unittest.main()
