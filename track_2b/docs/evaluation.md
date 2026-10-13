# Development evaluation

Six public, fictional threads cover German, French, Italian and English. A separate German smoke is also part of prompt development. All semantic judgements below were made by Codex agents. A consenting property-office trial is the next validation stage.

| Measurement | JSON-object baseline | Fixed schema |
| --- | ---: | ---: |
| Accepted application responses | 5/6 | 6/6 |
| Populated fields with literal source quotes | 21/27 | 30/30 |
| Populated fields complete in business meaning and citation support | 21/27 | 25/30 |
| Complete meaning and literal citation on populated fields | 18/27 | 25/30 |
| All seven fields semantically complete | 1/6 | 3/6 |
| Whole case complete, including all supplied quotes | 0/6 | 2/6 |
| Required follow-up states preserved | 0/2 | 2/2 |

The baseline is commit `3a92887`, run [38326610654](https://github.com/blucca/hauspost/actions/runs/38326610654). The fixed schema is commit `bb1f70f`, run [38328626014](https://github.com/blucca/hauspost/actions/runs/38328626014). Both keep raw responses, source text, timing and field-level review under `data/evaluation/`.

**Metric scope.** Literal matching checks the quoted character sequence. Complete meaning checks the actual current fact, required intent and relevance of its citation. Populated-field denominators cover accepted responses. Whole-case checks include expected empty fields and quote-only conflicts. English-summary style is separate: the German and French model summaries remain in their input languages.

## Remaining model errors

- The Italian case retains heating recovery and omits the explicit request to close the ticket.
- The administrative German case places a March door complaint in the resolved field. Correcting that field returns the draft to administrative routing.
- The English footer supplies `all clear` and `99Z`. Its repaired-intercom value cites an older failure. The coordinator corrects the active fault and source relevance.
- Conflicting availability correctly leaves the value empty. Its quote joins one source newline with a space; a verbatim source correction preserves the conflict.
- The separately authored German smoke omits the cancelled Wednesday appointment with the schema prompt. Seven of its nine checks pass in both schema runs; the workflow retains the failure.

## Deterministic improvement after the measured run

The current parser and browser require copied address, apartment and contact-name values to occur in their cited passage after whitespace/case normalization. Replaying the actual footer answer (`99Z`, cited `Apartment 4B`) now yields `value_mismatch`; confirmation remains blocked until correction. Raw model responses above stay unchanged. The local contract check and browser recording exercise this gate.

Source buttons have explicit accessible names. This fixes the recording selector affected by decorative arrow text. The final film combines the original live CPU request (87.917 seconds) with labelled replay of that same answer for scripted coordinator review, clarification, supplied unit 3B and handoff. The footer segment uses its original development response.

## Capacity

The six fixed-schema HTTP requests took **376.527 seconds**, mean **62.755**, median **65.442**, range **50.068–72.967** seconds on a four-vCPU GitHub Ubuntu host with roughly 15 GiB visible RAM. First provision/start took 93 seconds. Model cgroup peak was **7 GiB**, with zero OOM events; Docker's separate working-set snapshot was **3.938 GiB**. The application snapshot was **19.23 MiB**.

For 60 equally short messages, the same output mix, warm prefix cache and sequential single-slot service, linear compute time is **62.8 minutes**. Adding the observed provision and smoke gives **66.9 minutes**. Operator review time and power consumption belong to the office pilot measurement. Concurrent arrivals use the caller's serial queue or a retry after the busy response.
