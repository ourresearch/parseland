from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import EMAIL_RE


class Optica(PublisherParser):
    parser_name = 'optica'

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('optica.org')

    def authors_found(self):
        return bool(self.soup.select('#authorAffiliations'))

    @staticmethod
    def merge_authors(authors):
        authors_d = {}
        for author in authors:
            if author['name'] not in authors_d:
                authors_d[author['name']] = author
            else:
                authors_d[author['name']]['affiliations'].extend(
                    author['affiliations'])

        return list(authors_d.values())

    def parse_authors(self):
        meta_authors = self.parse_author_meta_tags()
        merged = self.merge_authors(meta_authors)
        for author in merged:
            for aff in author['affiliations']:
                if EMAIL_RE.search(aff):
                    author['is_corresponding'] = True
            author['affiliations'] = [aff for aff in author['affiliations'] if not EMAIL_RE.search(aff)]
        return merged

    def parse(self):
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract_meta_tags()}
