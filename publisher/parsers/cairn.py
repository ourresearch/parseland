from publisher.parsers.parser import PublisherParser


class CAIRN(PublisherParser):
    parser_name = "cairn"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('cairn.info')

    def authors_found(self):
        return bool(self.soup.select('div.auteur'))

    def parse_authors(self):
        author_tags = self.soup.select('div.auteur')
        authors = []
        for author_tag in author_tags:
            name = ' '.join([tag.text for tag in author_tag.select_one('.nompers').children if len(tag.text) > 2])
            affs = []
            aff_raw = ''
            if aff_raw_tag := author_tag.select_one('div.affiliation'):
                aff_raw = aff_raw_tag.text
                aff = aff_raw_tag.text.split('E-mail')[0]
                affs = [aff]
            authors.append({'name': name, 'affiliations': affs, 'is_corresponding': 'correspondant' in aff_raw})
        return authors

    def parse(self):
        authors = self.parse_authors() or self.parse_author_meta_tags()
        return {'authors': authors, 'abstract': self.parse_abstract_meta_tags()}
