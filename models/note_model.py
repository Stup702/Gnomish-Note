from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid

NOTE_TYPE_EMERGENCY = "emergency"
NOTE_TYPE_NORMAL = "normal"

@dataclass
class NoteModel:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    note_type: str = NOTE_TYPE_NORMAL
    content_html: str = ""
    color: str = "#fdf5c9"
    font_color: str = "#333333"
    font_family: str = "Sans Serif"
    font_size: int = 11
    pos_x: int = 100
    pos_y: int = 100
    width: int = 280
    height: int = 320
    minimized: bool = False
    collapsed: bool = False
    opacity: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> 'NoteModel':
        return cls(
            id=d.get("id", str(uuid.uuid4())),
            title=d.get("title", ""),
            note_type=d.get("note_type", NOTE_TYPE_NORMAL),
            content_html=d.get("content_html", ""),
            color=d.get("color", "#fdf5c9"),
            font_color=d.get("font_color", "#333333"),
            font_family=d.get("font_family", "Sans Serif"),
            font_size=d.get("font_size", 11),
            pos_x=d.get("pos_x", 100),
            pos_y=d.get("pos_y", 100),
            width=d.get("width", 280),
            height=d.get("height", 320),
            minimized=d.get("minimized", False),
            collapsed=d.get("collapsed", False),
            opacity=float(d.get("opacity", 1.0)),
            created_at=d.get("created_at", datetime.now().isoformat())
        )
