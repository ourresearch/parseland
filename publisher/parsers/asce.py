from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import strip_suffix


class AmericanSocietyOfCivilEngineers(PublisherParser):
    parser_name = "american_society_of_civil_engineers"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('ascelibrary.org')

    def authors_found(self):
        return bool(self.soup.select('.author-block'))

    def parse_authors(self):
        author_tags = self.soup.select('.author-block')
        authors = []
        for author_tag in author_tags:
            name = author_tag.select_one('.authorName').text
            is_corresponding = 'corresponding author' in author_tag.text.lower()
            affs_tag = author_tag.select_one('.authorAffiliation')
            for email_tag in affs_tag.select('a[href*=email-protection]'):
                email_tag.decompose()
            affs = [strip_suffix('\W', aff.split('Email')[0].replace('(corresponding author)', '')) for aff in affs_tag.text.split(';')]
            affs = [aff.strip('(). ').replace(' . ', '. ') for aff in affs if len(aff) > 3]
            author = {'name': name, 'affiliations': affs, 'is_corresponding': is_corresponding}
            authors.append(author)
        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('div[class*=Abstract] p'):
            return abs_tag.text
        return None

    def parse(self):
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract()}