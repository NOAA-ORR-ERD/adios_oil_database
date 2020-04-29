

ERRORS = {"E001": "Record has no oil_id: every record must have an ID",
          "E002": "Crude Oils must have an API",
          "E003": "No Properties data at all",
          }

ERRORS = {code: (code + ": " + msg) for code, msg in ERRORS.items()}
