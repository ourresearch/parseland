import re

from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import strip_prefix


class UniversityOfCalifornia(PublisherParser):
    parser_name = 'university_of_california_press'

    AFF_PATTERN = re.compile(r'at ([a-zA-Z\d, .]+)')

    def is_publisher_specific_parser(self):
        return self.text_in_meta_og_site_name('University of California Press')

    def authors_found(self):
        return bool(self.soup.select('.al-author-name'))

    # This should be handled by changing AFF_REGEX but couldn't figure out how to do it properly
    @staticmethod
    def format_aff(aff):
        final = ''
        aff = strip_prefix('the ', aff)
        split = aff.split('.')
        for i, part in enumerate(split):
            if i != len(split) - 1:
                part = part + '.'
                final += part
            # len(split) <= 3 to accomodate strings like "St.", "Dr." etc
            elif len(part) <= 3 or len(split) == 1:
                final += part
        return final.strip('.')

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
                # affs = self.__class__.AFF_PATTERN.findall(
                #     info_tag.text)
                # affs = [self.format_aff(aff) for aff in affs]
                # author['affiliations'] = affs
            authors.append(author)
        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('section.abstract p'):
            return abs_tag.text
        return None

    def parse(self):
        meta_authors = self.parse_meta_tags()
        body_authors = self.parse_authors()
        for b_author in body_authors:
            if b_author['is_corresponding']:
                for author in meta_authors:
                    split = author['name'].split(',')
                    if all([part in b_author['name'] for part in split]):
                        author['is_corresponding'] = True
        return {'authors': self.parse_meta_tags(),
                'abstract': self.parse_abstract()}
