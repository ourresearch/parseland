from publisher.parsers.parser import PublisherParser


class RoyalSociety(PublisherParser):
    parser_name = "royal_society_publishing"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('royalsocietypublishing.org')

    def authors_found(self):
        return bool(self.soup.select('[title="list of authors"] > div'))

    def parse_authors(self):
        author_tags = self.soup.select('[title="list of authors"] > div')
        authors = []
        for author_tag in author_tags:
            name = author_tag.select_one('a span').text
            aff = None
            author_info_tag = author_tag.select_one('.author-info')
            if aff_tag := author_info_tag.find(
                lambda tag: tag.name == 'p' and ',' in tag.text):
                aff = aff_tag.text
            author = {'name': name,
                      'affiliations': [aff] if aff else [],
                      'is_corresponding': bool(author_tag.select('a[href*=email-protection]'))}
            authors.append(author)
        return authors

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}

    def parse_abstract(self):
        return self.soup.select_one('.abstractInFull').text
