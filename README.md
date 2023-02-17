# Skzi: security requirements for cryptographic modules

[![build](https://github.com/bcrypto/skzi/actions/workflows/build.yaml/badge.svg)](https://github.com/bcrypto/skzi/actions/workflows/build.yaml)

## What is Skzi?

Skzi is a set of security requirements for cryptographic modules standardized in
Belarus as STB 34.101.27. The first versions of STB 34.101.27, released in 2007
and 2011, cover only software modules. The latest version, dated 2022, covers
both software and hardware modules.

Skzi defines 4 security levels: 2 for software modules and 2 for hardware.
Security requirements are divided into 3 groups:

A) functional requirements for the module;
B) functional requirements for the system environment of the module;
C) assurance requirements for the module.

Requirements are structured into the following packages.

| Package                                | Type | Mandatory | Starting level |
|----------------------------------------|:----:|:---------:|:--------------:|
| Cryptographic support (КП)             |  A   |     +     |        1       |
| Services (РС)                          |  A   |     +     |        1       |
| Access control (УД)                    |  A   |     +     |        1       |
| Data protection (ЗО)                   |  A   |     +     |        1       |
| Self-testing (СТ)                      |  A   |     +     |        1       |
| Audit (АУ)                             |  A   |     +     |        3       |
| Physical security (ФБ)                 |  A   |     +     |        3       |
| Environmental failure protection (ЗВ)  |  A   |     +     |        3       |
| Non-Invasive security (ЗУ)             |  A   |     +     |        4       |
| Random number generators (СЧ)          |  A   |     -     |        1       |
| Software update (ОП)                   |  A   |     -     |        1       |
| Decommissioning (ВЭ)                   |  A   |     -     |        1       |
| Identification and authentication (ИА) |  B   |     +     |        1       |
| Environment setup (НС)                 |  B   |     +     |        1       |
| Trusted channel (ДК)                   |  B   |     -     |        1       |
| Design and implementation (ПР)         |  C   |     +     |        1       |
| Lifecycle (ЖЦ)                         |  C   |     +     |        1       |
| Guides (РД)                            |  C   |     +     |        1       |
| Tests (ПИ)                             |  C   |     +     |        1       |
| Code review (АП)                       |  C   |     +     |        1       |

## What is this repo?

In this repo, we process comments on the current version of Skzi,
discuss future versions, provide additional supporting material.

The latest releases of Skzi can be found at 
[Releases](https://github.com/bcrypto/skzi/releases).

Comments and proposals are processed at 
[Issues](https://github.com/bcrypto/skzi/issues). 

