import socket
import unittest
from unittest.mock import patch

from tools.safe_http import (
    SafeAsyncClient,
    UnsafeOutboundRequestError,
    normalize_public_https_url,
    public_https_url_host,
    validate_public_https_url,
)


def _addrinfo(address: str):
    if ":" in address:
        return (socket.AF_INET6, socket.SOCK_STREAM, 6, "", (address, 443, 0, 0))
    return (socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, 443))


def _mock_dns(*addresses: str):
    return patch(
        "tools.safe_http.socket.getaddrinfo",
        return_value=[_addrinfo(address) for address in addresses],
    )


class PublicHttpsUrlValidationTests(unittest.TestCase):
    def test_normalizes_domain_input_to_https_url(self):
        with _mock_dns("93.184.216.34"):
            self.assertEqual(
                normalize_public_https_url("Example.COM./jobs?role=backend"),
                "https://example.com/jobs?role=backend",
            )

    def test_empty_optional_url_stays_empty(self):
        self.assertEqual(normalize_public_https_url("   "), "")

    def test_extracts_normalized_public_host(self):
        with _mock_dns("93.184.216.34"):
            self.assertEqual(
                public_https_url_host("https://www.Example.com/careers"),
                "www.example.com",
            )

    def test_accepts_default_https_port(self):
        with _mock_dns("93.184.216.34"):
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

    def test_rejects_domain_that_resolves_to_private_address(self):
        with _mock_dns("10.0.0.4"):
            with self.assertRaises(UnsafeOutboundRequestError):
                validate_public_https_url("https://jobs.example.com/posting")

    def test_rejects_domain_with_any_private_resolution(self):
        with _mock_dns("93.184.216.34", "169.254.169.254"):
            with self.assertRaises(UnsafeOutboundRequestError):
                validate_public_https_url("https://jobs.example.com/posting")

    def test_rejects_unresolvable_domain(self):
        with patch(
            "tools.safe_http.socket.getaddrinfo",
            side_effect=socket.gaierror,
        ):
            with self.assertRaises(UnsafeOutboundRequestError):
                validate_public_https_url("https://jobs.example.com/posting")

    def test_rejects_reserved_internal_domains(self):
        for url in (
            "https://service.local/jobs",
            "https://metadata.google.internal/computeMetadata/v1",
            "https://example.test/jobs",
        ):
            with self.subTest(url=url):
                with self.assertRaises(UnsafeOutboundRequestError):
                    validate_public_https_url(url)


class SafeAsyncClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_post_validates_url_before_delegating(self):
        class DummyClient:
            def __init__(self):
                self.url = None

            async def post(self, url, **kwargs):
                self.url = url
                return "ok"

        client = DummyClient()
        wrapper = SafeAsyncClient(client, {"api.resend.com"})

        result = await wrapper.post("https://api.resend.com/emails")

        self.assertEqual(result, "ok")
        self.assertEqual(client.url, "https://api.resend.com/emails")

    async def test_post_rejects_unapproved_host_before_delegating(self):
        class DummyClient:
            def __init__(self):
                self.called = False

            async def post(self, url, **kwargs):
                self.called = True
                return "ok"

        client = DummyClient()
        wrapper = SafeAsyncClient(client, {"api.resend.com"})

        with self.assertRaises(UnsafeOutboundRequestError):
            await wrapper.post("https://169.254.169.254/latest/meta-data")

        self.assertFalse(client.called)


if __name__ == "__main__":
    unittest.main()
