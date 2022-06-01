from abc import ABC, abstractmethod

from repository.elements import AuthorAffiliations


class RepositoryParser(ABC):
    def __init__(self, soup):
        self.soup = soup

    @property
    @abstractmethod
    def parser_name(self):
        pass

    @abstractmethod
    def is_correct_parser(self):
        pass

    @abstractmethod
    def authors_found(self):
        pass

    @staticmethod
    def no_authors_output():
        return []

    @abstractmethod
    def parse(self):
        pass

    def domain_in_canonical_link(self, domain):
        canonical_link = self.soup.find("link", {"rel": "canonical"})
        if (
            canonical_link
            and canonical_link.get("href")
            and domain in canonical_link.get("href")
        ):
            return True

    def domain_in_meta_og_url(self, domain):
        meta_og_url = self.soup.find("meta", property="og:url")
        if (
            meta_og_url
            and meta_og_url.get("content")
            and domain in meta_og_url.get("content")
        ):
            return True

    def parse_meta_tags(self):
        results = []
        metas = self.soup.findAll("meta")

        result = None
        for meta in metas:
            if meta.get("name") == "citation_author":
                if result:
                    # reset for next author
                    results.append(result)
                name = meta["content"].strip()
                result = {
                    "name": name,
                    "affiliations": [],
                    "is_corresponding_author": False,
                }
            if result and meta.get("name") == "citation_author_institution":
                result["affiliations"].append(meta["content"].strip())

        # append name from last loop
        if result:
            results.append(result)

        return results

    @staticmethod
    def format_name(name):
        return " ".join(reversed(name.split(", ")))

    @staticmethod
    def merge_authors_affiliations(authors, affiliations):
        results = []
        for author in authors:
            author_affiliations = []

            # scenario 1 affiliations with ids
            for aff_id in author.aff_ids:
                for aff in affiliations:
                    if aff_id == aff.aff_id:
                        author_affiliations.append(str(aff.organization))

            # scenario 2 affiliations with no ids (applied to all authors)
            for aff in affiliations:
                if len(author.aff_ids) == 0 and aff.aff_id is None:
                    author_affiliations.append(str(aff.organization))

            results.append(
                AuthorAffiliations(name=author.name, affiliations=author_affiliations)
            )
        return results

    test_cases = []
