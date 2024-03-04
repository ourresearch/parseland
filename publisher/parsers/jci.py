from publisher.parsers.parser import PublisherParser


class JCI(PublisherParser):
    parser_name = "jci"

    def is_publisher_specific_parser(self):
        return self.substr_in_citation_journal_title('JCI Insight')

    def authors_found(self):
        return bool(self.soup.select_one('.author-list'))

    def parse_affs_map(self):
        affs_map = {}
        for tag in self.soup.select('p.affiliations'):
            if id_tag := tag.select_one('sup'):
                _id = id_tag.text.strip()
                id_tag.decompose()
                inst = tag.text.strip()
                affs_map[_id] = inst
        return affs_map

    def parse_authors(self):
        authors = []
        affs_map = self.parse_affs_map()
        for tag in self.soup.select('a.author-affiliation'):
            aff_ids = []
            if aff_ids_tag := tag.select_one('sup'):
                aff_ids = aff_ids_tag.text.strip().split(',')
                aff_ids_tag.decompose()
            name = tag.text.strip(' ,\t\n')
            affs = [affs_map[_id] for _id in aff_ids]
            authors.append({
                'name': name,
                'affiliations': affs,
                'is_corresponding': None
            })
        return authors

    def parse(self):
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract_meta_tags()}