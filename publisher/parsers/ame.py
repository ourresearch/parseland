from bs4 import NavigableString

from publisher.elements import Author, Affiliation
from publisher.parsers.parser import PublisherParser


class AMEPublishing(PublisherParser):
    parser_name = "ame_publishing"

    def is_publisher_specific_parser(self):
        return self.substr_in_citation_publisher('AME ')

    def authors_found(self):
        return bool(self.soup.select('p.authors'))

    def parse_affs(self):
        affs = []
        aff_tags = self.soup.select('p.affiliation aff')
        for aff_tag in aff_tags:
            sup = aff_tag.select_one('sup')
            aff_id = sup.text.strip()
            sup.decompose()
            aff = aff_tag.text.strip()
            affs.append(Affiliation(aff, aff_id))
        return affs

    def parse_authors(self):
        authors = []
        authors_tag = self.soup.select_one('p.authors')
        for author_tag in authors_tag.children:
            if isinstance(author_tag, NavigableString):
                name = author_tag.text.strip(' ,')
                aff_ids = []
                if sup := author_tag.find_next_sibling('sup'):
                    aff_ids = [char for char in sup.text if
                               char and char.isnumeric()]
                authors.append(Author(name=name, aff_ids=aff_ids))
        affs = self.parse_affs()
        return self.merge_authors_affiliations(authors, affs)

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('#abstract'):
            return abs_tag.text.strip()
    def parse(self):
        authors = self.parse_authors()
        corr_authors = self.soup.select('div[class*=corr] [id*=cor]')
        for corr_author in corr_authors:
            for author in authors:
                if author.name.lower() in corr_author.text.lower():
                    author.is_corresponding = True
        return {'authors': authors,
                'abstract': self.parse_abstract()}
