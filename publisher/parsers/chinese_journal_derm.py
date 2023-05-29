from publisher.parsers.parser import PublisherParser


class ChineseJournalOfDermatology(PublisherParser):
    parser_name = "chinese_journal_of_dermatology"

    def is_publisher_specific_parser(self):
        return self.substr_in_citation_journal_title('中华皮肤科杂志')

    def authors_found(self):
        return bool(
            self.soup.select_one('meta[name=citation_authors][xml\:lang=en]'))

    def parse_authors(self):
        authors_tag = self.soup.select_one(
            'meta[name=citation_authors][xml\:lang=en]')
        names = authors_tag.attrs['content'].split(', ')
        authors = [
            {'name': name,
             'affiliations': [],
             'is_corresponding': None}
            for name in names
        ]
        if aff_tags := self.soup.select('#divPanelEn address li'):
            for aff_tag in aff_tags:
                for author in authors:
                    author['affiliations'].append(aff_tag.text.strip())

        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('.panel-body.line-height p'):
            return abs_tag.text
        return None

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
