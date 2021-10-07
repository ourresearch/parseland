from abc import ABC, abstractmethod


class PublisherParser(ABC):
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
    def no_authors_ouput():
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
            if meta.get("name", None) and meta["name"] == "citation_author":
                if result:
                    # reset for next author
                    results.append(result)
                    result = None
                name = self.format_name(meta["content"])
                result = {
                    "name": name,
                    "affiliations": [],
                }
            if meta.get("name", None) and meta["name"] == "citation_author_institution":
                result["affiliations"].append(meta["content"])

        # append name from last loop
        if result:
            results.append(result)

        return results

    @staticmethod
    def format_name(name):
        return " ".join(reversed(name.split(", ")))

    @property
    def test_cases(self):
        return []
