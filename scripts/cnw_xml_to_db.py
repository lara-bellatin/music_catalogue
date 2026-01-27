"""Transform a Carl Nielsen Works MEI document into a WorkCreate-style payload."""

import argparse
import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple, TypedDict
from urllib.request import urlopen
from xml.etree import ElementTree

from music_catalogue.crud import persons, works
from music_catalogue.models.persons import PersonCreate
from music_catalogue.models.works import Work, WorkCreate, WorkCreditCreate

MEI_NS = {"mei": "http://www.music-encoding.org/ns/mei"}


class ExtractedContributor(TypedDict):
    name: str
    role: str
    is_primary: bool


class ExtractedIdentifier(TypedDict):
    label: str
    value: str


class ExtractedTitle(TypedDict):
    title: str
    language: str
    type: str


class ExtractedExternalLink(TypedDict):
    label: str
    url: str
    source_verified: bool = True


class ExtractedWorkData(TypedDict):
    title: str
    language: str
    titles: Optional[List[ExtractedTitle]] = None
    identifiers: Optional[List[ExtractedIdentifier]] = None
    origin_year_start: Optional[int] = None
    origin_year_end: Optional[int] = None
    history: Optional[str] = None
    contributors: Optional[List[ExtractedContributor]] = None
    external_links: Optional[List[Dict[str, Any]]] = None


def _strip(text: Optional[str]) -> Optional[str]:
    return text.strip() if text and text.strip() else None


def parse_titles(work_element: ElementTree.Element) -> Tuple[Optional[str], List[ExtractedTitle]]:
    titles: List[Dict[str, Any]] = []
    primary_title: Optional[str] = None

    for title in work_element.findall("mei:title", MEI_NS):
        value = _strip(title.text)
        lang = title.get("{http://www.w3.org/XML/1998/namespace}lang")
        title_type = title.get("type")

        if value:
            if not title_type and primary_title is None:
                primary_title = value
            titles.append(ExtractedTitle(title=value, language=lang, type=title_type or "primary"))

    return primary_title, titles


def parse_identifiers(work_element: ElementTree.Element) -> List[ExtractedIdentifier]:
    identifiers: List[Dict[str, Any]] = []
    for identifier in work_element.findall("mei:identifier", MEI_NS):
        label = identifier.get("label")
        value = _strip(identifier.text)
        if value:
            identifiers.append(ExtractedIdentifier(label=label, value=value))
    return identifiers


def parse_language(root: ElementTree.Element) -> Optional[str]:
    language = root.find(".//mei:langUsage/mei:language", MEI_NS)
    if language is None:
        return None
    return language.get("{http://www.w3.org/XML/1998/namespace}id") or _strip(language.text)


def parse_creation_dates(work_element: ElementTree.Element) -> Tuple[Optional[int], Optional[int]]:
    creation_dates = work_element.find("mei:creation/mei:date", MEI_NS)
    if creation_dates is None:
        return None, None

    def to_int(value: Optional[str]) -> Optional[int]:
        if not value:
            return None
        digits = value.replace("-", "-")
        try:
            return int(digits.split("-")[0])
        except ValueError:
            return None

    not_before = to_int(creation_dates.get("notbefore"))
    start_date = to_int(creation_dates.get("startdate"))
    not_after = to_int(creation_dates.get("notafter"))
    end_date = to_int(creation_dates.get("enddate"))
    return not_before or start_date, not_after or end_date


def parse_contributors(work_element: ElementTree.Element) -> List[ExtractedContributor]:
    contributors = work_element.findall("mei:contributor/mei:persName", MEI_NS)
    if contributors is None:
        return None

    return [
        ExtractedContributor(
            name=_strip(contributor.text),
            role=_strip(contributor.get("role")),
            is_primary=contributor.get("role") == "composer" if _strip(contributor.get("role")) else False,
        )
        for contributor in contributors
    ]


def parse_history(work_element: ElementTree.Element) -> Optional[str]:
    history_el = work_element.find("mei:history/mei:p", MEI_NS)
    if history_el is None:
        return None
    return _strip(ElementTree.tostring(history_el, method="text", encoding="unicode"))


def transform_mei(source: str) -> Dict[str, Any]:
    with urlopen(source) as file:
        data = file.read()
    tree = ElementTree.ElementTree(ElementTree.fromstring(data))
    root = tree.getroot()

    work_element = root.find(".//mei:work", MEI_NS)
    if work_element is None:
        raise ValueError("No <work> element found in MEI document")

    title, titles = parse_titles(work_element)
    language = parse_language(root)
    identifiers = parse_identifiers(work_element)
    origin_year_start, origin_year_end = parse_creation_dates(work_element)
    history_text = parse_history(work_element)
    contributors = parse_contributors(work_element)
    external_link = ExtractedExternalLink(
        label="Catalogue of Carl Nielsen's Works",
        url=source,
        source_verified=True,
    )

    work_payload: Dict[str, Any] = ExtractedWorkData(
        title=title,
        language=language,
        titles=titles or None,
        identifiers=identifiers or None,
        origin_year_start=origin_year_start,
        origin_year_end=origin_year_end,
        history=history_text,
        contributors=contributors,
        external_links=[external_link],
    )

    return work_payload


async def add_to_database(extracted_data: ExtractedWorkData) -> Work:
    # Check if there's already people with those legal names in the database
    credits = []
    for contributor in extracted_data.get("contributors", []):
        possible_matches = await persons.search(contributor["name"])
        # If nothing found, create new person
        if not possible_matches:
            person = await persons.create(PersonCreate(legal_name=contributor["name"]))
        # If there's matches, assume it's the first one
        else:
            person = possible_matches[0]
        credits.append(
            WorkCreditCreate(person_id=person.id, role=contributor["role"], is_primary=contributor["is_primary"])
        )

    return await works.create(
        WorkCreate(
            title=extracted_data["title"],
            language=extracted_data["language"],
            titles=extracted_data["titles"],
            identifiers=extracted_data.get("identifiers"),
            origin_year_start=extracted_data.get("origin_year_start"),
            origin_year_end=extracted_data.get("origin_year_end"),
            notes=extracted_data.get("history"),
            external_links=extracted_data.get("external_links"),
            credits=credits or None,
        )
    )


async def main() -> None:
    parser = argparse.ArgumentParser(description="Convert MEI to WorkCreate JSON payload")
    parser.add_argument("mei_source", help="URL to the MEI XML file")
    parser.add_argument("--save", action="store_true", help="Whether or not to save the result to the database")
    args = parser.parse_args()

    payload = transform_mei(args.mei_source)
    print("Scanning..")
    print("Extracted Data:")
    print(json.dumps(payload, ensure_ascii=False))

    if args.save:
        print("\nAdding to Database...")
        work = await add_to_database(payload)
        print(f"Work created with ID: {work.id}")


if __name__ == "__main__":
    asyncio.run(main())
