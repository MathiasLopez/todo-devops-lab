from uuid import UUID

SYSTEM_USER_ID = UUID("00000000-0000-0000-0000-000000000000")

SYSTEM_PRIORITIES = [
    {
        "id": UUID("00000000-0000-0000-0000-00000000000a"),
        "title": "Low",
        "color": "#22C55E",
    },
    {
        "id": UUID("00000000-0000-0000-0000-00000000000b"),
        "title": "Medium",
        "color": "#EAB308",
    },
    {
        "id": UUID("00000000-0000-0000-0000-00000000000c"),
        "title": "High",
        "color": "#EF4444",
    },
]

SYSTEM_PRIORITY_IDS = {priority["id"] for priority in SYSTEM_PRIORITIES}
