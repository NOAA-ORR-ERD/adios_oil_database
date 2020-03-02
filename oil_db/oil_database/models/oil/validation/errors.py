

ERRORS = {"E001": "Record has no name: every record must have a name",
          "E002": "Crude Oils must have an API",
          "E003": "No Properties data at all",
          }

ERRORS = {code: (code + ": " + msg) for code, msg in ERRORS.items()}
