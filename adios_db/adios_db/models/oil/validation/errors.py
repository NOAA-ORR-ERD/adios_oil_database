

ERRORS = {
          # E01* : meta data related
          "E010": "Record has no oil_id: every record must have an ID",
          "E011": ("Record has invlid oil_id: every record must have a valid ID. "
                   "{} is not valid"),
          "E012": "Reference year: {} is not a valid year (between {} and {})",
          # E03* -- physical properties related
          "E030": "Oils must have an API",
          "E031": "No Properties data at all",
          }

ERRORS = {code: (code + ": " + msg) for code, msg in ERRORS.items()}
