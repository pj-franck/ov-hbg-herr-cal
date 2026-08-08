"""Läs matchdata från Svenska Handbollförbundets offentliga Profixio-sidor."""

from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
import json
import re
from http.cookiejar import CookieJar
from urllib.error import HTTPError, URLError
from urllib.request import HTTPCookieProcessor, Request, build_opener


DEFAULT_TIMEOUT_SECONDS = 30
MAX_LOAD_MORE_REQUESTS = 10
DEFAULT_LEAGUE_SCHEDULE_URL = (
    "https://www.profixio.com/app/lx/competition/leagueid28137/teams/1584193"
)


class SourceError(RuntimeError):
    """Raised when the official schedule cannot be read safely."""


@dataclass(frozen=True)
class Match:
    """A match as published by Profixio; no calendar-specific fields yet."""

    match_id: str
    date: str
    time: str | None
    home_team: str
    away_team: str
    venue: str | None
    source_url: str
    notes: str | None = None


class _ScheduleParser(HTMLParser):
    """Parse the small stable subset of Profixio's server-rendered markup."""

    def __init__(self, source_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.source_url = source_url
        self.matches: list[Match] = []
        self._match: dict[str, object] | None = None
        self._li_depth = 0
        self._anchor: tuple[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "li" and (key := attributes.get("wire:key", "")).startswith("listkamp_"):
            self._match = {"id": key.removeprefix("listkamp_"), "text": [], "teams": []}
            self._li_depth = 1
            return
        if self._match is not None:
            if tag == "li":
                self._li_depth += 1
            if tag == "a":
                self._anchor = (attributes.get("href", ""), "")

    def handle_endtag(self, tag: str) -> None:
        if self._match is None:
            return
        if tag == "a" and self._anchor is not None:
            href, label = self._anchor
            label = " ".join(label.split())
            if "/teams/" in href and label:
                self._match["teams"].append(label)  # type: ignore[union-attr]
            elif "/facility/" in href and label:
                self._match["venue"] = label
            self._anchor = None
        if tag == "li":
            self._li_depth -= 1
            if self._li_depth == 0:
                self._finish_match()
                self._match = None

    def handle_data(self, data: str) -> None:
        if self._match is None:
            return
        self._match["text"].append(data)  # type: ignore[union-attr]
        if self._anchor is not None:
            href, label = self._anchor
            self._anchor = (href, label + data)

    def _finish_match(self) -> None:
        assert self._match is not None
        text = " ".join(" ".join(self._match["text"]).split())  # type: ignore[arg-type]
        date_match = re.search(r"\b\d{1,2}\s+(?:jan|feb|mar|apr|maj|jun|jul|aug|sep|okt|nov|dec)\s+\d{4}\b", text, re.I)
        teams: list[str] = self._match["teams"]  # type: ignore[assignment]
        if date_match is None or len(teams) < 2:
            return
        time_match = re.search(r"\b\d{1,2}:\d{2}\b", text)
        self.matches.append(
            Match(
                match_id=str(self._match["id"]),
                date=date_match.group(0),
                time=time_match.group(0) if time_match else None,
                home_team=teams[0],
                away_team=teams[1],
                venue=self._match.get("venue"),  # type: ignore[arg-type]
                source_url=self.source_url,
            )
        )


def parse_matches(html: str, source_url: str) -> list[Match]:
    """Extract the matches presently rendered by a Profixio schedule page."""
    parser = _ScheduleParser(source_url)
    parser.feed(html)
    parser.close()
    return parser.matches


def _livewire_metadata(html: str) -> tuple[str, str]:
    snapshot_match = re.search(r'wire:key="[^\"]*-schedule-[^\"]*" wire:snapshot="([^\"]+)"', html)
    csrf_match = re.search(r'data-csrf="([^\"]+)"', html)
    if snapshot_match is None or csrf_match is None:
        raise SourceError("Profixios sidformat saknar den data som krävs för att läsa alla matcher.")
    return unescape(snapshot_match.group(1)), csrf_match.group(1)


class ProfixioSource:
    """Fetch every match visible through one official Profixio team schedule URL."""

    def __init__(
        self,
        schedule_url: str = DEFAULT_LEAGUE_SCHEDULE_URL,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.schedule_url = schedule_url
        self.timeout_seconds = timeout_seconds

    def fetch_matches(self) -> list[Match]:
        """Fetch the initial page, then request every additional page of matches."""
        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        initial_url = self._all_matches_url()
        html = self._get(opener, initial_url)
        previous_count = len(parse_matches(html, self.schedule_url))
        snapshot, csrf_token = _livewire_metadata(html)

        for _ in range(MAX_LOAD_MORE_REQUESTS):
            response = self._load_more(opener, snapshot, csrf_token)
            component = response["components"][0]
            rendered_html = component["effects"].get("html", "")
            matches = parse_matches(rendered_html, self.schedule_url)
            if len(matches) <= previous_count:
                return matches
            previous_count = len(matches)
            snapshot = component["snapshot"]

        raise SourceError("Profixio returnerade fler matchsidor än den tillåtna säkerhetsgränsen.")

    def _all_matches_url(self) -> str:
        separator = "&" if "?" in self.schedule_url else "?"
        return f"{self.schedule_url}{separator}t=schedule&f=all"

    def _get(self, opener: object, url: str) -> str:
        request = Request(url, headers={"User-Agent": "ov-hbg-herr-cal/0.1"})
        try:
            with opener.open(request, timeout=self.timeout_seconds) as response:  # type: ignore[union-attr]
                return response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError) as error:
            raise SourceError(f"Kunde inte hämta Profixios spelschema: {error}") from error

    def _load_more(self, opener: object, snapshot: str, csrf_token: str) -> dict[str, object]:
        payload = json.dumps(
            {"components": [{"snapshot": snapshot, "updates": {}, "calls": [{"path": "", "method": "loadMore", "params": []}]}]}
        ).encode("utf-8")
        request = Request(
            "https://www.profixio.com/app/livewire/update",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Livewire": "true",
                "X-CSRF-TOKEN": csrf_token,
                "User-Agent": "ov-hbg-herr-cal/0.1",
            },
            method="POST",
        )
        try:
            with opener.open(request, timeout=self.timeout_seconds) as response:  # type: ignore[union-attr]
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError) as error:
            raise SourceError(f"Kunde inte läsa nästa sida från Profixio: {error}") from error
