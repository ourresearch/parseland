from publisher.parsers.parser import PublisherParser


class ASM(PublisherParser):
    parser_name = "american_science_for_microbiology"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('journals.asm.org')

    def authors_found(self):
        return bool(self.soup.select("[property=author]"))

    def parse_authors(self):
        authors = {}
        author_tags = self.soup.select("[property=author]")
        for author_tag in author_tags:
            given_name = author_tag.select_one('[property=givenName]').text
            family_name = author_tag.select_one('[property=familyName]').text
            name = f'{given_name} {family_name}'
            affs = [tag.text for tag in (author_tag.select('[property=organization]') or author_tag.select('[property=affiliation]'))]
            author = {'name': name, 'affiliations': affs, 'is_corresponding': bool(author_tag.select('a[href*=email-protection]'))}
            if name not in authors or (not authors[name]['affiliations'] and author['affiliations']):
                authors[name] = author
        return list(authors.values())

    def parse_abstract(self):
        return self.soup.select_one('section#abstract [role=paragraph]').text

    def parse(self):
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract()}