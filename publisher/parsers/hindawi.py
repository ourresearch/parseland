from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import remove_parents


class Hindawi(PublisherParser):
    parser_name = "hindawi"

    def is_publisher_specific_parser(self):
        return self.domain_in_canonical_link('hindawi.com')

    def authors_found(self):
        return bool(self.soup.select('.article_authors'))

    def parse_associations(self):
        affs = {}
        if show_more_btn := remove_parents(self.soup.find_all(lambda tag: 'Show more' in tag.text)):
            affs_tag = show_more_btn[0].previous_sibling
            affs_tags = affs_tag.find_all('p')
            for tag in affs_tags:
                sup = tag.sup.text
                name = tag.span.text
                affs[sup] = name
        return affs

    def parse_authors(self):
        authors = []
        affs = self.parse_associations()
        author_tags = self.soup.select('.article_authors > span')
        for tag in author_tags:
            name = tag.next_element.text
            author = {'name': name, 'affiliations': [], 'is_corresponding': bool(tag.select_one('a[href*=mailto]'))}
            sups = tag.sup
            for sup in sups:
                if sup.text and sup.text.isnumeric():
                    author['affiliations'].append(affs[sup.text])
            authors.append(author)
        return authors

    def parse_abstract(self):
        return self.soup.select_one('#abstract').find_next_sibling('p').text

    def parse(self):
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract()}