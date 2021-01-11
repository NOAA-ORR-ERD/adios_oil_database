"""
warnings.py

All the warnings
"""

WARNINGS = {"W001": "Record name: {} is not very descriptive",
            "W002": "Record has no product type",
            "W003": '"{}" is not a valid product type. Options are: {}',
            "W004": "No api value provided",
            "W005": "API value: {api} seems unlikely",
            "W006": "No density values provided",
            "W007": "No distillation data provided",
            "W008": "No reference year provided",
            }

WARNINGS = {code: (code + ": " + msg) for code, msg in WARNINGS.items()}

