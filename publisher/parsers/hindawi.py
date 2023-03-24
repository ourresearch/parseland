import json

from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import remove_parents


class Hindawi(PublisherParser):
    parser_name = "hindawi"

    def is_publisher_specific_parser(self):
        return self.domain_in_canonical_link('hindawi.com')

    def authors_found(self):
        return bool(self.soup.select('.article_authors') or self.soup.select(
            '.articleHeader__authors'))

    def parse_affiliations_1(self):
        affs = {}
        if show_more_btn := remove_parents(
                self.soup.find_all(lambda tag: 'Show more' in tag.text)):
            affs_tag = show_more_btn[0].previous_sibling
            affs_tags = affs_tag.find_all('p')
            for tag in affs_tags:
                sup = tag.sup.text
                name = tag.span.text
                affs[sup] = name
        return affs

    def parse_authors(self):
        authors = []
        affs = self.parse_affiliations_1()
        author_tags = self.soup.select('.article_authors > span')
        for tag in author_tags:
            name = tag.next_element.text
            author = {'name': name, 'affiliations': [],
                      'is_corresponding': bool(
                          tag.select_one('a[href*=mailto]'))}
            sups = tag.sup
            for sup in sups:
                if sup.text and sup.text.isnumeric():
                    author['affiliations'].append(affs[sup.text])
            authors.append(author)
        return authors

    def parse_abstract(self):
        return self.soup.select_one('#abstract').find_next_sibling('p').text

    @staticmethod
    def format_aff(aff_obj):
        return ', '.join([line for line in aff_obj['addrLines'][0].values()])

    def parse_json(self):
        authors = []
        data_tag = self.soup.select_one('script#__NEXT_DATA__')
        j = json.loads(data_tag.text)
        article_obj = j['props']['pageProps']['article']
        article_obj['affiliations'] = sorted(article_obj['affiliations'], key=lambda obj: obj['affId'])
        for author in article_obj['authors']:
            auth = {'name': f'{author["givenName"]} {author["surName"]}',
                    'affiliations': [],
                    'is_corresponding': bool(author.get('email'))}
            for aff_sup in author['affSup']:
                auth['affiliations'].append(self.format_aff(
                    article_obj['affiliations'][aff_sup['affId'] - 1]))

            authors.append(auth)
        return {'authors': authors, 'abstract': article_obj['abstract']}

    def parse(self):
        try:
            return self.parse_json()
        except Exception:
            pass
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
