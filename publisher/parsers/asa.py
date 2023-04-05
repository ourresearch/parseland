from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import strip_seq


class AcousticalSocietyOfAmerica(PublisherParser):
    parser_name = "acoustical_society_of_america"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('asa.scitation')

    def authors_found(self):
        return bool(self.soup.select('.entryAuthor .contrib-author'))

    def parse_affiliations(self):
        affs = {}
        aff_tags = self.soup.select('#affiliationsDiv li')
        for aff_tag in aff_tags:
            if sup_tag := aff_tag.find('sup'):
                sup = sup_tag.text.strip(' ()')
                if not sup.isnumeric():
                    continue
                sup_tag.decompose()
                affs[sup] = aff_tag.text.strip()
            else:
                return aff_tag.text.strip()
        return affs

    def parse_authors(self):
        authors = []
        affs = self.parse_affiliations()
        author_tags = self.soup.select('.entryAuthor .contrib-author')
        for author_tag in author_tags:
            is_corresponding = bool(author_tag.select('a.email'))
            name = author_tag.select_one('a[href*="/author/"]').text.strip()
            author_affs = []
            if not affs:
                if aff_tag := author_tag.find_next_sibling('li', class_='author-affiliation'):
                    is_corresponding = bool(aff_tag.select('a.email'))
                    author_affs = [aff_tag.text.strip()]
            elif isinstance(affs, dict):
                sups = [tag.text.strip(' ()') for tag in (author_tag.find('sup') or []) if tag.text.strip(' ()').isnumeric()]
                author_affs = [affs[sup] for sup in sups if not sup.isalpha()]
            else:
                author_affs = [affs]
            authors.append({
                'name': name,
                'affiliations': [strip_seq('\[email\Wprotected\]', aff.strip()).strip(' ,') for aff in author_affs],
                'is_corresponding': is_corresponding,
            })
        return authors

    def parse_abstract(self):
        if abs_heading := self.soup.select_one('.abstractSectionHeading'):
            return abs_heading.find_next_sibling('div', class_='NLM_paragraph').text.strip()
        return None

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
