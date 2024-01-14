from publisher.parsers.parser import PublisherParser


class SCitation(PublisherParser):
    parser_name = "s_citation"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("scitation.org")

    def authors_found(self):
        return bool(self.soup.select('span.contrib-author'))

    def parse_authors(self):
        author_tags = self.soup.select('span.contrib-author')
        all_affs = [tag.text.strip() for tag in self.soup.select('li.author-affiliation')]
        authors = []
        for author_tag in author_tags:
            name = author_tag.text.strip()
            author = {'name': name,
                      'is_corresponding': None,
                      'affiliations': []}
            if aff_tag := author_tag.find_next_sibling('li', class_='author-affiliation'):
                author['affiliations'].append(aff_tag.text.strip())
            else:
                author['affiliations'] = all_affs
            authors.append(author)
        return authors

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract_meta_tags()}
