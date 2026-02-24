"""Transform a Carl Nielsen Works MEI document into a WorkCreate-style payload."""

import argparse
import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, TypedDict
from urllib.request import urlopen
from xml.etree import ElementTree

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.inputs.credit_create import CreditCreate
from music_catalogue.models.inputs.genre_create import GenreCreate
from music_catalogue.models.inputs.performance_create import (
    PerformanceArtistCreate,
    PerformanceCreate,
    PerformanceWorkCreate,
)
from music_catalogue.models.inputs.person_create import PersonCreate
from music_catalogue.models.inputs.work_create import WorkCreate
from music_catalogue.models.responses.genres import Genre
from music_catalogue.models.responses.performances import Performance
from music_catalogue.models.responses.persons import Person
from music_catalogue.models.responses.works import Work

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


class ExtractedPerformer(TypedDict):
    name: str
    role: str


class ExtractedPerformance(TypedDict):
    date: Optional[str] = None
    venue: Optional[str] = None
    city: Optional[str] = None
    notes: Optional[str] = None
    performers: Optional[List[ExtractedPerformer]] = None


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
    genres: Optional[List[str]] = None
    performances: Optional[List[ExtractedPerformance]] = None


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


def parse_genres(work_element: ElementTree.Element) -> List[str]:
    terms = work_element.findall(".//mei:classification/mei:termList/mei:term", MEI_NS)
    return [name for t in terms if (name := _strip(t.text))]


def _parse_performer(pers_el: ElementTree.Element) -> Optional[ExtractedPerformer]:
    raw = _strip(pers_el.text)
    if not raw:
        return None
    xml_role = pers_el.get("role", "performer")

    # For performers, the text can contain "Name, instrument"
    if xml_role == "performer" and ", " in raw:
        name, instrument = raw.rsplit(", ", 1)
        return ExtractedPerformer(name=name.strip(), role=instrument.strip())

    return ExtractedPerformer(name=raw, role=xml_role)


def parse_performances(work_element: ElementTree.Element) -> List[ExtractedPerformance]:
    events = work_element.findall(
        ".//mei:expressionList/mei:expression/mei:history/mei:eventList[@type='performances']/mei:event", MEI_NS
    )
    performances: List[ExtractedPerformance] = []
    for event in events:
        date_el = event.find("mei:date", MEI_NS)
        venue_el = event.find("mei:geogName[@role='venue']", MEI_NS)
        place_el = event.find("mei:geogName[@role='place']", MEI_NS)
        desc_el = event.find("mei:desc", MEI_NS)

        performers = [p for pers_el in event.findall("mei:persName", MEI_NS) if (p := _parse_performer(pers_el))]

        performances.append(
            ExtractedPerformance(
                date=date_el.get("isodate") if date_el is not None else None,
                venue=_strip(venue_el.text) if venue_el is not None else None,
                city=_strip(place_el.text) if place_el is not None else None,
                notes=_strip(ElementTree.tostring(desc_el, method="text", encoding="unicode"))
                if desc_el is not None
                else None,
                performers=performers or None,
            )
        )
    return performances


def _build_performance_name(title: str, perf: ExtractedPerformance) -> str:
    parts = [title]
    if perf.get("venue"):
        parts.append(f"at {perf['venue']}")
    elif perf.get("city"):
        parts.append(f"in {perf['city']}")
    if perf.get("date"):
        parts.append(f"({perf['date']})")
    return " ".join(parts)


def _parse_isodate(isodate: Optional[str] = None) -> Optional[str]:
    """Parse an ISO date string into a date."""
    if not isodate:
        return None
    cleaned = isodate.strip()
    try:
        datetime.strptime(cleaned, "%Y-%m-%d")
        return cleaned
    except ValueError:
        return None


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
    genres = parse_genres(work_element)
    performances = parse_performances(work_element)
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
        genres=genres or None,
        performances=performances or None,
    )

    return work_payload


async def _resolve_person(name: str) -> Person:
    """Find an existing person by name, or create one."""
    matches = await Person.search(name)
    # If there's matches, get only exact ones and assume it's the first one
    exact = next((m for m in matches if m.name.lower() == name.lower()), None)
    if exact:
        return exact
    return await Person.create(PersonCreate(legal_name=name))


async def add_to_database(extracted_data: ExtractedWorkData) -> Work:
    # Check if there's already people with those legal names in the database
    credits = []
    for contributor in extracted_data.get("contributors", []):
        person = await _resolve_person(contributor["name"])
        credits.append(
            CreditCreate(person_id=person.id, role=contributor["role"], is_primary=contributor["is_primary"])
        )

    # Search or create genres, collect genre_ids
    genre_ids = []
    for genre_name in extracted_data.get("genres", []):
        matches = await Genre.search(genre_name)
        exact = next((g for g in matches if g.name.lower() == genre_name.lower()), None)
        if exact:
            genre_ids.append(exact.id)
        else:
            genre = await Genre.create(GenreCreate(name=genre_name))
            genre_ids.append(genre.id)

    work = await Work.create(
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
            genre_ids=genre_ids or None,
        )
    )

    # Link performances to the work, reusing existing ones when possible
    supabase = await get_supabase()
    for perf_data in extracted_data.get("performances", []):
        perf_date = _parse_isodate(perf_data.get("date"))
        venue = perf_data.get("venue")
        city = perf_data.get("city")

        existing = None
        if perf_date:
            query = supabase.table("performances").select("performance_id").eq("performance_date", perf_date)
            if venue:
                query = query.eq("venue", venue)
            elif city:
                query = query.eq("city", city)
            res = await query.execute()
            if res.data:
                existing = res.data[0]["performance_id"]

        if existing:
            # Add work to existing performance
            await supabase.table("performance_works").insert({"performance_id": existing, "work_id": work.id}).execute()
        else:
            # Resolve performers to person IDs
            artists = []
            for performer in perf_data.get("performers") or []:
                person = await _resolve_person(performer["name"])
                artists.append(PerformanceArtistCreate(person_id=person.id, role=performer["role"]))

            # Create new performance
            name = _build_performance_name(extracted_data["title"], perf_data)
            await Performance.create(
                PerformanceCreate(
                    name=name,
                    performance_date=perf_date,
                    venue=venue,
                    city=city,
                    notes=perf_data.get("notes"),
                    works=[PerformanceWorkCreate(work_id=work.id)],
                    artists=artists or None,
                )
            )

    return work


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
