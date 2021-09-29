from unicodedata import normalize


class Springer:
    def __init__(self, soup):
        self.soup = soup
        self.parser_name = "springer"

    def is_correct_parser(self):
        header_link = self.soup.find("link", {"rel": "canonical"})
        if header_link and "link.springer.com" in header_link["href"]:
            return True

    def parse(self):
        authors = self.get_authors()
        if authors:
            affiliations = self.get_affiliations()
            authors_affiliations = self.combine_authors_affiliations(
                authors, affiliations
            )
        else:
            authors_affiliations = "no authors found"
        return authors_affiliations

    def get_authors(self):
        authors = []
        section = self.soup.find(id="authorsandaffiliations")
        if not section:
            return None
        author_soup = section.findAll("li", {"itemprop": "author"})
        for author in author_soup:
            ref_ids = []
            references = author.find("ul", {"data-role": "AuthorsIndexes"})
            if references:
                for reference in references:
                    ref_ids.append(int(reference.text))
            name = normalize("NFKD", author.span.text)
            authors.append({"name": name, "ref_ids": ref_ids})
        return authors

    def get_affiliations(self):
        affiliations = {}
        section = self.soup.find(id="authorsandaffiliations")
        aff_soup = section.findAll("li", class_="affiliation")
        for aff in aff_soup:
            aff_id = int(aff["data-affiliation-highlight"][-1])

            # get affiliations
            spans = aff.findAll("span")
            affiliation_data = []
            for span in spans:
                if span.has_attr("itemprop") and span["itemprop"] != "address":
                    affiliation_data.append(span.text)
            affiliation = ", ".join(affiliation_data)

            affiliations[aff_id] = affiliation
        return affiliations

    def combine_authors_affiliations(self, authors, affiliations):
        results = []
        for author in authors:
            matched_affiliations = []
            for ref_id in author["ref_ids"]:
                if ref_id in affiliations.keys():
                    matched_affiliations.append(affiliations[ref_id])
            results.append(
                {"name": author["name"], "affiliations": matched_affiliations}
            )
        return results
