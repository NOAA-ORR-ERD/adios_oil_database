

ERRORS = {"E001": "Record has no oil_id: every record must have an ID",
          "E002": "Crude Oils must have an API",
          "E003": "No Properties data at all",
          "E004": "Reference year: {} is not a valid year (between {} and {})"
          }

ERRORS = {code: (code + ": " + msg) for code, msg in ERRORS.items()}
