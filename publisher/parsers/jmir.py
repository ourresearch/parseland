import re

from publisher.parsers.parser import PublisherParser
from nameparser import HumanName

from publisher.parsers.utils import names_match


class JMIR(PublisherParser):
    parser_name = "jmir"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('jmir.org')

    def authors_found(self):
        return bool(self.soup.select('p.authors-list .authors'))

    def corresponding_author_name(self):
        if corr_tag := self.soup.select_one('.corresponding-author li'):
            return HumanName(corr_tag.text.strip())
        return None

    def affs_map(self):
        m = {}
        for aff_tag in self.soup.select('.affiliation-item'):
            org = aff_tag.next_sibling.text.strip()
            aff_id = aff_tag.text.strip()
            m[aff_id] = org
        return m

    @staticmethod
    def parse_aff_ids(affs_txt):
        cleaned = re.sub(r'[^\d,]', '', affs_txt)
        return cleaned.split(',')

    def parse_authors(self):
        authors = []
        corresponding_author_name = self.corresponding_author_name()
        affs = self.affs_map()
        for author_tag in self.soup.select('p.authors-list .authors'):
            name = author_tag.select_one('a').text.strip()
            name_parsed = HumanName(name)
            is_corresponding = names_match(name_parsed, corresponding_author_name)
            affiliations = []
            if affs_tag := author_tag.select_one('.affiliation-link'):
                aff_ids = self.parse_aff_ids(affs_tag.text)
                for aff_id in aff_ids:
                    affiliations.append(affs[aff_id])
            authors.append({'name': name,
                            'is_corresponding': is_corresponding,
                            'affiliations': affiliations})
        return authors

    def parse(self):
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract_meta_tags()}
