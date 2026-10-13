# Authored examples and expected annotations

`cases.json` contains six synthetic maintenance-inbox examples written for HausPost. All names, addresses, tenants and correspondence are fictional. These are authored examples and expected annotations; model responses will be collected separately through CI.

Each letter separates its received date, current message and dated quoted history. Language codes use `de`, `fr`, `it` and `en`.

| Case | Language | Purpose |
| --- | --- | --- |
| `de-doorbell-reschedule` | German | Demo: repaired tap, active doorbell fault, cancelled Wednesday visit, Friday request, missing apartment |
| `fr-light-after-leak` | French | Demo: repaired leak, active bathroom light fault, supplied apartment |
| `it-heating-closure` | Italian | Demo: heating recovered and closure requested; active issue is empty |
| `en-conflicting-slots` | English | Difficult case: mutually exclusive visit requests need clarification |
| `de-archive-only` | German | Current administrative request; March repair complaint stays in quoted history |
| `en-instruction-footer` | English | Difficult case: an embedded instruction footer attempts to replace maintenance facts |

## Annotation contract

- `expected.active_issue_terms` and `resolved_issue_terms` describe the current message's maintenance meaning in English. Empty lists mark an absent current category. The archive-only case leaves both lists empty because its current request concerns receipt of a rent-payment document.
- `required_missing` names fields that need a follow-up question. The German demo needs `apartment`; the conflicting-slots case needs `requested_visit` clarification.
- `source_quotes` locates each field in the input. Every populated quote is one exact, unique, continuous substring of that letter. `null` marks absent current-field evidence.
- `example` is a hand-authored illustrative extraction using the seven field keys. Values contain English summaries or the supplied address, name and visit time. It serves the offline demo and expected-behaviour review.
- The conflicting visit field deliberately has `value: null` with its full contradictory passage retained as `quote`. A follow-up question settles the visit. All visit values are tenant proposals or cancellations; scheduling confirmation remains a separate action.
- Quoted history supplies context. Repairs reported as resolved remain resolved, and the copied instruction footer remains input text. Human review confirms source-linked fields before a work-order draft or clarification is exported.

Local validation checks six records, seven field keys, the 220-word limit, and exact unique quote matching. These checks validate sample structure and field locations. Actual model extraction quality is measured with separately saved responses.

## Licence

The synthetic case text and expected annotations are made available under the [Community Data License Agreement – Permissive 2.0](LICENSE). `recorded-runs.json` stores separately identified outputs from real Apertus runs as they are collected.
