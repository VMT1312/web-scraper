import unittest
from crawl import (
    normalize_url,
    get_heading_from_html,
    get_first_paragraph_from_html,
    get_urls_from_html,
    get_images_from_html,
    extract_page_data,
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

    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = (
            '<html><body><a href="/doc.html"><span>Boot.dev</span></a></body></html>'
        )
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/doc.html"]
        self.assertEqual(actual, expected)

    def test_get_urls_err(self):
        input_url = "https://crawler-test.com"
        input_body = """
<html>
    <body>
        <a href="/valid-path">Valid Link</a>
        <a>No href attribute here</a>
        <a href="">Empty href</a>
    </body>
</html>
"""
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/valid-path"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="https://crawler-test.com/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_err(self):
        input_url = "https://crawler-test.com"
        input_body = """
<html>
    <body>
        <img src="/logo.png" alt="Valid image">
        <img alt="No src attribute here">
        <img src="" alt="Empty src">
    </body>
</html>
"""
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_absolute_paths_only(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Absolute Page</h1>
            <p>All URLs are fully-qualified.</p>
            <a href="https://crawler-test.com/about">About</a>
            <img src="https://crawler-test.com/logo.png" alt="Logo">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Absolute Page",
            "first_paragraph": "All URLs are fully-qualified.",
            "outgoing_links": ["https://crawler-test.com/about"],
            "image_urls": ["https://crawler-test.com/logo.png"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_mixed_absolute_and_relative_paths(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Mixed Paths</h1>
            <p>Relative and absolute links should both resolve.</p>
            <a href="/docs">Docs</a>
            <a href="https://crawler-test.com/contact">Contact</a>
            <img src="/images/banner.jpg" alt="Banner">
            <img src="https://crawler-test.com/assets/logo.png" alt="Logo">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Mixed Paths",
            "first_paragraph": "Relative and absolute links should both resolve.",
            "outgoing_links": [
                "https://crawler-test.com/docs",
                "https://crawler-test.com/contact",
            ],
            "image_urls": [
                "https://crawler-test.com/images/banner.jpg",
                "https://crawler-test.com/assets/logo.png",
            ],
        }
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
