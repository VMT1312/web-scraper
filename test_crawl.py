import unittest
from crawl import (
    normalize_url,
    get_heading_from_html,
    get_first_paragraph_from_html,
)


class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_removes_http_scheme(self):
        input_url = "http://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_removes_trailing_slash(self):
        input_url = "https://www.boot.dev/blog/path/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_handles_root_domain(self):
        input_url = "https://www.boot.dev/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev"
        self.assertEqual(actual, expected)

    def test_normalize_url_http(self) -> None:
        input_url = "http://CRAWLER-TEST.com/path"
        actual = normalize_url(input_url)
        expected = "crawler-test.com/path"
        self.assertEqual(actual, expected)

    def test_get_h1(self):
        input_body = """<html>
  <body>
    <h1>Welcome to Boot.dev</h1>
    <main>
      <p>Learn to code by building real projects.</p>
      <p>This is the second paragraph.</p>
    </main>
  </body>
</html>"""
        actual = get_heading_from_html(input_body)
        expected = "Welcome to Boot.dev"
        self.assertEqual(actual, expected)

    def test_get_h2_fallback(self):
        input_body = """<html>
  <body>
    <h2>Welcome to Boot.dev</h2>
    <main>
      <p>Learn to code by building real projects.</p>
      <p>This is the second paragraph.</p>
    </main>
  </body>
</html>"""
        actual = get_heading_from_html(input_body)
        expected = "Welcome to Boot.dev"
        self.assertEqual(actual, expected)

    def test_get_no_heading(self):
        input_body = """<html>
  <body>
    <main>
      <p>Learn to code by building real projects.</p>
      <p>This is the second paragraph.</p>
    </main>
  </body>
</html>"""
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_with_multi_paragraphs(self):
        input_body = """<html>
  <body>
    <h1>Welcome to Boot.dev</h1>
    <main>
      <p>Learn to code by building real projects.</p>
      <p>This is the second paragraph.</p>
    </main>
  </body>
</html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Learn to code by building real projects."
        self.assertEqual(actual, expected)

    def test_get_no_paragraph(self):
        input_body = """<html>
  <body>
    <h1>Welcome to Boot.dev</h1>
    <main>
    </main>
  </body>
</html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
