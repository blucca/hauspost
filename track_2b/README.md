# HausPost — Track 2B

The application turns multilingual tenant email updates into a source-checked repair brief and tenant-language follow-up draft.

## Start

```sh
make run
# http://127.0.0.1:4377
make stop
```

The full profile requires Docker Compose v2, 8 GiB RAM, 8 GiB free disk, and 4 CPU threads. The first run obtains the pinned 5.06 GB Apertus 1.5 8B Q4_K_M weights from the publisher. `make demo` starts the lightweight authored-example desk; `make hosted` uses the endpoint configured in `.env`.

See the [project README](../README.md) for the workflow and [deployment guide](docs/deployment.md) for the model, container versions, data flow and configuration. Source lives in `src/`; synthetic cases and measured outputs live in `data/`.

## Submission materials

- [Technical report source](technical_report.md)
- [Public example desk](https://blucca.github.io/hauspost/)
- Real on-prem model and Docker checks: **Apertus on-prem smoke** workflow in this repository

The PDF and two-minute video are being prepared for the official Track 2B submission.

Code: Apache-2.0. Documentation: CC-BY-4.0. Synthetic case data: CC0-1.0.
