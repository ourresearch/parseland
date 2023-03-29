import re

from publisher.parsers.parser import PublisherParser


class UniversityOfCalifornia(PublisherParser):
    parser_name = 'university_of_california_press'

    AFF_PATTERN = re.compile(r'at ([a-zA-Z\d, ]+)')

    def is_publisher_specific_parser(self):
        return self.text_in_meta_og_site_name('University of California Press')

    def authors_found(self):
        return bool(self.soup.select('.al-author-name'))

    def parse_authors(self):
        author_tags = self.soup.select('.al-author-name')
        authors = []
        for author_tag in author_tags:
            name = author_tag.find('a').text
            author = {'name': name, 'affiliations': [],
                      'is_corresponding': None}
            if info_tag := author_tag.select_one('.al-author-info-wrap'):
                author['is_corresponding'] = bool(
                    info_tag.select('a[href*="mailto"]'))
                affs = self.__class__.AFF_PATTERN.findall(
                    info_tag.text)
                affs = [aff.strip('the ') for aff in affs]
                author['affiliations'] = affs
            authors.append(author)
        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('section.abstract p'):
            return abs_tag.text
        return None

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
