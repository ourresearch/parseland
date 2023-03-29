import requests


def get_parseland(doi):
    r = requests.get(f"https://parseland.herokuapp.com/parse-publisher?doi={doi}")
    return r.json()


def raw_affiliations_match(parseland, record):
    all_match = True
    if "authors" not in parseland.get("message"):
        for author in record["authorships"]:
            if author.get("raw_affiliation_string"):
                return False
        return True
    for parseland_author, openalex_author in zip(
        parseland["message"]["authors"], record["authorships"]
    ):
        # prep lists of affiliations
        parseland_affiliations = parseland_author.get("affiliations", [])
        openalex_affiliations = openalex_author.get("raw_affiliation_string", []).split(
            ";"
        )
        if openalex_affiliations and openalex_affiliations[0] == "":
            openalex_affiliations = []
        openalex_affiliations = [aff.strip().lower() for aff in openalex_affiliations]
        parseland_affiliations = [aff.strip().lower() for aff in parseland_affiliations]
        # remove trailing periods
        openalex_affiliations = [
            aff.rstrip(".").replace(",", "") for aff in openalex_affiliations
        ]
        parseland_affiliations = [
            aff.rstrip(".").replace(",", "") for aff in parseland_affiliations
        ]
        if parseland_affiliations != openalex_affiliations:
            all_match = False
            break
    return all_match


def affiliations_matched_to_institutions(record):
    for author in record["authorships"]:
        for institution in author.get("institutions", []):
            if not institution.get("id"):
                return False
    return True


def is_corresponding_matches(parseland, record):
    if "authors" not in parseland.get("message"):
        return True
    for parseland_author, openalex_author in zip(
        parseland["message"]["authors"], record["authorships"]
    ):
        if (
            str(parseland_author.get("is_corresponding")).lower()
            != str(openalex_author.get("is_corresponding")).lower()
        ):
            print(
                f"corresponding author mismatch for https://api.openalex.org/works/doi:{record['doi']}"
            )
            return False
    return True


def main():
    result = {}
    doi_count = 0
    for page in range(1, 11):
        url = f"https://api.openalex.org/works?page={page}&per-page=100&sample=1000&seed=23&filter=has_doi:true"
        r = requests.get(url)
        for record in r.json()["results"]:
            try:
                print(f"checking record {record['doi']}")
                doi_count += 1
                parseland = get_parseland(record["doi"])
                affiliations_match = raw_affiliations_match(parseland, record)
                institutions_match = affiliations_matched_to_institutions(record)
                corresponding_match = is_corresponding_matches(parseland, record)
                if affiliations_match:
                    result["affiliations_match"] = (
                        result.get("affiliations_match", 0) + 1
                    )
                if institutions_match:
                    result["institutions_match"] = (
                        result.get("institutions_match", 0) + 1
                    )
                if corresponding_match:
                    result["corresponding_match"] = (
                        result.get("corresponding_match", 0) + 1
                    )
            except Exception as e:
                print(f"error with doi {record['doi']}")
                continue
    print(f"total number of records: {doi_count}")
    print(result)


if __name__ == "__main__":
    main()
