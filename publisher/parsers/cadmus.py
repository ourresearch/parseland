from publisher.parsers.parser import PublisherParser


class CadmusPress(PublisherParser):
    parser_name = "cadmus_press"

    def is_publisher_specific_parser(self):
        if publisher_meta := self.soup.select_one('meta[name=citation_publisher]'):
            return 'The Association for Research in Vision and Ophthalmology' in publisher_meta['content']
        return False

    def authors_found(self):
        return bool(self.soup.select('ul[class*=affiliationList]'))

    def parse_authors(self):
        authors = self.parse_author_meta_tags()
        if corresponding_tag := self.soup.find(lambda tag: tag.name == 'div' and 'class' in tag.attrs and 'para' in tag['class'] and 'correspondence' in tag.text.lower()):
            corresponding_text = corresponding_tag.text
            for author in authors:
                if author['name'] in corresponding_text:
                    author['is_corresponding'] = True
                else:
                    author['is_corresponding'] = False
        return authors

    def parse_abstract(self):
        abs_tags = self.soup.select('.abstract p')
        return '\n'.join([tag.text.strip() for tag in abs_tags])

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
