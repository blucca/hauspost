# HausPost

**A clear brief for the next visit.**

A tenant says the tap is fixed, the doorbell is still broken, and Wednesday’s visit has moved to Friday. HausPost separates those updates, links each detail to the original words, and helps a property coordinator prepare the right repair brief or follow-up question.

[Open the example desk](https://blucca.github.io/hauspost/) · [104-second demonstration](https://blucca.github.io/hauspost/demo/) · [Report PDF](track_2b/docs/technical-report.pdf) · [Deployment](track_2b/docs/deployment.md) · [Technical report](track_2b/technical_report.md)

## Use the desk

1. Open a synthetic German, French, Italian, or English example, or paste a tenant thread into the running application.
2. Apertus extracts the current repair, resolved issue, property, unit, and changed visiting window.
3. Select a detail to highlight its source. Correct a broken source link or add a clearly labelled coordinator entry.
4. Confirm the reviewed details. Missing information produces a clarification draft; a resolved update produces a closure reply.
5. Copy or download the internal brief and the tenant-language reply. Appointment windows stay **requested / awaiting confirmation**.

The public example desk runs locally in the browser. Author-written examples and recorded model outputs have separate labels. The application’s live mode calls the operator-configured Apertus endpoint.

## Run HausPost

Requires Docker with Compose v2. The measured CPU profile uses a **16-GB-class host, 8 GiB free disk, and 4 CPU threads**. The 8 GiB RAM planning floor requires local headroom and acceptance above the observed 7 GiB model peak. Run from either the repository root or `track_2b/`:

```sh
make run
# Open http://127.0.0.1:4377
make stop
```

The first launch obtains a pinned **Apertus v1.5 8B Q4_K_M** model directly from its Hugging Face publisher, then starts the application and llama.cpp on an internal Docker network. The model download is 5.06 GB. Dependencies and their licences, including the Apertus usage policy, are listed in the [deployment guide](track_2b/docs/deployment.md). Model weights stay in your local `track_2b/models/` directory.

For the lightweight example workflow:

```sh
make demo
```

For an existing OpenAI-compatible Apertus service:

```sh
cp track_2b/.env.example track_2b/.env
# Set LLM_BASE_URL, LLM_NAME and, for authenticated services, LLM_API_KEY.
make hosted
```

The hosted profile sends the message to the configured service. The on-prem profile keeps inference between the organisation-managed application and model containers. Build and model provisioning are separate from runtime.

## Checks and evaluation

```sh
PYTHONDONTWRITEBYTECODE=1 python track_2b/tests/check.py
```

The repository includes six small, synthetic cases with explicit expected fields. They cover four languages, stale quoted repairs, missing unit numbers, conflicting visit times, and instruction-like text inside an email. [Data notes](track_2b/data/README.md) distinguish author annotations from measured model results.

The manual **Apertus on-prem smoke** GitHub Actions workflow runs the real model and application Docker stack on a public Linux runner, analyses a new German thread, and saves its raw response, source checks, runtime, and resource snapshot. Results belong to the recorded run’s model, quantisation, hardware, and cases. The [measured comparison](track_2b/docs/evaluation.md) keeps all six real responses and remaining failures. The updated copied-identifier gate blocks a model value that differs from its cited address, unit or name.

## Scope

HausPost handles short text threads about one property. The coordinator reviews the model’s interpretation and controls the handoff. Exact substring checks establish source locations; the coordinator checks what those passages mean. Longer histories, attachments, tenancy-law decisions, mailbox integration, and automatic dispatch are future product work.

## Project and licences

Started on **13 October 2026** for **Hack Apertus, Track 2B**, from the official project template. Participant and repository owner: **blucca**. The implementation, research, synthetic examples, and checks were produced with the Codex AI agent; the repository records that contribution openly.

Application code: [Apache-2.0](LICENSE). Documentation: CC-BY-4.0. Synthetic data: CDLA-Permissive-2.0. Bundled fonts retain their OFL notices. Model weights are obtained separately under the publisher’s stated terms.
