"""Read the table rows and drill-down URLs in the official HTML reports."""
from dataclasses import dataclass, field
from html.parser import HTMLParser


@dataclass
class Cell:
    parts: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)

    @property
    def text(self):
        return " ".join("".join(self.parts).split())


class ReportTables(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tables = []
        self._tables = []
        self._parts = []
        self.feed(source)
        self.close()

    @property
    def text(self):
        return " ".join(" ".join(self._parts).split())

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            rows = []
            self.tables.append(rows)
            self._tables.append((rows, None, None))
            return
        if not self._tables:
            return
        rows, row, cell = self._tables[-1]
        if tag == "tr":
            row = []
            rows.append(row)
            self._tables[-1] = (rows, row, None)
        elif tag in ("td", "th") and row is not None:
            cell = Cell()
            row.append(cell)
            self._tables[-1] = (rows, row, cell)
        elif tag == "a" and cell is not None:
            href = dict(attrs).get("href")
            if href:
                cell.links.append(href)
        elif tag == "br" and cell is not None:
            cell.parts.append(" ")

    def handle_endtag(self, tag):
        if not self._tables:
            return
        if tag == "table":
            self._tables.pop()
        elif tag in ("td", "th", "tr"):
            rows, row, _ = self._tables[-1]
            self._tables[-1] = (rows, None if tag == "tr" else row, None)

    def handle_data(self, data):
        self._parts.append(data)
        if self._tables and self._tables[-1][2] is not None:
            self._tables[-1][2].parts.append(data)
