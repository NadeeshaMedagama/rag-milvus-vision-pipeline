"""URL content reader service implementation."""
import os
import re
from typing import List, Optional
from urllib.parse import urlparse, unquote
import requests

from interfaces import IVisionAnalyzer
from models.data_models import Document, DocumentType


class URLContentReader:
    """Service for reading and analyzing content from URLs."""

    # Supported image extensions
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'}

    # Common image hosting patterns
    IMAGE_URL_PATTERNS = [
        r'.*\.(png|jpg|jpeg|gif|bmp|webp|svg)(\?.*)?$',
        r'.*githubusercontent\.com.*',
        r'.*cloudinary\.com.*',
        r'.*imgur\.com.*',
        r'.*s3\.amazonaws\.com.*\.(png|jpg|jpeg|gif|bmp|webp|svg)',
    ]

    def __init__(self, vision_analyzer: IVisionAnalyzer = None, timeout: int = 30):
        """
        Initialize the URL content reader.

        Args:
            vision_analyzer: Optional vision analyzer for processing images
            timeout: Request timeout in seconds
        """
        self.vision_analyzer = vision_analyzer
        self.timeout = timeout

    def is_image_url(self, url: str) -> bool:
        """
        Check if a URL points to an image.

        Args:
            url: URL to check

        Returns:
            True if URL is an image, False otherwise
        """
        parsed = urlparse(url.lower())
        path = parsed.path

        # Check file extension
        ext = os.path.splitext(path)[1]
        if ext in self.IMAGE_EXTENSIONS:
            return True

        # Check against common patterns
        for pattern in self.IMAGE_URL_PATTERNS:
            if re.match(pattern, url.lower()):
                return True

        # Try to check content-type via HEAD request
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            content_type = response.headers.get('content-type', '')
            if content_type.startswith('image/'):
                return True
        except Exception:
            pass

        return False

    def read_url(self, url: str) -> Optional[Document]:
        """
        Read content from a URL.

        Args:
            url: URL to read

        Returns:
            Document object or None if URL cannot be processed
        """
        try:
            if self.is_image_url(url):
                return self._process_image_url(url)
            else:
                return self._process_text_url(url)
        except Exception as e:
            print(f"Error processing URL {url}: {str(e)}")
            return None

    def read_urls(self, urls: List[str]) -> List[Document]:
        """
        Read content from multiple URLs.

        Args:
            urls: List of URLs to read

        Returns:
            List of Document objects
        """
        documents = []
        for url in urls:
            try:
                document = self.read_url(url)
                if document:
                    documents.append(document)
                    print(f"Processed URL: {url}")
            except Exception as e:
                print(f"Error processing URL {url}: {str(e)}")

        print(f"Total URLs processed: {len(documents)}")
        return documents

    def _process_image_url(self, url: str) -> Document:
        """Process image URLs using Vision API."""
        if not self.vision_analyzer:
            return Document(
                content=f"Image URL: {url} (Vision API not configured)",
                file_path=url,
                repository_url="url",
                document_type=DocumentType.IMAGE,
                metadata={
                    "source": "url",
                    "file_type": "image",
                    "url": url
                }
            )

        # Use Vision API to analyze the image from URL
        summary = self.vision_analyzer.generate_summary_from_url(url)

        return Document(
            content=summary,
            file_path=url,
            repository_url="url",
            document_type=DocumentType.IMAGE,
            metadata={
                "source": "url",
                "file_type": "image",
                "url": url,
                "analyzed_by": "google_vision_api"
            }
        )

    def _process_text_url(self, url: str) -> Document:
        """Process text/HTML URLs."""
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            content_type = response.headers.get('content-type', '')

            # Handle different content types
            if 'text/html' in content_type:
                # Extract text from HTML
                content = self._extract_text_from_html(response.text, url)
            elif 'text/plain' in content_type or 'text/markdown' in content_type:
                content = response.text
            elif 'application/json' in content_type:
                content = f"JSON Content from {url}:\n{response.text}"
            else:
                content = response.text

            return Document(
                content=content,
                file_path=url,
                repository_url="url",
                document_type=DocumentType.MARKDOWN,  # Treat as markdown for chunking
                metadata={
                    "source": "url",
                    "file_type": "text",
                    "url": url,
                    "content_type": content_type
                }
            )
        except Exception as e:
            return Document(
                content=f"URL: {url}\nError fetching content: {str(e)}",
                file_path=url,
                repository_url="url",
                document_type=DocumentType.MARKDOWN,
                metadata={
                    "source": "url",
                    "file_type": "text",
                    "url": url,
                    "error": str(e)
                }
            )

    def _extract_text_from_html(self, html: str, url: str) -> str:
        """
        Extract readable text from HTML.

        Args:
            html: HTML content
            url: Source URL

        Returns:
            Extracted text content
        """
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()

            # Get title
            title = soup.title.string if soup.title else ""

            # Get main content
            # Try to find main content areas
            main_content = soup.find('main') or soup.find('article') or soup.find('body')

            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                text = soup.get_text(separator='\n', strip=True)

            # Clean up excessive whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = '\n'.join(lines)

            return f"Title: {title}\nURL: {url}\n\n{text}"

        except ImportError:
            # BeautifulSoup not available, return raw text with basic cleanup
            import re
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', html)
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return f"URL: {url}\n\n{text}"

    def extract_image_urls_from_text(self, text: str) -> List[str]:
        """
        Extract image URLs from text content.

        Args:
            text: Text content that may contain image URLs

        Returns:
            List of image URLs found
        """
        # Common URL patterns for images
        url_pattern = r'https?://[^\s<>"\']+?\.(?:png|jpg|jpeg|gif|bmp|webp|svg)(?:\?[^\s<>"\']*)?'

        # Also match markdown image syntax
        markdown_pattern = r'!\[.*?\]\((https?://[^\s\)]+)\)'

        urls = set()

        # Find direct URLs
        urls.update(re.findall(url_pattern, text, re.IGNORECASE))

        # Find markdown image URLs
        urls.update(re.findall(markdown_pattern, text))

        return list(urls)

    def process_urls_from_file(self, file_path: str) -> List[Document]:
        """
        Read URLs from a file and process them.

        Args:
            file_path: Path to file containing URLs (one per line)

        Returns:
            List of Document objects
        """
        try:
            with open(file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

            return self.read_urls(urls)
        except Exception as e:
            print(f"Error reading URLs from file {file_path}: {str(e)}")
            return []
