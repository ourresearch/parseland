from publisher.parsers.nejm_unformatted_utils import \
    parse_affs_by_unformatted_text
from publisher.parsers.parser import PublisherParser


class Radiology(PublisherParser):
    parser_name = "rsna"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('rsna.org')

    def authors_found(self):
        return bool(self.parse_abstract_meta_tags())

    def parse_authors(self):
        authors = self.parse_author_meta_tags()
        if unformatted_affs_tag := self.soup.select_one('ul.affList li'):
            return parse_affs_by_unformatted_text(authors, unformatted_affs_tag.text.strip())
        return authors

    def parse(self):
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract_meta_tags()}


