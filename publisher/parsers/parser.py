import re
from abc import ABC, abstractmethod

from publisher.elements import AuthorAffiliations
from publisher.utils import remove_parents


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
        return {"authors": [], "abstract": None, "published_date": None,
                "genre": None}

    @abstractmethod
    def parse(self):
        pass

    def domain_in_canonical_link(self, domain):
        canonical_link = self.soup.find("link", {"rel": "canonical"})
        return (
                canonical_link
                and canonical_link.get("href")
                and domain in canonical_link.get("href")
        )

    def domain_in_meta_og_url(self, domain):
        meta_og_url = self.soup.find("meta", property="og:url")
        return (meta_og_url
                and meta_og_url.get("content")
                and domain in meta_og_url.get("content")
                )

    def text_in_meta_og_site_name(self, txt):
        meta_og_site_name = self.soup.find('meta', property='og:site_name')
        return (meta_og_site_name
                and meta_og_site_name.get("content")
                and txt in meta_og_site_name.get("content")
                )

    def parse_meta_tags(self, corresponding_tag=None, corresponding_class=None):
        results = []
        metas = self.soup.findAll("meta")

        corresponding_text = None
        if corresponding_tag and corresponding_class:
            corresponding_text = self.get_corresponding_text(
                corresponding_tag, corresponding_class
            )

        author_meta_keys = {'citation_author', 'dc.Creator'}

        result = None
        for meta in metas:
            if 'name' in meta.attrs and meta['name'] in author_meta_keys:
                if result:
                    # reset for next author
                    results.append(result)
                    result = None
                if not (name := meta.get('content')):
                    continue
                if corresponding_text and name.lower() in corresponding_text:
                    is_corresponding = True
                elif corresponding_text and name.lower() not in corresponding_text:
                    is_corresponding = False
                else:
                    is_corresponding = None
                result = {
                    "name": name,
                    "affiliations": [],
                    "is_corresponding": is_corresponding,
                }
            if meta.get("name", None) and meta[
                "name"] == "citation_author_institution":
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
                        "meta", {
                            meta_property_name: re.compile(f"^{meta_tag_name}$",
                                                           re.I)}
                ):
                    if description := meta_tag.get("content", '').strip():
                        if (
                                len(description) > 200
                                and not description.endswith("...")
                                and not description.endswith("…")
                                and not description.startswith("http")
                        ):
                            description = re.sub(
                                r"^abstract[:.]?\s*", "", description,
                                flags=re.I
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
                    is_corresponding=author.is_corresponding,
                )
            )
        return results

    def format_ids(self, ids, chars_to_ignore=None):
        ids_cleaned = ids.strip()
        if chars_to_ignore:
            for char in chars_to_ignore:
                ids_cleaned = ids_cleaned.replace(f",{char}", "").replace(
                    f"{char}", "")
        ids_split = ids_cleaned.split(",")
        aff_ids = []
        for aff_id in ids_split:
            if aff_id and aff_id.isdigit():
                aff_ids.append(int(aff_id))
        return aff_ids

    def fallback_mark_corresponding_authors(self, authors):
        def func(tag):
            for attr, value in tag.attrs.items():
                if ('author' in str(value).lower() and
                        tag.select_one('a[href*=mailto]')):
                    return True
            return False

        tags = self.soup.find_all(func)

        # Return only smallest tags, we don't want any tags with class*= authors that may contain multiple author names
        final_tags = remove_parents(tags)

        for tag in final_tags:
            tag_str = str(tag)
            for author in authors:
                if author['name'] in tag_str:
                    author['is_corresponding'] = True
                elif ',' in author['name']:
                    if all([name.strip(' ') in tag_str for name in
                            author['name'].split(',')]):
                        author['is_corresponding'] = True
        return authors

    def fallback_parse_abstract(self):
        for tag in self.soup.find_all():
            for attr, value in tag.attrs.items():
                if 'abstract' in str(value).lower():
                    for desc in tag.descendants:
                        if len(desc.text) > 100 and desc.name in {'p', 'div', 'span', 'section', 'article'}:
                            return re.sub('^abstract', '', desc.text, flags=re.IGNORECASE)
        return None

    test_cases = []
