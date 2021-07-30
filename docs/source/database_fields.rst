######################
Fields in the database
######################

** Status **


** ID **

** Name **

** Location **

** Product Type **

** API **

** Score **

The completeness score (“Score”) in the data table is a rough assessment of how complete the data record is -- a higher score should result in more accurate oil fate modeling. The score is computed as follows:

The scores are normalized by the total possible score, resulting in a score between 0 and 100

Fresh oil: 
* One density or API. Score = 1
* Second density separated by temperature. Score = deltaT/40 but not greater than 0.5
* One viscosity. Score = 0.5
* Second viscosity at a different temperature. Score = maxDeltaT/40, but not greater than 0.5 
* Two Distillation cuts separated by mass or volume fraction.  Score = 3*maxDeltaFraction
* Fraction recovered <1. Score = 1.
One Weathered oil:
* Density. Score = 1
* Viscosity. Score = 1
One emulsion water content in any subsample. Score = 2.5

** Date **

** GNOME Suitable **

