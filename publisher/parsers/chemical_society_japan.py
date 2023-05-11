from bs4 import NavigableString

from publisher.parsers.parser import PublisherParser


class CSJ(PublisherParser):
    parser_name = "chemical_society_of_japan"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('journal.csj.jp')

    def authors_found(self):
        return bool(self.soup.select('[class*=ContribAuthor]'))

    def parse_affs(self):
        affs_tag = self.soup.select_one('div.affiliationsGroup')
        if not affs_tag.find('sup'):
            return affs_tag.text.strip()
        affs = {}
        current_num = None
        for tag in affs_tag.children:
            if tag.name == 'sup' and tag.text.strip().isdigit():
                current_num = tag.text.strip()
            elif isinstance(tag, NavigableString):
                affs[current_num] = tag.text.strip()
        return affs

    def parse_authors(self):
        authors_tag = self.soup.select_one('[class*=ContribAuthor]')
        authors = []
        affs = self.parse_affs()
        for author_tag in authors_tag.select('.contribDegrees'):
            name = author_tag.select_one('.entryAuthor').text
            aff_nums = [tag.text.strip() for tag in author_tag.select('sup')]
            author_affs = [affs[num] for num in aff_nums if
                           num.isdigit()] if isinstance(affs, dict) else [affs]
            authors.append({'name': name,
                            'affiliations': author_affs,
                            'is_corresponding': '*' in aff_nums})
        return authors

    def parse_abstract(self):
        abs_tags = self.soup.select('.abstractInFull')
        return '\n'.join([tag.text.strip() for tag in abs_tags])

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
