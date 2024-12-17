from urllib.parse import urlparse
import re


def get_base_url_from_soup(soup):
    """Extract base URL from BeautifulSoup object."""
    base_tag = soup.find('base', href=True)
    if base_tag:
        return base_tag['href']

    canonical = soup.find('link', {'rel': 'canonical', 'href': True})
    if canonical:
        return canonical['href']

    og_url = soup.find('meta', {'property': 'og:url', 'content': True})
    if og_url:
        return og_url['content']

    meta_url_tags = [
        ('meta', {'name': 'citation_url', 'content': True}),
        ('meta', {'name': 'dc.identifier', 'content': True}),
        ('meta', {'property': 'al:web:url', 'content': True}),
    ]

    for tag, attrs in meta_url_tags:
        meta = soup.find(tag, attrs)
        if meta:
            return meta['content']

    for meta in soup.find_all('meta', content=True):
        content = meta['content']
        if content.startswith(('http://', 'https://')):
            parsed = urlparse(content)
            return f"{parsed.scheme}://{parsed.netloc}"

    return None


def find_publisher(page_content, soup):
    """
    Find publisher information from HTML content, prioritizing specific publishers.

    Args:
        page_content: Raw HTML content
        soup: BeautifulSoup object

    Returns:
        str: Publisher name or None if not found
    """
    # Priority publishers we need to detect
    PRIORITY_PUBLISHERS = {
        'nejm': 'New England Journal of Medicine',
        'massmed': 'Massachusetts Medical Society',
        'uchicago': 'University of Chicago Press',
        'elsevier': 'Elsevier',
        'informa': 'Informa UK Limited',
        'oxford': 'Oxford University Press',
        'ieee': 'IEEE',
        'wiley': 'Wiley'
    }

    # Domain to publisher mapping
    DOMAIN_PUBLISHERS = {
        'nejm.org': 'New England Journal of Medicine',
        'massmed.org': 'Massachusetts Medical Society',
        'uchicago.edu': 'University of Chicago Press',
        'sciencedirect.com': 'Elsevier',
        'elsevier.com': 'Elsevier',
        'tandfonline.com': 'Informa UK Limited',
        'oxford.com': 'Oxford University Press',
        'oup.com': 'Oxford University Press',
        'ieee.org': 'IEEE',
        'wiley.com': 'Wiley',
        'onlinelibrary.wiley.com': 'Wiley'
    }

    # Common name variations
    PUBLISHER_ALIASES = {
        'nejm': 'New England Journal of Medicine',
        'mass medical': 'Massachusetts Medical Society',
        'massachusetts medical': 'Massachusetts Medical Society',
        'chicago': 'University of Chicago Press',
        'science direct': 'Elsevier',
        'taylor & francis': 'Informa UK Limited',
        'taylor and francis': 'Informa UK Limited',
        'oxford academic': 'Oxford University Press',
        'oup': 'Oxford University Press',
        'ieee xplore': 'IEEE',
        'institute of electrical': 'IEEE',
        'john wiley': 'Wiley'
    }

    def normalize_publisher(name: str):
        """Normalize publisher name using aliases."""
        if not name:
            return None

        name = name.lower().strip()

        # Check priority publishers first
        for key, value in PRIORITY_PUBLISHERS.items():
            if key in name:
                return value

        # Check aliases
        for alias, full_name in PUBLISHER_ALIASES.items():
            if alias in name:
                return full_name

        return None

    # 1. Check meta tags first
    meta_publisher_tags = [
        ('citation_publisher', 'name'),
        ('DC.Publisher', 'name'),
        ('publisher', 'name'),
        ('og:site_name', 'property'),
        ('citation_journal_publisher', 'name'),
        ('prism.publisher', 'name'),
    ]

    for name, attr_type in meta_publisher_tags:
        meta = soup.find('meta', {attr_type: name})
        if meta and meta.get('content'):
            if normalized := normalize_publisher(meta['content']):
                return normalized

    # 2. Check URL domain
    url = get_base_url_from_soup(soup)
    if url:
        domain = urlparse(url).netloc.lower()
        for known_domain, publisher in DOMAIN_PUBLISHERS.items():
            if known_domain in domain:
                return publisher

    # 3. Check specific HTML patterns
    publisher_html_patterns = [
        (r'nejm\.org|new\s*england\s*journal', 'New England Journal of Medicine'),
        (r'massmed\.org|mass\s*medical\s*society', 'Massachusetts Medical Society'),
        (r'press\.uchicago\.edu|chicago\s*press', 'University of Chicago Press'),
        (r'sciencedirect\.com|elsevier', 'Elsevier'),
        (r'tandfonline\.com|informa|taylor\s*&?\s*francis', 'Informa UK Limited'),
        (r'oxford\s*university\s*press|oup\.com', 'Oxford University Press'),
        (r'ieee\.org|ieee\s*xplore', 'IEEE'),
        (r'wiley\.com|wiley\s*online', 'Wiley'),
    ]

    for pattern, publisher in publisher_html_patterns:
        if re.search(pattern, page_content, re.IGNORECASE):
            return publisher

    # 4. Look for publisher in common locations
    publisher_indicators = [
        soup.find('a', string=re.compile(r'publisher', re.I)),
        soup.find('div', {'class': re.compile(r'publisher', re.I)}),
        soup.find('span', {'class': re.compile(r'publisher', re.I)}),
        soup.find(string=re.compile(r'published\s+by', re.I)),
        soup.find(string=re.compile(r'©.*\d{4}.*', re.I))
    ]

    for indicator in publisher_indicators:
        if indicator:
            text = indicator.get_text() if hasattr(indicator, 'get_text') else str(indicator)
            if normalized := normalize_publisher(text):
                return normalized

    return None


def clean_publisher_name(name: str) -> str:
    """Clean and normalize publisher name."""
    # Remove common suffixes
    name = re.sub(r'\s*\([^)]*\)', '', name)
    name = re.sub(r',?\s*(?:Inc|LLC|Ltd|Limited|Publishing|Publications|Publisher|Press)\s*$', '', name,
                  flags=re.IGNORECASE)

    # Remove extra whitespace
    name = ' '.join(name.split())

    # Common name mappings
    name_mappings = {
        'OUP': 'Oxford University Press',
        'CUP': 'Cambridge University Press',
        'T&F': 'Taylor & Francis',
        'IEEE': 'Institute of Electrical and Electronics Engineers',
        'ACS': 'American Chemical Society',
        'RSC': 'Royal Society of Chemistry',
        'IOP': 'Institute of Physics',
        'APS': 'American Physical Society',
        'SAGE': 'SAGE Publishing',
        'NPG': 'Nature Publishing Group',
    }

    # Apply mappings
    return name_mappings.get(name.upper(), name)