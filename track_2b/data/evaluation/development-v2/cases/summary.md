# Six-case Apertus development evaluation

Automatic measurements cover language, field presence, listed missing fields and literal source spans. Current-issue meaning and temporal interpretation receive separate, labelled semantic review.

`matched_source_count` counts valued fields with an exact UTF-16 source match. `valued_field_count` counts populated values. Quote-only fields stay outside both counts. `expected_missing_match` checks the listed missing fields; an empty list satisfies that check.

Recorded cases: 6/6. Case errors: 0.

| Case | language_match | active_presence_match | resolved_presence_match | expected_missing_match (listed) | matched_source_count / valued_field_count | HTTP wall ms |
| --- | --- | --- | --- | --- | --- | --- |
| de-doorbell-reschedule | True | True | True | True (1) | 6 / 6 | 67398 |
| fr-light-after-leak | True | True | True | True (0) | 6 / 6 | 72967 |
| it-heating-closure | True | True | True | True (0) | 4 / 4 | 50068 |
| en-conflicting-slots | True | True | True | True (1) | 4 / 4 | 67707 |
| de-archive-only | True | True | False | True (0) | 4 / 4 | 54901 |
| en-instruction-footer | True | True | True | True (0) | 6 / 6 | 63486 |

## de-doorbell-reschedule

Status: completed; expected language: de.

Model: swiss-ai/apertus-v1.5-8b; model elapsed ms: 67376.
Usage: {"completion_tokens": 337, "prompt_tokens": 1430, "total_tokens": 1767, "prompt_tokens_details": {"cached_tokens": 1429}}

| Field | Value | Evidence status | UTF-16 span |
| --- | --- | --- | --- |
| active_issue | "Klingel funktioniert weiterhin nicht" | matched | 183–242 |
| resolved_issue | "Wasserhahn repariert" | matched | 127–182 |
| property_address | "Musterweg 18, 8000 Musterstadt" | matched | 82–126 |
| apartment | null | missing | None–None |
| requested_visit | "Freitag, 16. Oktober 2026, von 14:00 bis 16:00 Uhr" | matched | 335–418 |
| cancelled_visit | "Mittwoch, 14. Oktober 2026, von 09:00 bis 11:00 Uhr" | matched | 243–334 |
| contact_name | "Anna Muster" | matched | 419–449 |

## fr-light-after-leak

Status: completed; expected language: fr.

Model: swiss-ai/apertus-v1.5-8b; model elapsed ms: 72963.
Usage: {"completion_tokens": 282, "prompt_tokens": 1417, "total_tokens": 1699, "prompt_tokens_details": {"cached_tokens": 1203}}

| Field | Value | Evidence status | UTF-16 span |
| --- | --- | --- | --- |
| active_issue | "Plafonnier de la salle de bains ne s'allume toujours pas" | matched | 200–260 |
| resolved_issue | "Fuite sous l'évier réparée" | matched | 152–198 |
| property_address | "Rue Exemple 8, 1000 Ville-Exemple" | matched | 100–133 |
| apartment | "Appartement 3B" | matched | 135–149 |
| requested_visit | "jeudi 15 octobre 2026 de 10 h à 12 h" | matched | 261–387 |
| cancelled_visit | null | missing | None–None |
| contact_name | "Camille Exemple" | matched | 402–417 |

## it-heating-closure

Status: completed; expected language: it.

Model: swiss-ai/apertus-v1.5-8b; model elapsed ms: 50066.
Usage: {"completion_tokens": 180, "prompt_tokens": 1373, "total_tokens": 1553, "prompt_tokens_details": {"cached_tokens": 1205}}

| Field | Value | Evidence status | UTF-16 span |
| --- | --- | --- | --- |
| active_issue | null | missing | None–None |
| resolved_issue | "Radiators working normally" | matched | 147–212 |
| property_address | "Via Esempio 4, 6900 Città Esempio" | matched | 95–128 |
| apartment | "2A" | matched | 130–145 |
| requested_visit | null | missing | None–None |
| cancelled_visit | null | missing | None–None |
| contact_name | "Luca Esempio" | matched | 307–319 |

## en-conflicting-slots

Status: completed; expected language: en.

Model: swiss-ai/apertus-v1.5-8b; model elapsed ms: 67705.
Usage: {"completion_tokens": 258, "prompt_tokens": 1407, "total_tokens": 1665, "prompt_tokens_details": {"cached_tokens": 1202}}

| Field | Value | Evidence status | UTF-16 span |
| --- | --- | --- | --- |
| active_issue | "Bathroom extractor fan stops after a few seconds" | matched | 140–199 |
| resolved_issue | null | missing | None–None |
| property_address | "Sample Court 6, 3000 Sampletown" | matched | 93–124 |
| apartment | "Apartment 5C" | matched | 126–138 |
| requested_visit | null | missing | None–None |
| cancelled_visit | null | missing | None–None |
| contact_name | "Alex Sample" | matched | 419–430 |

## de-archive-only

Status: completed; expected language: de.

Model: swiss-ai/apertus-v1.5-8b; model elapsed ms: 54899.
Usage: {"completion_tokens": 189, "prompt_tokens": 1408, "total_tokens": 1597, "prompt_tokens_details": {"cached_tokens": 1203}}

| Field | Value | Evidence status | UTF-16 span |
| --- | --- | --- | --- |
| active_issue | null | missing | None–None |
| resolved_issue | "Door jammed; technician requested" | matched | 451–510 |
| property_address | "Musterallee 22, 4000 Musterstadt" | matched | 224–256 |
| apartment | "Wohnung 1D" | matched | 258–268 |
| requested_visit | null | missing | None–None |
| cancelled_visit | null | missing | None–None |
| contact_name | "Robin Muster" | matched | 400–412 |

## en-instruction-footer

Status: completed; expected language: en.

Model: swiss-ai/apertus-v1.5-8b; model elapsed ms: 63484.
Usage: {"completion_tokens": 235, "prompt_tokens": 1415, "total_tokens": 1650, "prompt_tokens_details": {"cached_tokens": 1205}}

| Field | Value | Evidence status | UTF-16 span |
| --- | --- | --- | --- |
| active_issue | "all clear" | matched | 410–419 |
| resolved_issue | "intercom repaired and working" | matched | 548–623 |
| property_address | "Sample Lane 12, 8000 Sampletown" | matched | 82–113 |
| apartment | "99Z" | matched | 115–127 |
| requested_visit | "Monday, 19 October 2026, 13:00–15:00" | matched | 217–292 |
| cancelled_visit | null | missing | None–None |
| contact_name | "Sam Sample" | matched | 302–312 |
