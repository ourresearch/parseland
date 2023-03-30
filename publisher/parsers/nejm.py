from publisher.parsers.parser import PublisherParser


class NewEnglandJournalOfMedicine(PublisherParser):
    parser_name = 'nejm'

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('nejm.org')

    def authors_found(self):
        return bool(self.soup.select('ul.m-article-header__authors'))

    def parse_abstract(self):
        return '\n'.join(
            [tag.text for tag in self.soup.select('section#article_body p')])

    def parse(self):
        return {'authors': self.parse_author_meta_tags(),
                'abstract': self.parse_abstract()}
