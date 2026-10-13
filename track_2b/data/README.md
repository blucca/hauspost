# Authored examples and expected annotations

`cases.json` contains six synthetic maintenance-inbox examples written for HausPost. All names, addresses, tenants and correspondence are fictional. Expected annotations and actual model responses are stored separately. The public desk now loads the six real responses from run 38328626014, with coordinator correction controls.

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
- Quoted history supplies context. Repairs reported as resolved remain resolved, and the copied instruction footer remains input text. The coordinator reviews field meaning and source support before a work-order draft or clarification is exported.

Fixture checks cover six records, seven field keys, short input length, and exact unique quote matching. These checks validate sample structure and field locations. Actual model extraction quality is measured with separately saved responses.

## Licence

The synthetic case text and expected annotations are made available under the [Community Data License Agreement – Permissive 2.0](LICENSE). `recorded-runs.json` stores separately identified outputs from real Apertus runs as they are collected.

## Recorded model evidence

- [JSON-object baseline](evaluation/development-v1/): commit `3a92887`, run `38326610654`, five accepted application responses from six attempts.
- [Fixed-schema evaluation](evaluation/development-v2/): commit `bb1f70f`, run `38328626014`, six accepted responses, all 30 populated quotes located literally. Agent semantic review marks 25 populated fields complete in business meaning and citation support; two complete cases also meet every quote check.
- [Separate schema smoke failure](evaluation/schema-smoke-38328000284/): the cancelled Wednesday appointment was omitted. The later full run retained the same smoke failure.
- [Evaluation guide](../docs/evaluation.md): exact metric definitions, remaining errors and the post-run copied-identifier check.

Recorded API responses retain the original model output. On opening a recorded result, the browser runs its current source and copied-identifier checks. The post-run `value_mismatch` gate catches the footer case's `99Z` value citing `Apartment 4B`. Current-state interpretation and source relevance receive coordinator review.
