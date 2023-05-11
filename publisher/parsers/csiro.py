import re

from bs4 import NavigableString, Tag

from publisher.parsers.parser import PublisherParser
import html

from publisher.parsers.utils import strip_prefix


class CSIRO(PublisherParser):
    parser_name = "csiro_publishing"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('publish.csiro.au')

    def authors_found(self):
        return bool(self.soup.select('.editors'))

    def parse_affs(self):
        affs = {}
        aff_tags = self.soup.select('#full-description p')
        for aff_tag in aff_tags:
            sup = aff_tag.find('sup')
            num = sup.text.strip()
            sup.decompose()
            aff_text = aff_tag.text.strip()
            affs[num] = aff_text
        return affs

    def parse_authors(self):
        authors_tag = self.soup.select_one('.editors')
        authors = []
        affs = self.parse_affs()
        for tag in authors_tag.children:
            if isinstance(tag, NavigableString):
                if name := strip_prefix('and', tag.text.strip(' .,')).strip(' .,'):
                    author = {'name': name,
                              'affiliations': [],
                              'is_corresponding': None}
                    authors.append(author)
            elif isinstance(tag, Tag) and tag.name == 'sup':
                num = tag.text.strip()
                aff = affs[num]
                if 'corresponding' in aff.lower():
                    authors[-1]['is_corresponding'] = True
                else:
                    authors[-1]['affiliations'].append(affs[num])
        return authors

    def mark_corresponding(self, authors):
        authors_tag = self.soup.select_one('.editors')
        current_name = None
        for child in authors_tag.children:
            if isinstance(child, NavigableString):
                if name := html.unescape(
                        re.sub('^and', '', child.text.strip()).strip(' .,')):
                    current_name = name
            elif isinstance(child,
                            Tag) and child.name == 'sup' and child.text.strip() == '*':
                for author in authors:
                    if author['name'] == current_name:
                        author['is_corresponding'] = True
        return authors

    def parse(self):
        authors = self.parse_author_meta_tags()
        authors = self.mark_corresponding(authors)
        if not any([author['is_corresponding'] for author in authors]):
            authors = self.parse_authors()

        return {'authors': authors,
                'abstract': self.parse_abstract_meta_tags()}
