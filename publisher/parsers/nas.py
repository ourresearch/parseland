from publisher.parsers.parser import PublisherParser


class NationalAcademyOfScience(PublisherParser):
    parser_name = "national_academy_of_science"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('pnas.org')

    def authors_found(self):
        return bool(self.soup.select(
            'div[id*=author-popups] > div[class*=author-tooltip-]'))

    def parse_affiliations(self):
        affs = {}
        aff_tags = self.soup.select('.affiliation-list address')
        for aff_tag in aff_tags:
            sup = aff_tag.find('sup').text.strip()
            aff_tag.find('sup').decompose()
            aff = aff_tag.text.strip()
            affs[sup] = aff
        return affs

    def parse_authors(self):
        author_tags = self.soup.select(
            'div[id*=author-popups] > div[class*=author-tooltip-]')
        authors = []
        for author_tag in author_tags:
            name = author_tag.select_one('.author-tooltip-name').text
            aff_tags = author_tag.select('.author-affiliation')
            affs = []
            for aff_tag in aff_tags:
                aff_tag.select_one('[class*=sup]').decompose()
                affs.append(aff_tag.text)
            is_corresponding = bool(
                author_tag.select_one('.author-corresp-email-link'))
            author = {'name': name, 'affiliations': affs,
                      'is_corresponding': is_corresponding}
            authors.append(author)

        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('div.abstract p'):
            return abs_tag.text
        return None

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
