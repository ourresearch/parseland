from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import logging
import re
import os
from base64 import b64decode

import requests

from find_shared import get_base_url_from_soup

logger = logging.getLogger(__name__)


@dataclass
class PdfLink:
    href: str
    anchor: str
    source: str = None
    error: str = None


def find_pdf_link(soup):
    """find a single potential PDF link in BeautifulSoup object, prioritizing meta tags."""
    try:
        base_url = get_base_url_from_soup(soup)
        print(f"Base URL: {base_url}")

        # try meta tags first
        meta_pdf = get_pdf_from_meta(soup)
        if meta_pdf:
            print(f"Meta PDF: {meta_pdf}")
            if base_url:
                meta_pdf.href = urljoin(base_url, meta_pdf.href)
                meta_pdf.href = transform_pdf_url(meta_pdf.href)
            if is_valid_pdf_link(meta_pdf.href):
                if validate_pdf(meta_pdf):
                    return meta_pdf
        else:
            print(f"No meta PDF")

        # try JavaScript next
        js_pdf = get_pdf_from_javascript(str(soup))
        if js_pdf:
            print(f"JS PDF: {js_pdf}")
            if base_url:
                js_pdf.href = urljoin(base_url, js_pdf.href)
                js_pdf.href = transform_pdf_url(js_pdf.href)
            if is_valid_pdf_link(js_pdf.href):
                if validate_pdf(js_pdf):
                    return js_pdf
        else:
            print(f"No JS PDF")

        # try content links
        for link in get_pdf_links_from_content(soup):
            if base_url:
                link.href = urljoin(base_url, link.href)
                link.href = transform_pdf_url(link.href)
            if is_valid_pdf_link(link.href):
                if validate_pdf(link):
                    return link
        print(f"No content PDF")

        for button_link in get_pdf_links_from_buttons(soup):
            if base_url:
                button_link.href = urljoin(base_url, button_link.href)
                button_link.href = transform_pdf_url(button_link.href)
            if is_valid_pdf_link(button_link.href):
                if validate_pdf(button_link):
                    return button_link

    except Exception as e:
        logger.error(f"Error finding PDF link: {str(e)}")

    return None


def get_pdf_from_meta(soup):
    """Extract PDF link from meta tags."""
    for meta in soup.find_all('meta'):
        if meta.get('name') == 'citation_pdf_url' or meta.get('property') == 'citation_pdf_url':
            if 'content' in meta.attrs:
                return PdfLink(
                    href=meta['content'],
                    anchor="<meta citation_pdf_url>",
                    source="meta"
                )
    return None


def get_pdf_from_javascript(html_content):
    """Extract PDF link from JavaScript variables."""
    patterns = [
        r'"pdfUrl":"(.*?)"',
        r'"exportPdfDownloadUrl": ?"(.*?)"',
        r'"downloadPdfUrl":"(.*?)"',
        r'"fullTextPdfUrl":"(.*?)"'
    ]

    for pattern in patterns:
        matches = re.findall(pattern, html_content)
        if matches:
            href = matches[0]
            if '\\u' in href:
                try:
                    href = href.encode().decode('unicode-escape')
                except UnicodeDecodeError:
                    continue
            return PdfLink(
                href=href,
                anchor=pattern.split('"')[1],
                source="javascript"
            )
    return None


def get_pdf_links_from_content(soup):
    """Extract PDF links from BeautifulSoup content."""
    pdf_links = []

    bad_sections = [
        "div.relatedItem",
        "div.citedBySection",
        "div.references",
        "div#supplementary-material",
        "div.table-of-content",
        "div.footnotes",
        "section#article-references",
    ]

    for section in soup.select(', '.join(bad_sections)):
        section.decompose()

    for link in soup.find_all('a', href=True):
        href = link['href']

        if has_bad_pattern(href):
            continue

        anchor_text = link.get_text().strip().lower()
        if has_bad_anchor_word(anchor_text):
            continue

        if is_pdf_link(link):
            pdf_links.append(PdfLink(
                href=href,
                anchor=anchor_text or '<no text>',
                source="content"
            ))

    return pdf_links


def get_pdf_links_from_buttons(soup):
    """Extract PDF links from button elements."""
    pdf_links = []
    for button in soup.find_all('button', {'onclick': True}):
        onclick = button['onclick']
        match = re.search(r"(https?:\/\/[^\s'\"]+\.pdf)", onclick)
        if match:
            href = match.group(1)
            anchor_text = button.get_text().strip() or '<button>'
            pdf_links.append(PdfLink(
                href=href,
                anchor=anchor_text,
                source="button"
            ))
    return pdf_links



def is_pdf_link(link):
    """Check if link is likely a PDF download with stricter validation."""
    href = link['href'].lower()
    anchor_text = link.get_text().strip().lower()

    # Direct PDF file links are most reliable
    if href.endswith('.pdf'):
        return True

    # Check for PDF extensions in paths
    path_components = urlparse(href).path.lower().split('/')
    if any(comp.endswith('.pdf') for comp in path_components):
        return True

    # Check PDF indicators in query parameters
    if 'pdf' in href and any(param in href for param in [
        'download=',
        'format=pdf',
        'type=pdf',
        'mimeType=pdf',
        '/pdf/',
        'action=download'
    ]):
        return True

    # If "PDF" is in anchor text, require additional download indicators
    if "pdf" in anchor_text:
        download_indicators = [
            "download",
            "télécharger",
            "get",
            "view",
            "access",
            "full text"
        ]
        return any(indicator in anchor_text for indicator in download_indicators)

    # Check for download buttons/links with PDF context
    if any(text in anchor_text for text in ["download", "télécharger"]):
        # Must have PDF context either in href or nearby elements
        has_pdf_context = (
                'pdf' in href or
                any('pdf' in img.get('src', '').lower() for img in link.find_all('img')) or
                any('pdf' in cls for cls in link.get('class', [])) or
                link.find_parent(class_=lambda x: x and 'pdf' in x.lower())
        )
        return has_pdf_context and "citation" not in anchor_text

    # Check for PDF-specific icons
    pdf_icons = [
        "fa-file-pdf",
        "fa-pdf",
        "pdf-icon",
        "icon-pdf"
    ]
    if any(cls in ' '.join(link.get('class', [])) for cls in pdf_icons):
        return True

    # Check parent elements for PDF context
    parent_pdf_classes = [
        "pdf-download",
        "download-pdf",
        "pdf-options",
        "pdf-container"
    ]
    for parent in link.parents:
        if any(cls in ' '.join(parent.get('class', [])) for cls in parent_pdf_classes):
            return True

    return False


def has_bad_pattern(href):
    """Check if URL contains patterns indicating it's not a valid PDF link."""
    bad_patterns = [
        # Supplementary materials
        '/suppl_file/',
        'supplementary+file',
        '_supplement',
        '/Appendix',
        'supinfo.pdf',
        'supplementary-materials',

        # Navigation/UI elements
        '/faq',
        'figures',
        '_toc_',
        'download_statistics',

        # Archives/compressed files
        '.zip',
        '.tar.',
        '.gz',

        # Sample/example content
        '/samples/',
        'example.pdf',

        # Purchase/subscription
        'showsubscriptions',
        'price-lists',
        'libraryrequestform',
        'pricing.pdf',

        # Administrative
        'content_policy.pdf',
        'BookTOC.pdf',
        'BookBackMatter.pdf',
        'Deposit_Agreement',
        'ethicspolicy.pdf',
        'TermsOfUse.pdf',
        'license_agreement.pdf',
        'authors_guide.pdf',

        # Other
        'first-page.pdf',
        'preview.pdf'
    ]
    return any(pattern in href.lower() for pattern in bad_patterns)


def has_bad_anchor_word(anchor_text):
    """Check if anchor text contains words indicating it's not a valid PDF link."""
    bad_words = [
        # Supplementary content
        'supplement',
        'appendix',
        'supporting information',
        'additional files',

        # Figures/media
        'figure',
        'table',
        'video',
        'image',

        # Administrative
        'faq',
        'help',
        'checklist',
        'guidelines',
        'instructions',
        'policy',
        'agreement',
        'terms',

        # Navigation
        'abstract',
        'toc',
        'contents',
        'index',

        # Statistics
        'download statistics',
        'citation statistics',
        'metrics',

        # Other
        'purchase',
        'subscribe',
        'preview'
    ]
    return any(word in anchor_text.lower() for word in bad_words)


def transform_pdf_url(url):
    """Transform PDF URLs based on publisher-specific patterns."""
    if not url:
        return url

    # Recyt
    if re.match(r'https?://recyt\.fecyt\.es/index\.php/EPI/article/view/', url):
        url = url.replace('/article/view/', '/article/download/')

    # MIT Press Journals and Chicago
    if (re.match(r'https?://(www.)?mitpressjournals\.org/doi/full/10\.+', url) or
            re.match(r'https?://(www.)?journals\.uchicago\.edu/doi/full/10\.+', url)):
        url = url.replace('/doi/full/', '/doi/pdf/')

    # ASCO
    if re.match(r'https?://(www.)?ascopubs\.org/doi/full/10\.+', url):
        url = url.replace('/doi/full/', '/doi/pdfdirect/')

    # AHA Journals
    if re.match(r'https?://(www\.)?ahajournals\.org/doi/reader/10\..+', url):
        url = url.replace('/doi/reader/', '/doi/pdf/')

    # SAGE
    if re.match(r'https?://(www\.)?journals.sagepub.com/doi/reader/10\..+', url):
        url = url.replace('/doi/reader/', '/doi/pdf/')

    # Taylor & Francis
    if re.match(r'https?://(www\.)?tandfonline.com/doi/epdf/10\..+', url):
        url = url.replace('/doi/epdf/', '/doi/pdf/')

    # American Journal of Roentgenology
    if re.match(r'https?://(www\.)?ajronline.org/doi/epdf/10\..+', url):
        url = url.replace('/doi/epdf/', '/doi/pdf/')

    # ACS Publications
    if re.match(r'https?://(www\.)?pubs.acs.org/doi/epdf/10\..+', url):
        url = url.replace('/doi/epdf/', '/doi/pdf/')

    # Royal Society Publishing
    if re.match(r'https?://(www\.)?royalsocietypublishing.org/doi/epdf/10\..+', url):
        url = url.replace('/doi/epdf/', '/doi/pdf/')

    # Wiley
    if re.match(r'https?://(www\.)?onlinelibrary.wiley.com/doi/epdf/10\..+', url):
        url = url.replace('/epdf/', '/pdfdirect/')
    url = re.sub(r'(onlinelibrary\.wiley\.com/doi/)pdf(/.+)', r'\1pdfdirect\2', url)

    # Healio
    if re.match(r'https?://(journals\.)?healio.com/doi/epdf/10\..+', url):
        url = url.replace('/doi/epdf/', '/doi/pdf/')

    # RSNA
    if re.match(r'https?://(pubs\.)?rsna.org/doi/epdf/10\..+', url):
        url = url.replace('/doi/epdf/', '/doi/pdf/')

    # General epdf to pdf conversion
    if '/epdf/' in url:
        url = url.replace('/epdf/', '/pdf/')

    # Science Direct
    if url.startswith('https://www.sciencedirect.com/science/article/pii/'):
        url = url.replace('/article/pii/', '/article/am/pii/')
    url = re.sub(r'(science)direct.com/science/article/pii/(.*?)/pdf\?md5=.*?-main\.pdf$',
                 r'\1direct.com/science/article/pii/\2/pdfft', url)

    # Nature
    if '/articles/' in url and url.endswith('.pdf'):
        url = url.replace('.pdf', '_reference.pdf')

    # IEEE
    url = re.sub(r'(ieeexplore\.ieee\.org/stamp/stamp\.jsp\?tp=&arnumber=\d+)',
                 r'\1&tag=1', url)

    # JSTOR
    url = re.sub(r'(jstor\.org/stable/)(.*?)$',
                 r'\1pdfplus/\2.pdf', url)

    return url


def is_valid_pdf_link(url):
    """Check if PDF link is valid."""
    bad_domains = [
        'exlibrisgroup.com',
        'citeseerx.ist.psu.edu',
        'deepdyve.com',
        'researchgate.net',
        'academia.edu'
    ]

    parsed_url = urlparse(url)
    if any(domain in parsed_url.netloc.lower() for domain in bad_domains):
        return False

    if 'temporary' in url.lower() or 'temp' in url.lower():
        return False

    if 'expired' in url.lower():
        return False

    return True


def validate_pdf(pdf_link):
    """Validate PDF link using Zyte API, status code, and content type."""
    if not pdf_link:
        return False

    href = pdf_link.href.lower()

    # Special cases that can be directly trusted
    trusted_direct_patterns = [
        'onlinelibrary.wiley.com/pdfdirect',
        'onlinelibrary.wiley.com/doi/pdfdirect',
        '/article/download/',
        '/index.php/',
        '/download/'
    ]
    if any(pattern in href for pattern in trusted_direct_patterns):
        return True

    try:
        use_zyte_api = ["oup.com", "ieee.org", "ajog.org", "journals.sagepub.com", "journals.uchicago.edu"]
        if any(domain in href for domain in use_zyte_api) and validate_with_zyte_api(href):
            return True

        # Use HEAD request to check the link
        response = requests.head(href, allow_redirects=True, timeout=5)

        # Check response status code
        if response.status_code != 200:
            logger.warning(f"PDF link ({pdf_link.href}) returned status code {response.status_code}")
            return False

        # Validate content type
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/pdf' in content_type:
            return True

        # Validate content start (fallback to GET if necessary)
        with requests.get(href, stream=True, timeout=10, headers={'User-Agent': 'Mozilla/5.0'}) as get_response:
            get_response.raise_for_status()  # Raise an exception for non-2xx responses
            content_start = get_response.raw.read(5)
            if content_start == b'%PDF-':
                return True

        logger.warning(f"PDF link ({pdf_link.href}) does not appear to be a valid PDF.")
        return False

    except Exception as e:
        logger.error(f"Error validating PDF link: {str(e)}")

    # Fallback to trusted patterns if Zyte validation fails
    trusted_fallback_patterns = [
        r'onlinelibrary\.wiley\.com/doi/pdfdirect/',
        r'science\.org/doi/pdf/',
        r'springer\.com/content/pdf/',
        r'tandfonline\.com/doi/pdf/'
    ]
    return any(re.search(pattern, pdf_link.href) for pattern in trusted_fallback_patterns)


def validate_with_zyte_api(url):
    """Validate PDF link using Zyte API."""
    print("Validating PDF link with Zyte API.")
    zyte_api_key = os.getenv("ZYTE_API_KEY")
    api_response = requests.post(
        "https://api.zyte.com/v1/extract",
        auth=(zyte_api_key, ""),
        json={
            "url": url,
            "httpResponseBody": True
        },
    )
    http_response_body: bytes = b64decode(api_response.json()["httpResponseBody"])
    if http_response_body.startswith(b'%PDF'):
        return True