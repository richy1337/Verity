# Design milestone: MG / MIS Revision -1

- [Module Guide source](SoftArchitecture/MG.tex) and [PDF](../../pdfs/Design/SoftArchitecture/MG.pdf): module secrets, change ownership, dependencies and requirement/hazard allocation.
- [Module Interface Specification source](SoftDetailedDes/MIS.tex) and [PDF](../../pdfs/Design/SoftDetailedDes/MIS.pdf): shared types, constants, initialization, operations and lifecycle/assessment contracts.
- [Fall custom document](../CDs/MLReport/main.tex) and [PDF](../../pdfs/CDs/MLReport/main.pdf): the ML report is supplied separately by [PR #68](https://github.com/richy1337/Verity/pull/68). PR #69 alone retains the report template.
- [Review findings and submission follow-ups](Review-69.md).

Build both documents from the repository root with the installed TeX toolchain:

```sh
make -B docs/Design/SoftArchitecture/MG.pdf docs/Design/SoftDetailedDes/MIS.pdf
```

Copy compiled documents to the matching `pdfs/Design/` paths and remove the compiled document PDFs from `docs/`. The individual reflection accounts and human verification record require the contributors' own input. Informal-presentation participation requires attendance and engagement; document builds do not establish that criterion.
