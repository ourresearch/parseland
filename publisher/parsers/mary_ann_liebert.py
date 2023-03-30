from publisher.parsers.parser import PublisherParser


class MaryAnnLiebert(PublisherParser):
    parser_name = "mary_ann_liebert"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('liebertpub.com')

    def authors_found(self):
        return bool(self.soup.select('div[class*=tab-mobile]'))

    def parse_authors(self):
        author_tags = self.soup.select('div[class*=tab-mobile]')
        authors = []
        for author_tag in author_tags:
            name = author_tag.find('span').text
            author = {'name': name, 'affiliations': [], 'is_corresponding': bool(author_tag.select('i.icon-Email'))}
            aff_tags = author_tag.select_one('p.author-type').find_next_siblings('p')
            for aff_tag in aff_tags:
                if bool(aff_tag.text):
                    author['affiliations'].append(aff_tag.text)
            authors.append(author)
        return authors

    def parse(self):
        if abs_tags := self.soup.select('.abstractInFull p'):
            abs_txt = '\n'.join([tag.text for tag in abs_tags])
        else:
            abs_txt = None
        return {'authors': self.parse_authors(), 'abstract': abs_txt}
