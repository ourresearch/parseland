import copy
import re

from nameparser import HumanName

from publisher.elements import Author, Affiliation
from publisher.parsers.nejm_unformatted_utils import \
    parse_affs_by_unformatted_text
from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import strip_seqs, strip_prefix


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
                authors = parse_affs_by_unformatted_text(authors,
                                                              unformatted_affs_text)

        return {'authors': authors,
                'abstract': self.parse_abstract()}
