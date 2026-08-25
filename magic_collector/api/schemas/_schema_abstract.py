UUID_REGEX = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


ROOT_SCHEMA = {
    "type": "object",
    "properties": {
        "meta": {"$ref": "#/definitions/Meta"},
        "data": {"$ref": "#/definitions/Data"},
    },
    "required": ["data", "meta"],
    "title": "MTGJSONv5",
}

META_SCHEMA = {
    "type": "object",
    "properties": {
        "date": {"type": "string", "format": "date"},
        "version": {"type": "string"},
    },
    "required": ["date", "version"],
    "title": "Meta",
}
