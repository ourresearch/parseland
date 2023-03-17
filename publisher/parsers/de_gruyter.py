from publisher.parsers.parser import PublisherParser


class DeGruyter(PublisherParser):
    parser_name = "de_gruyter"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('degruyter.com')

    def authors_found(self):
        return bool(self.soup.select('span.contributor'))

    def parse_authors(self):
        author_tags = self.soup.select('span.contributor')
        authors = []
        for author_tag in author_tags:
            name = author_tag.text.strip('\n ')
            if cont_popdown := author_tag.select_one('contributor-popdown'):
                is_corresponding = bool(cont_popdown.get('email', ''))
                affiliations = [aff for aff in cont_popdown.get('affiliations', '').split(';') if aff]
            else:
                is_corresponding = '@' in author_tag.get('title', '')
                affiliations = [aff for aff in author_tag.get('title', '').split(';') if '@' not in aff and aff]

            authors.append({
                'name': name,
                'is_corresponding': is_corresponding,
                'affiliations': affiliations
            })
        return authors

    def parse_abstract(self):
        paragraphs = self.soup.select('section[id*=_abs_] p')
        return '\n'.join([p.text for p in paragraphs])

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
