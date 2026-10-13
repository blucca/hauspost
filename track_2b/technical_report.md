# Technical report — HausPost

- **Track:** Track 2B — Own Project
- **Event:** Hack Apertus Online
- **Team:** blucca — solo participant, with Codex AI-assisted implementation
- **Demo:** [Interactive example desk](https://blucca.github.io/hauspost/); recorded video in preparation
- **Revision:** working draft, 13 October 2026

## 1. Summary

HausPost helps a property coordinator turn a multilingual tenant email thread into a current repair brief. A completed repair, an active fault, a cancelled appointment, and a newly requested window can coexist in one message. Apertus proposes seven source-linked fields; the application checks each quoted passage against the original text. The coordinator reviews or corrects the details, then exports an internal brief and a reply in the tenant’s language. A missing apartment number produces a clarification draft. A fully resolved update produces a closure reply.

The first implementation includes the complete browser workflow, a Python standard-library API, six synthetic cases across four languages, and a reproducible Apertus 1.5 8B CPU deployment. Measured model outcomes are recorded by the repository’s manual on-prem workflow and added to the evaluation evidence.

## 2. Architecture

Browser → Python intake API → OpenAI-compatible Apertus endpoint → fixed-field JSON → exact-source validation → coordinator review → text handoff.

The browser holds the current thread, field edits and review state. A changed message clears the previous extraction and approvals. The server uses one model request at a time and returns source offsets in JavaScript UTF-16 units. Matching requires one continuous, unique occurrence. Missing, ambiguous and unmatched passages retain distinct states. Coordinator-supplied information is labelled separately.

### Target architecture (mandatory)

**a) On-premise.** Docker Compose runs the application and a pinned llama.cpp server on an internal network under the operator’s administration. The 8B Q4_K_M weights are mounted from the operator’s model directory. The UI is bound to the host’s loopback interface; a remote coordinator can use an SSH tunnel.

Build/provisioning contacts Docker Hub, GHCR and the Hugging Face model publisher. Runtime inference in the on-prem profile stays between the two containers. The optional hosted profile sends prompts and source text to the configured provider. The static public example desk processes its prepared examples inside the browser. The application has zero third-party Python runtime dependencies; fonts and browser assets are bundled locally.

## 3. Use of Apertus

- **Model:** Apertus v1.5 8B, text-only Q4_K_M community conversion, revision `248ec68a63e219e3f061e4c946fc8a20d63b9975`.
- **Use:** inference, extracting current semantic state and exact supporting passages from German, French, Italian and English text.
- **Serving:** pinned llama.cpp `server-b11561`, 4096-token context, one slot, four CPU threads, thinking disabled.
- **Prompt:** the full system prompt is in `src/server.py`. It gives priority to later updates, separates completed and active repairs, preserves original names and times, and treats embedded commands as source content.
- **Output:** `active_issue`, `resolved_issue`, `property_address`, `apartment`, `requested_visit`, `cancelled_visit`, `contact_name`, plus the language code. Each field has a value and a source quote.

The application builds the final handoff and language-specific reply templates from reviewed fields. Appointment windows remain tenant requests until the coordinator confirms them through their own workflow.

## 4. Data

`data/cases.json` contains six author-written fictional threads, each 71–102 words, with expected fields and source passages. Names and addresses are fictional. The cases cover an amended German repair, a French second fault after a completed repair, an Italian resolved update, conflicting English availability, a stale quoted repair, and an instruction-like footer.

Authored examples and measured model responses are stored separately and labelled in the UI. Synthetic input and annotations are released under CDLA-Permissive-2.0. Runtime tenant text stays in the current request and browser interaction. The repository’s model checks use synthetic content.

## 5. Evaluation

The task is field extraction with correct current-state interpretation and exact source links. The comparison of interest is an unchecked model answer versus a coordinator handoff with explicit source and review states.

| Check | Observed result at this draft |
|---|---|
| Python contract check | PASS: model parser, source states, Unicode offsets, input/origin boundaries, single dispatch and configured timeouts |
| Browser workflow | PASS: German missing-unit reply, coordinator-added unit, repair export, unconfirmed visit wording, Italian closure reply |
| Mobile workflow | 390 px width, zero horizontal overflow; zero page exceptions in the browser smoke |
| Real Apertus 8B on-prem extraction | Collected by the manual deployment workflow; raw input, answer and metrics retained per run |

A public PublicAI chat preflight displayed Apertus 1.5 70B and returned the correct active/resolved distinction on one synthetic German message. One evidence string reordered two source sentences, so it failed an exact substring check. This observation motivated the explicit source-link correction path. The 8B quantised model has its own measured evaluation.

The small fixture set measures the named cases. A field-worker trial would measure time to a correct handoff, edit burden and useful replies on consenting real workflows.

## 6. Limitations

Supported workload: short text threads about one property, with four reply languages and a 4096-token model context. The runtime enforces character and response-size limits; model context errors prompt a shorter excerpt. Exact source matching checks location. The coordinator reviews the passage’s meaning, the active/resolved classification and the final wording.

The on-prem capacity target is 8 GiB RAM, 8 GiB free disk and four CPU threads. Observed memory and latency are reported for the actual CI host. A larger office deployment needs its own concurrency, access-control and operator acceptance testing.

## 7. Reproducibility

Run `make run` from a clean checkout. The first launch downloads the fixed 5,059,027,136-byte GGUF directly from the publisher; the application and model images are pinned. After provisioning, `make run` launches both services, with the desk at `http://127.0.0.1:4377`.

Run `python track_2b/tests/check.py` for the local contract check. Dispatch the **Apertus on-prem smoke** workflow for a real fresh model deployment and synthetic message through the application API. The public runner is a standard Ubuntu 24.04 machine; its actual specifications, commit, container logs, response, usage and elapsed time accompany the artifact. Model-response timeout is 420 seconds in the CPU profile.

See `docs/deployment.md` for pinned artifacts, separate hosted configuration, network flow and licensing.

## 8. Next steps

Complete the measured four-language evaluation, the six-page PDF and the two-minute film for submission. Recruit a property coordinator to compare a small anonymised mailbox batch with their current process. Commercial hypothesis: offices with existing private model infrastructure pay for a focused installation and acceptance batch, then ongoing support if the reduction in handoff work justifies it.

## License

Documentation: Creative Commons Attribution 4.0 (CC-BY-4.0). Application source: Apache-2.0. Synthetic data: CDLA-Permissive-2.0. Model publisher terms and font notices are retained in their respective references.

## References

1. Hack Apertus Track 2B template: https://github.com/HackApertus/project-template/tree/main/track_2b
2. Apertus 1.5 8B: https://huggingface.co/swiss-ai/Apertus-v1.5-8B
3. Q4_K_M conversion: https://huggingface.co/Colby/apertus-v1.5-8b-text-Q4_K_M-GGUF
4. llama.cpp server: https://github.com/ggml-org/llama.cpp/tree/master/tools/server
5. PublicAI Apertus 1.5 release: https://publicai.co/stories/apertus-1-5
6. GitHub runner specifications: https://docs.github.com/en/actions/reference/runners/github-hosted-runners
