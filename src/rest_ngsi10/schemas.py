SUBSCRIPTION_CREATION_SCHEMA = {
    "type": "object",
    "required": ["entities", "reference", "duration"],
    "properties": {
        "entities" : {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type", "id"],
                "properties": {
                    "type": {"type" : "string"},
                    "id": {"type" : "string"},
                },
            },
        },
        "attributes": {
            "type": "array",
            "items": {"type": "string"},
        },
        "reference": {"type" : "string"},
        "duration": {"type" : "string"},
        "notifyConditions": {
            "type": "array",
            "required": ["type"],
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type" : "string",
                        "enum": ["ONCHANGE"],
                    },
                    "condValues": {
                        "type" : "array",
                        "items": {"type" : "string"},
                    },
                },
            },
        },
    },
}

SUBSCRIPTION_UPDATE_SCHEMA = {
    "type": "object",
    "required": ["subscriptionId"],
    "properties": {
        "subscriptionId": {"type" : "string"},
        "duration": {"type" : "string"},
        "notifyConditions": {
            "type": "array",
            "required": ["type"],
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type" : "string",
                        "enum": ["ONCHANGE"],
                    },
                    "condValues": {
                        "type" : "array",
                        "items": {"type" : "string"},
                    },
                },
            },
        },
    },
}

GET_CONTEXT_SCHEMA = {
    "type": "object",
    "required": ["entities"],
    "properties": {
        "attributes": {
            "type" : "array",
            "items": {"type": "string"}
        },
        "entities": {
            "type": "array",
            "required": ["type", "id"],
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type" : "string"},
                    "id": {"type" : "string"},
                },
            },
        },
    },
}


SUBSCRIPTION_CREATION_EXAMPLE = {
    "entities": [
        {
            "type": "Room",
            # "isPattern": "false",
            "id": "Room1"
        }
    ],
    "attributes": [
        "temperature"
    ],
    "reference": "http://localhost:1028/accumulate",
    "duration": "P1M",
    "notifyConditions": [
        {
            "type": "ONCHANGE",
            "condValues": [
                "PT10S"
            ]
        }
    ]
}

SUBSCRIPTION_UPDATE_EXAMPLE = {
    "subscriptionId": "51c04a21d714fb3b37d7d5a7",
    "notifyConditions": [
        {
            "type": "ONCHANGE",
            "condValues": [
                "PT5S"
            ]
        }
    ]
}
