from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from typing import Optional
import logging

from find_shared import get_base_url_from_soup

logger = logging.getLogger(__name__)

# License patterns dictionary
LICENSE_PATTERNS = {
    'cc-by': [
        r'creative\s*commons\s*attribution',
        r'cc\s*by\b',
    ],
    'cc-by-nc': [
        r'creative\s*commons\s*attribution\s*-?\s*non\s*commercial',
        r'cc\s*by\s*-?\s*nc\b',
    ],
    'cc-by-sa': [
        r'creative\s*commons\s*attribution\s*-?\s*share\s*alike',
        r'cc\s*by\s*-?\s*sa\b',
    ],
    'cc-by-nc-sa': [
        r'creative\s*commons\s*attribution\s*-?\s*non\s*commercial\s*-?\s*share\s*alike',
        r'cc\s*by\s*-?\s*nc\s*-?\s*sa\b',
    ],
    'cc-by-nc-nd': [
        r'creative\s*commons\s*attribution\s*-?\s*non\s*commercial\s*-?\s*no\s*derivatives',
        r'cc\s*by\s*-?\s*nc\s*-?\s*nd\b',
    ],
}

# Text patterns to search for license info
TEXT_PATTERNS = [
    r"(creativecommons.org/licenses/[a-z\-]+)",
    r"distributed under the terms (.*?) which permits",
    r"This is an open access article under the terms (.*?) which permits",
    r"This is an open-access article distributed under the terms (.*?), where it is permissible",
    r"This is an open access article published under (.*?) which permits",
    r'<div class="openAccess-articleHeaderContainer(.*?)</div>',
    r'this article is published under the creative commons (.*?) licence',
    r'This work is licensed under a Creative Commons (.*?) which permits',
    r'licensed under a Creative Commons (.*?) License',
    r'under Creative Commons (.*?) license',
    r'distributed under a Creative Commons (.*?) License',
    r'текст статьи',
    r'Available under( the)? Creative Commons (.*?) License',
    r'This is an Open Access article distributed under (.*?) license',
]


def find_license_in_html(page_content: str) -> Optional[str]:
    """Find license information in HTML content using BeautifulSoup."""
    try:
        soup = BeautifulSoup(page_content, 'html.parser')

        # Check if we should trust this publisher
        if not _trust_publisher_license(soup):
            logger.info("Publisher not trusted for license information")
            return None

        # Get the potential text that might contain license info
        license_text = page_potential_license_text(page_content)
        if not license_text:
            return None

        # First look for Creative Commons license URLs
        cc_url_match = re.search(r'creativecommons\.org/licenses/([a-z-]+)', license_text, re.IGNORECASE)
        if cc_url_match:
            license_code = cc_url_match.group(1)
            if license_code:
                return license_code

        # Then look for license text patterns
        for pattern in TEXT_PATTERNS:
            matches = re.findall(pattern, license_text, re.IGNORECASE)
            if matches:
                normalized_license = find_normalized_license(matches[0])
                if normalized_license:
                    return normalized_license
                return "unspecified-oa"

        # Check for specific publisher license patterns
        publisher_license = check_publisher_specific_licenses(soup, license_text)
        if publisher_license:
            return publisher_license

        return None

    except Exception as e:
        logger.error(f"Error finding license: {str(e)}")
        return None


def check_publisher_specific_licenses(soup: BeautifulSoup, license_text: str) -> Optional[str]:
    """Check for publisher-specific license indicators."""
    base_url = get_base_url_from_soup(soup)
    if not base_url:
        return None

    hostname = urlparse(base_url).hostname or ''

    # Publisher-specific patterns
    publisher_patterns = [
        (r'sciencedirect\.com/', r'<div class="OpenAccessLabel">open access</div>', 'unspecified-oa'),
        (r'projecteuclid\.org/', r'<strong>Full-text: Open access</strong>', 'unspecified-oa'),
        (r'journals\.ametsoc\.org/', r'src="/templates/jsp/_style2/_ams/images/access_free\.gif"', 'unspecified-oa'),
        (r'cambridge\.org/', r'<span[^>]*class="open-access"[^>]*>Open access</span>', 'unspecified-oa'),
        (r'degruyter\.com/', r'<span>Open Access</span>', 'unspecified-oa'),
    ]

    for url_pattern, text_pattern, license_type in publisher_patterns:
        if re.search(url_pattern, hostname, re.IGNORECASE):
            if re.search(text_pattern, license_text, re.IGNORECASE):
                return license_type

    # Special handling for T&F license tab
    if re.match(r'^https?://(?:www\.)?tandfonline\.com/doi/full/(10\..+)', base_url, re.IGNORECASE):
        tf_license = check_tandfonline_license(base_url)
        if tf_license:
            return tf_license

    return None


def check_tandfonline_license(url: str) -> Optional[str]:
    """Check T&F license tab for license info."""
    try:
        if url_match := re.match(r'^https?://(?:www\.)?tandfonline\.com/doi/full/(10\..+)', url, re.IGNORECASE):
            license_tab_url = f'https://www.tandfonline.com/action/showCopyRight?doi={url_match.group(1)}'
            logger.info(f'Checking T&F license tab: {license_tab_url}')

            # Note: You'll need to implement the actual HTTP request and parsing
            # This is just the structure
            return None
    except Exception as e:
        logger.error(f"Error checking T&F license: {str(e)}")
        return None


def page_potential_license_text(page: str) -> Optional[str]:
    """Get text that might contain license info using BeautifulSoup."""
    try:
        soup = BeautifulSoup(page, 'html.parser')

        # Additional sections to remove that might have false positives
        selectors_to_remove = [
            "div.view-pnas-featured",
            "div.references",
            "div.footnotes",
            "div.supplementary",
            "div.table-of-content",
            "div.author-notes",
            "div.related-content",
            ".citation-references",
            # Adding missing sections from original
            "div.citedBySection",
            "div#supplementary-material",
            "section#article-references",
            "div.relatedItem",
            "div.table-of-content",
        ]

        for selector in selectors_to_remove:
            for element in soup.select(selector):
                element.decompose()

        # Get specific sections that often contain license info
        license_sections = []

        # Check meta tags first
        meta_tags = ['dc.rights', 'prism.copyright', 'citation_license',
                     'dc.accessRights', 'dc.rights.license']  # Added missing meta tags
        license_meta = soup.find('meta', {'name': meta_tags})
        if license_meta and license_meta.get('content'):
            license_sections.append(license_meta['content'])

        # Extended list of license containers
        license_containers = soup.select(
            'div.license, '
            'div.permissions, '
            'div.copyright-notice, '
            'div.article-license, '
            'section.license, '
            'div[id*="license"], '
            'div[class*="license"], '
            'div[id*="copyright"], '
            'div[class*="copyright"], '
            # Adding missing containers
            'div.openAccessLabel, '
            'div.article-header__access, '
            'span.pdf-notice'
        )

        for container in license_containers:
            license_sections.append(container.get_text(' ', strip=True))

        # Combine and clean text
        if license_sections:
            combined_text = ' '.join(license_sections)
            return ' '.join(combined_text.split())

        # If no specific sections found, try full page content
        main_content = soup.find(['main', 'article'])
        if main_content:
            return main_content.get_text(' ', strip=True)

        body = soup.find('body')
        if body:
            return body.get_text(' ', strip=True)

        return page

    except Exception as e:
        logger.error(f"Error parsing HTML: {str(e)}")
        return page


def find_normalized_license(text: str) -> Optional[str]:
    """
    Convert license text to a normalized format.

    Args:
        text: License text to normalize

    Returns:
        str: Normalized license string or None
    """
    text = text.lower().strip()

    # Check for Creative Commons URL pattern first
    cc_url_match = re.search(r'creativecommons\.org/licenses/([a-z-]+)', text)
    if cc_url_match:
        license_code = cc_url_match.group(1)
        if license_code in LICENSE_PATTERNS:
            return license_code

    # Check each license pattern
    for normalized_license, patterns in LICENSE_PATTERNS.items():
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
            return normalized_license

    return None


def _trust_publisher_license(soup: BeautifulSoup) -> bool:
    """
    Check if publisher's license info should be trusted.

    Args:
        soup: BeautifulSoup object

    Returns:
        bool: Whether to trust the publisher
    """
    base_url = get_base_url_from_soup(soup)
    if not base_url:
        return True

    hostname = urlparse(base_url).hostname
    if not hostname:
        return True

    # Publishers known to have unreliable license info
    untrusted_hosts = {
        'indianjournalofmarketing.com',
        'rnajournal.cshlp.org',
        'press.umich.edu',
        'genome.cshlp.org',
        'medlit.ru',
        'journals.eco-vector.com',
        'alife-robotics.co.jp',
        'molbiolcell.org',
        'jcog.com.tr',
        'aimsciences.org',
        'berghahnjournals.com',
        'ojs.ual.es',
    }

    # Special case for rupress.org
    if hostname.endswith('rupress.org'):
        volume_match = re.findall(r'rupress\.org/jcb/[^/]+/(\d+)', base_url)
        try:
            return bool(volume_match and int(volume_match[0]) < 217)
        except ValueError:
            return False

    return not any(hostname.endswith(host) for host in untrusted_hosts)
