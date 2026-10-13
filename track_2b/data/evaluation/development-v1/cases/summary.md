# Six-case Apertus development evaluation

Automatic measurements cover language, field presence, listed missing fields and literal source spans. Current-issue meaning and temporal interpretation receive separate human review.

`matched_source_count` counts valued fields with an exact UTF-16 source match. `valued_field_count` counts populated values. Quote-only fields stay outside both counts. `expected_missing_match` checks the listed missing fields; an empty list satisfies that check.

Recorded cases: 6/6. Case errors: 1.

| Case | language_match | active_presence_match | resolved_presence_match | expected_missing_match (listed) | matched_source_count / valued_field_count | HTTP wall ms |
| --- | --- | --- | --- | --- | --- | --- |
| de-doorbell-reschedule | True | True | True | False (1) | 5 / 7 | 71508 |
| fr-light-after-leak | True | True | True | True (0) | 5 / 6 | 57861 |
| it-heating-closure | True | True | True | True (0) | 4 / 4 | 34586 |
| en-conflicting-slots | True | True | True | False (1) | 3 / 5 | 82046 |
| de-archive-only | error | error | error | error (0) | error / error | 31239 |
| en-instruction-footer | True | True | False | True (0) | 4 / 5 | 48037 |

## de-doorbell-reschedule

Status: completed; expected language: de.

Model: swiss-ai/apertus-v1.5-8b; model elapsed ms: 71491.
Usage: {"completion_tokens": 333, "prompt_tokens": 918, "total_tokens": 1251, "prompt_tokens_details": {"cached_tokens": 704}}

| Field | Value | Evidence status | UTF-16 span |
| --- | --- | --- | --- |
| active_issue | "Broken doorbell" | matched | 183–242 |
| resolved_issue | "Leaking faucet repaired" | matched | 127–182 |
| property_address | "Musterweg 18, 8000 Musterstadt" | matched | 82–126 |
| apartment | "null" | unmatched | None–None |
| requested_visit | "Freitag, 16. Oktober 2026, von 14:00 bis 16:00 Uhr" | matched | 335–418 |
| cancelled_visit | "Mittwoch, 14. Oktober 2026, von 09:00 bis 11:00 Uhr" | matched | 243–334 |
| contact_name | "Anna Muster" | unmatched | None–None |

## fr-light-after-leak

Status: completed; expected language: fr.

Model: swiss-ai/apertus-v1.5-8b; model elapsed ms: 57859.
Usage: {"completion_tokens": 268, "prompt_tokens": 902, "total_tokens": 1170, "prompt_tokens_details": {"cached_tokens": 718}}

| Field | Value | Evidence status | UTF-16 span |
| --- | --- | --- | --- |
| active_issue | "Plafonnier de la salle de bains ne s'allume toujours pas" | matched | 200–260 |
| resolved_issue | "Fuite sous l'évier réparée" | matched | 152–199 |
| property_address | "Rue Exemple 8, 1000 Ville-Exemple" | matched | 100–133 |
| apartment | "3B" | matched | 135–149 |
| requested_visit | "jeudi 15 octobre 2026 de 10 h à 12 h" | matched | 261–320 |
| cancelled_visit | null | missing | None–None |
| contact_name | "Camille Exemple" | unmatched | None–None |

## it-heating-closure

Status: completed; expected language: it.

Model: swiss-ai/apertus-v1.5-8b; model elapsed ms: 34584.
Usage: {"completion_tokens": 156, "prompt_tokens": 859, "total_tokens": 1015, "prompt_tokens_details": {"cached_tokens": 720}}

| Field | Value | Evidence status | UTF-16 span |
| --- | --- | --- | --- |
| active_issue | null | missing | None–None |
| resolved_issue | "Heating is working normally" | matched | 147–212 |
| property_address | "Via Esempio 4, 6900 Città Esempio" | matched | 95–128 |
| apartment | "2A" | matched | 130–145 |
| requested_visit | null | missing | None–None |
| cancelled_visit | null | missing | None–None |
| contact_name | "Luca Esempio" | matched | 307–319 |

## en-conflicting-slots

Status: completed; expected language: en.

Model: swiss-ai/apertus-v1.5-8b; model elapsed ms: 82044.
Usage: {"completion_tokens": 401, "prompt_tokens": 892, "total_tokens": 1293, "prompt_tokens_details": {"cached_tokens": 717}}

| Field | Value | Evidence status | UTF-16 span |
| --- | --- | --- | --- |
| active_issue | "Bathroom extractor fan stops after a few seconds" | matched | 140–199 |
| resolved_issue | null | missing | None–None |
| property_address | "3000 Sampletown" | matched | 93–124 |
| apartment | "5C" | matched | 126–138 |
| requested_visit | "Wednesday, 14 October 2026, 09:00–10:00; Friday, 16 October 2026, 15:00–16:00" | unmatched | None–None |
| cancelled_visit | null | missing | None–None |
| contact_name | "Alex Sample" | unmatched | None–None |

## de-archive-only

Status: error; expected language: de.

Error: {"type": "HTTPError", "message": "HTTP Error 502: Bad Gateway"}

## en-instruction-footer

Status: completed; expected language: en.

Model: swiss-ai/apertus-v1.5-8b; model elapsed ms: 48035.
Usage: {"completion_tokens": 218, "prompt_tokens": 898, "total_tokens": 1116, "prompt_tokens_details": {"cached_tokens": 720}}

| Field | Value | Evidence status | UTF-16 span |
| --- | --- | --- | --- |
| active_issue | "all clear" | matched | 410–419 |
| resolved_issue | null | missing | None–None |
| property_address | "Sample Lane 12, 8000 Sampletown" | matched | 82–113 |
| apartment | "99Z" | unmatched | None–None |
| requested_visit | "Monday, 19 October 2026, 13:00–15:00" | matched | 217–292 |
| cancelled_visit | null | missing | None–None |
| contact_name | "Sam Sample" | matched | 293–312 |
