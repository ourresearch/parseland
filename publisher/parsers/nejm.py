import re

from nameparser import HumanName

from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import strip_seqs


class NewEnglandJournalOfMedicine(PublisherParser):
    parser_name = 'nejm'

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('nejm.org')

    def authors_found(self):
        return bool(self.soup.select('ul.m-article-header__authors'))

    def parse_abstract(self):
        return '\n'.join(
            [tag.text for tag in self.soup.select('section#article_body p')])

    @staticmethod
    def parse_affiliations(authors, affs_text):
        affs = re.findall(r'(?:and|;|\A)(.*?\([\- ,A-Z.]+\))', affs_text)
        cleaned_affs = [re.sub(r'\([\- .,A-Za-z]+\)', '', aff).strip() for aff in affs]
        cleaned_affs = [strip_seqs(['and', 'From', 'the'], aff).strip() for aff in cleaned_affs]
        for author in authors:
            name = HumanName(author['name'])
            initial_matches = {name.initials().replace(' ', '')}
            if '-' in name.first:
                split = [part[0] if i == 0 else '-' + part[0] for i, part in enumerate(name.first.split('-'))]
                initials = '.'.join([*split, *[part[0] for part in name.as_dict().values() if part][1:]])
                initial_matches.add(initials)
            for i, aff in enumerate(affs):
                for match in initial_matches:
                    if match in aff:
                        author['affiliations'].append(cleaned_affs[i])
        return authors

    def parse(self):
        authors = self.parse_author_meta_tags()
        if affs_tag := self.soup.select_one('#author_affiliations p'):
            authors = self.parse_affiliations(authors, affs_tag.text)

        return {'authors': authors,
                'abstract': self.parse_abstract()}
