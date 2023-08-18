import copy
import re

from nameparser import HumanName
import spacy

from publisher.elements import AuthorAffiliations, Author, Affiliation
from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import strip_seqs, strip_prefix

nlp = spacy.load("en_core_web_lg")


class NewEnglandJournalOfMedicine(PublisherParser):
    parser_name = 'nejm'

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('nejm.org')

    def authors_found(self):
        return bool(self.soup.select('ul.m-article-header__authors'))

    def parse_abstract(self):
        return '\n'.join(
            [tag.text for tag in self.soup.select('section#article_body p')])

    def parse_affs(self):
        affs = []
        aff_tags = self.soup.select('#author_affiliations div[id*=A]')
        for tag in aff_tags:
            affs.append(
                Affiliation(organization=strip_prefix(r'^(\W)',
                                                      tag.text.strip()).strip(),
                            aff_id=tag.get('id')))
        return affs

    def parse_author_affiliations(self):
        authors_tags = self.soup.select('ul.m-article-header__authors li')
        authors = []
        for tag in authors_tags:
            _tag = copy.copy(tag)
            if sups := _tag.find_all('sup'):
                for sup in sups:
                    sup.decompose()
            aff_ids = []
            for sup in tag.find_all('sup'):
                aff_ids.append(sup.a.get('href').strip('#'))
            author = Author(name=_tag.text.strip(),
                            aff_ids=aff_ids,
                            is_corresponding=None)
            authors.append(author)
        affs = self.parse_affs()
        return self.merge_authors_affiliations(authors, affs)

    @staticmethod
    def clean_aff(aff):
        cleaned = re.sub(r'\([\- .,A-Za-z]+\)', '', aff).strip(', ')
        cleaned = strip_seqs(['From', ' the', ' and', 'the ', 'and '], cleaned,
                             recursive=True).strip(' ,')
        return cleaned

    def affs_initials_dict(self, affs):
        d = {}
        for aff in affs:
            initials = re.findall(r'\([\- .,A-Za-z]+\)', aff)[0]
            cleaned = self.clean_aff(aff)
            d[cleaned] = initials
        return d

    def modify_nested_affs(self, affs_initials_dict: dict, nested_affs):
        if not nested_affs:
            return affs_initials_dict
        affs_initials = [list(item) for item in affs_initials_dict.items()]
        nested_truths = [(nested in aff[0], nested if nested in aff[0] else None) for nested in nested_affs for aff in
                         affs_initials]
        last_nested_index = 0
        nested_count = 0
        for i, aff in enumerate(affs_initials):
            if nested_truths[i][0]:
                for j in range(last_nested_index, i):
                    affs_initials[j][0] = f'{affs_initials[j][0]}, {nested_affs[nested_count]}'
                last_nested_index = i
                nested_count += 1
        for i, t in enumerate(nested_truths):
            if t[0]:
                aff = self.clean_aff(affs_initials[i][0].replace(t[1], ''))
                if aff:
                    affs_initials[i][0] = aff
                else:
                    affs_initials.pop(i)
        return dict(affs_initials)

    def parse_affs_by_unformatted_text(self, authors, affs_text):
        affs = re.findall(r'(?:and|;|\A|,)(.*?\([\- .,A-Za-z]+\))',
                          affs_text)
        nested_affs = [self.clean_aff(aff) for aff in re.findall(
            r', and [a-zA-Z ]+ \([\-A-Z.]+\), ([a-zA-Z ,]+)(?:and|;)',
            affs_text)]
        if not affs:
            for author in authors:
                author['affiliations'].append(affs_text)
            return authors
        aff_initials_dict = self.affs_initials_dict(affs)
        aff_initials_dict = self.modify_nested_affs(aff_initials_dict, nested_affs)
        for author in authors:
            name = HumanName(author['name'])
            initial_matches = {name.initials().replace(' ', ''),
                               f'{name.first[0]}. {name.last}'}
            if '-' in name.first:
                split = [part[0] if i == 0 else '-' + part[0] for i, part in
                         enumerate(name.first.split('-'))]
                initials = '.'.join([*split, *[part[0] for part in
                                               name.as_dict().values() if part][
                                              1:]])
                initial_matches.add(initials)
            for aff, initials in aff_initials_dict.items():
                for match in initial_matches:
                    if match in initials:
                        author['affiliations'].append(aff)
        return authors

    def _parse_unformatted_affs_text(self):
        if affs_tag := self.soup.select_one('#author_affiliations p'):
            if "The authors' affiliations are listed in the Appendix" in affs_tag.text:
                possible_affs_tags = self.soup.select(
                    'section[id*=article_appendix] p')
                for tag in possible_affs_tags:
                    if tag.text.startswith(
                            "The authors' affiliations are as follows:"):
                        return strip_prefix(
                            "The authors' affiliations are as follows:",
                            tag.text.strip())
            else:
                return affs_tag.text
        return None

    def parse(self):
        affs_labeled = bool(
            self.soup.select('ul.m-article-header__authors li sup a[href*=A]'))
        if affs_labeled:
            authors = self.parse_author_affiliations()
        else:
            authors = self.parse_author_meta_tags()
            if unformatted_affs_text := self._parse_unformatted_affs_text():
                authors = self.parse_affs_by_unformatted_text(authors,
                                                              unformatted_affs_text)

        return {'authors': authors,
                'abstract': self.parse_abstract()}
