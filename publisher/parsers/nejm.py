import copy
import re

import spacy
from nameparser import HumanName

from publisher.elements import Author, Affiliation
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
        cleaned = re.sub(r'\([\- .,A-Za-z]+\)', '', aff).strip(';, ')
        cleaned = strip_seqs(['From', ' the', ' and', 'the ', 'and '], cleaned,
                             recursive=True).strip(';, ')
        return cleaned

    def affs_initials_dict(self, affs):
        d = {}
        for aff in affs:
            initials_matches = re.findall(r'\([\- .,A-Za-z]+\)', aff)
            initials = initials_matches[0] if initials_matches else None
            cleaned = self.clean_aff(aff)
            d[cleaned] = initials
        return d

    def modify_nested_affs(self, affs_initials_dict: dict, nested_affs):
        if not nested_affs:
            return affs_initials_dict
        affs_initials = [list(item) for item in affs_initials_dict.items()]
        last_nested_index = 0
        nested_count = 0
        for i, aff in enumerate(affs_initials):
            if not affs_initials[i][1]:
                for j in range(last_nested_index, i):
                    affs_initials[j][0] = f'{affs_initials[j][0]}, {nested_affs[nested_count].strip(" ;,").split("—")[0].strip(" ;,")}'
                last_nested_index = i
                nested_count += 1
        return dict([(self.clean_aff(item[0]), item[1]) for item in affs_initials if item[1]])

    @staticmethod
    def _make_initials_patterns(name: HumanName):
        #M.G.-O.
        initial_matches = {re.sub(r'\.\W*\.+', '.', name.initials().replace(' ', '')),
                           f'{name.first[0]}. *{name.last}',
                           '.'.join(re.findall(r'([A-Z])', name.full_name)) + '.'}
        if name.middle:
            initial_matches.add(f'{name.first[0]}. *{name.middle[0]}. {name.last}',)
        parts = [name.first, name.middle, name.last]
        parts = [part for part in parts if part]
        for i, part in enumerate(parts):
            new_parts = parts.copy()
            split = part.split('-')
            if len(split) > 1:
                for j, _part in enumerate(split):
                    if j == 0:
                        new_parts[i] = _part
                    else:
                        new_parts.insert(i + j, '-' + _part)
                initials = '.'.join([name[:2] if name.startswith('-') else name[0] for name in new_parts])
                initials += '.'
                initial_matches.add(initials)
        patterns = []
        for match in initial_matches:
            safe_match = match.replace(".", "\.")
            patterns.append(re.compile(f'[(,] *{safe_match}[),]'))
        return patterns

    def parse_affs_by_unformatted_text(self, authors, affs_text):
        affs = re.findall(r'(?:;|\)|and|—)?(.*?(?:\(.*?\)|;|, and the |\Z))',
                          affs_text)
        affs = [aff for aff in affs if not aff.startswith('—') and len(aff) > 3]
        nested_affs = [aff for aff in affs if not re.search(r'\(.*?\)', aff)]
        if not affs:
            for author in authors:
                author['affiliations'].append(affs_text)
            return authors
        aff_initials_dict = self.affs_initials_dict(affs)
        if len(aff_initials_dict) == 1:
            for author in authors:
                author['affiliations'].append(tuple(aff_initials_dict.keys())[0])
            return authors
        aff_initials_dict = self.modify_nested_affs(aff_initials_dict, nested_affs)
        for author in authors:
            name = author['name']
            split = name.split(', ')
            if len(split) == 2:
                name = ' '.join(split[::-1])
            name = HumanName(name)
            patterns = self._make_initials_patterns(name)
            for aff, initials in aff_initials_dict.items():
                for pattern in patterns:
                    if pattern.search(initials):
                        author['affiliations'].append(aff)
        return authors

    def _parse_unformatted_affs_text(self):
        if affs_tag := self.soup.select_one('#author_affiliations p'):
            if re.search(r"The authors' affiliations [a-z ]+ the Appendix", affs_tag.text):
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
