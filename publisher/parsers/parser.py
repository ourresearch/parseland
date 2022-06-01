import re
from abc import ABC, abstractmethod

from publisher.elements import Author, AuthorAffiliations


class PublisherParser(ABC):
    def __init__(self, soup):
        self.soup = soup

    @property
    @abstractmethod
    def parser_name(self):
        pass

    @abstractmethod
    def is_publisher_specific_parser(self):
        pass

    @abstractmethod
    def authors_found(self):
        pass

    @staticmethod
    def no_authors_output():
        return {"authors": [], "abstract": None, "published_date": None, "genre": None}

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

    def parse_meta_tags(self, corresponding_tag=None, corresponding_class=None):
        results = []
        metas = self.soup.findAll("meta")

        corresponding_text = None
        if corresponding_tag and corresponding_class:
            corresponding_text = self.get_corresponding_text(
                corresponding_tag, corresponding_class
            )

        result = None
        for meta in metas:
            if meta.get("name", None) and meta["name"] == "citation_author":
                if result:
                    # reset for next author
                    results.append(result)
                    result = None
                name = self.format_name(meta["content"])
                if corresponding_text and name.lower() in corresponding_text:
                    is_corresponding = True
                else:
                    is_corresponding = False
                result = {
                    "name": name,
                    "affiliations": [],
                    "is_corresponding_author": is_corresponding,
                }
            if meta.get("name", None) and meta["name"] == "citation_author_institution":
                if meta.get("content") and meta["content"].strip():
                    result["affiliations"].append(meta["content"].strip())

        # append name from last loop
        if result:
            results.append(result)

        return results

    def parse_abstract_meta_tags(self):
        meta_tag_names = [
            "citation_abstract",
            "og:description",
            "dc.description",
            "description",
        ]
        meta_property_names = ["property", "name"]

        for meta_tag_name in meta_tag_names:
            for meta_property_name in meta_property_names:
                if meta_tag := self.soup.find(
                    "meta", {meta_property_name: re.compile(f"^{meta_tag_name}$", re.I)}
                ):
                    if description := meta_tag.get("content").strip():
                        if (
                            len(description) > 200
                            and not description.endswith("...")
                            and not description.endswith("…")
                            and not description.startswith("http")
                        ):
                            description = re.sub(
                                r"^abstract[:.]?\s*", "", description, flags=re.I
                            )
                            return description

        return None

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
                AuthorAffiliations(
                    name=author.name,
                    affiliations=author_affiliations,
                    is_corresponding_author=author.is_corresponding_author,
                )
            )
        return results

    def format_ids(self, ids, chars_to_ignore=None):
        ids_cleaned = ids.strip()
        if chars_to_ignore:
            for char in chars_to_ignore:
                ids_cleaned = ids_cleaned.replace(f",{char}", "").replace(f"{char}", "")
        ids_split = ids_cleaned.split(",")
        aff_ids = []
        for aff_id in ids_split:
            if aff_id and aff_id.isdigit():
                aff_ids.append(int(aff_id))
        return aff_ids

    test_cases = []
