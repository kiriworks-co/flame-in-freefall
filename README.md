# Flame in Freefall

An interactive platform for exploring NASA research on combustion in microgravity.

**[Open the web application](https://flame-in-freefall-kiriworks.streamlit.app/)** · [NASA Space Apps Challenge 2026](https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/)

## About the project

Fire behaves differently when buoyancy-driven convection is reduced. Flame shape, oxygen transport, extinction conditions, and the movement of smoke all depend on the surrounding flow and experimental setup. These differences matter when studying fire prevention, detection, and suppression aboard spacecraft.

NASA's Physical Sciences Informatics (PSI) repository contains experimental tables, numerical results, investigation metadata, and technical reports relevant to these questions. However, the source material is distributed across several file formats and studies. Flame in Freefall brings a selection of these records into one interface while keeping links to the original documents.

The application was developed in Python using Streamlit. It provides two guided introductions for visitors alongside more detailed tools for examining the underlying data.

## What you can do

- **Explore investigations.** Browse twelve NASA PSI studies, search by topic, and open the original sources and DOIs.
- **Inspect data.** Review tables, plot numerical variables, examine PDF pages, and export selected views.
- **Compare studies.** Check whether variables, physical units, and types of evidence are compatible before drawing comparisons.
- **Find relevant research.** Search the collected NASA material in English or Portuguese and inspect citations at the document, page, or table-row level.
- **Summarize, rank, and interpret.** Review a study's documented scope, order investigations by their relevance to a research question, and examine possible implications and limitations for spacecraft fire safety.

The ranking is a reading-priority aid, **not** a measure of fire risk or a spacecraft safety certification.

## NASA data

The current collection covers **12 PSI investigations** and two NASA reference guides:

| Research area | Investigations |
| --- | --- |
| Solid-fuel combustion and spacecraft fire experiments | PSI-25 (BASS-II), PSI-26 (BASS), PSI-62 (flame-spread modeling), PSI-98 (Saffire-I), PSI-99 (Saffire-II), PSI-100 (Saffire-III) |
| Smoke aerosols and detection | PSI-101 (SAME-R), PSI-102 (SAME) |
| Droplet and gas-phase combustion and flame extinction | PSI-68 (FLEX-2), PSI-69 (FLEX), PSI-117 (cool-flame dynamics), PSI-159 (ACME CFI-G) |

Forty source documents are preserved, including three ISA metadata placeholders. The local processing pipeline extracted 117 tables and 10,114 tabular rows. Its 26,803 typed records include simulation values, reported results, test conditions, calculations, and metadata; they do **not** represent 26,803 separate experiments.

The NASA data are accompanied by source identifiers, permanent URLs, DOIs where available, and SHA-256 checksums. PSI-62 has descriptive metadata but no numerical series in the files collected for this project. Some other sources contain missing or ambiguous units; these are retained rather than silently corrected.

The project uses [NASA Physical Sciences Informatics](https://psi.nasa.gov/physci/repo/search?q=combustion) as its primary data source. Detailed file provenance is recorded in [docs/DATA_PROVENANCE.md](docs/DATA_PROVENANCE.md).

## How it works

The application extracts information from CSV, XLSX, PDF, and ISA-Tab material and stores processed records in SQLite. Plotly provides the interactive figures. Scientific search combines SQLite FTS5 with local semantic embeddings when available, or a lighter lexical index in cloud environments. Retrieved material retains references to its source documents.

The scientific assistant works without external AI services. An optional Google Gemini integration can provide brief explanations of retrieved material when a key is configured; it is not required for the published application. See [AI implementation and limitations](docs/AI_USAGE.md).

This is an exploratory research and educational tool. It does not independently validate NASA measurements, simulate a new spacecraft fire, or establish operational safety limits.

## Run locally

Python 3.11 is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Streamlit will display the local URL after startup. The application builds its SQLite databases from the preserved NASA source files. No Gemini API key is necessary.

To run the test suite:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

## Documentation

- [Project overview (Portuguese)](docs/PROJECT_OVERVIEW_PTBR.md)
- [Feature guide and workflows (Portuguese)](docs/FEATURES_AND_WORKFLOWS_PTBR.md)
- [Complete technical manual (PDF, Portuguese)](docs/FLAME_IN_FREEFALL_MANUAL_COMPLETO_PTBR.pdf)
- [Scientific data and provenance](docs/DATA_PROVENANCE.md)
- [Technical testing](docs/TEST_REPORT.md)
- [Deployment guide](docs/DEPLOYMENT.md)
- [NASA Space Apps submission description](docs/SUBMISSION_DESCRIPTION_EN.md)

## Licensing and sources

Original project software is made available under the [MIT License](LICENSE). NASA research files and other third-party materials retain their respective source terms; they are not relicensed by the project's code license. See [third-party resources](THIRD_PARTY_NOTICES.md).
