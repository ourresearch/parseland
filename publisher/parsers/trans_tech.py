from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import is_h_tag, remove_parents


class TransTechPub(PublisherParser):
    parser_name = "trans_tech_publications"

    def is_publisher_specific_parser(self):
        if meta := self.soup.select_one('meta[name=citation_publisher]'):
            return 'Trans Tech' in meta['content']
        return False

    def authors_found(self):
        return bool(self.soup.find(
            lambda tag: 'Authors' in tag.text))

    def parse_authors(self):
        authors = []
        if authors_headings := remove_parents(self.soup.find_all(
            lambda tag: 'Authors' in tag.text)):
            authors_heading = authors_headings[0]
            authors_tags = authors_heading.parent.parent.next_sibling.next_sibling.find_all('a')
            for tag in authors_tags:
                if 'author-papers' not in tag['href']:
                    continue
                name = tag.text
                is_corresponding = '*' in tag.next_sibling.text
                authors.append({'name': name, 'affiliations': [], 'is_corresponding': is_corresponding})
        return authors

    def parse_abstract(self):
        return self.soup.select_one('.abstract-block-description p').text

    def parse(self):
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract()}
