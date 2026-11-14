# SkyFlow narrated evidence demo

## 00:00:00.000 — Airline events. Traceable outcomes.

This is SkyFlow, a complete airline DataOps portfolio demonstration using synthetic data. The project brings together batch processing, streaming events, quality checks, monitoring, Terraform, automated tests, and AI assisted diagnostics. This walkthrough presents results captured from a fresh verification on November fifteenth, twenty twenty six, in India time. It is a narrated evidence walkthrough, not a screen recording or an airline production system.

## 00:00:33.560 — Two paths. One monitoring layer.

The architecture has two separate data paths. Batch events are generated in Python, loaded into BigQuery, normalized with SQL, and summarized into airport and route metrics. Streaming events travel through a Pub/Sub topic and subscription, then a Python consumer writes them to BigQuery. Operational views and batch run logs supply diagnostic evidence. The language model explains findings, but it cannot execute commands or change cloud resources.

## 00:01:04.210 — A fresh batch passed every gate.

The fresh observed batch run processed one thousand records. Raw and clean row counts matched, all event identifiers were unique, and the ten quality checks passed. Those checks cover required values, route validity, nonnegative delays, normalized statuses, event types, and the derived metrics. The curated results contained ten airports and ninety routes. The observed run took about eighteen seconds, and its successful outcome was stored in BigQuery.

## 00:01:35.330 — Verify the events. Not just the count.

The streaming check published twenty new events and verified each event identifier against its actual Pub/Sub message identifier in BigQuery. All twenty matched. There were no missing events, duplicate rows, or wrong message identifiers in that verification run. This improves the earlier test, where unrelated traffic could increase the row count and cause a false pass. The monitoring snapshot then showed sixty total unique events, including the twenty just published.

## 00:02:06.420 — The final audit found a real fault.

The final audit found that the streaming subscription was missing. Its configuration allowed expiration after thirty one days of inactivity, which is consistent with the gap between demonstrations. The exact deletion cause was not independently established. Terraform restored only that missing subscription, with idle expiration disabled. The existing datasets and topic were preserved. A fresh plan after the repair reported zero additions, zero changes, and zero destructions.

## 00:02:38.480 — A real explanation. Bounded claims.

The live diagnostic request used the fresh monitoring snapshot and completed successfully through Abacus Route L L M. The deterministic rules returned no flags, and the model produced a structured explanation with suggested checks and explicit limitations. That does not prove overall system health. The independent batch and exact event streaming tests provide the stronger evidence shown here. The optional OpenAI adapter is not required for this completed Abacus based portfolio.

## 00:03:09.520 — Built, verified, and ready to review.

The finished portfolio includes fifty eight offline tests, GitHub continuous integration, infrastructure configuration, a runbook, timestamped acceptance evidence, and this narrated demo. Tests cover failures as well as successful paths, including rejected writes and false positive streaming verification. This is an on demand portfolio system. It does not claim continuous production deployment, exactly once delivery, or autonomous repair. The source and evidence are available in the SkyFlow airline DataOps repository on GitHub.
