from publisher.parsers.parser import PublisherParser


class RussianAcademyOfSciences(PublisherParser):
    parser_name = "russian_academy_of_sciences"

    def is_publisher_specific_parser(self):
        founders_tags = self.soup.select('.founders-one-descr')
        for tag in founders_tags:
            if 'russian academy of sciences' in tag.text.lower():
                return True
        return bool(self.soup.find(
            lambda tag: tag.name == 'a' and 'ras.ru' in tag.get('href', '')))

    def authors_found(self):
        return bool(self.soup.select('div.authors div.clearfix'))

    def parse_authors(self):
        authors = []
        for author_tag in self.soup.select('div.authors div.clearfix'):
            name = author_tag.find('a').text.strip()
            aff_tags = author_tag.select('div.authors-affiliation span[class]')
            affs = [tag.text for tag in aff_tags]
            authors.append(
                {'name': name, 'affiliations': affs, 'is_corresponding': None})
        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.find(
                lambda tag: tag.name == 'div' and 'pub-annotation-info-one-label' in tag.get(
                        'class', {}) and 'abstract' in tag.text.lower()):
            return abs_tag.find_next_sibling('div').find('p').text.strip()
        return None

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
