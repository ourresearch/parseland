from publisher.parsers.parser import PublisherParser


class TheAstronomicalJournal(PublisherParser):
    parser_name = "the_astronomical_journal"

    def is_publisher_specific_parser(self):
        return self.substr_in_citation_journal_title('Astronomical Journal')

    def authors_found(self):
        return bool(self.soup.select('li.author'))

    def parse_authors(self):
        author_tags = self.soup.select('li.author')
        authors = []
        for author_tag in author_tags:
            name = author_tag.select_one('a').text.strip()
            affs = []
            if aff_tag := author_tag.select_one('span.affiliation'):
                affs.append(aff_tag.text.strip())
            authors.append({
                'name': name,
                'is_corresponding': None,
                'affiliations': affs
            })
        return authors

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_author_meta_tags()}
