# Third-party resources and attribution

The MIT license in [LICENSE](LICENSE) applies to original Flame in Freefall
software contributed to this repository. It does **not** grant new rights to
NASA research documents, data, images, scientific publications, Python
packages, or other third-party works.

## NASA scientific sources

Scientific data and documents are drawn from the public
[NASA Physical Sciences Informatics repository](https://psi.nasa.gov/physci/repo/search?q=combustion).
The included investigations are PSI-25, PSI-26, PSI-62, PSI-68, PSI-69,
PSI-98, PSI-99, PSI-100, PSI-101, PSI-102, PSI-117, and PSI-159.
See [the data provenance inventory](docs/DATA_PROVENANCE.md) for study-specific
DOIs, source URLs, original filenames, versions, and integrity hashes.

Two NASA reference publications are also used:
- [A Researcher's Guide to International Space Station Combustion Science](https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/)
- [Complete PSI Database Guide](https://assets.science.nasa.gov/content/dam/science/bps/bps-general/bps-data_osdr_psi/Complete_PSI_Database_Guide.pdf)

NASA's authorship of research materials does not imply endorsement of this
project. Users should consult the source records and any notices accompanying
individual documents before redistributing or adapting those materials.

## Software dependencies

The application uses third-party open-source Python packages, including
Streamlit, pandas, Plotly, PyMuPDF, Pint, and optionally sentence-transformers.
Their respective authors and licenses are not replaced by this project's MIT
license. Consult the package metadata and [requirements.txt](requirements.txt).

The optional Gemini API is a separate service and is not a dependency for the
published offline evidence retrieval mode.
