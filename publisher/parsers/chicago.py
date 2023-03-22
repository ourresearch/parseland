from publisher.parsers.parser import PublisherParser


class Chicago(PublisherParser):
    parser_name = "university_of_chicago"

    def is_publisher_specific_parser(self):
        if self.domain_in_meta_og_url('journals.uchicago.edu'):
            return True
        if meta_tag := self.soup.select_one('meta[name=citation_publisher]'):
            return 'Theory of Computing' in meta_tag['content']

    def authors_found(self):
        return bool(self.soup.select('.author-name') or self.soup.select('span#authornames'))

    def parse_authors_method_1(self):
        author_tags = self.soup.select('.author-name')
        authors = []
        for tag in author_tags:
            name = tag.text
            affiliations = tag.next_sibling.find_all(lambda t: t.name == 'p' and bool(t.text) and not t.find('a'))
            authors.append({'name': name, 'affiliations': [aff.text for aff in affiliations],
                            'is_corresponding': None})
        return authors

    # Theory of Computing journal
    def parse_authors_method_2(self):
        authors = []
        author_tags = self.soup.select('span#authornames')
        for tag in author_tags:
            name = tag.text
            authors.append({'name': name, 'affiliations': [], 'is_corresponding': None})
        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('.abstractInFull'):
            return abs_tag.text

        elif abs_heading := self.soup.find(lambda tag: tag.name == 'p' and 'abstract' in tag.text.lower()):
            if abs_heading.next_sibling.text.strip('\n '):
                return abs_heading.next_sibling.text.strip('\n ')
            else:
                return abs_heading.next_sibling.next_sibling.text.strip('\n ')
        return None

    def parse(self):
        authors = self.parse_authors_method_1()
        if not authors:
            authors = self.parse_authors_method_2()
        return {'authors': authors,
                'abstract': self.parse_abstract()}
