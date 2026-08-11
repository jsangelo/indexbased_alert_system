# An index-based system for early alerts of potential zoonotic disease outbreaks

This repository contains the datasets and Python scripts used in the analyses presented in the paper:

**An index-based system for early alerts of potential zoonotic disease outbreaks**

**Authors:** Jaqueline S. Angelo, Livia Abdalla, Douglas A. Augusto, Marcia Chame, Eduardo Krempser

**DOI:** [10.1371/journal.pone.0356739](https://doi.org/10.1371/journal.pone.0356739)

---

## Repository overview

This repository provides the computational resources used in the study, including a minimal dataset and author-generated Python scripts for data preprocessing, geocoding, spatial and temporal clustering, cluster characterization and the generation of the Z-Alert Index of the resulting clusters.

The objective is to facilitate the reproducibility of the experiments and provide sufficient information for researchers to understand and reproduce the main steps described in the paper.

The complete dataset used in the study cannot be publicly released because it contains sensitive geolocated information related to confirmed Yellow Fever (YF) cases. Therefore, this repository provides a minimal dataset that is sufficient to reproduce the analyses presented in the study while respecting the applicable data-access restrictions.

---

# Data Availability

The data used in this study originate from the **SISS-Geo platform**, a governmental system that provides different levels of data access. Registered users are granted limited access to general datasets, whereas access to sensitive information, such as geolocated confirmed disease cases and animal health conditions, is restricted to authorized institutional users only.

Data made available to all SISS-Geo users are continuously updated and can be accessed at:

https://sissgeo.lncc.br/mapaRegistrosInicial.xhtml

Due to legal and privacy constraints related to geolocated confirmed Yellow Fever (YF) cases, the complete dataset used in this study cannot be shared publicly.

However, the **Brazilian Ministry of Health** freely provides individualized and anonymized municipality-level data on confirmed human cases and non-human primate epizootics of YF. These data can be accessed through the OpenDataSUS platform:

https://opendatasus.saude.gov.br/dataset/febre-amarela-em-humanos-e-primatas-naohumanos

Information on confirmed YF cases from SISS-Geo can be requested through the **SISS-Geo Institutional Data Access** process. Details on data access procedures, including the required permissions, can be obtained by contacting the SISS-Geo coordination team:

**[biodiversidade@fiocruz.br](mailto:biodiversidade@fiocruz.br)**

Additional information on institutional data access is available at:

https://sissgeo.lncc.br/apresentacao.xhtml#signup

To ensure transparency and reproducibility, a minimal dataset sufficient to reproduce the analyses presented in this study, together with all author-generated code, is made publicly available in this GitHub repository. The repository includes documentation and instructions for reproducing the analyses.

---


# User Guide

## Workflow

The analysis follows a sequential workflow consisting of four main steps:

1. **Data preprocessing** – prepares and filters the input data used in the analyses.
2. **Geocoding** – adds geographic information required for the spatial analysis.
3. **Spatial and temporal clustering** – identifies clusters based on spatial and temporal proximity.
4. **Cluster characterization** – calculates the attributes used to characterize the generated clusters.
5. **Cluster geocoding** – adds geographic information to the generated clusters (only for validation purposes).
6. **Optimization of the Z-Alert Index** – multiobjective optimization for optimizing cluster attribute weights.
7. **Validation** - validation of the Z-Alert Index using data from the BMoH containing records of YF cases.

The scripts should be executed in the following order:

```text
Input data
    │
    ▼
01. Data preprocessing
    │
    ▼
02. Geocoding
    │
    ▼
03. Spatial and temporal clustering
    │
    ▼
04. Cluster characterization
    │
    ▼
05. Cluster geocoding
    │
    ▼
06. Optimization of the Z-Alert Index
    │
    ▼
07. Validation
```

# Reproducibility

The data and scripts provided in this repository are intended to support the reproducibility of the computational analyses described in the paper.

Because the complete SISS-Geo dataset contains restricted geolocated information, results obtained using the publicly available minimal dataset may not be identical to results obtained using the complete dataset used in the study.

The restricted data can be accessed through the institutional data-access procedure described above.

---

# Citation

If you use the code or data provided in this repository, please cite the corresponding publication:

> Angelo, J. S., Abdalla, L., Augusto, D. A., Chame, M., & Krempser, E.
> *An index-based system for early alerts of potential zoonotic disease outbreaks.*
> PLOS ONE. doi:10.1371/journal.pone.0356739

---

# License

Please refer to the `LICENSE` file in this repository for information about the terms under which the code and data are made available.

