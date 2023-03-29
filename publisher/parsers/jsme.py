
from publisher.parsers.parser import PublisherParser


class JSME(PublisherParser):
    parser_name = "japan_society_of_mechanical_engineers"

    def is_publisher_specific_parser(self):
        if journal_tag := self.soup.select_one('meta[name="journal_code"]'):
            return 'jsme' in journal_tag['content']
        return False

    def authors_found(self):
        return bool(self.soup.select('.global-authors-name-tags a'))

    def parse_abstract(self):
        p_tags = self.soup.select('#article-overiew-abstract-wrap p')
        for tag in p_tags:
            if len(tag.text) > 3:
                return tag.text
        return None

    def parse(self):
        authors = self.parse_meta_tags()
        author_tags = self.soup.select('.global-authors-name-tags a')
        for author_tag in author_tags:
            if '*' in author_tag.text:
                for author in authors:
                    if author['name'] in author_tag.text:
                        author['is_corresponding'] = True
        return {'authors': authors, 'abstract': self.parse_abstract()}
