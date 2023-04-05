from publisher.parsers.parser import PublisherParser


class InderScience(PublisherParser):
    parser_name = "inderscience"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('inderscienceonline.com')

    def authors_found(self):
        return bool(self.soup.select('div[class*=tab-mobile]'))

    def parse_authors(self):
        authors = []
        for author_tag in self.soup.select('div[class*=tab-mobile]'):
            name = author_tag.find('a').text
            is_corresponding = None
            info_tag = author_tag.select_one('.author-info')
            info_tag.select_one('.bottom-info').decompose()
            authors.append({
                'name': name,
                'affiliations': [info_tag.text.strip()],
                'is_corresponding': is_corresponding,
            })
        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('.abstractInFull p'):
            return abs_tag.text
        return None

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract_meta_tags()}
