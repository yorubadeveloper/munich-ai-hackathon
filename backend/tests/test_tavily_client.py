import os
import unittest
from unittest.mock import patch

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://huntagent:huntagent@localhost:5432/huntagent",
)

from tools import tavily_client
from tools.safe_http import UnsafeOutboundRequestError


class TavilySearchQueryValidationTests(unittest.TestCase):
    def test_plain_search_operator_is_not_treated_as_url(self):
        query = 'site:example.com "Backend Engineer" hiring'

        with patch("tools.tavily_client.validate_public_https_url") as validate:
            self.assertEqual(tavily_client._normalize_search_query(query), query)

        validate.assert_not_called()

    def test_https_url_query_uses_public_url_validator(self):
        with patch(
            "tools.tavily_client.validate_public_https_url",
            return_value="https://example.com/jobs",
        ) as validate:
            self.assertEqual(
                tavily_client._normalize_search_query("https://Example.COM./jobs"),
                "https://example.com/jobs",
            )

        validate.assert_called_once_with("https://Example.COM./jobs")

    def test_non_http_url_query_is_rejected(self):
        with self.assertRaises(UnsafeOutboundRequestError):
            tavily_client._normalize_search_query("file:///etc/passwd")


if __name__ == "__main__":
    unittest.main()
