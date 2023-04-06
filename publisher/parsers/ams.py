from publisher.parsers.parser import PublisherParser


class AmericanMathematicalSociety(PublisherParser):
    parser_name = "american_mathematical_society"

    def is_publisher_specific_parser(self):
        if og_title := self.soup.select_one('meta[property="og:title"]'):
            return 'American Mathematical Society' in og_title['content']
        return False

    def authors_found(self):
        return bool(self.parse_author_meta_tags())

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('a[name=Abstract]'):
            return abs_tag.next_sibling.text.strip()
        elif abs_tag := self.soup.select_one('section#Abstract'):
            if heading := abs_tag.find('h2'):
                heading.decompose()
            return abs_tag.text.strip()
        return None

    def parse(self):
        return {'authors': self.parse_author_meta_tags(),
                'abstract': self.parse_abstract()}
