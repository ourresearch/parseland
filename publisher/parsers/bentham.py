from bs4 import BeautifulSoup

from publisher.parsers.parser import PublisherParser


class BenthamScience(PublisherParser):
    parser_name = "bentham_science"

    def is_publisher_specific_parser(self):
        return len(self.soup.select('a[href*="bentham"]')) >= 5

    def authors_found(self):
        return bool(self.soup.find(
            lambda tag: tag.name == 'span' and 'l-h-3' in tag.get('class',
                                                                  '') and tag.find(
                'strong') and 'author' in tag.find('strong').text.lower()))

    def parse_authors(self):
        authors_tag = self.soup.find(
            lambda tag: tag.name == 'span' and 'l-h-3' in tag.get('class',
                                                                  '') and tag.find(
                'strong') and 'author' in tag.find('strong').text.lower())
        authors = []
        for author_tag in authors_tag.select('a'):
            name = author_tag.text.strip().strip('*')
            if not name:
                continue
            affs_html = author_tag['data-content'] if 'data-content' in author_tag.attrs else ''
            affs_soup = BeautifulSoup(affs_html, parser='lxml')
            affs = [tag.text.strip() for tag in affs_soup.find_all('li')]
            is_corresponding = '*' in author_tag.text
            authors.append({
                'name': name,
                'affiliations': affs,
                'is_corresponding': is_corresponding
            })
        return authors

    def parse_abstract(self):
        abs_tags = self.soup.select('#abstract p')
        return '\n'.join([tag.text.strip() for tag in abs_tags])

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
