from publisher.parsers.parser import PublisherParser


class Brill(PublisherParser):
    parser_name = "brill"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('brill.com')

    def authors_found(self):
        return bool(self.soup.select('div.contributor-line'))

    def parse_authors(self):
        authors_block = self.soup.select_one('div.contributor-line')
        author_tags = authors_block.select('.contributor-details')
        authors = []
        for author_tag in author_tags:
            name = author_tag.select_one('span.contributor-details-link').text
            affiliations = [aff.text for aff in
                            author_tag.select('span.institution')]
            is_corresponding = None
            authors.append({'name': name,
                            'affiliations': affiliations,
                            'is_corresponding': is_corresponding})
        return authors

    def parse_abstract(self):
        abs_tag = self.soup.select_one('section.abstract')
        return '\n'.join([p.text for p in abs_tag.select('p')])

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
