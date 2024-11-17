from typing import Optional
import re

from find_shared import get_base_url_from_soup, find_publisher


def check_access_type(page_content: str, soup) -> Optional[str]:
    """
    Check if article has bronze or hybrid access.
    Returns 'bronze', 'hybrid', or None.

    Args:
        page_content: HTML content
        soup: BeautifulSoup object of the page

    Returns:
        str: 'bronze', 'hybrid', or None if neither
    """
    # Check publisher-specific patterns first
    if publisher_access := check_publisher_patterns(page_content, soup):
        return publisher_access

    # Check bronze patterns
    if check_bronze_patterns(page_content, soup):
        return 'bronze'

    # Check hybrid patterns
    if check_hybrid_patterns(page_content, soup):
        return 'hybrid'

    return None


def check_bronze_patterns(page_content: str, soup) -> bool:
    """Check if page matches any bronze access patterns."""
    url = get_base_url_from_soup(soup)
    bronze_url_patterns = [
        ('sciencedirect.com/', '<div class="OpenAccessLabel">open archive</div>'),
        ('sciencedirect.com/', r'<span[^>]*class="[^"]*pdf-download-label[^"]*"[^>]*>Download PDF</span>'),
        ('onlinelibrary.wiley.com', '<div[^>]*class="doi-access"[^>]*>Free Access</div>'),
        ('openedition.org', r'<span[^>]*id="img-freemium"[^>]*></span>'),
        ('microbiologyresearch.org', r'<span class="accesstext">(?:</span>)?Free'),
        ('journals.lww.com', r'<li[^>]*id="[^"]*-article-indicators-free"[^>]*>'),
        ('ashpublications.org', r'<i[^>]*class="[^"]*icon-availability_free'),
        ('academic.oup.com', r'<i[^>]*class="[^"]*icon-availability_free'),
        ('degruyter.com/', '<span>Free Access</span>'),
        ('degruyter.com/', 'data-accessrestricted="false"'),
    ]

    for url_pattern, html_pattern in bronze_url_patterns:
        if url_pattern in url.lower():
            if re.findall(html_pattern, page_content, re.IGNORECASE | re.DOTALL):
                return True
    return False


def check_hybrid_patterns(page_content: str, soup) -> bool:
    """Check if page matches any hybrid access patterns."""
    url = get_base_url_from_soup(soup)
    hybrid_url_patterns = [
        ('projecteuclid.org/', '<strong>Full-text: Open access</strong>'),
        ('sciencedirect.com/', '<div class="OpenAccessLabel">open access</div>'),
        ('journals.ametsoc.org/', r'src="/templates/jsp/_style2/_ams/images/access_free\.gif"'),
        ('apsjournals.apsnet.org', r'src="/products/aps/releasedAssets/images/open-access-icon\.png"'),
        ('psychiatriapolska.pl', 'is an Open Access journal:'),
        ('journals.lww.com', '<span class="[^>]*ejp-indicator--free'),
        ('iospress.com', r'<img[^>]*src="[^"]*/img/openaccess_icon.png[^"]*"[^>]*>'),
        ('cambridge.org/', r'<span[^>]*class="open-access"[^>]*>Open access</span>'),
    ]

    for url_pattern, html_pattern in hybrid_url_patterns:
        if url_pattern in url.lower():
            if re.findall(html_pattern, page_content, re.IGNORECASE | re.DOTALL):
                return True
    return False


def check_publisher_patterns(page_content: str, soup) -> Optional[str]:
    """Check publisher-specific patterns."""
    publisher = find_publisher(page_content, soup)
    print(f"Publisher: {publisher}")
    publisher_patterns = [
        # Bronze patterns
        ("New England Journal of Medicine", '<meta content="yes" name="evt-free"', "bronze"),
        ("Massachusetts Medical Society", '<meta content="yes" name="evt-free"', "bronze"),
        ("University of Chicago Press", r'<img[^>]*class="[^"]*accessIconLocation', "bronze"),
        ("Elsevier", r'<span[^>]*class="[^"]*article-header__access[^"]*"[^>]*>Open Archive</span>', "bronze"),

        # Hybrid patterns
        ("Informa UK Limited", "/accessOA.png", "hybrid"),
        ("Oxford University Press", "<i class='icon-availability_open'", "hybrid"),
        ("IEEE", r'"isOpenAccess":true', "hybrid"),
        ("IEEE", r'"openAccessFlag":"yes"', "hybrid"),
        ("Wiley", r'<div[^>]*class="doi-access"[^>]*>Open Access</div>', "hybrid")
    ]

    for pub, pattern, access_type in publisher_patterns:
        if publisher and publisher.lower() in pub.lower():
            if re.findall(pattern, page_content, re.IGNORECASE | re.DOTALL):
                return access_type
    return None
