from bs4 import NavigableString, Tag

from publisher.parsers.parser import PublisherParser


class F1000(PublisherParser):
    parser_name = "f1000_taylor"

    def is_publisher_specific_parser(self):
        return self.substr_in_citation_journal_title('f1000')

    def authors_found(self):
        return self.soup.select_one('.asset-authors')

    def parse_affiliations(self):
        affs_tag = self.soup.select_one('.author-affiliations')
        affs = {}
        current_num = None
        for tag in affs_tag.children:
            if isinstance(tag, Tag) and tag.name == 'sup':
                current_num = tag.text.strip()
            elif isinstance(tag, NavigableString) and len(tag.text) > 3:
                affs[current_num] = tag.text.strip()
        return affs

    def parse_authors(self):
        authors_tag = self.soup.select_one('.asset-authors')
        affs = self.parse_affiliations()
        authors = []
        for tag in authors_tag.children:
            if not hasattr(tag, 'name') or tag.name not in {'span', 'a'}:
                continue
            author = {'name': tag.text.strip(' ,'),
                      'affiliations': [],
                      'is_corresponding': None}
            if tag.name == 'a':
                author['is_corresponding'] = True
            _tag = tag.next_sibling
            while hasattr(_tag, 'name') and _tag.name == 'sup':
                author['affiliations'].append(affs[_tag.text.strip()])
                _tag = _tag.next_sibling
            authors.append(author)
        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('.abstract__content'):
            if not abs_tag.text.strip():
                if abs_tag := abs_tag.select_one('input[type=hidden]'):
                    return abs_tag.attrs['value']
            return abs_tag.text.strip()
        return None

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
