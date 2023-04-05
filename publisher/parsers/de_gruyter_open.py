import json

from publisher.parsers.parser import PublisherParser


class DeGruyterOpen(PublisherParser):
    parser_name = "de_gruyter_open"

    def is_publisher_specific_parser(self):
        return bool(self.soup.find(lambda
                                       tag: 'Sciendo is a De Gruyter company'.lower() in tag.text.lower()))

    def authors_found(self):
        return bool(self.soup.select('div[class*=author-popup]'))

    def parse_json(self):
        if json_tag := self.soup.select_one('script#__NEXT_DATA__'):
            return json.loads(json_tag.text)
        return {}

    @staticmethod
    def parse_authors(j):
        authors = []
        contrib_group = j['props']['pageProps']['product']['articleData'][
            'contribGroup']
        for author in contrib_group['contrib']:
            name = f'{author["name"]["given-names"]} {author["name"]["surname"]}'
            is_corresponding = 'y' in (author.get('corresp', '') or '')
            affs = []
            aff_id = author['xref']['rid']
            if isinstance(contrib_group['aff'], dict):
                contrib_group['aff'] = [contrib_group['aff']]
            for aff in contrib_group['aff']:
                if aff['id'] == aff_id:
                    if isinstance(aff['institution'], list):
                        desc = ''
                        for item in aff['institution']:
                            if isinstance(item, str):
                                desc += item + ', '
                            elif isinstance(item, dict):
                                desc += item.get('content', '') + ', '
                        affs.append(desc.strip(' ,'))
                    elif isinstance(aff['institution'], str):
                        affs.append(aff['institution'])
            authors.append({
                'name': name,
                'affiliations': affs,
                'is_corresponding': is_corresponding,
            })
        return authors

    def parse(self):
        j = self.parse_json()
        return {'authors': self.parse_authors(j), 'abstract': self.parse_abstract_meta_tags()}
