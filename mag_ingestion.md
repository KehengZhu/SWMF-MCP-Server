# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `6b721524-26c5-45df-9f15-0beaeaaacf70`  
> - **Started:** 4/21/2026, 12:38:56 PM  
> - **Duration:** 5m 49s  
> - **Exported:** 4/21/2026, 12:44:45 PM  

---

<sub>⏱️ 0s</sub>

### ℹ️ Info

💡 No copilot instructions found. Run /init to generate a copilot-instructions.md file for this project.

---

<sub>⏱️ 0s</sub>

### ℹ️ Info

Environment loaded: 2 MCP servers, 6 skills, Visual Studio Code connected

---

<sub>⏱️ 6s</sub>

### 👤 User

Search across SWMF and SWMFSOLAR for everything related to magnetogram ingestion, then summarize the main code paths.

---

<sub>⏱️ 19s</sub>

### 💬 Copilot

I’m going to sweep the indexed SWMF/SWMFSOLAR corpus with several magnetogram-related queries, then drill into the key files to map ingestion flow.

---

<sub>⏱️ 30s</sub>

### ✅ `swmf-prototype-swmf_search_source`

**magnetogram**

<details>
<summary>Arguments</summary>

```json
{
  "query": "magnetogram",
  "max_results": 50
}
```

</details>

```
Output too large to read at once (31.6 KB). Saved to: /var/folders/pn/yhfjt4h144j54nktzjsjv_j80000gp/T/1776789567130-copilot-tool-output-i62cj2.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
{"ok":true,"query":"magnetogram","filters":{"component":null,"kind":null,"corpus_slice":null},"result_count":24,"results":[{"name":"read_magnetogram","kind":"subroutine","start_line":120,"component":null,"docstring":"============================================================================","source_kind":"fortran_source","authority":"heuristic","uses":["ModIoUnit"],"file_path":"/Users/zkeheng/SWMFSoftware/SWMF/util/DATAREAD/srcMagnetogram/potential_field.f90","corpus_root":"/Users/zkeheng/SWM
```


---

<sub>⏱️ 31s</sub>

### ✅ `swmf-prototype-swmf_search_source`

**read magnetogram**

<details>
<summary>Arguments</summary>

```json
{
  "query": "read magnetogram",
  "max_results": 50
}
```

</details>

````
{"ok":true,"query":"read magnetogram","filters":{"component":null,"kind":null,"corpus_slice":null},"result_count":13,"results":[{"name":"read_magnetogram","kind":"subroutine","start_line":120,"component":null,"docstring":"============================================================================","source_kind":"fortran_source","authority":"heuristic","uses":["ModIoUnit"],"file_path":"/Users/zkeheng/SWMFSoftware/SWMF/util/DATAREAD/srcMagnetogram/potential_field.f90","corpus_root":"/Users/zkeheng/SWMFSoftware/SWMF","corpus_slice":"swmf_source"},{"name":"read_modified_magnetogram","kind":"subroutine","start_line":227,"component":null,"docstring":"============================================================================","source_kind":"fortran_source","authority":"heuristic","uses":["ModReadMagnetogram","ModConst"],"file_path":"/Users/zkeheng/SWMFSoftware/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90","corpus_root":"/Users/zkeheng/SWMFSoftware/SWMF","corpus_slice":"swmf_source"},{"name":"read_modified_magnetogram","kind":"subroutine","start_line":239,"component":null,"docstring":"============================================================================","source_kind":"fortran_source","authority":"heuristic","uses":["ModReadMagnetogram","ModConst"],"file_path":"/Users/zkeheng/SWMFSoftware/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90","corpus_root":"/Users/zkeheng/SWMFSoftware/SWMF","corpus_slice":"swmf_source"},{"name":"read_modified_magnetogram","kind":"subroutine","start_line":106,"component":null,"docstring":"============================================================================","source_kind":"fortran_source","authority":"heuristic","uses":["ModReadMagnetogram","ModPlotFile"],"file_path":"/Users/zkeheng/SWMFSoftware/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90","corpus_root":"/Users/zkeheng/SWMFSoftware/SWMF","corpus_slice":"swmf_source"},{"name":"read_magnetogram_param","kind":"subroutine","start_line":501,"component":null,"docstring":"============================================================================","source_kind":"fortran_source","authority":"heuristic","uses":["ModReadParam"],"file_path":"/Users/zkeheng/SWMFSoftware/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90","corpus_root":"/Users/zkeheng/SWMFSoftware/SWMF","corpus_slice":"swmf_source"},{"name":"read_magnetogram_param","kind":"subroutine","start_line":71,"component":null,"docstring":"============================================================================","source_kind":"fortran_source","authority":"heuristic","uses":["ModReadParam","ModPlotFile","ModConst","ModTimeConvert","ModIoUnit","ModUtilities"],"file_path":"/Users/zkeheng/SWMFSoftware/SWMF/util/DATAREAD/srcMagnetogram/ModReadMagnetogram.f90","corpus_root":"/Users/zkeheng/SWMFSoftware/SWMF","corpus_slice":"swmf_source"},{"name":"read_orig_magnetogram","kind":"subroutine","start_line":101,"component":null,"docstring":"============================================================================","source_kind":"fortran_source","authority":"heuristic","uses":["ModPlotFile","ModConst","ModTimeConvert","ModIoUnit","ModUtilities"],"file_path":"/Users/zkeheng/SWMFSoftware/SWMF/util/DATAREAD/srcMagnetogram/ModReadMagnetogram.f90","corpus_root":"/Users/zkeheng/SWMFSoftware/SWMF","corpus_slice":"swmf_source"},{"name":"read_magnetogram","kind":"function","start_line":3,"component":null,"docstring":"For reading magnetograms in FITS or BATS-R-US format.","source_kind":"idl_source","authority":"heuristic","uses":[],"file_path":"/Users/zkeheng/SWMFSoftware/SWMF/util/DATAREAD/srcMagnetogram/read_magnetogram.pro","corpus_root":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR","corpus_slice":"swmfsolar_source"},{"name":"GLSETUP1","kind":"pro","start_line":1,"component":null,"docstring":"-----------------------------------------------------------------------\nNAME:\nGLSETUP1\nOUTPUTS:\nuser choise for stdout file\nSYSTEM REQUIREMENTS:\nMouse with left and right button\nKEYWORDS:\nFILE = input magnetogram file (can be FITS or SWMF format).\nUseBATS = if set, will read BATS-R-US format (2D or 3D). Default\nwill read FITS format.","source_kind":"idl_source","authority":"heuristic","uses":[],"file_path":"/Users/zkeheng/SWMFSoftware/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP1.pro","corpus_root":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR","corpus_slice":"swmfsolar_source"},{"name":"GLSETUP2","kind":"pro","start_line":1,"component":null,"docstring":"-----------------------------------------------------------------------\nNAME:\nGLSETUP2\nOUTPUTS:\nuser choise for stdout file\nSYSTEM REQUIREMENTS:\nMouse with left and right button\nKEYWORDS:\nFILE = input magnetogram file (can be FITS or SWMF format).\nUseBATS = if set, will read BATS-R-US format (2D or 3D). Default\nwill read FITS format.","source_kind":"idl_source","authority":"heuristic","uses":[],"file_path":"/Users/zkeheng/SWMFSoftware/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP2.pro","corpus_root":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR","corpus_slice":"swmfsolar_source"},{"name":"✅ `view`","kind":"doc_section","start_line":767,"component":null,"docstring":"### ✅ `view`\n\n**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/catalog/idl_catalog.py.**\n\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/catalog/idl_catalog.py\n\n<details>\n<summary>103 lines</summary>\n\n```\n1. from __future__ import annotations\n2. \n3. from pathlib import Path\n4. from typing import Any\n5. \n6. from ..parsing.idl_parser import parse_idl_file\n7. \n8. \n9. def _infer_category(name: str, file_path: Path, docstring: str | None) -> str:\n10.     lowered_name = name.lower()\n11.     lowered_path = str(file_path).lower()\n12.     lowered_doc = (docstring or \"\").lower()\n13.     stacked = \" \".join([lowered_name, lowered_path, lowered_doc])\n14. \n15.     if any(token in stacked for token in [\"magnetogram\", \"fits\", \"read_magnetogram\"]):\n16.         return \"magnetogram\"\n17.     if any(token in stacked for token in [\"animate\", \"movie\", \"videofile\", \"moviedir\"]):\n18.         return \"animation\"\n19.     if any(token in stacked for token in [\"plot\", \"contour\", \"stream\", \"vector\", \"show_data\", \"plot_log\"]):\n20.         return \"plotting\"\n21.     if any(token in stacked for token in [\"read_\", \"getpict\", \"getlog\", \"read_log_data\", \".log\", \".sat\"]):\n22.         return \"data_reading\"\n23.     return \"utility\"\n24. \n25. \n26. def discover_idl_procedures(swmf_root: Path, max_results: int = 4000) -> dict[str, dict[str, Any]]:\n27.     idl_dir = swmf_root / \"share\" / \"IDL\"\n28.     if not idl_dir.is_dir():\n29.         return {}\n30. \n31.     procedures: dict[str, dict[str, Any]] = {}\n32.     discovered = 0\n33. \n34.     for path in sorted(idl_dir.rglob(\"*.pro\")):\n35.         for item in parse_idl_file(path):\n36.             discovered += 1\n37.             if discovered > max_results:\n38.                 return procedures\n39. \n40.             category = _infer_category(item.name, path, item.docstring)\n41.             key = item.name.lower()\n42.             payload = {\n43.                 \"name\": item.name,\n44.                 \"kind\": item.kind,\n45.                 \"file_path\": str(path.resolve()),\n46.                 \"signature\": item.signature,\n47.                 \"params\": item.params,\n48.                 \"keywords\": item.keywords,\n49.                 \"docstring\": item.docstring,\n50.                 \"category\": category,\n51.                 \"line_number\": item.line_number,\n52.             }\n53. \n54.             if key not in procedures:\n55.                 procedures[key] = payload\n56. \n57.     return procedures\n58. \n59. \n60. def discover_idl_macros(swmf_root: Path, max_results: int = 1000) -> list[str]:\n61.     idl_dir = swmf_root / \"share\" / \"IDL\"\n62.     if not idl_dir.is_dir():\n63.         return []\n64. \n65.     macros: list[str] = []\n66.     for path in sorted(idl_dir.rglob(\"*.pro\")):\n67.         macros.append(str(path.resolve()))\n68.         if len(macros) >= max_results:\n69.             break\n70. \n71.     return macros\n72. \n73. \n74. def list_idl_procedures(\n75.     procedures: dict[str, dict[str, Any]],\n76.   ","source_kind":"manual_doc","authority":"heuristic","uses":[],"file_path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/copilot-session-a72776c1-8296-4345-bbd5-e96aee7416cf.md","corpus_root":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype","corpus_slice":"analyst_context"},{"name":"__preamble__","kind":"doc_section","start_line":1,"component":null,"docstring":"**Script**:\nwriteRestartRunsToFile.jl:\nThis script will write a `param_list` with the following components:\n1) Event specific params (to be read in from a file such as EEGGL_Params_CR2154.txt). Will begin with header `#CME`.\n2) Background runs - these will only consist of params downselected from sensitivity analysis, sampled from their respective posterior distributions that data assimilation provides. This is also read in from a file.\n3) Restart runs. We specify which background runs we want to restart and insert a flux rope into, the params for these are calculated with formulae that use the event specific params read in 1) and Design Parameters sampled from uniform distributions imposed on their respective ranges. \n\nwriteSEPBackgroundList.jl\nWrite param list for background parameters.\n\nProcess to run:\n- Navigate to ParamListScripts, and go to Julia REPL\n```julia\njulia> using Pkg\njulia> Pkg.activate()\njulia> Pkg.resolve()     # rebuild Manifest if dependencies have changed\njulia> Pkg.instantiate() # install packages for environment as specified by Manifest\n```\n- run script from \n1) the Julia REPL using `include(\"path/to/writeRestartRunsToFile.jl)` \nOR \n2) use the `Execute File in REPL` command if using VSCode. \nOR\n3) the Terminal / shell via `julia --project=. writeRestartRunsToFile.jl`\n\nThese options will only parse default arguments so we will need to manually change the defaults if a different `param_list` is desired.\n\n- In the terminal, type\n`julia --project=. writeRestartRunsToFile.jl --help` \nto list all options\n```\nusage: writeRestartRunsToFile.jl [--fileEEGGL FILEEEGGL]\n                        [--fileBackground FILEBACKGROUND]\n                        [--fileRestart FILERESTART]\n                        [--fileOutput FILEOUTPUT] [--mg MG] [--cr CR]\n                        [--md MD] [--start_time START_TIME]\n                        [--restartID RESTARTID] [-h]\n\nGenerate run list for background and restart\n\noptional arguments:\n  --fileEEGGL FILEEEGGL\n                        Path to load EEGGL Params from. (default:\n                        \"./output/restartRunDesignFiles/EEGGLParams_CR2154.txt\")\n  --fileBackground FILEBACKGROUND\n                        Path to load background wind runs from.\n                        (default:\n                        \"./output/restartRunDesignFiles/Params_MaxPro_postdist.csv\")\n  --fileRestart FILERESTART\n                        Path to load restart runs from. (default:\n                        \"./output/restartRunDesignFiles/X_design_CME_2021_10_18.csv\")\n  --fileOutput FILEOUTPUT\n                        Give path to file where we wish to write param\n                        list (default:\n                        \"./output/param_list_2021_10_19.txt\")\n  --mg MG               Magnetogram to use, for example, GONG.\n                        (default: \"ADAPT\")\n  --cr CR               CR to use eg: 2152. (type: Int64, default:\n                        2154)\n  --md MD               Model to use, for example AWSoM, AWSoMR","source_kind":"manual_doc","authority":"heuristic","uses":[],"file_path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/ParamListScripts/README_Julia.md","corpus_root":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR","corpus_slice":"analyst_context"},{"name":"✅ `rg`","kind":"doc_section","start_line":233,"component":null,"docstring":"### ✅ `rg`\n\n**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF**\n\n<details>\n<summary>Arguments</summary>\n\n```json\n{\n  \"pattern\": \"\\\\.pro\",\n  \"path\": \"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF\",\n  \"output_mode\": \"content\",\n  \"-n\": true,\n  \"head_limit\": 200\n}\n```\n\n</details>\n\n<details>\n<summary>93 lines</summary>\n\n```\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Makefile:165:\t@echo \"IDL scripts           : `wc -l */*/*/*.pro */*/*/*/*.pro | tail -1`\"\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/Makefile:40:\t\tln -s ${MAGNETOGRAMDIR}/read_magnetogram.pro .; \\\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/Makefile:41:\t\tln -s ${MAGNETOGRAMDIR}/readfits.pro .; \\\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/.gitignore:7:*.protex\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:26:COUPLE_IHGM = ${CONDIR}/Interface/src/CON_couple_ih_gm.protex #     ^CMP IF IH\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:27:COUPLE_GMIE = ${CONDIR}/Interface/src/CON_couple_gm_ie.protex #     ^CMP IF IE\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:28:COUPLE_GMIM = ${CONDIR}/Interface/src/CON_couple_gm_im.protex #     ^CMP IF IM\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:32:COUPLE_IEIM = ${CONDIR}/Interface/src/CON_couple_ie_im.protex #     ^CMP IF IM\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:33:COUPLE_IEUA = ${CONDIR}/Interface/src/CON_couple_ie_ua.protex #     ^CMP IF UA\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:36:SCRIPT_CONF = ${SCRIPTDIR}/Configure.protex #^CMP IF CONFIGURE\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:39:\t${DIR}/GM/BATSRUS/TestBatsrus.protex \\\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:40:\t${DIR}/GM/BATSRUS/TestSuite.protex \\\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:41:\t${DIR}/GM/BATSRUS/TestCompare.protex\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:47:\t\techo \"make GM/BATSRUS/*.protex\"; \\\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:49:\t\techo \"cat GM/BATSRUS/*.protex > BATSRUS_SCRIPTS.tex\"; \\\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:54:\t${DIR}/Config.protex ${SCRIPT_CONF} \\\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:55:\t${DIR}/Scripts/TestParam.protex \\\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:56:\t${DIR}/Scripts/Performance.protex \\\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:58:\t${SCRIPTDIR}/CheckParam.protex \\\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:59:\t${SCRIPTDIR}/ParamConvert.protex \\\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:60:\t${SCRIPTDIR}/ParamEditor.protex \\\n/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/Makefile:61:\t${SCRIPTDIR}/PostProc.pro","source_kind":"manual_doc","authority":"heuristic","uses":[],"file_path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/copilot-session-a72776c1-8296-4345-bbd5-e96aee7416cf.md","corpus_root":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype","corpus_slice":"analyst_context"}],"authority":"heuristic","source_kind":"source_index","note":"Results are heuristic (regex/FTS5-based). Use PARAM.XML and TestParam.pl for authoritative validation.","swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked heuristic candidate: /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype","Checked heuristic candidate: /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF","Resolved from heuristic search (cwd/workspace/run_dir/symlink-aware)."]}
````


---

<sub>⏱️ 33s</sub>

### ✅ `swmf-prototype-swmf_search_source`

**GONG magnetogram synoptic**

<details>
<summary>Arguments</summary>

```json
{
  "query": "GONG magnetogram synoptic",
  "max_results": 50
}
```

</details>

```
{"ok":true,"query":"GONG magnetogram synoptic","filters":{"component":null,"kind":null,"corpus_slice":null},"result_count":1,"results":[{"name":"Model Parameterization \\label{section:SCparameterization","kind":"doc_section","start_line":387,"component":"GM","docstring":"\\section{Model Parameterization \\label{section:SCparameterization}}\n\nThe SC model was originally planned to have fixed parameters so the only \nchange from one CR to another is the input magnetogram. Our experience has \nshown however, that a better solution can be obtained for a particular \nCR by modifying the base density (BodyNDim in the \\#BODY command) and the \nmagnetogram scaling factor (UnitB in the \\#PFSSM command). The value \nrange for BodyNDim should be $1\\times10^8 - 5\\times10^8$ (in $cm^{-3}$) \nand for UnitB should be $1-4$. The recommended scaling factor for MDI \nmagnetograms is 1.8 and our experience showed that a value of 2.5 is \nbetter for solar minimum rotations of 1997. For solar maximum, we recommend \nto use higher value of 4. \n\nWe should note that the fine tuning is important for obtaining good agreement \nwith 1AU data, which is very hard when using global model. The \nparameterization should be easier in the case of simulations of the solar \ncorona only. A more detailed validation of the model can be found in:\n\\begin{verbatim}Cohen, O.; Sokolov, I. V.; Roussev, I. I.; Gombosi, T. I., \nValidation of a synoptic solar wind model, \nJournal of Geophysical Research, VOL. 113, A03104, doi:10.1029/2007JA012797, 2008\\end{verbatim}\n\nAll parameterization above was done using MDI magnetograms. For other data \nsources one should use different values. WSO, MWO, and GONG data seems to have \nweaker field than MDI and SOLIS data. Therefore, a larger scaling factor \nshould be used. \n","source_kind":"manual_doc","authority":"heuristic","uses":[],"file_path":"/Users/zkeheng/SWMFSoftware/SWMF/GM/BATSRUS/Doc/Tex/synopticSW.tex","corpus_root":"/Users/zkeheng/SWMFSoftware/SWMF","corpus_slice":"swmf_manuals"}],"authority":"heuristic","source_kind":"source_index","note":"Results are heuristic (regex/FTS5-based). Use PARAM.XML and TestParam.pl for authoritative validation.","swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked heuristic candidate: /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype","Checked heuristic candidate: /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF","Resolved from heuristic search (cwd/workspace/run_dir/symlink-aware)."]}
```


---

<sub>⏱️ 33s</sub>

### ✅ `swmf-prototype-swmf_search_source`

**HMI magnetogram**

<details>
<summary>Arguments</summary>

```json
{
  "query": "HMI magnetogram",
  "max_results": 50
}
```

</details>

```
{"ok":true,"query":"HMI magnetogram","filters":{"component":null,"kind":null,"corpus_slice":null},"result_count":0,"results":[],"authority":"heuristic","source_kind":"source_index","note":"Results are heuristic (regex/FTS5-based). Use PARAM.XML and TestParam.pl for authoritative validation.","swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked heuristic candidate: /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype","Checked heuristic candidate: /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF","Resolved from heuristic search (cwd/workspace/run_dir/symlink-aware)."]}
```


---

<sub>⏱️ 34s</sub>

### ✅ `swmf-prototype-swmf_search_source`

**ADAPT map**

<details>
<summary>Arguments</summary>

```json
{
  "query": "ADAPT map",
  "max_results": 50
}
```

</details>

```
{"ok":true,"query":"ADAPT map","filters":{"component":null,"kind":null,"corpus_slice":null},"result_count":0,"results":[],"authority":"heuristic","source_kind":"source_index","note":"Results are heuristic (regex/FTS5-based). Use PARAM.XML and TestParam.pl for authoritative validation.","swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked heuristic candidate: /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype","Checked heuristic candidate: /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF","Resolved from heuristic search (cwd/workspace/run_dir/symlink-aware)."]}
```


---

<sub>⏱️ 35s</sub>

### ✅ `swmf-prototype-swmf_search_source`

**synoptic map solar**

<details>
<summary>Arguments</summary>

```json
{
  "query": "synoptic map solar",
  "max_results": 50
}
```

</details>

```
{"ok":true,"query":"synoptic map solar","filters":{"component":null,"kind":null,"corpus_slice":null},"result_count":0,"results":[],"authority":"heuristic","source_kind":"source_index","note":"Results are heuristic (regex/FTS5-based). Use PARAM.XML and TestParam.pl for authoritative validation.","swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked heuristic candidate: /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype","Checked heuristic candidate: /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF","Resolved from heuristic search (cwd/workspace/run_dir/symlink-aware)."]}
```


---

<sub>⏱️ 45s</sub>

### ✅ `glob`

**SWMF/**/*magnet***

"SWMF/**/*magnet*"

```
No files matched the pattern.
```


---

<sub>⏱️ 45s</sub>

### ✅ `glob`

**SWMFSOLAR/**/*magnet***

"SWMFSOLAR/**/*magnet*"

```
No files matched the pattern.
```


---

<sub>⏱️ 49s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "read_magnetogram|ModReadMagnetogram|PFSSM|magnetogram|readfits|GONG|ADAPT|HMI|synoptic",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF",
  "output_mode": "files_with_matches"
}
```

</details>

<details>
<summary>20 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Makefile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/PARAM.XML
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Makefile.test
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/Makefile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Param/PARAM.in.test.OHPT.FLEKS.outerhelio.swh
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/SWMF_example_runs.tex
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Param/PARAM.in.test.OHPT.FLEKS.outerhelio.swhpui
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Param/PARAM.in.realtime.restart.SCIH_threadbc
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/doc/Tex/PHYSICS.tex
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/CON/Control/src/Makefile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Param/PARAM.in.test.GMPC.FLEKS.2D.restart
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Param/PARAM.in.test.GMPC.FLEKS.periodic
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Param/map_04.out
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Param/PARAM.in.test.GMPC.FLEKS.2D.2steps
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Param/PARAM.in.test.GMPC.FLEKS.2D.adapt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Param/PARAM.in.test.GMPC.FLEKS.2D.periodic
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Param/PARAM.in.test.GMPC.FLEKS.2D.4steps
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Param/map_1.out
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Param/PARAM.in.test.GMPC.FLEKS.3D
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/Param/SWPC/PARAM.in_aepic_init
```

</details>


---

<sub>⏱️ 50s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "read_magnetogram|ModReadMagnetogram|PFSSM|magnetogram|readfits|GONG|ADAPT|HMI|synoptic",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR",
  "output_mode": "files_with_matches"
}
```

</details>

<details>
<summary>131 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/README
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Makefile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/.gitignore
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/writeMaxProRunsToFile.jl
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/writeRestartRunsToFile.jl
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/HARMONICS.in
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/writeLHSRunsToFileRandomized.jl
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/harmonics_adapt.dat
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/sub_runs.py
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/FDIPS.in
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/writeQMCRunsToFile.jl
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Events/param_list.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/writeSEPBackgroundList.jl
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/writeBaselineRunsToFile.jl
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Events/CR2209/AWSoM_AWSoMR_comp_06Oct2020/PARAM.in.awsomr
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CR2192_AWSoM2T_CME_2022_10_28.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/README_Julia.md
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CR2219_AWSoM2T_backgrounds.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Events/CR2209/AWSoM_AWSoMR_comp_Jun2020/Input/PARAM.in.AWSOMR
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Prompts.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CR2154_backgrounds_validation_study_2024_02_05.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_bg_CR2095.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CR2140_AWSoM2T_backgrounds.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/GSA/gsaUtilities.jl
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CR2154_2022_09_08.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Events/CR2209/AWSoM_AWSoMR_comp_Jun2020/Figures/CR2209_los_aia_AWSOMR_scheme5_TR_IB1_05.eps
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_bg_CR2270.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/writeQMCModelComparisonList.jl
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CR2281_AWSoM2T_backgrounds.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CR2107_2134_2142_backgrounds_validation_study_2024_06_19.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/writeLHSRunsToFile.jl
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CR2152_updated.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Events/CR2209/AWSoM_AWSoMR_comp_Jun2020/Input/PARAM.in.AWSOM
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/writeQMCReducedSpaceModelComparisonList.jl
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Events/CR2209/AWSoM_AWSoMR_comp_Jun2020/Figures/CR2209_los_aia_AWSOMR_scheme5_TR.eps
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_baseline_3models.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Events/CR2107/AWSoM_Reflection_July2020/Figures/CR2107_los_aia_refl_1_1.eps
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CME_CR2095.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/Backgrounds_AWSoM3T_6_events.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/unused_param_lists/param_list_ADAPT_AWSoM_CR2154_2021_10_06.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/unused_param_lists/param_list_CR2107_AWSoM2T_validation_study_2024_03_08.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Events/CR2209/AWSoM_AWSoMR_comp_Jun2020/Figures/CR2209_los_aia_AWSOM_scheme5.eps
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/revised_threshold/2021_07_11_18_01_52_event_list_SolarMax_ADAPT_AWSoMR_CR2152.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/unused_param_lists/param_list_ADAPT_AWSoM_CR2154_2021_10_05.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/revised_threshold/2021_07_30_00_28_54_event_list_SolarMin_ADAPT_AWSoM_CR2208.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CME_CR2270.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/unused_param_lists/param_list_ADAPT_AWSoM_CR2154_2021_10_01.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/unused_param_lists/param_list_ADAPT_AWSoM_CR2152_2021_10_08.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CR2192_backgrounds_validation_study_2024_02_05.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/revised_threshold/2021_07_11_18_18_06_event_list_SolarMin_ADAPT_AWSoM2T_CR2208.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/revised_threshold/2021_07_11_18_16_10_event_list_SolarMax_ADAPT_AWSoM2T_CR2152.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/revised_threshold/2021_07_30_00_44_41_event_list_SolarMax_ADAPT_AWSoM_CR2152.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/X_discrete_factors_QMC_eventList.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/unused_param_lists/param_list_ADAPT_AWSoM_CR2154_2021_10_02.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/unused_param_lists/param_list_CR2134_AWSoM2T_validation_study_2024_03_08.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/revised_thresholds/X_design_QMC_masterList_solarMin_AWSoM_reducedThreshold.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/original_threshold/2021_07_10_20_18_41_event_list_SolarMax_ADAPT_AWSoM_CR2152.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/revised_threshold/2021_07_11_18_14_05_event_list_SolarMin_ADAPT_AWSoM_CR2208.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/revised_threshold/2021_07_11_18_11_46_event_list_SolarMin_ADAPT_AWSoMR_CR2208.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/unused_param_lists/param_list_CR2142_AWSoM2T_validation_study_2024_03_08.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/X_design_QMC_masterList_solarMin_AWSoM2T.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/revised_threshold/2021_07_11_18_11_12_event_list_SolarMax_ADAPT_AWSoM_CR2152.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/unused_param_lists/param_list_ADAPT_AWSoM_CR2154_2021_10_19.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/revised_thresholds/X_design_QMC_masterList_solarMax_AWSoMR_reducedThreshold.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CR2161_backgrounds_validation_study_2024_02_05.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/unused_param_lists/param_list_ADAPT_AWSoM_CR2154_2021_10_08.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/revised_thresholds/X_design_QMC_masterList_solarMin_AWSoM_reducedThreshold.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/X_design_QMC_masterList_solarMax_AWSoM2T.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CR2192_AWSoM2T_backgrounds.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/original_threshold/2021_07_10_20_22_17_event_list_SolarMin_ADAPT_AWSoM_CR2208.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/revised_thresholds/X_design_QMC_masterList_solarMax_AWSoM_reducedThreshold.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/unused_param_lists/param_list_ADAPT_AWSoM_CR2154_2021_09_29.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/sep_param_lists/SEP_Background_20220321.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/X_design_QMC_reducedSpace_solarMin.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CR2161_AWSoM2T_backgrounds.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/sep_param_lists/SEP_Range_20220321.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/X_design_QMC_masterList_solarMax_AWSoMR.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/unused_param_lists/param_list_ADAPT_AWSoM_CR2154_2021_10_18.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/X_design_QMC_reducedSpace_solarMax.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/unused_param_lists/param_list_ADAPT_AWSoM_CR2192_2022_03_02.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/revised_thresholds/X_design_QMC_masterList_solarMin_AWSoMR_reducedThreshold.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/sample_outputs/example_some_backgrounds_param_list.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/original_threshold/2021_07_10_20_21_02_event_list_SolarMin_ADAPT_AWSoMR_CR2208.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_baseline_16runs.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/X_design_QMC_masterList_solarMin_AWSoMR.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/revised_thresholds/X_design_QMC_masterList_solarMin_AWSoMR_reducedThreshold.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/unused_param_lists/param_list_2022_01_21.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/X_design_QMC_masterList_solarMin_AWSoM.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/X_design_QMC_masterList_solarMax_AWSoM.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/param_list_CR2208_updated.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/sample_outputs/example_all_backgrounds_param_list.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/original_threshold/2021_07_10_22_22_10_event_list_SolarMax_ADAPT_AWSoM2T_CR2152.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/revised_thresholds/X_design_QMC_masterList_solarMax_AWSoM_reducedThreshold.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/QMC_Data_for_param_lists/revised_thresholds/X_design_QMC_masterList_solarMax_AWSoMR_reducedThreshold.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/original_threshold/2021_07_10_22_22_44_event_list_SolarMin_ADAPT_AWSoM2T_CR2208.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/param_list_ADAPT_AWSoM_CR2161_2022_01_28.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/all_backgrounds/2021_04_16_09_06_29_event_list_MaxPro_ADAPT_AWSoM_CR2208.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/all_backgrounds/X_design_QMC_ADAPT_AWSoM_solarMax.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/all_backgrounds/X_design_QMC_ADAPT_AWSoM_solarMin.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/background_model_comparison_param_lists/original_threshold/2021_07_10_20_09_38_event_list_SolarMax_ADAPT_AWSoMR_CR2152.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/2021_01_19_14_29_02_event_list_lhs.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/2021_01_29_00_04_58_event_list_randomized.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/2021_01_27_10_18_29_event_list_randomized.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/all_backgrounds/2021_07_04_09_37_12_event_list_SolarMin_ADAPT_AWSoM_CR2208.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/all_backgrounds/2021_06_02_21_00_05_event_list_MaxPro_ADAPT_AWSoM_CR2152.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/restartRunDesignFiles/CR2192/X_background_post_range_CR2192.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/2021_01_30_03_11_50_event_list_randomized.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/all_backgrounds/2021_07_04_09_35_26_event_list_SolarMax_ADAPT_AWSoM_CR2152.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/2021_01_29_09_51_50_event_list_randomized.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/restartRunDesignFiles/CR2095/EEGGL_Params.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/restartRunDesignFiles/CR2161/param_list_CR2161_modified.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/param_list_CR2192_modified.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/param_list_ADAPT_AWSoM_CR2154_2021_11_08.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/2021_02_06_04_51_17_event_list_randomized.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/2021_01_30_18_58_25_event_list_randomized.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/2021_01_28_21_00_38_event_list_randomized.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/restartRunDesignFiles/unusedDesignFiles/SEP_Range_20220311.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/2021_04_09_X_design_MaxPro_ADAPT_AWSoM.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/2021_04_09_13_34_23_event_list_MaxPro_ADAPT_AWSoM_CR2208.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/restartRunDesignFiles/CR2161/X_design_CME_2022_01_28_wrongBrFactor.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/restartRunDesignFiles/unusedDesignFiles/X_background_CR2192_2022_02_14_old.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/CR2154/param_list_CR2154_modified.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/restartRunDesignFiles/CR2270/EEGGL_Params.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/restartRunDesignFiles/unusedDesignFiles/param_list_ADAPT_AWSoM_CR2192_2022_03_21_old_BrFactor.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/CR2154/3params_background_0928.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/restartRunDesignFiles/unusedDesignFiles/SEP_Background_20220311.csv
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/restartRunDesignFiles/unusedDesignFiles/param_list_CR2161_AWSoM2T_CME_2022_10_31.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/restartRunDesignFiles/unusedDesignFiles/param_list_background_CR2192_oldBrFactor.txt
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/output/old_code_v_lists/CR2154/Params_MaxPro_postdist.csv
```

</details>


---

<sub>⏱️ 59s</sub>

### 💬 Copilot

I found the likely hotspots; next I’m reading the magnetogram modules and SWMFSOLAR scripts to reconstruct the actual ingestion flow.

---

<sub>⏱️ 1m 1s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram

<details>
<summary>64 lines</summary>

```
BOUNDARY.in
CME.ref
FDIPS.f90
FDIPS.in.orig
FDIPS.in.wedge
FDIPS_hypre.f90
FDIPS_module.f90
FDIPS_module_twoghostcells.f90
FDIPS_nohypre.f90
GLSETUP.py
GLSETUP1.pro
GLSETUP2.pro
GLSETUPAlg.py
GLSETUPAlg_ccmc.py
HARMONICS.in.ADAPT.orig
HARMONICS.in.orig
HARMONICSGRID.in.orig
MagHarmonics.pl
Makefile
Makefile.RULES
Makefile.RULES.all
ModMagHarmonics.f90
ModMagnetogram.f90
ModOpenClosedBoundary.f90
ModReadMagnetogram.f90
POTENTIAL.in
README
README_GLSETUP
SWMF_GLSETUP.pro
TDSETUP.py
TDSETUPAlg.py
adapt40411_02e012_201708132000_i00020000n0.fts
awsom_script.py
convert_harmonics.f90
dipole11.f90
download_ADAPT.py
fdips.ref
fdips_bxyz_ref.out.gz
fdips_hypre.ref
fdips_ref.out.gz
fdips_wedge.ref
fdips_wedge_input.gz
fdips_wedge_ref.gz
fits_to_ascii.pro
fits_to_hipfth5.pro
fitsfile.fits
get_magnetogram.py
harmonics.f90
harmonics.pro
harmonics.ref
magneticfield_1.0.sav
open_closed_boundary.f90
potential.ref
potential_field.f90
pyfits
read_fits.py
read_magnetogram.pro
readfits.pro
redistribute.pl
remap_magnetogram.py
run_fits_to_ascii.pro
test.fits
test.in
verify11.pro
```

</details>


---

<sub>⏱️ 1m 1s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts

<details>
<summary>8 lines</summary>

```
change_awsom_param.py
change_param.py
compare_insitu.py
download_ADAPT.py
procedures_insitu.py
sub_ft_bundle_job.py
sub_runs.py
watch_runlog.py
```

</details>


---

<sub>⏱️ 1m 1s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param

<details>
<summary>14 lines</summary>

```
FDIPS.in
HARMONICS.in
PARAM.in.awsom
PARAM.in.awsom.CME
PARAM.in.awsom.CME_gpu
PARAM.in.awsom.STITCH
PARAM.in.awsom_gpu
PARAM.in.awsomr
PARAM.in.awsomr.CME
PARAM.in.sofie
PARAM.in.sofie.CCMC
PARAM.in.sofie.CME
PARAM.in.sofie.MFLAMPA
harmonics_adapt.dat
```

</details>


---

<sub>⏱️ 1m 14s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "use\\s+ModReadMagnetogram|read_magnetogram_param\\(|read_orig_magnetogram\\(|read_modified_magnetogram\\(|use\\s+ModMagnetogram",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF",
  "output_mode": "content",
  "-n": true,
  "head_limit": 300
}
```

</details>

```
No matches found.
```


---

<sub>⏱️ 1m 14s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/PARAM.XML**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "#HARMONICSFILE|#MAGNETOGRAMFILE|#PFSSM|Magnetogram|DoUseHarmonics|NameFileMap|NameFileHarmonics",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/PARAM.XML",
  "output_mode": "content",
  "-n": true,
  "head_limit": 300
}
```

</details>

```
No matches found.
```


---

<sub>⏱️ 1m 14s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "download_ADAPT|magnetogram|HARMONICS|FDIPS|PFSSM|NameFile|BrFactor|ADAPT|GONG|HMI",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts",
  "output_mode": "content",
  "-n": true,
  "head_limit": 300
}
```

</details>

<details>
<summary>51 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/sub_runs.py:25:                TypeMap      = 'ADAPT'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/sub_runs.py:28:                TypeMap      = 'GONG'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/sub_runs.py:148:                            + 'BrFactor*PoyntingFlux',
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/sub_runs.py:214:            PFSS  = 'HARMONICS'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/sub_runs.py:238:                BrFactor_local     = float(NewParam['change']['BrFactor'])
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/sub_runs.py:240:                if BrFactor_local*PoyntingFlux_local > ARGS.ThresholdBrPoynting:
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/sub_runs.py:242:                                  +'BrFactor           ='+str(BrFactor_local)           + '\n'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/sub_runs.py:244:                                  +'BrFactor*PoyntingFluxPerBSi ='+str(BrFactor_local*PoyntingFlux_local) + '\n'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/sub_runs.py:245:                                  +'BrFactor*PoyntingFluxPerBSi >'+str(ARGS.ThresholdBrPoynting))
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/sub_runs.py:311:            # copy the PARAM.in, HARMONICS.in and FDIPS.in files
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/sub_runs.py:354:            # clean the PARAM.in, HARMONICS.in, FDIPS.in and map_*.out files 
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py:10:def download_ADAPT_magnetogram(timeIn, NameTypeMap='fixed'):
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py:13:    line and download the corresponding ADAPT map.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py:21:        raise ValueError('Unrecognized type of ADAPT map: '+NameTypeMap)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py:23:    # ADAPT maps only contains the hours for even numbers
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py:29:    # Go to the the ADAPT ftp server
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py:33:    # Only ADAPT GONG is considered
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py:46:    # Only consider the public (4) Carrington Fixed (0) GONG (3) ADAPT maps
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py:93:        # try to download the magnetogram
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py:126:    NameTypeMap = input('Type of ADAPT maps: fixed or central?  ')
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py:128:    download_ADAPT_magnetogram(timeIn,NameTypeMap)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:9:from remap_magnetogram import FITS_RECOGNIZE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:10:import download_ADAPT
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:16:    params_pfss = ['CHANGEWEAKFIELD', 'BrFactor', 'BrMin', 'nHarmonics']
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:19:        # need to turn on CHANGEWEAKFIELD if BrFactor and/or BrMin are changed
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:20:        if 'BrFactor' in new_params['change'].keys() or 'BrMin' in new_params['change'].keys():
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:37:    # set the PFSS solver, FDIPS or Harmonics
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:38:    # If it is HARAMONICS, no need to change as HARMONICS is the default
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:39:    if (pfss == 'FDIPS'):
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:41:            new_params['add']=new_params['add']+',LOOKUPTABLE(FDIPS)'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:43:            new_params['add']='LOOKUPTABLE(FDIPS)'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:45:            new_params['rm'] =new_params['rm']+',HARMONICSFILE,HARMONICSGRID' 
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:47:            new_params['rm'] = 'HARMONICSFILE,HARMONICSGRID'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:48:    elif pfss not in ['FDIPS','HARMONICS']:
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:49:        raise ValueError(pfss + ' must be either FDIPS')
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:104:            # Download the ADAPT magnetogram if no map is pvoided
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:106:            filename_map = download_ADAPT.download_ADAPT_magnetogram(time_input)[0]
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:110:                             + 'by -t/--time to download the ADAPT map.')
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:112:        # The ADAPT map is provied
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:118:        # Very weird GONG Synoptic map, the map time is a few days after the end of the CR.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:120:        if (map_local[0] == 'NSO-GONG Synoptic'):
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:126:            # on the time info from the ADAPT map.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:185:    str_exe = str('Scripts/remap_magnetogram.py ' + filename_map)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:194:                        + ' automatically download the ADAPT map.')
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:205:                            help='(default: HARMONICS.)'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:207:                            type=str, default='HARMONICS')
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:210:                            + ' Use if you want to specify the ADAPT map.',
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_param.py:11:    Add commands in PARAM.in/FDIPS.in/HARMONICS.in files.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_param.py:133:    Add commands in PARAM.in/FDIPS.in/HARMONICS.in files.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_param.py:220:    Replace commands with their parameters in PARAM.in/FDIPS.in/HARMONICS.in
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_param.py:409:    Change the value of a parameter in PARAM.in/FDIPS.in/HARMONICS.in files.
```

</details>


---

<sub>⏱️ 1m 14s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "#HARMONICSFILE|#MAGNETOGRAMFILE|#PFSSM|magnetogram|harmonics|FDIPS",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param",
  "output_mode": "content",
  "-n": true,
  "head_limit": 300
}
```

</details>

<details>
<summary>68 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:14:For changing the distance of the source surface, rMax in FDIPS.in
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:15:needs to change if using FDIPS and rSourceSurface in this file
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:16:needs to change if using harmonics.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:87:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:93:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:94:SC/harmonics_adapt.dat		NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:14:For changing the distance of the source surface, rMax in FDIPS.in
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:15:needs to change if using FDIPS and rSourceSurface in this file
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:16:needs to change if using harmonics.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:85:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:91:#HARMONICSFILE		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:92:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:10:For changing the distance of the source surface, rMax in FDIPS.in
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:11:needs to change if using FDIPS and rSourceSurface in this file
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:12:needs to change if using harmonics.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:83:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:89:#HARMONICSFILE		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:90:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.STITCH:9:For changing the distance of the source surface, rMax in FDIPS.in
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.STITCH:10:needs to change if using FDIPS and rSourceSurface in this file
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.STITCH:11:needs to change if using harmonics.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.STITCH:81:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.STITCH:88:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:11:For changing the distance of the source surface, rMax in FDIPS.in
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:12:needs to change if using FDIPS and rSourceSurface in this file
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:13:needs to change if using harmonics.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:82:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:88:#HARMONICSFILE		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:89:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:10:For changing the distance of the source surface, rMax in FDIPS.in
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:11:needs to change if using FDIPS and rSourceSurface in this file
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:12:needs to change if using harmonics.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:78:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:84:#HARMONICSFILE		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:85:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:11:For changing the distance of the source surface, rMax in FDIPS.in
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:12:needs to change if using FDIPS and rSourceSurface in this file
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:13:needs to change if using harmonics.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:85:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:91:#HARMONICSFILE		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:92:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:14:For changing the distance of the source surface, rMax in FDIPS.in
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:15:needs to change if using FDIPS and rSourceSurface in this file
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:16:needs to change if using harmonics.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:87:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:93:#HARMONICSFILE		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:94:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/HARMONICS.in:5:! Name of the input magnetogram ascii file
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/HARMONICS.in:6:#MAGNETOGRAMFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/HARMONICS.in:14:! Default output file name is harmonics.dat
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/HARMONICS.in:17:harmonics_adapt.dat		NameFileOut
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/HARMONICS.in:19:! Default is the number of latitudes in the magnetogram but at most
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/FDIPS.in:1:! Provide name of magnetogram file and specify maximum field strength
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/FDIPS.in:4:#MAGNETOGRAMFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/FDIPS.in:41:! nProcTheta*nProcPhi should agree with the number of procs FDIPS.exe uses
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:14:For changing the distance of the source surface, rMax in FDIPS.in
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:15:needs to change if using FDIPS and rSourceSurface in this file
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:16:needs to change if using harmonics.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:84:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:90:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:91:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:13:For changing the distance of the source surface, rMax in FDIPS.in
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:14:needs to change if using FDIPS and rSourceSurface in this file
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:15:needs to change if using harmonics.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:75:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:81:#HARMONICSFILE		^		
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:82:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CCMC:78:#HARMONICSFILE
```

</details>


---

<sub>⏱️ 1m 28s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "subroutine\\s+read_|module\\s+ModReadMagnetogram|call\\s+read_|#MAGNETOGRAMFILE|NameFile|TypeFile|TypeMap|readfits|fits|harmonics|FDIPS|PFSS",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram",
  "output_mode": "content",
  "-n": true,
  "head_limit": 400
}
```

</details>

<details>
<summary>6 lines</summary>

```
Output too large to read at once (99.5 KB). Saved to: /var/folders/pn/yhfjt4h144j54nktzjsjv_j80000gp/T/copilot-tool-output-1776789624637-jl9ybk.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/MagHarmonics.pl:9:# Asking for filename, CR, data source, max harmonics, and number of processors
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/MagHarmonics.pl:31:# Calling idl to read the fits file. This idl routine
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/MagHarmonics.pl:32:# creates a file contains the fits file's header (filename.H) and a
```

</details>


---

<sub>⏱️ 1m 28s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "ModMagnetogram|ModReadMagnetogram|NameHarmonicsFile|HARMONICSFILE|LOOKUPTABLE\\s+FDIPS|PFSS|FDIPS",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC",
  "output_mode": "content",
  "-n": true,
  "head_limit": 400
}
```

</details>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/Makefile:30:		ln -s ${BINDIR}/FDIPS.exe .; \
```


---

<sub>⏱️ 1m 28s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/PARAM.XML**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "#HARMONICSFILE|NameHarmonicsFile|LOOKUPTABLE\\s+FDIPS|#MAGNETOGRAMFILE|NameFileMap|BrFactor|PFSS",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/PARAM.XML",
  "output_mode": "content",
  "-n": true,
  "head_limit": 400
}
```

</details>

```
No matches found.
```


---

<sub>⏱️ 1m 28s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "remap_magnetogram|download_ADAPT|change_param|NameTypeMap|NameMap|BrFactor|#MAGNETOGRAMFILE|HARMONICS.in|FDIPS.in",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR",
  "output_mode": "content",
  "-n": true,
  "glob": "*.{py,in,jl,txt,md,README}",
  "head_limit": 500
}
```

</details>

<details>
<summary>6 lines</summary>

```
Output too large to read at once (2.4 MB). Saved to: /var/folders/pn/yhfjt4h144j54nktzjsjv_j80000gp/T/copilot-tool-output-1776789624647-ucctat.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/writeRestartRunsToFile.jl:25:# 1 model=          map=                BrFactor=       PoyntingFluxPerBSi=         LperpTimesSqrtBSi=
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/ParamListScripts/writeLHSRunsToFileRandomized.jl:54:# Order: BrFactor_GONG, BrFactor_ADAPT, rMin_AWSoMR, nChromoSi_AWSoM, PoyntingFluxPerBSI, LperpTimesSqrtBSI, StochasticExponent. 
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOL
```

</details>


---

<sub>⏱️ 1m 35s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModReadMagnetogram.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModReadMagnetogram.f90 (lines 1-260)

<details>
<summary>260 lines</summary>

```
1. !  Copyright (C) 2002 Regents of the University of Michigan,
2. !  portions used with permission
3. !  For more information, see http://csem.engin.umich.edu/tools/swmf
4. 
5. module ModReadMagnetogram
6. 
7.   ! Read the raw magnetogram and modify the field as needed.
8. 
9.   use ModNumConst
10.   use ModUtilities, ONLY: CON_stop
11.   use ModConst, ONLY: cHalfPi, cPi, cTwoPi
12. 
13.   implicit none
14. 
15.   private ! except
16. 
17.   public:: read_magnetogram_param ! reads the input parameters
18.   public:: read_orig_magnetogram  ! reads and modifies the magnetogram
19. 
20.   real,    public, allocatable:: Br0_II(:,:) ! Final Magnetic field
21.   integer, public:: nThetaAll, nPhiAll    ! Size of remeshed grid for FDIPS
22.   integer, public:: nTheta0, nPhi0        ! size passed to harmonics & fdips
23.   integer, public:: nThetaorig, nPhiorig  ! original magnetogram theta and phi
24.   logical, public:: UseCosTheta = .true.  ! To check the latitude grid
25.   real,    public:: dPhi=1.0, dTheta=1.0, dSinTheta=1.0
26.   logical, public:: UseChebyshevNode = .true.
27.   real,    public,  allocatable:: ChebyshevWeightE_I(:), ChebyshevWeightW_I(:)
28. 
29.   ! Carrington rotation # plus  fraction of the synodic Carrington rotation
30.   ! period passed since the CR start till the time of magnetogram.
31.   ! For a particular case of the GONG synoptic map this equals CR#+0.5.
32.   ! For a particular case of the GONG hourly magnetogram, this parameter
33.   ! equals CRNOW as provided in the fitsfile header. Once read from the
34.   ! magnetogram file, this parameter is converted to the fromat similar to
35.   ! #STARTTIME and saved to MAGNETOGRAMTIME.in file. It is strongly
36.   ! recommended to check if this saved time looks reasonable
37.   real, public:: MagnetogramTimeCR = 0.
38. 
39.   ! Carrington longitude of the left margin of the map ("leading longitude")
40.   real, public:: LongShift = 0.
41. 
42.   ! Phi, Lat passed to FDIPS
43.   real, public, allocatable:: Phi0_I(:), Lat0_I(:)
44. 
45.   ! Header
46.   character(len=500), public :: StringMagHeader
47. 
48.   ! Input parameters
49.   character (len=100):: NameFileIn = 'fitsfile.out'
50.   real:: BrMax = 3500.0
51. 
52.   ! Optional enhancement of the polar magnetic field with a factor
53.   !  1 + (PolarFactor-1)*abs(sin(Latitude))^PolarExponent
54.   logical           :: DoChangePolarField = .false.
55.   real              :: PolarFactor = 1.0
56.   real              :: PolarExponent = 2.0
57. 
58.   ! Parameters used to apply modified scaling to the raw magnetogram
59.   ! Apply a scaling factor to small magnetic fields, to compensate
60.   ! the measurement error for the coronal hole (=very low) field
61.   logical :: DoChangeWeakField = .false.
62.   real    :: BrFactor = 1.0, BrMin = 0.0
63. 
64.   ! To indicate if fdips is done or harmonics
65.   logical :: IsFdips = .false.
66.   logical :: UseMagnetogramDate = .false.
67. 
68. contains
69.   !============================================================================
70. 
71.   subroutine read_magnetogram_param(NameCommand)
72. 
73.     use ModReadParam, ONLY: read_var
74. 
75.     character(len=*), intent(in):: NameCommand
76.     character(len=*), parameter:: NameSub = 'read_magnetogram_param'
77.     !--------------------------------------------------------------------------
78.     select case(NameCommand)
79.     case("#MAGNETOGRAMFILE")
80.        call read_var('NameFileIn', NameFileIn)
81.        call read_var('BrMax',      BrMax)
82.     case("#CHANGEPOLARFIELD")
83.        DoChangePolarField = .true.
84.        call read_var('PolarFactor',   PolarFactor)
85.        call read_var('PolarExponent', PolarExponent)
86.     case("#CHANGEWEAKFIELD")
87.        DoChangeWeakfield = .true.
88.        call read_var('BrFactor', BrFactor)
89.        call read_var('BrMin', BrMin)
90.     case("#CHEBYSHEV", "#UNIFORMTHETA")
91.        call read_var('UseChebyshevNode', UseChebyshevNode)
92.     case('#USEMAGNETOGRAMDATE')
93.        call read_var('UseMagnetogramDate', UseMagnetogramDate)
94.     case default
95.        call CON_stop(NameSub//': unknown command='//trim(NameCommand))
96.     end select
97. 
98.   end subroutine read_magnetogram_param
99.   !============================================================================
100. 
101.   subroutine read_orig_magnetogram(&
102.        IsPhiThetaOrder, UseWedge, DoRemoveMonopole, nThetaCoarse, nPhiCoarse)
103. 
104.     use ModPlotFile, ONLY: read_plot_file, save_plot_file
105.     use ModConst, ONLY: cDegToRad, tStartCarringtonRotation, &
106.          CarringtonSynodicPeriod
107.     use ModTimeConvert, ONLY: time_real_to_int, time_int_to_real
108.     use ModIoUnit, ONLY: UnitTmp_
109.     use ModUtilities,  ONLY: open_file, close_file, cTab
110. 
111.     logical, optional,  intent(in):: IsPhiThetaOrder
112.     logical, optional,  intent(in):: UseWedge
113.     logical, optional,  intent(in):: DoRemoveMonopole
114.     integer, optional,  intent(in):: nThetaCoarse, nPhiCoarse
115. 
116.     real:: Param_I(2)
117.     real:: BrAverage
118.     real, allocatable :: BrTmp_II(:,:), BrTrans_II(:,:), Var_VII(:,:,:)
119.     real :: MagnetogramTime, CRFraction
120.     integer :: iTime_I(7), iPos=0
121. 
122.     integer:: iError, nParam, iTheta, iPhi, nThetaRatio, nPhiRatio
123.     integer:: iTheta0, iTheta1, jPhi0, jPhi1, jPhi, nVar
124. 
125.     logical :: IsInputLatReverse = .false.
126.     logical :: IsRemoveMonopole = .true., DoEliminateCmeBr = .false.
127.     character(len=200) :: NameVarOut
128. 
129.     character(len=*), parameter:: NameSub = 'read_orig_magnetogram'
130.     !--------------------------------------------------------------------------
131.     call read_plot_file(NameFileIn, StringHeaderOut=StringMagHeader, &
132.          n1Out = nPhi0, n2Out = nTheta0, nVarOut = nVar, &
133.          ParamOut_I=Param_I, iErrorOut=iError, nParamOut=nParam, &
134.          TimeOut=CRFraction)
135. 
136.     if(iError /= 0) call CON_stop(NameSub// &
137.          ': could not read header from file '//trim(NameFileIn))
138. 
139.     ! Reading the original shift in Phi and
140.     ! Central Meridian Longitude from the Map
141.     if(nParam>0) LongShift = Param_I(1)
142.     if(nParam>1) MagnetogramTimeCR = Param_I(2) + CRFraction
143. 
144.     write(*,*) NameSub, &
145.          ': nTheta0, nPhi0, LongitudeShift, MagnetogramTimeCR = ', &
146.          nTheta0, nPhi0, LongShift, MagnetogramTimeCR
147.     ! Saves the original Magnetogram grid
148.     allocate(Phi0_I(nPhi0), Lat0_I(nTheta0))
149.     allocate(Br0_II(nPhi0,nTheta0), Var_VII(nVar,nPhi0,nTheta0))
150. 
151.     call read_plot_file(NameFileIn, &
152.          Coord1Out_I=Phi0_I, Coord2Out_I=Lat0_I, VarOut_VII = Var_VII, &
153.          iErrorOut=iError, NameVarOut=NameVarOut)
154. 
155.     if(iError /= 0) call CON_stop(NameSub// &
156.          ': could not read data from file '//trim(NameFileIn), iError)
157.     Br0_II = Var_VII(1,:,:); DoEliminateCmeBr = index(NameVarOut,'CmeBr') > 0
158.     if(MagnetogramTimeCR > 0.0)then
159.        if(UseMagnetogramDate)then
160.           ! Use MagnetogramDate field from the header to assign
161.           ! magnetogram time
162.           write(*,*)StringMagHeader
163.           iPos = index(StringMagHeader, 'MagnetogramDate = ')
164.           ! Skip 'MagnetogramDate = '
165.           iPos = iPos + 17
166.           if(iPos > 0) then
167.              iTime_I=0
168.              ! read YYYY-MM-DD"T"HH-MM-SS
169.              read(StringMagHeader(iPos+1:iPos+4),*) iTime_I(1)
170.              read(StringMagHeader(iPos+6:iPos+7),*) iTime_I(2)
171.              read(StringMagHeader(iPos+9:iPos+10),*) iTime_I(3)
172.              read(StringMagHeader(iPos+12:iPos+13),*) iTime_I(4)
173.              read(StringMagHeader(iPos+15:iPos+16),*) iTime_I(5)
174.              read(StringMagHeader(iPos+18:iPos+19),*) iTime_I(6)
175.              call time_int_to_real(iTime_I, MagnetogramTime)
176.              MagnetogramTimeCR = (MagnetogramTime - &
177.                   tStartCarringtonRotation)/CarringtonSynodicPeriod
178.           end if
179.        end if
180.        MagnetogramTime = MagnetogramTimeCR*CarringtonSynodicPeriod &
181.             + tStartCarringtonRotation
182.        call time_real_to_int(MagnetogramTime, iTime_I)
183.        call open_file(FILE='MAGNETOGRAMTIME.in', NameCaller=NameSub)
184.        write(UnitTmp_,'(i8,a)')iTime_I(1), cTab//cTab//'iYear'
185.        write(UnitTmp_,'(i8,a)')iTime_I(2), cTab//cTab//'iMonth'
186.        write(UnitTmp_,'(i8,a)')iTime_I(3), cTab//cTab//'iDay'
187.        write(UnitTmp_,'(i8,a)')iTime_I(4), cTab//cTab//'iHour'
188.        write(UnitTmp_,'(i8,a)')iTime_I(5), cTab//cTab//'iMinute'
189.        write(UnitTmp_,'(i8,a)')iTime_I(6), cTab//cTab//'iSecond'
190.        write(UnitTmp_,'(a)')'0.0'//cTab//cTab//cTab//'FracSecond'
191.        write(UnitTmp_,'(a)')'#END'
192.        write(UnitTmp_,*)
193.        call close_file(NameCaller=NameSub)
194.     end if
195. 
196.     ! Check if the latitude coordinate is uniform or not
197.     ! There is no point using Chebyshev transform if the original grid
198.     ! is already uniform in theta
199.     UseCosTheta = abs(Lat0_I(3) - 2*Lat0_I(2) + Lat0_I(1)) > 1e-6
200.     if(.not.UseCosTheta)then
201.        if(UseChebyshevNode) write(*,*) &
202.             'Already uniform in theta, Chebyshev transform is not needed'
203.        UseChebyshevNode = .false.
204.     endif
205. 
206.     IsInputLatReverse = Lat0_I(1) > Lat0_I(nTheta0)
207. 
208.     ! For #CHANGEPOLARFIELD
209.     if(DoChangePolarField)then
210.        ! Add and then subtract CmeBr field, if needed
211.        if(DoEliminateCmeBr)Br0_II = Br0_II - Var_VII(nVar,:,:)
212.        do iTheta = 1, nTheta0
213.           Br0_II(:,iTheta) = Br0_II(:,iTheta) * (1 + &
214.                (PolarFactor-1)*abs(sin(cDegToRad*Lat0_I(iTheta)))&
215.                **PolarExponent)
216.        end do
217.        write(StringMagHeader,'(a,f4.1,a,f4.1)')trim(StringMagHeader)//&
218.             '; PolarFactor = ', PolarFactor,'; PolarExponent = ', PolarExponent
219.        if(DoEliminateCmeBr)Br0_II = Br0_II + Var_VII(nVar,:,:)
220.     end if
221. 
222.     ! options not supported with UseWedge
223.     if(present(UseWedge))then
224.        if(DoChangePolarField .and. UseWedge) &
225.             call CON_stop('UseWedge does not support DoChangePolarField.')
226.        if(UseCosTheta .and. UseWedge) &
227.             call CON_stop(NameSub//&
228.                ': UseWedge only works with uniform latitude grid')
229. 
230.        if(present(DoRemoveMonopole)) &
231.             IsRemoveMonopole = DoRemoveMonopole .and. (.not. UseWedge)
232.     endif
233. 
234.     ! For #CHANGEWEAKFIELD
235.     if(DoChangeWeakField)then
236.        ! Add and then subtract CmeBr field, if needed
237.        if(DoEliminateCmeBr)Br0_II = Br0_II - Var_VII(nVar,:,:)
238.        if(BrMin > 0.0 .or. BrFactor > 1.0) &
239.             Br0_II = sign(min(abs(Br0_II) + BrMin, &
240.             BrFactor*abs(Br0_II)), Br0_II)
241.        write(StringMagHeader,'(a,f4.1,a,f4.1)')trim(StringMagHeader)//&
242.             '; BrFactor =', BrFactor, '; BrMin = ', BrMin
243.        if(DoEliminateCmeBr)Br0_II = Br0_II + Var_VII(nVar,:,:)
244.     endif
245. 
246.     ! Fix too large values of Br
247.     where (abs(Br0_II) > BrMax) Br0_II = sign(BrMax, Br0_II)
248. 
249.     ! Done for both Harmonics & Fdips unless specified otherwise
250.     if(IsRemoveMonopole) then
251.        if (UseCosTheta) then
252.           BrAverage = sum(Br0_II)/(nTheta0*nPhi0)
253.        else
254.           BrAverage = 0.0
255.           do iTheta = 1, nTheta0
256.              BrAverage = BrAverage + &
257.                   sum(Br0_II(:,nTheta0+1-iTheta)) * &
258.                   cos(cDegToRad*Lat0_I(nTheta0+1-iTheta))
259.           enddo
260.           BrAverage = BrAverage / (nTheta0*nPhi0)
```

</details>


---

<sub>⏱️ 1m 35s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModReadMagnetogram.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModReadMagnetogram.f90 (lines 261-520)

<details>
<summary>259 lines</summary>

```
261.        endif
262.        Br0_II = Br0_II - BrAverage
263.        write(*,*)NameSub,': Removing BrAverage =', BrAverage
264.     endif
265. 
266.     ! Save 2D Br in the original magnetogram grid
267.     ! call save_plot_file('field_2d.out', TypeFileIn='ascii',&
268.     !     StringHeaderIn='Longitude, Latitude [Deg], Br[G]', &
269.     !     NameVarIn='Longitude Latitude Br',&
270.     !     VarIn_II=Br0_II, &
271.     !     Coord1In_I=Phi0_I, &
272.     !     Coord2In_I=Lat0_I)
273. 
274.     ! to be passed to harmonics before remeshing
275.     nThetaorig = nTheta0
276.     nPhiorig   = nPhi0
277. 
278.     dPhi      = cTwoPi/nPhi0
279.     dTheta    = cPi/nTheta0
280.     dSinTheta = 2.0/nTheta0
281. 
282.     if(present(nThetaCoarse) .and. present(nPhiCoarse))then
283.        IsFdips = .true.
284.     else if(UseChebyshevNode) then
285.        ! For Harmonics Only
286.        call uniform_theta_transform
287.     endif
288. 
289.     ! To be done for FDIPS only
290.     ! Step 1 : Coarsening for FDIPS based on Input Theta & Phi
291.     if(IsFdips)then
292.        if(nThetaorig > nThetaCoarse .and. nThetaCoarse > 1)then
293.           if(modulo(nThetaorig, nThetaCoarse) /= 0)then
294.              write(*,*) NameSub,' nTheta in file    =', nThetaorig
295.              write(*,*) NameSub,' nTheta in FDIPS.in=', nThetaCoarse
296.              call CON_stop(NameSub//': not an integer coarsening ratio')
297.           end if
298.           ! Set integer coarsening ratio
299.           nThetaRatio = nThetaorig / nThetaCoarse
300.           nThetaAll   = nThetaorig / nThetaRatio
301.        else
302.           nThetaRatio = 1
303.           nThetaAll   = nThetaorig
304.        end if
305. 
306.        if(nPhiorig > nPhiCoarse .and. nPhiCoarse > 1)then
307.           if(modulo(nPhiorig, nPhiCoarse) /= 0)then
308.              write(*,*) NameSub,' nPhi in file    =', nPhiorig
309.              write(*,*) NameSub,' nPhi in FDIPS.in=', nPhiCoarse
310.              call CON_stop(NameSub//': not an integer coarsening ratio')
311.           end if
312.           nPhiRatio = nPhiorig / nPhiCoarse
313.           nPhiAll   = nPhiorig / nPhiRatio
314.        else
315.           nPhiRatio = 1
316.           nPhiAll   = nPhiorig
317.        end if
318. 
319.        allocate(BrTmp_II(nPhiAll,nThetaAll))
320.        BrTmp_II=0.0
321. 
322.        do iPhi = 1, nPhiAll
323.           jPhi0 = nPhiRatio*(iPhi-1) + 1
324.           jPhi1 = jPhi0 + nPhiRatio -1
325. 
326.           do jPhi = jPhi0, jPhi1
327. !!! SHOULD USE CELL AREA ???!!!
328.              do iTheta = 1, nThetaAll
329.                 iTheta0 = nThetaRatio*(iTheta-1) + 1
330.                 iTheta1 = iTheta0 + nThetaRatio - 1
331.                 BrTmp_II(iPhi,iTheta) = BrTmp_II(iPhi,iTheta) &
332.                      + sum( Br0_II(jPhi,iTheta0:iTheta1))
333.              end do
334.           end do
335.        end do
336.        BrTmp_II = BrTmp_II / (nThetaRatio*nPhiRatio)
337.        if(allocated(Br0_II)) deallocate(Br0_II)
338.        allocate(Br0_II(nPhiAll,nThetaAll))
339.        Br0_II = BrTmp_II
340.        deallocate(BrTmp_II)
341. 
342.        ! Save the 2D field after coarsening
343.        call save_plot_file('fdips_2d.out', TypeFileIn='ascii',&
344.             StringHeaderIn='Longitude, Latitude [Deg], Br[G]', &
345.             NameVarIn='Longitude Latitude Br',&
346.             VarIn_II=Br0_II, &
347.             CoordMinIn_D = [cPi/nPhiAll, -cHalfPi+cHalfPi/nThetaAll], &
348.             CoordMaxIn_D = [cTwoPi-cPi/nPhiAll, cHalfPi- cHalfPi/nThetaAll])
349. 
350.        ! Br0_II is phi,theta till here and not reverse
351.        if(UseChebyshevNode)then
352.           write(*,*)'Doing Uniform Theta Transform for FDIPS'
353.           call uniform_theta_transform
354.           UseCosTheta = .false.
355.           nThetaAll = nTheta0
356.           nPhiAll = nPhi0
357.        endif
358.        ! For FDIPS ONLY, transpose
359.        allocate(BrTrans_II(nThetaAll,nPhiAll))
360.        if(present(IsPhiThetaOrder)) then
361.           if(.not. IsPhiThetaOrder)then
362.              if (IsInputLatReverse) then
363.                 BrTrans_II = transpose(Br0_II)
364.              else
365.                 BrTrans_II = transpose(Br0_II(:,nThetaAll:1:-1))
366.              endif
367.           endif
368.        endif
369.        if(allocated(Br0_II)) deallocate(Br0_II)
370.        allocate(Br0_II(nThetaAll,nPhiAll))
371.        Br0_II = BrTrans_II
372.        ! Br0_II is now (Theta, Phi) not lon,Lat
373.        deallocate(BrTrans_II)
374.     endif
375. 
376.   end subroutine read_orig_magnetogram
377.   !============================================================================
378.   subroutine uniform_theta_transform
379. 
380.     ! The magnetogram is remeshed onto a uniform in theta (co-latitude) grid.
381.     ! This corresponds to the Chebyshev points with respect to cos theta,
382.     ! which is the argument of the associated Legendre polynomials.
383.     ! The equal spacing in the theta direction makes the calculation much
384.     ! more accurate, especially in the polar regions.
385.     ! The number of points in the theta direction of the remeshed grid
386.     ! is always an odd number.
387. 
388.     integer :: nThetaIn, nThetaOut, iW, iU, iTheta, iPhi
389.     integer :: iLower, iUpper
390.     real    :: dThetaChebyshev, dThetaInterpolate, BrSouthPole, BrNorthPole
391.     real, allocatable :: ThetaIn_I(:), ThetaOut_I(:), NewBr_II(:,:), &
392.          ChebyshevWeightEu_I(:), Br_II(:,:)
393. 
394.     character(len=*), parameter:: NameSub = 'uniform_theta_transform'
395.     !--------------------------------------------------------------------------
396.     write(*,*) ' Remeshing to Uniform Theta'
397. 
398.     if(IsFdips)then
399.        nTheta0   = nThetaAll
400.        nPhi0     = nPhiAll
401.        dPhi      = cTwoPi/nPhi0
402.        dTheta    = cPi/nTheta0
403.        dSinTheta = 2.0/nTheta0
404.        write(*,*)'IsFdips, nTheta0, nPhi0',IsFdips, nTheta0, nPhi0
405.     endif
406. 
407.     nThetaIn = nTheta0
408.     nThetaOut = ceiling(nThetaIn * cHalfPi)
409. 
410.     ! The number of points in theta direction should be odd
411.     if (modulo(nThetaOut,2) == 0) nThetaOut = nThetaOut+1
412. 
413.     write(*,*) 'Original nThetaIn      =', nThetaIn
414.     write(*,*) 'nThetaOut=nThetaIn*Pi/2=', nThetaOut
415. 
416.     ! Note that the indices start from 0 for both FDIPS & Harmonics
417.     ! Lat grid to Theta grid
418.     allocate(NewBr_II(0:nPhi0-1,0:nThetaOut-1))
419.     allocate(ThetaIn_I(0:nThetaIn-1))
420.     allocate(ThetaOut_I(0:nThetaOut-1))
421. 
422.     do iTheta = 0, nThetaIn-1
423.        if(UseCosTheta)then
424.           ThetaIn_I(iTheta) = cHalfPi - asin((iTheta+0.5)*dSinTheta - 1)
425.        else
426.           call CON_stop(NameSub//': UseCosTheta=F should not happen here')
427.           ThetaIn_I(iTheta) = cHalfPi - ((iTheta + 0.5)*dTheta - cHalfPi)
428.        end if
429.     end do
430. 
431.     dThetaChebyshev = cPi/(nThetaOut-1)
432. 
433.     ! +90 is 0 deg Theta
434.     do iTheta = 0, nThetaOut-1
435.        ThetaOut_I(iTheta) = cPi - iTheta*dThetaChebyshev
436.     end do
437. 
438.     iLower = -1
439.     iUpper = -1
440.     NewBr_II = 0
441. 
442.     ! Allocate a new magnetic field variable which has first index as 0
443.     ! common for both FDIPS and Harmonics
444.     allocate(Br_II(0:nPhi0-1,0:nTheta0-1))
445.     Br_II = Br0_II
446. 
447.     ! Still in PhiTheta order,
448.     ! Assumes that the Lat(0) is -90 (south pole)
449.     BrNorthPole = sum(Br_II(:,nThetaIn-1))/nPhi0
450.     BrSouthPole = sum(Br_II(:,0))/nPhi0
451. 
452.     ! Use linear interpolation to do the data remesh
453.     do iTheta=0, nThetaOut-1
454.        iUpper = floor((cos(ThetaOut_I(iTheta)) - cos(ThetaIn_I(0)))/dSinTheta)
455.        iLower = iUpper+1
456.        do iPhi = 0, nPhi0-1
457.           if (iUpper /= -1 .and. iUpper /= nThetaIn-1 ) then
458.              dThetaInterpolate = ThetaIn_I(iUpper) - ThetaIn_I(iLower)
459.              NewBr_II(iPhi,iTheta) = Br_II(iPhi,iLower)* &
460.                   (ThetaIn_I(iUpper)-ThetaOut_I(iTheta))/dThetaInterpolate &
461.                   +Br_II(iPhi,iUpper)* &
462.                   (ThetaOut_I(iTheta)-ThetaIn_I(iLower))/dThetaInterpolate
463.           else if (iUpper == nThetaIn-1) then
464.              dThetaInterpolate = ThetaIn_I(nThetaIn-1)
465.              NewBr_II(iPhi,iTheta) = BrNorthPole &
466.                   *(ThetaIn_I(nThetaIn-1)-ThetaOut_I(iTheta)) &
467.                   /dThetaInterpolate &
468.                   + Br_II(iPhi,nThetaIn-1) &
469.                   *(ThetaOut_I(iTheta))/dThetaInterpolate
470.           else
471.              dThetaInterpolate = cPi - ThetaIn_I(0)
472.              NewBr_II(iPhi,iTheta) = Br_II(iPhi,0)* &
473.                   (cPi - ThetaOut_I(iTheta))/dThetaInterpolate &
474.                   +BrSouthPole* &
475.                   (ThetaOut_I(iTheta) - ThetaIn_I(0))/dThetaInterpolate
476.           end if
477.        end do
478.     end do
479. 
480.     ! Copying the remeshed grid after interpolation into the previous theta
481.     ! Copy the remeshed grid size into nTheta
482.     nTheta0 = nThetaOut
483. 
484.     ! Copy the remeshed NewBr_II into Br0_II. Br0_II indices begin from 1
485.     if(allocated(Br0_II)) deallocate(Br0_II)
486.     allocate(Br0_II(1:nPhi0,1:nTheta0))
487.     Br0_II = NewBr_II
488. 
489.     ! Calculate the weights for the transformation in theta direction.
490.     allocate(ChebyshevWeightE_I(0: nThetaOut-1))
491.     allocate(ChebyshevWeightW_I(0: nThetaOut-1))
492.     allocate(ChebyshevWeightEu_I(0:(nThetaOut-1)/2))
493. 
494.     ChebyshevWeightW_I    = 0.0
495.     ChebyshevWeightE_I    = 1.0
496.     ChebyshevWeightE_I(0) = 0.5
497.     ChebyshevWeightE_I(nThetaOut-1) = 0.5
498. 
499.     ChebyshevWeightEu_I    = 1.0
500.     ChebyshevWeightEu_I(0) = 0.5
501.     ChebyshevWeightEu_I((nThetaOut-1)/2) = 0.5
502. 
503.     do iW = 0, nThetaOut-1
504.        do iU = 0, (nThetaOut-1)/2
505.           ChebyshevWeightW_I(iW) = ChebyshevWeightW_I(iW) + &
506.                ChebyshevWeightEu_I(iU)*(-2.0)/(4*(iU)**2 - 1)* &
507.                cos(iW*iu*cPi/((nThetaOut-1)/2))
508.        end do
509.     end do
510.     ChebyshevWeightW_I = ChebyshevWeightW_I/(nThetaOut-1)
511. 
512.     deallocate(NewBr_II, ThetaIn_I, ThetaOut_I, ChebyshevWeightEu_I)
513. 
514.   end subroutine uniform_theta_transform
515.   !============================================================================
516. 
517. end module ModReadMagnetogram
518. !==============================================================================
519.
```

</details>


---

<sub>⏱️ 1m 35s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90 (lines 1-260)

<details>
<summary>260 lines</summary>

```
1. !  Copyright (C) 2002 Regents of the University of Michigan,
2. !  portions used with permission
3. !  For more information, see http://csem.engin.umich.edu/tools/swmf
4. module ModMagnetogram
5. 
6.   use ModNumConst,       ONLY: cTwoPi, cRadToDeg, cDegToRad, cPi
7.   use CON_axes,          ONLY: dLongitudeHgrDeg
8.   use ModUtilities,      ONLY: CON_stop, CON_stop_simple
9.   use ModCoordTransform, ONLY: rot_xyz_sph, rot_xyz_rlonlat, rot_matrix_z,&
10.        xyz_to_rlonlat
11.   use ModLookupTable, ONLY: &
12.        i_lookup_table, init_lookup_table, make_lookup_table_3d, &
13.        get_lookup_table, interpolate_lookup_table, Table_I, TableType
14. 
15.   implicit none
16.   save
17. 
18.   private
19. 
20.   integer, public:: iTableB0    = -1     ! index of B0 lookup table
21.   integer, public:: iTableB0New = -1     ! index of new B0 lookup table
22.   integer, public:: iTableB0local    = -1     ! index of B1 lookup table,
23.   !$acc declare create(iTableB0, iTableB0New, iTableB0local)
24.   real:: rMinB0local ! radial limits of table
25.   real:: rMaxB0local
26.   !$acc declare create(rMinB0local, rMaxB0local)
27.   real:: LonMinB0local ! longitude limits of table in degrees
28.   real:: LonMaxB0local
29.   !$acc declare create(LonMinB0local, LonMaxB0local)
30.   real:: LatMinB0local ! latitude limits of table in degrees
31.   real:: LatMaxB0local
32.   !$acc declare create(LatMinB0local, LatMaxB0local)
33. 
34.   ! if point inside B1 table B0 will be set as B0 + B1
35.   public:: read_magnetogram_param        ! read parameters
36.   public:: init_magnetogram_lookup_table ! initialize lookup table
37.   public:: get_magnetogram_field         ! get field at a given point
38. 
39.   ! Local variables -------------
40. 
41.   ! True if new harmonics coefficients are to be read from harmonics files
42.   logical:: DoReadHarmonics = .false., DoReadHarmonicsNew = .false.
43. 
44.   ! Name of the harmonics files
45.   character(len=100):: NameHarmonicsFile = '???', NameHarmonicsFileNew = '???'
46. 
47.   ! variable names in the lookup table created from harmonics files
48.   character(len=*), parameter:: &
49.        NameVarLinear = 'r lon lat bx by bz rMin rMax dLon CR'
50.   character(len=100):: NameVar = NameVarLinear
51. 
52.   ! Carrington rotation of the magnetogram(s) for temporal interpolation
53.   real:: CarringtonRot = -1.0, CarringtonRotNew = -1.0
54.   !$acc declare create(CarringtonRot, CarringtonRotNew)
55. 
56.   ! radius of magnetogram and source surface for spatial extrapolation
57.   real   :: rMagnetogram=1.0, rSourceSurface=2.5
58.   logical:: IsLogRadius = .false.   ! logarithmic grid in radius
59.   integer:: nR=30, nLon=72, nLat=30 ! Size of grid created from harmonics
60. 
61.   ! Maximum and actual order of spherical harmonics
62.   integer:: MaxOrder = 30, nOrder = 30
63. 
64.   ! Weights of the spherical harmonics
65.   real, allocatable:: g_II(:,:), h_II(:,:)
66. 
67.   ! Powers of radius ratios
68.   real, allocatable:: rRsPower_I(:), RmRsPower_I(:), RmRPower_I(:)
69. 
70.   ! Legendre polynomials and its derivative
71.   real, allocatable:: p_II(:,:), Dp_II(:,:)
72. 
73.   ! Azimuthal functions sin(m*phi) and cos(m*phi)
74.   real, allocatable:: SinPhi_I(:), CosPhi_I(:)
75. 
76.   ! Square roots of integers in spherical harmonics
77.   real, allocatable:: Sqrt_I(:), SqrtRatio_I(:)
78. 
79.   ! Lookup table related variables
80.   real:: rMinB0=1.0 ! radial limits of table
81.   real, public:: rMaxB0=30.0 ! radial limits of table
82.   real:: LonMinB0 = 0.0    ! starting longitude in the field lookup table (rad)
83.   real:: dLonB0   = 0.0    ! longitude shift
84.   real:: RotB0_DD(3,3)     ! rotation matrix due to longitude shift
85.   real:: dLonB0New   = 0.0 ! longitude shift
86.   real:: RotB0New_DD(3,3)  ! rotation matrix due to longitude shift
87.   !$acc declare create(rMinB0, rMaxB0, LonMinB0, dLonB0)
88.   !$acc declare create(RotB0_DD, dLonB0New, RotB0New_DD)
89. 
90.   real:: FactorB0 = 1.0 ! multiplier for the magnetic field
91.   !$acc declare create(FactorB0)
92. 
93.   interface get_magnetogram_field
94.      module procedure get_magnetogram_field11, get_magnetogram_field31
95.   end interface get_magnetogram_field
96. 
97. contains
98.   !============================================================================
99.   subroutine init_magnetogram_lookup_table(iComm)
100. 
101.     use ModNumConst, ONLY: cDegToRad
102.     use ModMpi,      ONLY: MPI_comm_rank
103.     use ModPlotFile, ONLY: save_plot_file
104.     integer, intent(in), optional :: iComm
105. 
106.     real:: LonShift ! longitude shift, in degrees, usually semi-integer
107.     integer:: nParam
108.     real:: Param_I(4), IndexMin_I(3), IndexMax_I(3)
109.     logical:: IsLogIndex_I(3)
110.     ! Two  variables to store magnetogram time.
111.     ! Carrigton rootation number:
112.     integer:: nCR = 0
113.     ! Fraction of Carrington rotation since its beginning till magnetogram time
114.     real:: CRFraction  = 0.0
115.     type(TableType), pointer:: TablePtr
116.     real, allocatable:: Magnetogram_VII(:,:,:)
117.     real:: CosLat, OpenFluxNeg, OpenFluxPos
118.     real:: dLon, dLat, Lon, Lat ! in degrees
119.     real:: XyzRLonLat_DD(3,3)
120.     integer :: iLon, iLat
121.     integer :: iProc, iError
122. 
123.     character(len=*), parameter:: NameSub = 'init_magnetogram_lookup_table'
124.     !--------------------------------------------------------------------------
125.     iTableB0    = i_lookup_table('B0')
126.     iTableB0New = i_lookup_table('B0New')
127.     ! Nothing to do if there is no B0 table defined or to be made
128.     if(iTableB0 < 0 .and. .not.DoReadHarmonics) RETURN
129.     ! Get processor index and total number of processors
130.     if(present(iComm))then
131.        call MPI_comm_rank(iComm,iProc,iError)
132.     else
133.        iProc = 0
134.     end if
135.     if(DoReadHarmonics)then
136.        ! Read harmonics coefficients, shift in longitude and CR humber
137.        call read_harmonics_file(NameHarmonicsFile, CarringtonRot, LonShift)
138.        DoReadHarmonics = .false.
139.        nCR        = int(CarringtonRot)
140.        CRFraction = CarringtonRot  - nCR
141.        ! Initialize lookup table based on #HARMONICSGRID parameters
142.        call init_lookup_table( &
143.             NameTable   = 'B0',                    &
144.             NameCommand = 'save',                  &
145.             NameVar     = NameVar,                 &
146.             NameFile    = 'harmonics_bxyz.out',    &
147.             TypeFile    = 'real4',                 &
148.             nIndex_I    = [nR+1, nLon+1, nLat+1],  &
149.             IndexMin_I  = [rMagnetogram,     0.0, -90.0],    &
150.             IndexMax_I  = [rSourceSurface, 360.0,  90.0],    &
151.             Param_I = [rMagnetogram, rSourceSurface, LonShift, real(nCR)], &
152.             Time    = CRFraction,                  &
153.             StringDescription = 'Created from '//trim(NameHarmonicsFile) )
154.        iTableB0 = i_lookup_table('B0')
155. 
156.        ! If lookup table is not loaded from a file, make it and save it
157.        call make_lookup_table_3d(iTableB0, calc_b0_table, iComm)
158. 
159.        call deallocate_harmonics_arrays
160.        if(iProc==0) then
161.           TablePtr => Table_I(iTableB0)
162.           allocate(Magnetogram_VII(6,nLon,nLat+1))
163.           ! omit the strip at the longitude of 360 degrees and take radial cuts
164.           ! at r=1 and r=Rss
165.           Magnetogram_VII(1:3,:,:) = TablePtr%Value4_VC(:,1,1:nLon,:,1,1)
166.           Magnetogram_VII(4:6,:,:) = TablePtr%Value4_VC(:,nR+1,1:nLon,:,1,1)
167.           dLon = TablePtr%DIndex_I(2)
168.           dLat = TablePtr%DIndex_I(3)
169.           do iLat  = 1, nLat + 1
170.              Lat = -90 + dLat*(iLat - 1)
171.              do iLon = 1, nLon
172.                 Lon = dLon*(iLon - 1)
173.                 ! Convert to Br, BLon, BLat components
174.                 XyzRLonLat_DD = &
175.                      rot_xyz_rlonlat(cDegToRad*Lon, cDegToRad*Lat)
176.                 Magnetogram_VII(1:3, iLon, iLat) =            &
177.                      matmul(Magnetogram_VII(1:3,iLon,iLat), XyzRLonLat_DD)
178.                 Magnetogram_VII(4:6, iLon, iLat) =            &
179.                      matmul(Magnetogram_VII(4:6,iLon,iLat), XyzRLonLat_DD)
180.              end do
181.           end do
182.           ! Remesh from latitudinal nodes to pixels:
183.           Magnetogram_VII(:,:,1:nLat) = 0.5*(&
184.                Magnetogram_VII(:,:,1:nLat) + Magnetogram_VII(:,:,2:nLat+1))
185.           OpenFluxPos = 0.0; OpenFluxNeg = 0.0
186.           do iLat = 1, nLat
187.              CosLat = cos(cDegToRad*(-90.0 + dLat*(iLat - 0.5)))
188.              OpenFluxPos = OpenFluxPos + CosLat*sum(Magnetogram_VII(4,:,iLat),&
189.                   MASK=Magnetogram_VII(4,:,iLat)>0.0)
190.              OpenFluxNeg = OpenFluxNeg + CosLat*sum(Magnetogram_VII(4,:,iLat),&
191.                   MASK=Magnetogram_VII(4,:,iLat)<0.0)
192.           end do
193.           ! Scaling factor:
194.           OpenFluxPos = OpenFluxPos*cTwoPi*cPi/(nLon*nLat)*rSourceSurface**2
195.           OpenFluxNeg = OpenFluxNeg*cTwoPi*cPi/(nLon*nLat)*rSourceSurface**2
196.           write(*,'(a,f6.2,a,f4.1,a)')'Unsigned open flux =',&
197.                OpenFluxPos - OpenFluxNeg,&
198.                ' [Gs*R_s^2] at R_SS=', rSourceSurface,' [R_s]'
199.           call save_plot_file(NameFile = 'field_2d.out',  &
200.                nDimIn  = 2,                       &
201.                TimeIn = CRFraction,               &
202.                ParamIn_I= &
203.                [real(int(LonShift)), real(nCR), OpenFluxPos, OpenFluxNeg],&
204.                VarIn_VII= Magnetogram_VII(1:4,1:nLon,1:nLat), &
205.                TypeFileIn    = 'ascii',           &
206.                CoordMinIn_D  = [LonShift - int(LonShift), -90 + 90.0/nLat], &
207.                CoordMaxIn_D  = [360 - 360.0/nLon + LonShift - int(LonShift),&
208.                90 - 90.0/nLat ],&
209.                StringHeaderIn  = 'Created from '//trim(NameHarmonicsFile), &
210.                NameUnitsIn  = &
211.                ' [deg] [deg] [Gs] [Gs] [Gs] [Gs] [Gs] [Gs]'//&
212.                ' [deg] [] [Gs*R_s^2] [Gs*R_s^2]', &
213.                NameVarIn = 'Longitude Latitude Br BLon BLat'//&
214.                ' BrSS Long0 CRNumber OpenFluxPos OpenFluxNeg')
215.           deallocate(Magnetogram_VII)
216.           nullify(TablePtr)
217.        end if
218.     end if
219. 
220.     ! first read local b0
221.     iTableB0local    = i_lookup_table('B0local')
222.     if(iTableB0local > 0) then
223.        call get_lookup_table(iTableB0local, nParam=nParam, Param_I=Param_I, &
224.             IndexMin_I=IndexMin_I, IndexMax_I=IndexMax_I)
225.        rMinB0local = IndexMin_I(1); rMaxB0local = IndexMax_I(1)
226.        LonMinB0local = IndexMin_I(2); LonMaxB0local = IndexMax_I(2)
227.        LatMinB0local = IndexMin_I(3); LatMaxB0local = IndexMax_I(3)
228.        if(iProc == 0)then
229.           write(*,*)NameSub," read B0local table"
230.           write(*,*)NameSub," rMinB0local,   rMaxB0local  =", &
231.                rMinB0local, rMaxB0local
232.           write(*,*)NameSub," LonMinB0local, LonMaxB0local=", &
233.                LonMinB0local, LonMaxB0local
234.           write(*,*)NameSub," LatMinB0local, LatMaxB0local=", &
235.                LatMinB0local, LatMaxB0local
236.        endif
237.     endif
238. 
239.     ! Get coordinate limits, Carrington rotation
240.     call get_lookup_table(iTableB0, nParam=nParam, Param_I=Param_I, &
241.          IndexMin_I=IndexMin_I, IndexMax_I=IndexMax_I, Time=CRFraction, &
242.          IsLogIndex_I=IsLogIndex_I)
243. 
244.     if(IsLogIndex_I(1))then
245.        rMinB0 = 10**IndexMin_I(1); rMaxB0 = 10**IndexMax_I(1)
246.     else
247.        rMinB0 = IndexMin_I(1); rMaxB0 = IndexMax_I(1)
248.     end if
249.     LonMinB0 = IndexMin_I(2)*cDegToRad
250. 
251.     ! Rotation matrix for longitude shift if needed
252.     if(nParam > 2) then
253.        dLonB0 = (Param_I(3) - dLongitudeHgrDeg)*cDegToRad
254.        RotB0_DD = rot_matrix_z(dLonB0)
255.     end if
256.     ! There only 6 meaning digits in the magnetogram metadata fot the
257.     ! Carrington time:
258.     CRFraction = real(nint(CRFraction*1000000))/1000000
259.     ! Get Carrington rotation time of magnetogram
260.     if(nParam > 3) CarringtonRot = nint(Param_I(4)) + CRFraction
```

</details>


---

<sub>⏱️ 1m 35s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90 (lines 1-360)

<details>
<summary>360 lines</summary>

```
1. !  Copyright (C) 2002 Regents of the University of Michigan,
2. !  portions used with permission
3. !  For more information, see http://csem.engin.umich.edu/tools/swmf
4. module ModPotentialField
5. 
6.   use ModMpi
7.   use ModUtilities, ONLY: CON_stop
8.   use ModConst, ONLY: cPi, cTwoPi, cHalfPi
9.   use ModNumConst,    ONLY: cHalfPi, cPi, cDegToRad, cRadToDeg
10. 
11.   implicit none
12. 
13.   ! input parameter
14.   logical:: DoReadMagnetogram = .true.
15.   real :: LongCR = 0.0, CarRot = 0.0
16.   ! grid and domain parameters
17.   integer:: nR = 150, nThetaCoarse = 180, nPhiCoarse = 360
18.   real   :: rMin = 1.0, rMax = 2.5
19.   logical:: UseLogRadius = .false.  ! logarithmic or linear in radius
20. 
21.   ! wedge parameters
22.   logical:: UseWedge = .false.
23.   real   :: ThetaMin = 0, ThetaMax = cPi, PhiMin = 0, PhiMax = cTwoPi
24. 
25.   ! domain decomposition
26.   integer:: nProcTheta = 0, nProcPhi = 0
27.   logical :: IsProcIdle = .false.
28. 
29.   ! solver parameters
30.   character(len=20):: NameSolver         = 'BICGSTAB' ! or 'GMRES' or 'AMG'
31.   character(len=20):: NamePreconditioner = 'ILU' ! or 'AMG' or 'MG'
32.   logical          :: UseHypre           = .false.
33.   logical          :: UsePreconditioner  = .true.
34.   real             :: Tolerance          = 1e-10
35. 
36.   logical           :: DoRemoveMonopole = .true.
37. 
38.   ! output paramters
39.   logical           :: DoSaveBxyz   = .false.
40.   character(len=100):: NameFileBxyz = 'potentialBxyz.out'
41.   character(len=5)  :: TypeFileBxyz = 'real8'
42. 
43.   logical           :: DoSaveField   = .false.
44.   character(len=100):: NameFileField = 'potentialfield.out'
45.   character(len=5)  :: TypeFileField = 'real8'
46. 
47.   logical           :: DoSavePotential   = .false.
48.   character(len=100):: NameFilePotential = 'potentialtest'
49.   character(len=5)  :: TypeFilePotential = 'real8'
50. 
51.   logical           :: DoSaveTecplot   = .false.
52.   character(len=100):: NameFileTecplot = 'potentialfield.dat'
53. 
54.   ! testing parameters
55.   logical :: UseTiming = .true.
56.   real    :: TimeStart, TimeEnd
57. 
58.   logical :: DoTestMe  = .false.
59.   integer :: iRTest = 1, iPhiTest = 1, iThetaTest = 2
60. 
61.   ! local variables --------------------
62.   character(len=100):: NameFile
63. 
64.   logical :: UseBr = .true.
65. 
66.   real, dimension(:), allocatable :: &
67.        Radius_I, Theta_I, Phi_I, SinTheta_I, &
68.        dRadius_I, dPhi_I, dCosTheta_I, &
69.        RadiusNode_I, ThetaNode_I, PhiNode_I, SinThetaNode_I, &
70.        dRadiusNode_I, dTheta_I, dThetaNode_I, dPhiNode_I, dCosThetaNode_I
71. 
72.   real, allocatable::  Potential_C(:,:,:), Rhs_C(:,:,:), Br_II(:,:),&
73.        B0_DF(:,:,:,:), DivB_C(:,:,:), PlotVar_VC(:,:,:,:), BrLocal_II(:,:)
74. 
75.   ! Variables for hepta preconditioner
76.   real, parameter:: PrecondParam = 1.0 ! see ModLinearSolver
77. 
78.   ! Seven diagonals for the preconditioner
79.   real, dimension(:), allocatable :: &
80.        d_I, e_I, e1_I, e2_I, f_I, f1_I, f2_I
81. 
82.   integer, parameter :: iCommWorld = MPI_COMM_WORLD
83.   integer :: iComm = iCommWorld
84.   integer :: iProc, nProc, iProcTheta, iProcPhi
85.   integer :: iTheta0, iPhi0, iLat0
86.   integer :: nTheta, nPhi
87.   real,  allocatable :: TmpXPhi0_II(:,:),TmpXPhipi_II(:,:)
88.   integer :: nThetaLgr,nThetaSml,nPhiLgr,nPhiSml
89.   integer :: nProcThetaLgr,nProcThetaSml,nProcPhiLgr,nProcPhiSml
90. 
91.   real, allocatable :: &
92.        SendBC010_II(:,:), SendBC180_II(:,:), SendBC12_II(:,:), &
93.        SendBC21_II(:,:),  SendBC34_II(:,:), SendBC43_II(:,:), &
94.        SendBC020_II(:,:), SendBC360_II(:,:), &
95.        RecvBCLgr010_II(:,:), RecvBCSml010_II(:,:), &
96.        RecvBCLgr180_II(:,:), RecvBCSml180_II(:,:), &
97.        RecvBC12_II(:,:), RecvBC21_II(:,:), &
98.        RecvBC34_II(:,:), RecvBC43_II(:,:), &
99.        RecvBC020_II(:,:), RecvBC360_II(:,:)
100. 
101. contains
102.   !============================================================================
103. 
104.   subroutine read_fdips_param
105. 
106.     use ModReadParam
107.     use ModReadMagnetogram, ONLY: read_magnetogram_param
108. 
109.     character(len=lStringLine) :: NameCommand
110.     character(len=10):: TypeOutput
111.     integer:: i, iProcTest
112. 
113.     character(len=*), parameter:: NameSub = 'read_fdips_param'
114.     !--------------------------------------------------------------------------
115.     call read_file('FDIPS.in')
116.     call read_init
117.     if(iProc==0) call read_echo_set(.true.)
118. 
119.     do
120.        if(.not.read_line() ) EXIT
121.        if(.not.read_command(NameCommand)) CYCLE
122.        select case(NameCommand)
123.        case("#DOMAIN")
124.           call read_var('rMin', rMin)
125.           call read_var('rMax', rMax)
126.           call read_var('UseLogRadius', UseLogRadius)
127.           call read_var('UseWedge', UseWedge)
128.           if (UseWedge) then
129.              call read_var('wedgeLatMin',ThetaMax)
130.              ThetaMax = (90-ThetaMax) * cDegToRad
131.              call read_var('wedgeLatMax',ThetaMin)
132.              ThetaMin = (90-ThetaMin) * cDegToRad
133.              if (ThetaMax <= ThetaMin) then
134.                 call CON_stop(NameSub//': Wedge latitude_min > latitude_max.')
135.              endif
136.              call read_var('wedgeLonMin',PhiMin)
137.              PhiMin = PhiMin * cDegToRad
138.              call read_var('wedgeLonMax',PhiMax)
139.              PhiMax = PhiMax * cDegToRad
140.              if (PhiMin >= PhiMax) then
141.                 ! wedge over zero meridian
142.                 call CON_stop(NameSub//': '//&
143.                      'Currently does not support wedge over longitude=0.')
144.              endif
145.           endif
146.        case("#GRID")
147.           call read_var('nR',           nR)
148.           call read_var('nThetaCoarse', nThetaCoarse)
149.           call read_var('nPhiCoarse  ', nPhiCoarse)
150.        case("#PARALLEL")
151.           call read_var('nProcTheta', nProcTheta)
152.           call read_var('nProcPhi'  , nProcPhi)
153.        case("#MAGNETOGRAMFILE",'#CHANGEPOLARFIELD', '#CHANGEWEAKFIELD', &
154.             "#CHEBYSHEV")
155.           call read_magnetogram_param(NameCommand)
156.        case('#REMOVEMONOPOLE')
157.           call read_var('DoRemoveMonopole', DoRemoveMonopole)
158.        case("#TIMING")
159.           call read_var('UseTiming', UseTiming)
160.        case("#TEST")
161.           call read_var('iProcTest', iProcTest)
162.           DoTestMe = iProc == iProcTest
163.        case("#TESTIJK")
164.           call read_var('iRTest'    , iRTest)
165.           call read_var('iPhiTest'  , iPhiTest)
166.           call read_var('iThetaTest', iThetaTest)
167.        case("#SOLVER")
168.           call read_var('NameSolver',         NameSolver, &
169.                IsUpperCase=.true.)
170.           call read_var('NamePreconditioner', NamePreconditioner, &
171.                IsUpperCase=.true.)
172.           call read_var('Tolerance',          Tolerance)
173.           UseHypre = index(NameSolver,'MG') > 0 .or. &
174.                index(NamePreconditioner,'MG') > 0
175.           UsePreconditioner = NameSolver == 'BICGSTAB' .and. &
176.                NamePreconditioner /= 'NONE'
177.        case("#HYPRE")
178.           call read_hypre_param
179.        case("#OUTPUT")
180.           call read_var('TypeOutput', TypeOutput, IsLowerCase=.true.)
181.           select case(TypeOutput)
182.           case('b', 'bxyz')
183.              DoSaveBxyz = .true.
184.              call read_var('NameFileBxyz', NameFileBxyz)
185.              call read_var('TypeFileBxyz', TypeFileBxyz)
186.           case('field')
187.              DoSaveField = .true.
188.              call read_var('NameFileField', NameFileField)
189.              call read_var('TypeFileField', TypeFileField)
190.           case('potential')
191.              DoSavePotential = .true.
192.              call read_var('NameFilePotential', NameFilePotential)
193.              call read_var('TypeFilePotential', TypeFilePotential)
194.              ! remove .out extension if present
195.              i = index(NameFilePotential,'.out')
196.              if(i>0) NameFilePotential = NameFilePotential(1:i-1)
197.           case('tecplot')
198.              if(nProc > 1)call CON_stop(NameSub// &
199.                   ': TypeOutput=tecplot works for serial runs only')
200.              DoSaveTecplot = .true.
201.              call read_var('NameFileTecplot', NameFileTecplot)
202.           case default
203.              call CON_stop(NameSub//': unknown TypeOutput='//trim(TypeOutput))
204.           end select
205.        case default
206.           call CON_stop(NameSub//': unknown command='//trim(NameCommand))
207.        end select
208.     end do
209. 
210.     if (nProcTheta*nProcPhi > min(nProc,999) .or. &
211.         max(nProcTheta,nProcPhi) > 99 .or. min(nProcTheta,nProcPhi) <= 0) then
212.       if (iProc == 0) then
213.         write(*,*)
214.         write(*,'(A,2I4,I6)') 'WARNING: nProcTheta, nProcPhi, nProc=', nProcTheta, nProcPhi, nProc
215.         write(*,'(A)') 'Changing to default decomposition!'
216.         write(*,*)
217.       endif
218.       nProcTheta = 0
219.       nProcPhi = 0
220.     endif
221. 
222.     ! Do timing on proc 0 only, if at all
223.     if(iProc > 0) UseTiming = .false.
224. 
225.   end subroutine read_fdips_param
226.   !============================================================================
227.   subroutine read_modified_magnetogram
228. 
229.     use ModReadMagnetogram, ONLY: read_orig_magnetogram, Br0_II,  &
230.          Lat0_I, Phi0_I, nThetaAll, nPhiAll, LongShift, MagnetogramTimeCR
231. 
232.     logical :: IsPhiThetaOrder = .false.
233.     logical :: IsInputLonLatInDegree = .true.
234. 
235.     character(len=*), parameter:: NameSub = 'read_modified_magnetogram'
236.     !--------------------------------------------------------------------------
237.     call read_orig_magnetogram(IsPhiThetaOrder, UseWedge, DoRemoveMonopole, &
238.          nThetaCoarse, nPhiCoarse)
239. 
240.     allocate(Br_II(nThetaAll,nPhiAll))
241.     ! Converting Deg to Radians
242.     if (maxval(abs(Lat0_I)) > cHalfPi .or. &
243.          maxval(abs(Phi0_I)) > cTwoPi) then
244.        IsInputLonLatInDegree = .true.
245.     else
246.        IsInputLonLatInDegree = .false.
247.     endif
248.     if (IsInputLonLatInDegree) then
249.        Phi0_I = Phi0_I * cDegToRad
250.        Lat0_I = Lat0_I * cDegToRad
251.     endif
252. 
253.     Br_II=Br0_II
254. 
255.     ! The CR longitude of Left edge (Longitdue Shift)
256.     ! and the Carrington Rotation of the Central Meridian
257.     ! is read.
258.     LongCR = LongShift
259.     CarRot = MagnetogramTimeCR
260. 
261.   end subroutine read_modified_magnetogram
262.   !============================================================================
263. 
264.   subroutine init_potential_field
265. 
266.     use ModConst, ONLY: cTwoPi
267.     use ModReadMagnetogram, ONLY: UseCosTheta, nThetaAll, nPhiAll
268. 
269.     integer :: iR, iTheta, iPhi, nTotalProc
270.     integer :: i, j, k
271.     integer :: iError, iColor=0
272. 
273.     real:: dR, dLogR, dTheta, dPhi, dZ, z
274.     real:: Err, ErrNew
275. 
276.     !--------------------------------------------------------------------------
277. 
278.     ! decompose the total number of processors to
279.     ! theta (i) and phi (j) directions
280.     ! 0<ni<100, 0<nj<100, ni*nj<=1000, ni*nj<=nproc
281.     if (nProcTheta*nProcPhi == 0) then
282.        nTotalProc = min(nProc,1000)
283.        Err = real(nPhiAll)*real(nThetaAll)*nTotalProc
284.        i = 1
285.        do while (i<=floor(sqrt(real(nTotalProc))))
286.           j = nTotalProc/i
287.           if (j > 99) then
288.              i = i+1
289.              CYCLE
290.           endif
291.           do k = 0, 1
292.              ErrNew = (ceiling(nPhiAll/real(i))+2.) * &
293.                   (ceiling(nThetaAll/real(j))+2.)*real(nTotalProc)/real(i*j)
294.              if (ErrNew < Err) then
295.                 Err = ErrNew
296.                 nProcPhi = i
297.                 nProcTheta = j
298.              endif
299.              i = i+j
300.              j = i-j
301.              i = i-j
302.           enddo
303.           i = i+1
304.        enddo
305.        if (nProcPhi == 0 .and. iProc == 0) then
306.           ! Supposedly we shouldn't reach here
307.           write(*,*)
308.           write(*,'(A,I0,A)') &
309.                'Failed to find proper layout for ',nTotalProc,' processors.'
310.           write(*,*)
311.           nProcPhi = 1
312.           nProcTheta = 1
313.        endif
314.        if (iProc == 0) then
315.           write(*,*)
316.           write(*,'(A,2I4,I6)') 'New nProcTheta, nProcPhi, nProc=', &
317.                nProcTheta, nProcPhi, nProcTheta*nProcPhi
318.           write(*,*)
319.        endif
320.     endif
321. 
322.     nTotalProc = nProcTheta*nProcPhi
323.     if (iProc >= nTotalProc) then
324.        IsProcIdle = .true.
325.        iColor = 1
326.     endif
327.     if (nProc > nTotalProc) then
328.        if (iProc == 0) then
329.           write(*,*)
330.           write(*,'(A,I6,A)') 'WARNING: ',nProc-nTotalProc, &
331.                ' processor(s) are idle.'
332.           write(*,*)
333.        endif
334.        call MPI_Comm_split(iCommWorld,iColor,iProc,iComm,iError)
335.     endif
336.     if (IsProcIdle) RETURN
337. 
338.     ! The processor coordinate
339.     iProcTheta = iProc/nProcPhi
340.     iProcPhi   = iProc - iProcTheta*nProcPhi
341. 
342.     ! Calculate the nTheta, nPhi. To distribute as even as possible,
343.     ! there will be two different nTheta and nPhi.
344.     nThetaLgr  = ceiling(real(nThetaAll)/nProcTheta)
345.     nThetaSml  = floor(  real(nThetaAll)/nProcTheta)
346.     nPhiLgr    = ceiling(real(nPhiAll)/nProcPhi)
347.     nPhiSml    = floor(  real(nPhiAll)/nProcPhi)
348. 
349.     ! Calculate the number of processors which has large/small
350.     ! local number of Theta/Phi.
351.     nProcThetaLgr = mod(nThetaAll, nProcTheta)
352.     nProcThetaSml = nProcTheta - nProcThetaLgr
353.     nProcPhiLgr = mod(nPhiAll, nProcPhi)
354.     nProcPhiSml = nProcPhi - nProcPhiLgr
355. 
356.     ! Test if the partitioning works
357.     if (iProc == 0) then
358.        write(*,*) 'nThetaLgr = ',nThetaLgr, 'nThetaSml = ', nThetaSml
359.        write(*,*) 'nPhiLgr   = ', nPhiLgr,  'nPhiSml   = ', nPhiSml
360.        write(*,*) 'Partitioning in nThetaAll gives: ', &
```

</details>


---

<sub>⏱️ 1m 42s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "subroutine\\s+read_magnetogram_param|case\\(\"#HARMONICSFILE\"|#HARMONICSGRID|NameHarmonicsFile|DoReadHarmonics|read_harmonics_file",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90",
  "output_mode": "content",
  "-n": true,
  "head_limit": 200
}
```

</details>

<details>
<summary>29 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:42:  logical:: DoReadHarmonics = .false., DoReadHarmonicsNew = .false.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:45:  character(len=100):: NameHarmonicsFile = '???', NameHarmonicsFileNew = '???'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:128:    if(iTableB0 < 0 .and. .not.DoReadHarmonics) RETURN
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:135:    if(DoReadHarmonics)then
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:137:       call read_harmonics_file(NameHarmonicsFile, CarringtonRot, LonShift)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:138:       DoReadHarmonics = .false.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:141:       ! Initialize lookup table based on #HARMONICSGRID parameters
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:153:            StringDescription = 'Created from '//trim(NameHarmonicsFile) )
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:209:               StringHeaderIn  = 'Created from '//trim(NameHarmonicsFile), &
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:264:    if(DoReadHarmonicsNew)then
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:266:       call read_harmonics_file(NameHarmonicsFileNew, &
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:268:       DoReadHarmonicsNew = .false.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:283:            StringDescription = 'Created from '//trim(NameHarmonicsFileNew))
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:324:               StringHeaderIn  = 'Created from '//trim(NameHarmonicsFileNew), &
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:347:               trim(NameHarmonicsFileNew))
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:501:  subroutine read_magnetogram_param(NameCommand)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:515:    case("#HARMONICSGRID")
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:529:    case("#HARMONICSFILE")
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:530:       DoReadHarmonics = .true.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:531:       call read_var('NameHarmonicsFile', NameHarmonicsFile)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:534:       DoReadHarmonicsNew = .true.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:535:       call read_var('NameHarmonicsFileNew', NameHarmonicsFileNew)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:538:       call read_var('UseMagnetogram', DoReadHarmonics)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:539:       if(DoReadHarmonics)then
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:543:          call read_var('NameMagnetogramFile', NameHarmonicsFile)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:550:  end subroutine read_magnetogram_param
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:553:  subroutine read_harmonics_file(NameFile, Carrington, dLon)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:569:    character(len=*), parameter:: NameSub = 'read_harmonics_file'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:612:  end subroutine read_harmonics_file
```

</details>


---

<sub>⏱️ 1m 42s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90 (lines 260-520)

<details>
<summary>261 lines</summary>

```
260.     if(nParam > 3) CarringtonRot = nint(Param_I(4)) + CRFraction
261.     !
262.     ! Second lookup table for a different time for temporal interpolation
263.     !
264.     if(DoReadHarmonicsNew)then
265.        ! Read harmonics coefficients and Carrington rotation info
266.        call read_harmonics_file(NameHarmonicsFileNew, &
267.             CarringtonRotNew, LonShift)
268.        DoReadHarmonicsNew = .false.
269.        nCR        = int(CarringtonRotNew)
270.        CRFraction = CarringtonRotNew  - nCR
271.        ! Set up lookup table
272.        call init_lookup_table( &
273.             NameTable   = 'B0New',                         &
274.             NameCommand = 'save',                          &
275.             NameVar     = NameVar,                         &
276.             NameFile    = 'harmonics_new_bxyz.out',        &
277.             TypeFile    = 'real4',                         &
278.             nIndex_I    = [nR+1, nLon+1, nLat+1],          &
279.             IndexMin_I  = [rMagnetogram,     0.0, -90.0],  &
280.             IndexMax_I  = [rSourceSurface, 360.0,  90.0],  &
281.             Param_I = [rMagnetogram, rSourceSurface, LonShift, real(nCR)], &
282.             Time=CRFraction,                               &
283.             StringDescription = 'Created from '//trim(NameHarmonicsFileNew))
284. 
285.        iTableB0New = i_lookup_table('B0New')
286. 
287.        ! Make second lookup table using the just read harmonics coefficients
288.        call make_lookup_table_3d(iTableB0New, calc_b0_table, iComm)
289. 
290.        call deallocate_harmonics_arrays
291.        if(iProc==0) then
292.           TablePtr => Table_I(iTableB0New)
293.           allocate(Magnetogram_VII(3,nLon,nLat+1))
294. 
295.           ! Take the radial slice at the photospheric level,
296.           ! omit the strip at the longitude of 360 degrees:
297.           Magnetogram_VII = TablePtr%Value4_VC(:,1,1:nLon,:,1,1)
298.           dLon = TablePtr%DIndex_I(2)
299.           dLat = TablePtr%DIndex_I(3)
300.           do iLat  = 1, nLat + 1
301.              Lat = -90 + dLat*(iLat - 1)
302.              do iLon = 1, nLon
303.                 Lon = dLon*(iLon - 1)
304.                 ! Convert to Br, BLon, BLat components
305.                 XyzRLonLat_DD = &
306.                      rot_xyz_rlonlat(cDegToRad*Lon, cDegToRad*Lat)
307.                 Magnetogram_VII(1:3,iLon,iLat) =            &
308.                      matmul(Magnetogram_VII(1:3,iLon,iLat), XyzRLonLat_DD)
309.              end do
310.           end do
311.           ! Remesh from latitudinal nodes to pixels:
312.           Magnetogram_VII(:,:,1:nLat) = 0.5*(             &
313.                Magnetogram_VII(:,:,1:nLat) + Magnetogram_VII(:,:,2:nLat+1))
314.           call save_plot_file(NameFile = 'new_field_2d.out',  &
315.                nDimIn  = 2,                       &
316.                TimeIn = CRFraction,               &
317.                ParamIn_I= [real(int(LonShift)), real(nCR)], &
318.                VarIn_VII= Magnetogram_VII(:,1:nLon,1:nLat), &
319.                TypeFileIn    = 'ascii',           &
320.                CoordMinIn_D  = [0.0 + LonShift - int(LonShift),&
321.                -90.0 + 90.0/nLat],&
322.                CoordMaxIn_D  = [360.0 - 360.0/nLon + LonShift - int(LonShift),&
323.                90.0 - 90.0/nLat ],&
324.                StringHeaderIn  = 'Created from '//trim(NameHarmonicsFileNew), &
325.                NameUnitsIn  = ' [deg] [deg] [Gs] [Gs] [Gs] [deg] []', &
326.                NameVarIn = 'Longitude Latitude Br BLon BLat Long0 CRNumber')
327.           deallocate(Magnetogram_VII)
328.           nullify(TablePtr)
329.        end if
330.     end if
331. 
332.     if(iTableB0New > 0)then
333.        ! Get Carrington rotation (time) for new magnetogram
334.        call get_lookup_table(iTableB0New, nParam=nParam, Param_I=Param_I,&
335.             Time=CRFraction)
336.        ! Rotation matrix for longitude shift if needed
337.        if(nParam > 2) then
338.           dLonB0New = (Param_I(3) - dLongitudeHgrDeg)*cDegToRad
339.           RotB0New_DD = rot_matrix_z(dLonB0New)
340.        end if
341. 
342.        if(nParam > 3)then
343.           ! Get Carrington rotation time of magnetogram
344.           CarringtonRotNew = nint(Param_I(4)) + CRFraction
345.        else
346.           call CON_stop(NameSub//': missing Carrington rotation info in '// &
347.                trim(NameHarmonicsFileNew))
348.        end if
349.     end if
350. 
351.     !$acc update device(iTableB0, iTableB0New, iTableB0local)
352.     !$acc update device(rMinB0local, rMaxB0local)
353.     !$acc update device(LonMinB0local, LonMaxB0local)
354.     !$acc update device(LatMinB0local, LatMaxB0local)
355.     !$acc update device(CarringtonRot, CarringtonRotNew)
356.     !$acc update device(rMinB0, rMaxB0, LonMinB0, dLonB0)
357.     !$acc update device(RotB0_DD, dLonB0New, RotB0New_DD)
358.     
359.   end subroutine init_magnetogram_lookup_table
360.   !============================================================================
361.   subroutine calc_b0_table(iTable, r, Lon, Lat, b_D)
362. 
363.     ! Calculate B0 at the location
364. 
365.     integer, intent(in):: iTable
366.     real, intent(in)   :: r, Lon, Lat
367.     real, intent(out)  :: b_D(:)
368. 
369.     real:: Theta, Phi, Bsph_D(3)
370.     ! Rotation matrix to convert Br, BTheta, BPhi to  Bx, By, Bz.
371.     real :: XyzSph_DD(3,3)
372.     character(len=*), parameter:: NameSub = 'calc_b0_table'
373.     !--------------------------------------------------------------------------
374.     Phi   = cDegToRad*Lon
375.     Theta = cDegToRad*(90 - Lat)
376. 
377.     call get_harmonics_field(r, Theta, Phi, Bsph_D)
378. 
379.     ! Convert to Cartesian components
380.     XyzSph_DD = rot_xyz_sph(Theta, Phi)
381. 
382.     b_D = matmul(XyzSph_DD, Bsph_D)
383. 
384.   end subroutine calc_b0_table
385.   !============================================================================
386.   subroutine get_magnetogram_field31(x, y, z, B0_D, Carrington)
387.     !$acc routine seq
388. 
389.     real, intent(in) ::  x, y, z
390.     real, intent(out):: B0_D(3)
391.     real, intent(in), optional :: Carrington
392. 
393.     !--------------------------------------------------------------------------
394.     call  get_magnetogram_field11([x, y, z], B0_D, Carrington)
395. 
396.   end subroutine get_magnetogram_field31
397.   !============================================================================
398.   subroutine get_magnetogram_field11(Xyz_D, B0_D, Carrington)
399.     !$acc routine seq
400.     
401.     ! Return B0_D [Tesla] field at position Xyz_D [Rs]
402.     ! Interpolat to time Carrington if present and iTableB0New is defined
403. 
404.     real, intent(in) :: Xyz_D(3)
405.     real, intent(out):: B0_D(3)
406.     real, intent(in), optional :: Carrington
407. 
408.     real:: rLonLat_D(3), r, B0New_D(3)
409. 
410.     ! Converting to rlonlat (radians)
411.     character(len=*), parameter:: NameSub = 'get_magnetogram_field11'
412.     !--------------------------------------------------------------------------
413.     call xyz_to_rlonlat(Xyz_D, rLonLat_D)
414. 
415.     ! Include the shift in Phi coordinate and make sure that it is
416.     ! in the range provided by the lookup table
417.     if(dLonB0 /= 0.0 .or. LonMinB0 /= 0.0) rLonLat_D(2) = &
418.          modulo(rLonLat_D(2) - dLonB0 - LonMinB0, cTwoPi) + LonMinB0
419. 
420.     ! Lookup table uses degrees
421.     rLonLat_D(2:3) = cRadToDeg*rLonLat_D(2:3)
422. 
423.     ! Extrapolate for r < rMinB0
424.     r = rLonLat_D(1)
425. 
426.     if(iTableB0local > 0 .and. &
427.          rLonLat_D(1) <= rMaxB0local   .and. &  ! rMax
428.          rLonLat_D(2) >= LonMinB0local .and. &  ! LonMin
429.          rLonLat_D(2) <= LonMaxB0local .and. &  ! LonMax
430.          rLonLat_D(3) >= LatMinB0local .and. &  ! LatMin
431.          rLonLat_D(3) <= LatMaxB0local ) then   ! LatMax
432.        call interpolate_lookup_table(iTableB0local, rLonLat_D, B0_D, &
433.             DoExtrapolate=(r<rMinB0local) )
434.     else
435.        call interpolate_lookup_table(iTableB0, rLonLat_D, B0_D, &
436.             DoExtrapolate=(r<rMinB0) )
437.     endif
438.     ! Rotate Bx, By based on shifted coordinates
439.     if(dLonB0 /= 0.0) B0_D = matmul(RotB0_DD, B0_D)
440. 
441.     if(present(Carrington) .and. iTableB0New > 0)then
442. 
443.        if(CarringtonRot < 0.0 .or. CarringtonRotNew < 0.0) &
444.             call CON_stop_simple( &
445.             NameSub//': no Carrington time in at least one magnetogram')
446.        call xyz_to_rlonlat(Xyz_D, rLonLat_D)
447. 
448.        ! Include the shift in Phi coordinate and make sure that it is
449.        ! in the range provided by the lookup table
450.        if(dLonB0New /= 0.0 .or. LonMinB0 /= 0.0) rLonLat_D(2) = &
451.             modulo(rLonLat_D(2) - dLonB0New - LonMinB0, cTwoPi) + LonMinB0
452. 
453.        ! Lookup table uses degrees
454.        rLonLat_D(2:3) = cRadToDeg*rLonLat_D(2:3)
455. 
456.        if(CarringtonRot < CarringtonRotNew)then
457.           ! Check if time has passed the original magnetogram time
458.           if(Carrington > CarringtonRot)then
459.              call interpolate_lookup_table(iTableB0New, rLonLat_D, B0New_D, &
460.                   DoExtrapolate=(r<rMinB0) )
461.              ! Rotate Bx, By based on shifted coordinates
462.              if(dLonB0New /= 0.0) B0New_D = matmul(RotB0New_DD, B0New_D)
463.              if(Carrington > CarringtonRotNew)then
464.                 ! Time is beyond new table time, so take that
465.                 B0_D = B0New_D
466.              else
467.                 ! interpolate in time
468.                 B0_D = ((Carrington       - CarringtonRot)*B0New_D  &
469.                      +  (CarringtonRotNew - Carrington   )*B0_D   ) &
470.                      /  (CarringtonRotNew - CarringtonRot)
471.              end if
472.           end if
473.        else
474.           ! "new" table has earlier time than original table
475.           if(Carrington < CarringtonRot)then
476.              call interpolate_lookup_table(iTableB0New, rLonLat_D, B0New_D, &
477.                   DoExtrapolate=(r<rMinB0) )
478.              ! Rotate Bx, By based on shifted coordinates
479.              if(dLonB0New /= 0.0) B0New_D = matmul(RotB0New_DD, B0New_D)
480.              if(Carrington <= CarringtonRotNew)then
481.                 ! Time is before new table time, so take that
482.                 B0_D = B0New_D
483.              else
484.                 ! interpolate in time
485.                 B0_D = ((CarringtonRot - Carrington      )*B0New_D  &
486.                      +  (Carrington    - CarringtonRotNew)*B0_D   ) &
487.                      /  (CarringtonRot - CarringtonRotNew)
488.              end if
489.           end if
490.        end if
491.     end if
492. 
493.     ! Scale with r^2 for r > rMaxB0
494.     if(r > rMaxB0) B0_D = (rMaxB0/r)**2 * B0_D
495. 
496.     ! Multiply with B0 factor and convert from Gauss to Tesla
497.     B0_D = B0_D*FactorB0*1e-4
498. 
499.   end subroutine get_magnetogram_field11
500.   !============================================================================
501.   subroutine read_magnetogram_param(NameCommand)
502. 
503.     use ModReadParam, ONLY: read_var
504. 
505.     character(len=*), intent(in) :: NameCommand
506. 
507.     real:: Height ! pointless variable
508.     character(len=*), parameter:: NameSub = 'read_magnetogram_param'
509.     !--------------------------------------------------------------------------
510.     select case(NameCommand)
511.     case("#FACTORB0")
512.        call read_var("FactorB0", FactorB0)
513.        !$acc update device(FactorB0)
514. 
515.     case("#HARMONICSGRID")
516.        call read_var('rMagnetogram',   rMagnetogram)
517.        call read_var('rSourceSurface', rSourceSurface)
518.        call read_var('IsLogRadius',    IsLogRadius)
519.        call read_var('MaxOrder',       MaxOrder)
520.        call read_var('nR',             nR)
```

</details>


---

<sub>⏱️ 1m 42s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90 (lines 520-860)

<details>
<summary>341 lines</summary>

```
520.        call read_var('nR',             nR)
521.        call read_var('nLon',           nLon)
522.        call read_var('nLat',           nLat)
523.        if(IsLogRadius)then
524.           NameVar = 'log'//NameVarLinear
525.        else
526.           NameVar = NameVarLinear
527.        end if
528. 
529.     case("#HARMONICSFILE")
530.        DoReadHarmonics = .true.
531.        call read_var('NameHarmonicsFile', NameHarmonicsFile)
532. 
533.     case("#NEWHARMONICSFILE")
534.        DoReadHarmonicsNew = .true.
535.        call read_var('NameHarmonicsFileNew', NameHarmonicsFileNew)
536. 
537.     case("#MAGNETOGRAM") ! Kept For backward compatibility only
538.        call read_var('UseMagnetogram', DoReadHarmonics)
539.        if(DoReadHarmonics)then
540.           call read_var('rMagnetogram',        rMagnetogram)
541.           call read_var('rSourceSurface',      rSourceSurface)
542.           call read_var('HeightInnerBc',       Height)
543.           call read_var('NameMagnetogramFile', NameHarmonicsFile)
544.        end if
545. 
546.     case default
547.        call CON_stop(NameSub//' invalid NameCommand='//NameCommand)
548.     end select
549. 
550.   end subroutine read_magnetogram_param
551.   !============================================================================
552. 
553.   subroutine read_harmonics_file(NameFile, Carrington, dLon)
554. 
555.     use ModPlotFile, ONLY: read_plot_file
556. 
557.     character(len=*), intent(in) :: NameFile
558.     real,             intent(out):: Carrington ! Carrington rotation from file
559.     real,             intent(out):: dLon       ! longitude offset from file
560. 
561.     ! read properly formatted harmonics coefficient file
562. 
563.     integer:: nHarmonic ! number of harmonics = (nOrder+1)*(nOrder+2)/2
564.     integer:: nParam, nOrderIn, i, n, m
565. 
566.     real:: Param_I(3), Coef, Coef1, CRFraction
567.     real, allocatable:: Var_VI(:,:), Coord_DII(:,:,:)
568. 
569.     character(len=*), parameter:: NameSub = 'read_harmonics_file'
570.     !--------------------------------------------------------------------------
571. 
572.     call read_plot_file(NameFile, TimeOut = CRFraction, &
573.          nParamOut=nParam, ParamOut_I=Param_I, n1Out=nHarmonic)
574. 
575.     if(nParam < 3) call CON_stop(NameSub// &
576.          ': not enough parameters in '//trim(NameFile))
577. 
578.     nOrderIn   = nint(Param_I(1))
579.     nOrder     = min(MaxOrder, nOrderIn)
580.     Carrington = Param_I(2) + CRFraction
581.     dLon       = Param_I(3)
582. 
583.     if(nHarmonic /= (nOrderIn+1)*(nOrderIn+2)/2) call CON_stop(NameSub// &
584.          ': inconsistent n and nOrder in '//trim(NameFile))
585. 
586.     call allocate_harmonics_arrays
587. 
588.     allocate(Var_VI(2,nHarmonic), Coord_DII(2,nHarmonic,1))
589.     call read_plot_file(NameFile, VarOut_VI=Var_VI, CoordOut_DII=Coord_DII)
590. 
591.     do i = 1, nHarmonic
592.        n = nint(Coord_DII(1,i,1))
593.        if (n > nOrder) EXIT  ! the harmonics are listed in increasing order
594.        m = nint(Coord_DII(2,i,1))
595.        g_II(n,m) = Var_VI(1,i)
596.        h_II(n,m) = Var_VI(2,i)
597.     end do
598. 
599.     deallocate(Var_VI, Coord_DII)
600. 
601.     ! Normalize coefficients
602.     Coef = rSourceSurface
603.     do n = 0, nOrder
604.        Coef  = Coef/rSourceSurface**2
605.        Coef1 = 1.0/(n+1 + n*Coef)
606.        g_II(n,0:n) = g_II(n,0:n)*Coef1
607.        h_II(n,0:n) = h_II(n,0:n)*Coef1
608.     enddo
609.     ! Leave out monopole (n=m=0) term::
610.     g_II(0,0) = 0.0
611. 
612.   end subroutine read_harmonics_file
613.   !============================================================================
614. 
615.   subroutine allocate_harmonics_arrays
616. 
617.     ! Calculate square roots and their ratios used in the spherical harmonics
618.     ! functions up to order nOrder for speeding up the calculations
619. 
620.     integer:: m, MaxInt
621.     !--------------------------------------------------------------------------
622.     if(allocated(g_II)) RETURN
623. 
624.     ! Spherical harmonics coefficients
625.     allocate(g_II(0:nOrder,0:nOrder), h_II(0:nOrder,0:nOrder))
626.     g_II = 0.0; h_II = 0.0
627. 
628.     ! radial functions
629.     allocate(rRsPower_I(-1:nOrder+2), &
630.          RmRsPower_I(0:nOrder+2), RmRPower_I(0:nOrder+2))
631. 
632.     ! Legendre polynomlials
633.     allocate(p_II(0:nOrder,0:nOrder), Dp_II(0:nOrder,0:nOrder))
634. 
635.     ! Azimuthal functions
636.     allocate(SinPhi_I(0:nOrder), CosPhi_I(0:nOrder))
637. 
638.     MaxInt = max(nOrder**2, 5*nOrder, 10)
639.     allocate(Sqrt_I(MaxInt), SqrtRatio_I(nOrder+1))
640. 
641.     do m = 1, MaxInt
642.        Sqrt_I(m) = sqrt(real(m))
643.     end do
644. 
645.     ! Calculate the ratio sqrt(2m!)/(2^m*m!) recursively
646.     SqrtRatio_I(1) = 1.0
647.     do m = 1, nOrder
648.        SqrtRatio_I(m+1) = SqrtRatio_I(m)*Sqrt_I(2*m-1)/Sqrt_I(2*m)
649.     enddo
650. 
651.   end subroutine allocate_harmonics_arrays
652.   !============================================================================
653.   subroutine deallocate_harmonics_arrays
654.     !--------------------------------------------------------------------------
655.     if(.not.allocated(g_II)) RETURN
656. 
657.     deallocate(g_II, h_II, Sqrt_I, SqrtRatio_I, &
658.          rRsPower_I, RmRsPower_I, RmRPower_I, &
659.          SinPhi_I, CosPhi_I, p_II, Dp_II)
660. 
661.   end subroutine deallocate_harmonics_arrays
662.   !============================================================================
663.   subroutine get_harmonics_field(r, Theta, Phi, Bsph_D)
664. 
665.     ! Calculate the harmonics based potential field Bsph_D at r, Theta, Phi
666. 
667.     real, intent(in):: r, Theta, Phi ! r in Rs, Theta and Phi in radians
668.     real, intent(out):: Bsph_D(3)    ! Bsph_D with r, Theta, Phi components
669. 
670.     integer:: n, m
671.     real:: CosTheta, SinTheta
672. 
673.     ! The spherical components of the magnetic field
674.     real:: Br, Btheta, Bphi
675. 
676.     real:: Coef1, Coef2, Coef3, Coef4
677.     !--------------------------------------------------------------------------
678. 
679.     ! Calculate the radial part of spherical functions
680.     call calc_radial_functions(r)
681. 
682.     ! Calculate the set of Legendre polynoms for given Theta
683.     CosTheta = cos(Theta)
684.     SinTheta = max(sin(Theta), 1E-10)
685.     call calc_legendre_polynomial(SinTheta, CosTheta)
686. 
687.     ! Calculate azimuthal functions for given Phi
688.     call calc_azimuthal_functions(Phi)
689. 
690.     ! Initialize the components
691.     Br = 0.0; Btheta = 0.0; Bphi = 0.0
692. 
693.     ! Calculate B from spherical harmonics
694.     do m = 0, nOrder; do n = m, nOrder
695. 
696.        Coef1 = (n+1)*RmRPower_I(n+2) + RmRsPower_I(n+2)*n*rRsPower_I(n-1)
697.        Coef3 =       RmRPower_I(n+2) - RmRsPower_I(n+2)*rRsPower_I(n-1)
698.        Coef2 = g_II(n,m)*CosPhi_I(m) + h_II(n,m)*SinPhi_I(m)
699.        Coef4 = g_II(n,m)*SinPhi_I(m) - h_II(n,m)*CosPhi_I(m)
700. 
701.        ! Br = -d(Psi)/dR
702.        Br  = Br + p_II(n,m)*Coef1*Coef2
703. 
704.        ! Bt = -(1/r)*d(Psi)/dTheta
705.        Btheta  = Btheta - Dp_II(n,m)*Coef2*Coef3
706. 
707.        ! Bp = -(1/r)*d(Psi)/dPhi
708.        Bphi  = Bphi + p_II(n,m)*m/SinTheta*Coef3*Coef4
709. 
710.        ! Potential could be calculated if it was needed:
711.        ! Potential = Potential + r*p_II(n,m)*Coef2*Coef3
712. 
713.     enddo; enddo
714. 
715.     Bsph_D = [Br, Btheta, Bphi]
716. 
717.   contains
718.     !==========================================================================
719. 
720.     subroutine calc_legendre_polynomial(SinTheta, CosTheta)
721. 
722.       ! Calculate Legendre polynomials p_II and its derivative Dp_II
723.       ! with appropriate normalization for Theta
724.       ! Equation numbers refer to Altschuler et al. 1976
725. 
726.       real, intent(in):: SinTheta, CosTheta
727. 
728.       real:: SinThetaM, SinThetaM1  ! sin(Theta)^m, sin(Theta)^(m-1)
729.       integer:: m
730. 
731.       ! Cache previous values
732.       real:: SinThetaOld = -10.0, CosThetaOld = -10.0
733.       !------------------------------------------------------------------------
734.       if(SinTheta == SinThetaOld .and. CosTheta == CosThetaOld) RETURN
735. 
736.       SinThetaOld = SinTheta; CosThetaOld = CosTheta
737. 
738.       SinThetaM  = 1.0
739.       SinThetaM1 = 1.0
740.       p_II  = 0.0
741.       Dp_II = 0.0
742. 
743.       do m = 0, nOrder
744.          if (m == 0) then
745.             Coef1 = Sqrt_I(2*m+1)
746.          else
747.             Coef1 = Sqrt_I(2*(2*m+1))
748.          endif
749.          ! Eq.(27)
750.          p_II(m,m) = SqrtRatio_I(m+1)*Coef1* SinThetaM
751.          ! Eq.(28)
752.          if (m < nOrder) p_II(m+1,m) = p_II(m,m)*Sqrt_I(2*m+3)*CosTheta
753.          ! Eq.(30)
754.          Dp_II(m,m) = SqrtRatio_I(m+1)*Coef1*m*CosTheta*SinThetaM1
755.          ! Eq.(31)
756.          if (m < nOrder) &
757.               Dp_II(m+1,m) = Sqrt_I(2*m+3)* &
758.               (CosTheta*Dp_II(m,m) - SinTheta*p_II(m,m))
759. 
760.          ! Increase the powers
761.          SinThetaM1 = SinThetaM
762.          SinThetaM  = SinThetaM*SinTheta
763. 
764.       enddo
765. 
766.       ! Recursive rules
767.       do m = 0, nOrder-2; do n = m+2, nOrder
768.          ! Eq.(29)
769.          Coef1 = Sqrt_I(2*n+1)/Sqrt_I(n**2-m**2)
770.          Coef2 = Sqrt_I(2*n-1)
771.          Coef3 = Sqrt_I((n-1)**2-m**2)/Sqrt_I(2*n-3)
772. 
773.          p_II(n,m) = Coef1*(Coef2*CosTheta*p_II(n-1,m) - Coef3*p_II(n-2,m))
774. 
775.          ! Eq.(32)
776.          Dp_II(n,m) = Coef1*(Coef2*(CosTheta*Dp_II(n-1,m) &
777.               - SinTheta*p_II(n-1,m)) - Coef3*Dp_II(n-2,m))
778.       enddo; enddo
779. 
780.       ! Apply Schmidt normalization
781.       do m = 0, nOrder; do n = m, nOrder
782.          ! Eq.(33)
783.          Coef1 = 1.0/Sqrt_I(2*n+1)
784.          ! Eq.(34)
785.          p_II(n,m)  = p_II(n,m)*Coef1
786.          Dp_II(n,m) = Dp_II(n,m)*Coef1
787.       enddo; enddo
788. 
789.     end subroutine calc_legendre_polynomial
790.     !==========================================================================
791. 
792.     subroutine calc_radial_functions(r)
793. 
794.       real, intent(in):: r
795. 
796.       ! Calculate powers of the ratios of radii up to nOrder
797. 
798.       integer:: m
799.       real:: RmRs, RmR, rRs
800. 
801.       real:: rOld = -10.0
802.       !------------------------------------------------------------------------
803.       if(rOld == r) RETURN
804.       rOld = r
805. 
806.       RmRs = rMagnetogram/rSourceSurface
807.       RmR  = rMagnetogram/r
808.       rRs  = r/rSourceSurface
809. 
810.       ! Zero and -1 powers
811.       rRsPower_I(-1) = 1.0/rRs
812.       rRsPower_I(0)  = 1.0
813.       RmRsPower_I(0) = 1.0
814.       RmRPower_I(0)  = 1.0
815. 
816.       ! Recursive: x^m = x^m-1 * x
817.       do m = 1, nOrder+2
818.          RmRsPower_I(m) = RmRsPower_I(m-1) * RmRs
819.          RmRPower_I(m)  = RmRPower_I(m-1)  * RmR
820.          rRsPower_I(m)  = rRsPower_I(m-1)  * rRs
821.       end do
822. 
823.     end subroutine calc_radial_functions
824.     !==========================================================================
825.     subroutine calc_azimuthal_functions(Phi)
826. 
827.       ! Calculate azimuthal harmonics for given Phi
828. 
829.       real,    intent(in):: Phi
830. 
831.       integer:: m
832.       complex:: z, zM ! Powers of cos(Phi)+i*sin(Phi)
833. 
834.       real   :: PhiOld = -10.0
835.       !------------------------------------------------------------------------
836.       if(Phiold == Phi) RETURN
837.       PhiOld = Phi
838. 
839.       z  = exp( cmplx(0.0, Phi) )
840.       zM = z
841. 
842.       CosPhi_I(0) = 1.0
843.       SinPhi_I(0) = 0.0
844.       CosPhi_I(1) = real(zM)
845.       SinPhi_I(1) = aimag(zM)
846. 
847.       do m = 2, nOrder
848.          zM = zM*z
849.          CosPhi_I(m) = real(zM)
850.          SinPhi_I(m) = aimag(zM)
851.       end do
852. 
853.     end subroutine calc_azimuthal_functions
854.     !==========================================================================
855.   end subroutine get_harmonics_field
856.   !============================================================================
857. 
858. end module ModMagnetogram
859. !==============================================================================
860.
```

</details>


---

<sub>⏱️ 1m 42s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/potential_field.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/potential_field.f90 (lines 1-260)

<details>
<summary>260 lines</summary>

```
1. !  Copyright (C) 2002 Regents of the University of Michigan,
2. !  portions used with permission
3. !  For more information, see http://csem.engin.umich.edu/tools/swmf
4. module ModPotentialFieldSimple
5. 
6.   use ModUtilities, ONLY: CON_stop
7.   use ModNumConst, ONLY: cDegToRad
8. 
9.   implicit none
10. 
11.   ! input parameter
12.   logical:: DoReadMagnetogram = .true.
13. 
14.   ! grid and domain parameters
15.   integer:: nR = 150, nTheta = 180, nPhi = 360
16.   real   :: rMin = 1.0, rMax = 2.5
17. 
18.   ! solver parameters
19.   logical:: UsePreconditioner = .true.
20.   real   :: Tolerance         = 1e-10
21. 
22.   ! magnetogram parameters
23.   character(len=100):: NameFileIn = 'fitsfile.dat'  ! filename
24.   logical           :: UseCosTheta = .true.
25.   real              :: BrMax = 3500.0               ! Saturation level of MDI
26. 
27.   ! output paramters
28.   logical           :: DoSaveField   = .true.
29.   character(len=100):: NameFileField = 'potentialfield.out'
30.   character(len=5)  :: TypeFileField = 'real8'
31. 
32.   logical           :: DoSavePotential   = .true.
33.   character(len=100):: NameFilePotential = 'potentialtest.out'
34.   character(len=5)  :: TypeFilePotential = 'real8'
35. 
36.   logical           :: DoSaveTecplot   = .false.
37.   character(len=100):: NameFileTecplot = 'potentialfield.dat'
38. 
39.   integer:: iRTest = 1, iPhiTest = 1, iThetaTest = 2
40. 
41.   ! local variables
42.   logical :: UseBr = .true.
43. 
44.   real, dimension(:), allocatable :: &
45.        Radius_I, Theta_I, Phi_I, SinTheta_I, &
46.        dRadius_I, dPhi_I, dCosTheta_I, &
47.        RadiusNode_I, ThetaNode_I, PhiNode_I, SinThetaNode_I, &
48.        dRadiusNode_I, dTheta_I, dThetaNode_I, dPhiNode_I, dCosThetaNode_I
49. 
50.   real, allocatable:: Br_II(:,:), Potential_C(:,:,:), Rhs_C(:,:,:), &
51.        B0_DF(:,:,:,:), DivB_C(:,:,:), PlotVar_VC(:,:,:,:)
52. 
53.   ! Variables for hepta preconditioner
54.   real, parameter:: PrecondParam = 1.0 ! see ModLinearSolver
55. 
56.   ! Seven diagonals for the preconditioner
57.   real, dimension(:), allocatable :: &
58.        d_I, e_I, e1_I, e2_I, f_I, f1_I, f2_I
59. 
60. contains
61.   !============================================================================
62. 
63.   subroutine read_fdips_param
64. 
65.     use ModReadParam
66.     use ModMPI, ONLY: MPI_COMM_SELF
67. 
68.     character(len=lStringLine) :: NameCommand
69.     character(len=10):: TypeOutput
70.     character(len=*), parameter:: NameSub = 'read_fdips_param'
71.     !--------------------------------------------------------------------------
72.     call read_file('POTENTIAL.in', iCommIn = MPI_COMM_SELF)
73.     call read_init
74.     do
75.        if(.not.read_line() ) EXIT
76.        if(.not.read_command(NameCommand)) CYCLE
77.        select case(NameCommand)
78.        case("#DOMAIN")
79.           call read_var('rMin', rMin)
80.           call read_var('rMax', rMax)
81.        case("#GRID")
82.           call read_var('nR    ', nR)
83.           call read_var('nTheta', nTheta)
84.           call read_var('nPhi  ', nPhi)
85.        case("#MAGNETOGRAM")
86.           call read_var('NameFileIn' ,  NameFileIn)
87.           call read_var('UseCosTheta', UseCosTheta)
88.           call read_var('BrMax'      ,  BrMax)
89.        case("#TEST")
90.           call read_var('iRTest'    , iRTest)
91.           call read_var('iPhiTest'  , iPhiTest)
92.           call read_var('iThetaTest', iThetaTest)
93.        case("#SOLVER")
94.           call read_var('UsePreconditioner', UsePreconditioner)
95.           call read_var('Tolerance',         Tolerance)
96.        case("#OUTPUT")
97.           call read_var('TypeOutput', TypeOutput, IsLowerCase=.true.)
98.           select case(TypeOutput)
99.           case('field')
100.              DoSaveField = .true.
101.              call read_var('NameFileField', NameFileField)
102.              call read_var('TypeFileField', TypeFileField)
103.           case('potential')
104.              DoSavePotential = .true.
105.              call read_var('NameFilePotential', NameFilePotential)
106.              call read_var('TypeFilePotential', TypeFilePotential)
107.           case('tecplot')
108.              DoSaveTecplot = .true.
109.              call read_var('NameFileTecplot', NameFileTecplot)
110.           case default
111.              call CON_stop(NameSub//': unknown TypeOutput='//trim(TypeOutput))
112.           end select
113.        case default
114.           call CON_stop(NameSub//': unknown command='//trim(NameCommand))
115.        end select
116.     end do
117. 
118.   end subroutine read_fdips_param
119.   !============================================================================
120.   subroutine read_magnetogram
121. 
122.     use ModIoUnit, ONLY: UnitTmp_
123. 
124.     ! Read the raw magnetogram file into a 2d array
125. 
126.     integer:: iError
127.     integer:: nCarringtonRotation
128.     integer:: nTheta0, nPhi0, nThetaRatio, nPhiRatio
129.     integer:: iTheta, iPhi, iTheta0, iTheta1, jPhi0, jPhi1, jPhi, kPhi
130.     real :: BrAverage, Weight
131.     character (len=100) :: String
132. 
133.     real, allocatable:: Br0_II(:,:)
134. 
135.     character(len=*), parameter:: NameSub = 'read_magnetogram'
136.     !--------------------------------------------------------------------------
137.     open(UnitTmp_, file=NameFileIn, status='old', iostat=iError)
138.     if(iError /= 0)then
139.        write(*,*) 'Error in ',NameSub,': could not open input file ',NameFileIn
140.        stop
141.     end if
142.     do
143.        read(UnitTmp_,'(a)', iostat = iError ) String
144.        if(index(String,'#CR')>0)then
145.           read(UnitTmp_,*) nCarringtonRotation
146.        endif
147.        if(index(String,'#ARRAYSIZE')>0)then
148.           read(UnitTmp_,*) nPhi0
149.           read(UnitTmp_,*) nTheta0
150.        endif
151.        if(index(String,'#START')>0) EXIT
152.     end do
153. 
154.     write(*,*)'nCarringtonRotation, nTheta0, nPhi0: ',&
155.          nCarringtonRotation, nTheta0, nPhi0
156. 
157.     allocate(Br0_II(nTheta0,nPhi0))
158. 
159.     ! input file is in longitude, latitude
160.     do iTheta = nTheta0, 1, -1
161.        do iPhi = 1, nPhi0
162.           read(UnitTmp_,*) Br0_II(iTheta,iPhi)
163.           if (abs(Br0_II(iTheta,iPhi)) > BrMax) &
164.                Br0_II(iTheta,iPhi) = sign(BrMax, Br0_II(iTheta,iPhi))
165.        end do
166.     end do
167. 
168.     if(nTheta0 > nTheta)then
169.        ! Set integer coarsening ratio
170.        nThetaRatio = nTheta0 / nTheta
171.        nTheta      = nTheta0 / nThetaRatio
172.     else
173.        nThetaRatio = 1
174.        nTheta      = nTheta0
175.     end if
176. 
177.     if(nPhi0 > nPhi)then
178.        nPhiRatio = nPhi0 / nPhi
179.        nPhi      = nPhi0 / nPhiRatio
180.     else
181.        nPhiRatio = 1
182.        nPhi      = nPhi0
183.     end if
184. 
185.     allocate(Br_II(nTheta,nPhi))
186.     Br_II = 0.0
187. 
188.     do iPhi = 1, nPhi
189.        jPhi0 = nPhiRatio*(iPhi-1) + 1
190.        jPhi1 = jPhi0 + nPhiRatio - 1
191. 
192.        do jPhi = jPhi0, jPhi1
193. 
194.           do iTheta = 1, nTheta
195.              iTheta0 = nThetaRatio*(iTheta-1) + 1
196.              iTheta1 = iTheta0 + nThetaRatio - 1
197. 
198.              Br_II(iTheta,iPhi) = Br_II(iTheta,iPhi) &
199.                   + sum( Br0_II(iTheta0:iTheta1, jPhi))
200.           end do
201.        end do
202.     end do
203. 
204.     Br_II = Br_II / (nThetaRatio*nPhiRatio)
205. 
206.     ! remove monopole
207.     BrAverage = sum(Br_II)/(nTheta*nPhi)
208.     Br_II = Br_II - BrAverage
209. 
210.     deallocate(Br0_II)
211. 
212.     close(UnitTmp_)
213. 
214.   end subroutine read_magnetogram
215.   !============================================================================
216. 
217.   subroutine init_potential_field
218. 
219.     use ModConst, ONLY: cPi, cTwoPi
220. 
221.     integer :: iR, iTheta, iPhi
222.     real:: dR, dTheta, dPhi, dZ, z
223.     !--------------------------------------------------------------------------
224. 
225.     allocate( &
226.          Radius_I(0:nR+1), Theta_I(0:nTheta+1), Phi_I(0:nPhi+1), &
227.          dRadius_I(nR), dPhi_I(nPhi), &
228.          SinTheta_I(0:nTheta+1), dTheta_I(nTheta), dCosTheta_I(nTheta), &
229.          SinThetaNode_I(nTheta+1), dCosThetaNode_I(nTheta+1), &
230.          RadiusNode_I(nR+1), ThetaNode_I(nTheta+1), PhiNode_I(nPhi+1), &
231.          dRadiusNode_I(nR+1), dThetaNode_I(nTheta+1), dPhiNode_I(nPhi+1))
232. 
233.     ! nR is the number of mesh cells in radial direction
234.     ! cell centered radial coordinate
235.     dR = (rMax - rMin)/nR
236.     do iR = 0, nR+1
237.        Radius_I(iR) = rMin + (iR - 0.5)*dR
238.     end do
239.     ! node based radial coordinate
240.     do iR = 1, nR+1
241.        RadiusNode_I(iR) = rMin + (iR - 1)*dR
242.     end do
243.     dRadius_I = RadiusNode_I(2:nR+1) - RadiusNode_I(1:nR)
244.     dRadiusNode_I = Radius_I(1:nR+1) - Radius_I(0:nR)
245. 
246.     if(UseCosTheta)then
247.        dZ = 2.0/nTheta
248. 
249.        ! Set Theta_I
250.        do iTheta = 1, nTheta
251.           z = 1 - (iTheta - 0.5)*dZ
252.           Theta_I(iTheta) = acos(z)
253.        end do
254.        Theta_I(0)        = -Theta_I(1)
255.        Theta_I(nTheta+1) = cTwoPi - Theta_I(nTheta)
256. 
257.        ! Set ThetaNode_I
258.        do iTheta = 1, nTheta + 1
259.           z = max(-1.0, min(1.0, 1 - (iTheta-1)*dZ))
260.           ThetaNode_I(iTheta) = acos(z)
```

</details>


---

<sub>⏱️ 1m 49s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/read_magnetogram.pro.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/read_magnetogram.pro (lines 1-260)

<details>
<summary>157 lines</summary>

```
1. ;For reading magnetograms in FITS or BATS-R-US format.
2. 
3. FUNCTION read_magnetogram, file, PlotRadius, UseBATS
4. 
5.   if UseBATS then begin
6.                                 ; Setup common block for BATSRUS/Idl
7.      common getpict_param, filename
8.      common file_head
9.      common plot_data, grid, x, w
10. 
11.      filename = file
12.      read_data
13. 
14.      if gencoord then begin
15.         print, 'file '+file+' should contain a regular grid'
16.         retall
17.      endif
18. 
19.      case ndim of
20.         2:begin
21.            if PlotRadius ne 1.0 then begin
22.               print,'PlotRadius cannot be specified with 2D data!'
23.               retall
24.            endif
25. 
26.            if variables(0) ne "Longitude" or variables(1) ne "Latitude" or $
27.               variables(2) ne 'Br' then begin
28.               print, 'variables should be Longitude Latitude Br!'
29.               retall
30.            endif
31. 
32.            nlon = nx[0]
33.            nlat = nx[1]
34.            
35.            mag_info = {nlon:nlon,$
36.                        nlat:nlat,$
37.                        time:time,$
38.                        longitude:fltarr(nlon,nlat),$
39.                        latitude:fltarr(nlon,nlat),$
40.                        br_field:fltarr(nlon,nlat),$
41.                        blon_field:fltarr(nlon,nlat),$
42.                        blat_field:fltarr(nlon,nlat),$
43.                        occPos:fltarr(nlon,nlat),$
44.                        occNeg:fltarr(nlon,nlat),$
45.                        neqpar:neqpar,$
46.                        eqpar:fltarr(neqpar)}
47.            mag_info.longitude = x(*,*,0)*!dtor
48.            mag_info.latitude  = x(*,*,1)*!dtor
49.            mag_info.br_field = w(*,*,0)
50.            mag_info.eqpar    = eqpar
51.            if nw ge 2 then mag_info.blon_field = w(*,*,1)
52.            if nw ge 3 then mag_info.blat_field = w(*,*,2)
53.            if nw ge 4 then mag_info.occPos = w(*,*,3)
54.            if nw ge 5 then mag_info.occNeg = w(*,*,4)
55.            
56.         end
57. 
58.         3:begin
59.            if variables(0) ne "Radius" or variables(1) ne "Longitude" or $
60.               variables(2) ne "Latitude" or variables(3) ne 'Br' then begin
61.               print, 'variables should be Radius Longitude Latitude Br!'
62.               retall
63.            endif
64.            
65.            nlon = nx[1] - 1
66.            nlat = nx[2]
67.            
68.            mag_info = {nlon:nlon,$
69.                        nlat:nlat,$
70.                        time:time,$
71.                        longitude:fltarr(nlon,nlat),$
72.                        latitude:fltarr(nlon,nlat),$
73.                        br_field:fltarr(nlon,nlat),$
74.                        blon_field:fltarr(nlon,nlat),$
75.                        blat_field:fltarr(nlon,nlat),$
76.                        neqpar:neqpar,$
77.                        eqpar:fltarr(neqpar)}
78. 
79.            radius = x(*,0,0,0)
80.            longitude = x(0,*,*,1)
81.            latitude  = x(0,*,*,2)
82.            
83.                                 ; find index for the cut                                             
84.            d = abs(radius - PlotRadius)
85.            icut = where( d eq min(d) )
86.            br_field     = w(icut,*,*,0)
87.            bphi_field   = w(icut,*,*,1)
88.            btheta_field = w(icut,*,*,2)
89.            
90.            mag_info.br_field = reform(br_field[0,0:nlon-1,*])
91.            mag_info.blon_field = reform(blon_field[0,0:nlon-1,*])
92.            mag_info.blat_field = reform(blat_field[0,0:nlon-1,*])
93.            mag_info.longitude = reform(longitude[0,0:nlon-1,*])
94.            mag_info.latitude = reform(latitude[0,0:nlon-1,*])
95.         end
96.         else: begin
97.            print, 'ndim=', ndim, ' should be 2 or 3'
98.            retall
99.         end
100.      endcase
101.   endif else begin
102.                                 ;read magnetogram in FITS format. For
103.                                 ;transfering to Python, read_fits
104.                                 ;function can be replaced by astropy
105.                                 ;function.
106. 
107.      ; read_fits and readfits give the same result.
108.      ;except readfits now has options to recognize 
109.      ;sintheta/theta grids in latitude
110. 
111. 
112. ;     br_field=readfits(file,index,/noscale)
113.      br_field=readfits(file,index,StringHeader,LongShift,CRnumber,IsUniformLat,/noscale)
114.      
115.      s=size(br_field)
116.      nlon=s[1]
117.      nlat=s[2]
118.      
119.      mag_info = {nlon:nlon,$
120.                  nlat:nlat,$
121.                  longitude:fltarr(nlon,nlat),$
122.                  latitude:fltarr(nlon,nlat),$
123.                  br_field:fltarr(nlon,nlat),$
124.                  blon_field:fltarr(nlon,nlat),$
125.                  blat_field:fltarr(nlon,nlat),$
126.                  neqpar:0, eqpar:fltarr(1)}
127.      
128.     ;;;; already assumes that it is sin theta grid
129. 
130. 
131.      if(IsUniformLat EQ 0)then begin
132.         lat=findgen(nlat)*2./nlat
133.         lat=asin(lat-lat[nlat-1]/2.)
134.      endif else begin
135.         lat=findgen(nlat)*!dtor
136.         lat = lat - lat[nlat-1]/2.
137.      endelse
138.      print,lat/!dtor
139.      lon=findgen(nlon)*!DPI*2./nlon
140.      latitude=fltarr(nlon,nlat)
141.      longitude=fltarr(nlon,nlat)
142.      for i=0,nlon-1 do begin
143.         for j=0,nlat-1 do begin
144.            latitude[i,j]=lat[j]
145.            longitude[i,j]=lon[i]
146.         endfor
147.      endfor
148.      
149.      mag_info.longitude=longitude
150.      mag_info.latitude=latitude
151.      mag_info.br_field=br_field
152.   endelse
153. 
154.   return, mag_info
155. 
156. end
157.
```

</details>


---

<sub>⏱️ 1m 49s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/readfits.pro.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/readfits.pro (lines 1-320)

<details>
<summary>320 lines</summary>

```
1. ;  Copyright (C) 2002 Regents of the University of Michigan, portions used with permission 
2. ;  For more information, see http://csem.engin.umich.edu/tools/swmf
3. ; Purpose:
4. ;
5. ; Reading FITS files into IDL.
6. ;
7. ; This file contains all functions and procedures needed for
8. ; the basic features of the ts function.
9. ;
10. ; Basic usage:
11. ;
12. ; Array = read_fits('filename.fits' [, header])
13. ;
14. ; where the array is set to the data contained in the fits file, 
15. ; while the optional header parameter returns a string array 
16. ; with the header information.
17. 
18. function gettok,st,char
19. ;+
20. ; NAME:
21. ;   GETTOK
22. ; PURPOSE:
23. ;   Retrieve the first part of the string up to a specified character
24. ; EXPLANATION:
25. ;   GET TOKen - Retrieve first part of string until the character char
26. ;   is encountered.
27. ;
28. ; CALLING SEQUENCE:
29. ;   token = gettok( st, char )
30. ;
31. ; INPUT:
32. ;   char - character separating tokens, scalar string
33. ;
34. ; INPUT-OUTPUT:
35. ;   st - (scalar) string to get token from (on output token is removed)
36. ;
37. ; OUTPUT:
38. ;   token - scalar string value is returned
39. ;
40. ; EXAMPLE:
41. ;   If ST is 'abc=999' then gettok(ST,'=') would return
42. ;   'abc' and ST would be left as '999'
43. ;
44. ; NOTES:
45. ;       A version of GETTOK that accepts vector strings is available for users
46. ;       of IDL V5.3 or later from  http://idlastro.gsfc.nasa.gov/ftp/v53/
47. ; HISTORY
48. ;   version 1  by D. Lindler APR,86
49. ;   Remove leading blanks    W. Landsman (from JKF)    Aug. 1991
50. ;   Converted to IDL V5.0   W. Landsman   September 1997
51. ;-
52. ;----------------------------------------------------------------------
53.   On_error,2                           ;Return to caller
54. 
55. ; if char is a blank treat tabs as blanks
56. 
57.   tab = string(9b)
58.   while strpos(st,tab) GE 0 do begin    ;Search for tabs
59.     pos = strpos(st,tab)
60.     strput,st,' ',pos
61.   endwhile
62. 
63.   st = strtrim(st,1)              ;Remove leading blanks
64. 
65. ; find character in string
66. 
67.   pos = strpos(st,char)
68.   if pos EQ -1 then begin         ;char not found?
69.     token = st
70.     st = ''
71.     return, token
72.   endif
73. 
74. ; extract token
75. 
76.  token = strmid(st,0,pos)
77.  len = strlen(st)
78.  if pos EQ (len-1) then st = '' else st = strmid(st,pos+1,len-pos-1)
79. 
80. ;  Return the result.
81. 
82.  return,token
83.  end
84. 
85. ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
86. ;+
87. ; NAME:
88. ;     VALID_NUM
89. ; PURPOSE:
90. ;     Check if a string is a valid number representation.
91. ; EXPLANATION:
92. ;     The input string is parsed for characters that may possibly
93. ;     form a valid number.  It is more robust than simply checking
94. ;     for an IDL conversion error because that allows strings such
95. ;     as '22.3qwert' to be returned as the valid number 22.3
96. ;     See also the original NUM_CHK which returns the status in
97. ;     the opposite sense.
98. ;
99. ; CALLING SEQUENCE:
100. ;     IDL> status = valid_num(string  [,value]  [,/integer])
101. ;
102. ; Inputs      : string  -  the string to be tested
103. ;
104. ; Opt. Inputs : None
105. ;
106. ; Outputs     : The function returns 1 for valid, 0 for invalid number
107. ;
108. ; Opt. Outputs: value   - The value the string decodes to.  This will be
109. ;        returned as a double precision number unless /INTEGER
110. ;        is present, in which case a long integer is returned.
111. ;
112. ; Keywords    : Integer   -  if present code checks specfically for an integer.
113. ;
114. ; Calls       : None
115. ;
116. ; Restrictions: None
117. ;
118. ; Category    : Utilities, Numerical
119. ;
120. ; Prev. Hist. : Small changes from NUM_CHK by Andrew Bowen,
121. ;                                             Tessella Support Services, 8/3/93
122. ;
123. ; Written     : CDS version by C D Pike, RAL, 24-May-93
124. ;
125. ; Modified    : Version 1, C D Pike, RAL, 24-May-93
126. ;     Version 2, William Thompson, GSFC, 14 October 1994
127. ;      Added optional output parameter VALUE to allow
128. ;      VALID_NUM to replace STRNUMBER in FITS routines.
129. ;
130. ; Version     : Version 1  24-May-93
131. ;   Converted to IDL V5.0   W. Landsman   September 1997
132. ;-
133. 
134. FUNCTION valid_num, string, value, INTEGER=integer
135. 
136.        ;**** Set defaults for keyword ****
137.   IF NOT (KEYWORD_SET(integer)) THEN integer=0
138. 
139.        ;**** arrays of legal characters ****
140.   numbers   = '0123456789'
141.   signs     = '+-'
142.   decimal   = '.'
143.   exponents     = 'ED'
144. 
145.        ;**** trim leading and trailing blanks/compress white ****
146.        ;**** space and convert any exponents to uppercase.   ****
147.   numstr = strupcase(strtrim(strcompress(string),2))
148. 
149.        ;**** length of input string ****
150.   len = strlen(numstr)
151. 
152.   ok = 1
153. 
154.   if integer eq 0 then stage = 1 else stage = 6
155. 
156.   for i = 0, len-1 do begin
157. 
158.     char = strmid(numstr,i,1)
159. 
160.        ;**** the parsing steps 1 to 8 are for floating   ****
161.        ;**** point, steps 6 to 8, which test for a legal ****
162.        ;**** exponent, can be used to check for integers ****
163. 
164. ;**** The parsing structure is as follows.  Each character in the ****
165. ;**** string is checked against the valid list at the current     ****
166. ;**** stage.  If no match is found an error is reported.  When a  ****
167. ;**** match is found the stage number is updated as indicated     ****
168. ;**** ready for the next character.  The valid end points are     ****
169. ;**** indicated in the diagram.             ****
170. ;
171. ;Stage  1       2     3   4
172. ;
173. ;Valid  sign --> 2   dec-pt    --> 3  digit    --> 5  dec-pt   --> 5
174. ;  "    dec-pt --> 3   digit --> 4      digit   --> 4
175. ;  "    digit  --> 4              exp't  --> 6
176. ;  "                   END
177. ;
178. ;Stage  5       6     7   8
179. ;
180. ;Valid  digit    --> 5  sign --> 7   digit --> 8   digit -->8
181. ;  "    exp't  --> 6    digit  --> 8         END
182. ;  "    END
183. ;
184. 
185.     CASE stage OF
186. 
187.       1 : begin
188.         if      strpos(signs,char) ge 0    then stage = 2 $
189.     else if    decimal eq char    then stage = 3 $
190.     else if    strpos(numbers,char) ge 0     then stage = 4 $
191.     else    ok = 0
192.       end
193. 
194.       2 : begin
195.     if     decimal eq char    then stage = 3 $
196.     else if    strpos(numbers,char) ge 0     then stage = 4 $
197.     else    ok = 0
198.       end
199. 
200.       3 : begin
201.     if     strpos(numbers,char) ge 0     then stage = 5 $
202.     else    ok = 0
203.       end
204. 
205.       4 : begin
206.     if     decimal eq char    then stage = 5 $
207.     else if    strpos(numbers,char) ge 0     then stage = 4 $
208.     else if       strpos(exponents,char) ge 0   then stage = 6 $
209.     else    ok = 0
210.       end
211. 
212.       5 : begin
213.     if     strpos(numbers,char) ge 0     then stage = 5 $
214.     else if       strpos(exponents,char) ge 0   then stage = 6 $
215.     else    ok = 0
216.       end
217. 
218.       6 : begin
219.         if      strpos(signs,char) ge 0    then stage = 7 $
220.     else if    strpos(numbers,char) ge 0     then stage = 8 $
221.     else    ok = 0
222.       end
223. 
224.       7 : begin
225.     if     strpos(numbers,char) ge 0     then stage = 8 $
226.     else    ok = 0
227.       end
228. 
229.       8 : begin
230.     if     strpos(numbers,char) ge 0     then stage = 8 $
231.     else    ok = 0
232.       end
233. 
234.     ENDCASE
235. 
236.   end
237. 
238.        ;**** check that the string terminated legally ****
239.        ;**** i.e in stages 4, 5 or 8                  ****
240.   if (stage ne 4) and (stage ne 5) and (stage ne 8) then ok = 0
241. 
242.        ;**** If requested, then form the value. ****
243. 
244.   if (n_params() eq 2) and ok then begin
245.     if keyword_set(integer) then value = long(string) else $
246.        value = double(string)
247.   endif
248. 
249.        ;**** return error status to the caller ****
250.   RETURN, ok
251. 
252. 
253. END
254. 
255. ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
256. function SXPAR, hdr, name, abort, COUNT=matches, COMMENT = comments, $
257.                                   NoContinue = NoContinue, SILENT = silent
258. ;+
259. ; NAME:
260. ;      SXPAR
261. ; PURPOSE:
262. ;      Obtain the value of a parameter in a FITS header
263. ;
264. ; CALLING SEQUENCE:
265. ;      result = SXPAR( Hdr, Name, [ Abort, COUNT=, COMMENT =, /NoCONTINUE  ])   
266. ;
267. ; INPUTS:
268. ;      Hdr =  FITS header array, (e.g. as returned by READFITS) 
269. ;             string array, each element should have a length of 80 characters      
270. ;
271. ;      Name = String name of the parameter to return.   If Name is of the
272. ;             form 'keyword*' then an array is returned containing values of
273. ;             keywordN where N is an integer.  The value of keywordN will be
274. ;             placed in RESULT(N-1).  The data type of RESULT will be the
275. ;             type of the first valid match of keywordN found.
276. ;
277. ; OPTIONAL INPUTS:
278. ;       ABORT - string specifying that SXPAR should do a RETALL
279. ;               if a parameter is not found.  ABORT should contain
280. ;               a string to be printed if the keyword parameter is not found.
281. ;               If not supplied, SXPAR will return quietly with COUNT = 0
282. ;               (and !ERR = -1) if a keyword is not found.
283. ;
284. ; OPTIONAL INPUT KEYWORDS: 
285. ;       /NOCONTINUE = If set, then continuation lines will not be read, even
286. ;                 if present in the header
287. ;       /SILENT - Set this keyword to suppress warning messages about duplicate
288. ;                 keywords in the FITS header.
289. ;
290. ; OPTIONAL OUTPUT KEYWORDS:
291. ;       COUNT - Optional keyword to return a value equal to the number of 
292. ;               parameters found by SXPAR, integer scalar
293. ;
294. ;       COMMENT - Array of comments associated with the returned values
295. ;
296. ; OUTPUTS:
297. ;       Function value = value of parameter in header.
298. ;               If parameter is double precision, floating, long or string,
299. ;               the result is of that type.  Apostrophes are stripped
300. ;               from strings.  If the parameter is logical, 1b is
301. ;               returned for T, and 0b is returned for F.
302. ;               If Name was of form 'keyword*' then a vector of values
303. ;               are returned.
304. ;    
305. ; SIDE EFFECTS:
306. ;       !ERR is set to -1 if parameter not found, 0 for a scalar
307. ;       value returned.  If a vector is returned it is set to the
308. ;       number of keyword matches found.    The use of !ERR is deprecated, and
309. ;       instead the COUNT keyword is preferred
310. ;
311. ;       If a keyword (except HISTORY or COMMENT) occurs more than once in a 
312. ;       header, a warning is given, and the *last* occurence is used.
313. ;
314. ; EXAMPLES:
315. ;       Given a FITS header, h, return the values of all the NAXISi values
316. ;       into a vector.    Then place the history records into a string vector.
317. ;
318. ;       IDL> naxisi = sxpar( h ,'NAXIS*')         ; Extract NAXISi value
319. ;       IDL> history = sxpar( h, 'HISTORY' )      ; Extract HISTORY records
320. ;
```

</details>


---

<sub>⏱️ 1m 49s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py (lines 1-320)

<details>
<summary>320 lines</summary>

```
1. #!/usr/bin/env python3
2. 
3. # this magnetogram remapping can either be run as a script from 
4. # the unix command line
5. # or imported into Python. See description of use in the README file
6. #         by  Richard A. Frazin July 2014 - February 2015
7. # April 2020: 
8. # script updated to work for both reading & remapping fits magnetogram and 
9. # to be used from EEGGL as well
10. # uses pyfits instead of astropy
11. # separate functions for 1)remapping the grid, 2) reading fits file
12. # June 2020: generalized for any types of maps that have multiple realizations
13. # Read & remap HMI vector magnetogram (.fits)
14. # May 2024: read HMI synoptic Pol filled maps (BinTableHDU),needs astropy
15. 
16. import pyfits as fits
17. #from astropy.io import fits
18. #import matplotlib.pyplot as plt
19. from scipy import interpolate
20. from scipy import integrate
21. import numpy as np
22. import sys
23. import os
24. import fnmatch
25. import time
26. from datetime import datetime
27. import argparse
28. import pdb
29. 
30. def remap(inputfile, outputfile, nlat = -1, nlong = -1, out_grid = 'unspecified', i=-1, nSmooth=1, BMax=-1, DoHMI=0):
31.     """
32.     Flux-conserving magnetogram remapping tool.
33.     inputfile - FITS file containing original magnetogram (include path)
34.     outputfile - contains result in customized output format (include path)
35.     nlat  (opitonal) = desired number of latitude  points in output,
36.          if not specified, will be set to the same as the input file
37.     nlong (optional) = desired number of longitude points in output
38.         if not specified, will be set to the same as the input file
39.     out_grid (optional), choices are 'sin(lat)' or 'uniform'
40.         if not specified, the output grid will be the same type
41.     If nlat, nlong and out_grid are ALL left out, no remapping is done,
42.         and the code simply reformats.
43.     Note that ADAPT files may have multiple maps.  \
44.     Only the 1st is utilized unless specified otherwise.
45.     My MATLAB code remap_mag.m uses the same algorithm but runs much faster.
46.        by Richard Frazin, July 2014 - Feb 2015
47.     """
48.     mapdate = 0.
49.     pi = np.pi
50.     if ( (out_grid != 'sin(lat)') and (out_grid != 'uniform') and \
51.              (out_grid != 'unspecified') ):
52.         print ("Unknown output grid type.  Choices are blank, 'unspecified',\
53.  'uniform' and 'sin(lat)' ")
54.         return(-1)
55.     
56.     if(DoHMI !=0):
57.         magtype = 'HMI Synotic Vector Magnetogram'
58.         g=fits.open(inputfile)
59.         nlo = g[0].header['NAXIS1'] 
60.         nla = g[0].header['NAXIS2'] 
61.         CRnumber = 0
62.         long0 = 0
63.         CR  = 0
64.         grid_type='sin(lat)'
65.         input_grid = grid_type
66. 
67.     if(DoHMI == 0):
68.         cc =  FITS_RECOGNIZE(inputfile)
69.         if cc == -1:
70.             print ("Input file not recognized.")
71.             return(-1)
72.         else:
73.             magtype = cc[0]
74.             grid_type = cc[1]
75.             map_data = cc[2]
76.             input_grid = grid_type
77.             nlo = cc[3]
78.             nla = cc[4]
79.             CRnumber = cc[5]
80.             CR = cc[6]
81.             long0 = cc[7]
82.             bunit = cc[8]
83.             mapdate = cc[9]
84.     print('cc =',cc)
85.     if nlat == -1:
86.         nlat = nla
87.     elif nlat < 1:
88.         print ("nlat has to be -1 or a positive integer.")
89.         return(-1)
90.     
91.     if nlong == -1:
92.         nlong = nlo
93.     elif nlong < 1:
94.         print ("nlong has to be -1 or a positive integer.")
95.         return(-1)
96.     
97.     #what kind of transformation are we doing?        
98.     if out_grid == 'unspecified':
99.         out_grid = grid_type
100.     
101.     if grid_type == out_grid:
102.         transformation = 'rebin' #no change in grid type, so just rebin
103.     elif ( (grid_type == 'uniform') and (out_grid == 'sin(lat)') ):
104.         transformation = 'reg2sin'
105.     elif ( (grid_type == 'sin(lat)') and (out_grid == 'uniform') ):
106.         transformation = 'sin2reg'
107.     else:
108.         print ("Unknown transformation type.")
109.         return(-1)
110.     
111.     # read the data
112.     g = fits.open(inputfile)
113.     try:
114.         naxis=g[0].header['NAXIS']
115.     except KeyError as er:
116.         naxis = -1
117. 
118.     if naxis == 0:
119.         header0 = g[1].header
120.         d = g[1].data
121.         g[0].header=g[1].header
122.     else:
123.         header0 = g[0].header
124.         d = g[0].data
125. 
126.     ind = np.where(np.isnan(d))
127.     d[ind] = 0.
128. 
129.     # works for magnetograms with multiple realizations:
130.     # eg: ADAPT maps, newer polar filled HMI maps
131.     try:
132.         nim = g[0].header['NAXIS3']
133.     except KeyError as er:
134.         nim = -1
135.     if nim > -1:
136.         #    if magtype == 'ADAPT Synchronic':
137.         # nim = g[0].header['NAXIS3'] # number of images
138.         imdex = i  #which of the 12 maps do you want?
139.         print ('This file contains ', str(nim), ' images. Writing out file ', \
140.                '{:2d}'.format(i+1), ', output filename=', outputfile)
141.         if nim > 1:  #just keep one of them for now
142.             d = d[imdex,:,:]
143.     else:
144.         print ('This file contains only 1 images. Writing out file ', \
145.                '{:2d}'.format(i+1), ', output filename=', outputfile)
146.             
147.     g[0].header['NAXIS1'] = nlong # new number of longitude points
148.     g[0].header['NAXIS2'] = nlat  #               latitude
149. 
150.     try:
151.         g[0].header['GRID'] = out_grid #change the existing header value
152.     except KeyError as er:
153.         g[0].header.set('GRID',out_grid) #create FITS header keyword
154. 
155.     try:
156.         g[0].header['CTYPE2'] = out_grid #change the existing header value
157.     except KeyError as er:
158.         g[0].header.set('CTYPE2',out_grid) #create FITS header keyword
159. 
160.     # Conservative smoothing. Boundary condition:
161.     # Periodic in Longitude, reflect in Latitude.
162.     if (nSmooth>2):
163.         d=smooth(nlong,nlat,nSmooth,d)
164.         print('Smoothing Done with nsmooth = ',nSmooth)
165. 
166.     if out_grid == 'sin(lat)':
167.         newlat = (180/pi)*np.arcsin(np.linspace(-1. + 1./2/nlat,1. - \
168.                                                      1./2/nlat,nlat)) # in deg
169.     elif out_grid == 'uniform':
170.         newlat = (180/pi)*np.linspace(-pi/2 + pi/2/nlat,pi/2 - \
171.                                            pi/2/nlat,nlat) # in deg
172.     else:
173.         print ("out_grid incorrectly set.")
174.         return(-1)
175. 
176.     if ( (nlo == nlong) and (nla == nlat) and (grid_type == out_grid) ):
177.         newmap = d  #no remapping
178.         print('No grid Transformation')
179.     else:
180.         #first make a hybrid map that is (nla X nlong) by using the rebin
181.         #and add alg. in the longitude direction.  If nlo = nlong, hybrid --> d
182.         hybrid = np.zeros([nla,nlong]) 
183.         crap = np.arange(nlo+1)
184.         for pf in crap[nlo+1:0:-1]: #pf will be the greatest common factor of \
185.                                     #nlong and nlo
186.             if ( (np.mod(nlo,pf) == 0) and (np.mod(nlong,pf) == 0)): 
187.                 #common factor test
188.                 nlo_fac   = nlo/pf
189.                 nlong_fac = nlong/pf
190.                 break
191.         for k in np.arange(nla):
192.             w = np.kron(d[k,:],np.ones(int(nlong_fac))) #this array has length
193.                                                         #pf*nlo_fac*nlong_fac
194.             for l in np.arange(nlong): #take the average over nlo_fac bins of w
195.                 hybrid[k,l] = np.sum(w[int(l*nlo_fac):(l+1)*int(nlo_fac)])\
196.                     /nlo_fac
197. 
198.         newmap = np.zeros([nlat,nlong]) #output map                           
199.         if transformation == 'rebin': #do rebin and add in the latitude dir,\
200.                                       #if nlo = nlat, newmap --> d
201.             crap = np.arange(nla+1)
202.             for pf in crap[nla+1:0:-1]: #pf will be the greatest common factor
203.                                         #of nla and nlat
204.                 if ( (np.mod(nla,pf) == 0) and (np.mod(nlat,pf) == 0) ): 
205.                     # common factor test
206.                     nla_fac  = nla/pf
207.                     nlat_fac = nlat/pf
208.                     break
209.                 
210.             for k in np.arange(nlong):
211.                 w = np.kron(hybrid[:,k].T,np.ones(int(nlat_fac)))
212.                 #length is pf*nla_fac*nlat_fac
213.                 for l in np.arange(nlat):
214.                     newmap[l,k] = np.sum(w[int(l*nla_fac):(l+1)*int(nla_fac)])\
215.                     /nla_fac
216. 
217.         elif transformation == 'reg2sin':
218.             print('Transform uniform to sinlat grid' )
219.             #old latitude grid
220.             oldlat =  np.linspace(-pi/2 + pi/2/nla,pi/2 - pi/2/nla,nla) 
221.             #for interpolator
222.             oldlat = np.hstack((-pi/2-1.e-9,oldlat,pi/2+1.e-9))
223.             bin_boundary = np.arcsin(np.linspace(-1.,1.,nlat+1)) 
224.             #boundaries of new sin(latitude) grid
225.             for k in np.arange(nlong):   
226.             #the magnetic field value assigned is the flux divided by the area.
227.                 u = np.hstack((hybrid[0,k],hybrid[:,k],hybrid[nla-1,k]))
228.                 crap = interpolate.interp1d(oldlat,u,kind='linear') 
229.                 #magnetic field interpolator
230.                 fcn = lambda x : crap(x)*np.cos(x)  #B(theta)*cos(theta)
231.                 for l in np.arange(nlat):
232.                     result = integrate.quad(fcn,bin_boundary[l],\
233.                                                 bin_boundary[l+1],\
234.                                                 epsabs=1.e-3,epsrel=1.e-3)/\
235.                                                 (np.sin(bin_boundary[l+1]) - \
236.                                                      np.sin(bin_boundary[l]))
237.                     newmap[l,k] = result[0]
238.         elif transformation == 'sin2reg':
239.             print('Transform sinlat to uniform grid' )
240.             #arcsin(old sin(latitude) grid)
241.             oldlat = np.arcsin(np.linspace(-1. + 1./2/nla,1. - 1./2/nla,nla))
242.             oldlat = np.hstack((-pi/2-1.e-9,oldlat,pi/2+1.e-9)) #interpolator
243.             bin_boundary = np.linspace(-pi/2,pi/2,nlat+1) 
244.             #boundaries of new latitude grid
245.             #pdb.set_trace()
246.             for k in np.arange(nlong): #magnetic field = flux divided by area. 
247.                 u = np.hstack((hybrid[0,k],hybrid[:,k],hybrid[nla-1,k]))
248.                 crap = interpolate.interp1d(oldlat,u,kind='linear') 
249.                 #magnetic field interpolator
250.                 fcn = lambda x : crap(x)*np.cos(x)  # B(theta)*cos(theta)
251.                 for l in np.arange(nlat):
252.                     if DoHMI == 1 :
253.                         result = integrate.quad( \
254.                             fcn,bin_boundary[l], bin_boundary[l+1],\
255.                                 epsabs=1.e-2,epsrel=1.e-2)/\
256.                                 (np.sin(bin_boundary[l+1]) - \
257.                                      np.sin(bin_boundary[l]))
258.                     else:
259.                         result = integrate.quad(\
260.                             fcn,bin_boundary[l], bin_boundary[l+1],\
261.                                 epsabs=1.e-3,epsrel=1.e-3)/\
262.                                 (np.sin(bin_boundary[l+1]) - \
263.                                      np.sin(bin_boundary[l]))
264.                     newmap[l,k] = result[0]
265.                     
266.         else:
267.             print ("Unknown transformation type.")
268.             return(-1)
269. 
270.     #test for flux conservation in the transformation        
271.     test_flux = False 
272.     if test_flux:
273.         if grid_type == 'uniform':
274.             latt =  np.cos(np.linspace(-pi/2 + pi/2/nla,pi/2 - pi/2/nla,nla))
275.             cosgrid = np.kron(latt,np.ones((nlo,1))).T
276.             oldflux = np.sum(np.multiply(cosgrid,d))*2.*pi*pi/nlo/nla
277.         elif grid_type == 'sin(lat)':
278.             oldflux = np.sum(d)*4.*pi/nlo/nla
279.         else:
280.             print ("Bad grid_type.")
281.             return(-1)
282.         if out_grid == 'uniform':
283.             latt = np.cos(np.linspace(-pi/2 + pi/2/nlat,pi/2 - pi/2/nlat,nlat))
284.             cosgrid = np.kron(latt,np.ones((nlong,1))).T
285.             newflux = np.sum(np.multiply(cosgrid,newmap))*2.*pi*pi/nlong/nlat
286.         elif out_grid == 'sin(lat)':
287.             newflux = np.sum(newmap)*4.*pi/nlong/nlat
288.         else:
289.             print ("Bad out_grid.")
290.             return(-1)
291.         print ("original flux =",str(oldflux),", new flux =",str(newflux))
292.     
293.     # ascii output file, Gabor's format
294.     nParam = 2
295.     Param_I = np.zeros(nParam)
296.     Param_I[0] = long0
297.     Param_I[1] = int(float(CRnumber))
298.     Long_I = np.linspace(180.0/nlong, 360-180.0/nlong, nlong)
299.     # The first line is arbitary
300.     if (DoHMI == 0):
301.         if magtype == 'ADAPT Synchronic':
302.             StrHeader = 'MagnetogramType = '+magtype+'; ADAPTRealization = ' \
303.                 +str(imdex+1)+ '; InstrumentName = '+map_data+\
304.                 '; InputLatGrid = '\
305.                 +input_grid+'; OutputLatGrid = '+out_grid+'; MagUnit = ' \
306.                 +bunit+'; InputMapResolution = '+str(nlo)+','+str(nla)+\
307.                 '; MagnetogramDate = '+mapdate+'; CentralMeridianLong = '\
308.                 +format(float(CR)+0.5-float(long0)/360.,'f')+'; InputFile = '\
309.                 +str(inputfile)+\
310.                 ';ASCIIFileCreationDate = '\
311.                 +time.strftime("%Y-%m-%dT%H:%M:%S")
312.         else:
313.             StrHeader = 'MagnetogramType = '+magtype+'; InstrumentName = '\
314.                 +map_data+\
315.                 '; InputLatGrid = '+input_grid+'; OutputLatGrid = '+out_grid+\
316.                 '; MagUnit = '+bunit+'; InputMapResolution = '+str(nlo)+','\
317.                 +str(nla)+'; MagnetogramDate = '+mapdate+\
318.                 '; CentralMeridianLong = '+\
319.                 format(float(CR)+0.5-float(long0)/360.,'f')+\
320.                 '; InputFile = "'+str(inputfile)+\
```

</details>


---

<sub>⏱️ 1m 49s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/get_magnetogram.py.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/get_magnetogram.py (lines 1-320)

<details>
<summary>108 lines</summary>

```
1. #!/usr/bin/env python3
2. ############ Prototype: make_submission.py by Maksym Petrenko
3. ############ CMERAL modification of make_submission.py
4. ############ 30/11/2022
5. ############ This python script correspond to a part of the make_submission.py
6. ############ that only download the latest GONG magnetogram for realtime
7. ############ simulation in the run directory as fitsfile.fits
8. ###############################################################################################################
9. 
10. from html.parser import HTMLParser
11. import requests
12. import re
13. import os
14. import shutil
15. import gzip
16. import argparse
17. 
18. ISWA_DATA_URL = 'https://iswaa-webservice1.ccmc.gsfc.nasa.gov/iswa_data_tree/observation/solar/gong/mrzqs/'
19. 
20. #modify to change the output directory (run_realtime directory used for realtime simulations)
21. OUTPUT_BASE_PATH = os.getcwd()
22. 
23. HEADERS = {"User-Agent":"Mozilla/5.0 (Macintosh Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"}
24. 
25. 
26. class LinkScrape(HTMLParser):
27.     def reset(self):
28.         super().reset()
29.         self.links = []
30.         self.in_link = False
31.     def handle_starttag(self, tag, attrs):
32.         self.in_link = False
33.         if tag == 'a':
34.             self.in_link = True
35.             for (name, value) in attrs:
36.                 if name == 'href':
37.                     self.links.append({'href': value})
38.     def handle_endtag(self, attrs):
39.         self.in_link = False
40.     def handle_data(self, data):
41.         if self.in_link: self.links[-1]['text'] = data
42.     def clean(self):
43.         self.links = []
44. 
45. def get_highest(page_url, pattern, datetime):
46.     response = requests.get(page_url)
47.     page_html = response.text
48.     link_parser = LinkScrape()
49.     link_parser.feed(page_html)
50.     links = link_parser.links
51.     link_parser.clean()
52. 
53. 
54.     last_match = ''
55.     lats_link = ''
56.     last_text = ''
57.     for link in links:
58.         original_url = link['href']
59.         text = link['text']
60.         matches = re.search(pattern, text)
61.         if (matches):
62.             if (matches.group(1) > last_match and matches.group(1)<=datetime):
63.                 last_match = matches.group(1)
64.                 lats_link = original_url
65.                 last_text = text
66.     return [last_match, last_text, lats_link]
67. 
68. def download_file(url, save_path):
69.     try:
70.         # Send GET request to the URL
71.         response = requests.get(url)
72.         # Check if the request was successful (status code 200)
73.         if response.status_code == 200:
74.             # Write the content of the response to a local file
75.             with open(save_path, 'wb') as file:
76.                 file.write(response.content)
77.             print(f"File downloaded successfully: {save_path}")
78.         else:
79.             print(f"Failed to download file. Status code: {response.status_code}")
80.     except Exception as e:
81.         print(f"Error: {e}")
82. 
83. if __name__ == '__main__':
84. 
85.     parser = argparse.ArgumentParser(description=
86.                                      "Use python3 get_magnetogram.py datetime")
87.     parser.add_argument('datetime', help=
88.                         "Date_Time in the format yymmdd't'hhmm")
89.     args = parser.parse_args()
90.     datetime = str(args.datetime)
91.     matches=re.search(r'(\d\d\d\d\d\dt\d\d\d\d)',datetime)
92.     year = '20'+matches.group(1)[0:2]
93.     month = matches.group(1)[2:4]
94.     month_url = ISWA_DATA_URL.rstrip('/')+'/'+\
95.         str(year)+'/'+str(month)+'/'
96.     [cr, text, link] = get_highest(
97.         month_url,r'(\d\d\d\d\d\dt\d\d\d\d)',matches.group(1))
98.     granule_url = month_url.rstrip('/') + '/' + link
99.     print("granule_url="+granule_url)
100.     # Adjust input files
101.     fits_file = os.path.join(OUTPUT_BASE_PATH, "fitsfile.fits")
102.     fits_file_gz = os.path.join(OUTPUT_BASE_PATH,str(link))
103.     download_file(granule_url,fits_file_gz)
104.     with gzip.open(fits_file_gz, 'rb') as f_in:
105.         with open(fits_file, 'wb') as f_out:
106.             shutil.copyfileobj(f_in, f_out)
107.     os.unlink(fits_file_gz)
108.
```

</details>


---

<sub>⏱️ 1m 59s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py (lines 321-760)

<details>
<summary>440 lines</summary>

```
321.                 ';ASCIIFileCreationDate = '\
322.                 +time.strftime("%Y-%m-%dT%H:%M:%S")
323.         NameVar = 'Longitude Latitude Br LongitudeShift CarringtonRotation'
324.         if (BMax > 0.):
325.             Data_C=np.zeros([nlat,nlong])
326.             for k in np.arange(nlat):
327.                 for l in np.arange(nlong):
328.                     Data_C[k,l]=max([-BMax,min([BMax,newmap[k,l]])])
329.         else:
330.             Data_C = newmap
331.         outputfile = save_bats(outputfile,StrHeader,NameVar,[nlong, nlat],
332.                                1,nParam, Param_I,Long_I,newlat,Data_C,
333.                                float(CRnumber)-int(float(CRnumber)))
334.     g.close()
335.     Time=  float(CRnumber) - Param_I[1] # Time since the CR starts
336.     # Long and Lat in radians passed to GLSetup.py
337.     Long_I = (pi/180.) * Long_I
338.     # in radians
339.     Lat_I = newlat * (pi/180.) # radians
340.     # Bmax = 1900
341.     return(nlong, nlat, nParam, Param_I, Long_I, Lat_I, newmap, out_grid, 
342.            mapdate,Time)
343. 
344. ###############CONSERVATIVE (ON SIN(THETA) UNIFORM GRID########
345. def smooth(nLong, nLat, nSmooth, Br_C):
346.     nSmooth2 = nSmooth//2
347.     Coef    = 1./(nSmooth*nSmooth)
348.     BrOrig_G = np.zeros([nLat,nLong+2*nSmooth2])
349.     for iLat in np.arange(nLat):
350.         BrOrig_G[iLat,:] = np.hstack((
351.                 Br_C[iLat,nLong-nSmooth2:nLong],
352.                 Br_C[iLat,:],Br_C[iLat,0:nSmooth2]))
353.     Br_C=np.zeros([nLat,nLong])
354.     for iLat in np.arange(nLat):
355.         for iLong in np.arange(nLong):
356.             for iSubLat in np.arange(nSmooth):
357.                 iLatExt  = iLat  + iSubLat  - nSmooth2
358.                 iLatExt  = max([-iLatExt-1,min(
359.                             [iLatExt, 2*nLat-1-iLatExt])])
360.                 Br_C[iLat,iLong] += np.sum(
361.                     BrOrig_G[iLatExt,iLong:iLong+nSmooth])
362.             Br_C[iLat,iLong]  *= Coef
363.     return(Br_C)
364. ##############################################################################
365. # function to read hmi fits file from awsom_script.py
366. def read_hmi(nlat,nlon,mapgrid,DoHMI):
367.     filenames=[]
368.     #pass the required mag size
369.     for file_name in os.listdir('.'):
370.         if fnmatch.fnmatch(file_name, 'hmi_*B*.fits'):
371.             print('Found HMI Synoptic Vector Mag : ',file_name)
372.             filenames.append(file_name)
373. 
374.     if (len(filenames) == 0):
375.         print('No HMI maps found, helicity will be calculated based on the hemisphere')
376.         IsPresentHMI = [0]
377.         return(IsPresentHMI)
378.     elif (len(filenames) != 3):
379.         print('Too many HMI magnetograms: Check input')
380.         return(-1)
381.     else:
382.         IsPresentHMI = 1
383.         for filename in filenames:
384.             if(fnmatch.fnmatch(filename,'*Br.fits')):
385.                 hmi_Br=remap(filename,'hmi.out',nlat,nlon,mapgrid,0,1,-1,1)
386.             elif(fnmatch.fnmatch(filename,'*Bt.fits')):
387.                 hmi_Bt=remap(filename,'hmi.out',nlat,nlon,mapgrid,0,1,-1,1)
388.             elif(fnmatch.fnmatch(filename,'*Bp.fits')):
389.                 hmi_Bp=remap(filename,'hmi.out',nlat,nlon,mapgrid,0,1,-1,1)
390. 
391. 
392.         hmi_nParam = hmi_Br[2]
393.         hmi_ParamI = hmi_Br[3]
394.         hmi_LongI = hmi_Br[4] * 180./pi
395.         hmi_LatI = hmi_Br[5] * 180./pi
396.         hmi_BrMap = hmi_Br[6]
397.         hmi_BlatMap = -hmi_Bt[6] #Blat = - Bt
398.         hmi_BlonMap = hmi_Bp[6]
399.    #SAVE HMI Br, Bt , Bp in Batsrus format
400.         fid = open('hmi_map.out','w')
401.         line0='MagnetogramType = HMI_Synoptic_Vector_Mag; InstrumentName ='\
402.             'SDO/HMI; InputLatGrid = '+mapgrid+'; MapResolution = '\
403.             +str(nlon)+','+str(nlat)+'\n'
404.         fid.write(line0)
405.         line0 = '       0      0.00000       2       2       3 \n'
406.         fid.write(line0)
407.         fid.write('      '+str(nlon)+'     '+str(nlat)+'\n')
408.         fid.write(str(hmi_ParamI[0]) + ' ' + str(hmi_ParamI[1]) + '\n')
409.         fid.write('Longitude Latitude Br Blon Blat LongShift CarringtonRot \n')
410.         for k in np.arange(nlat):
411.             for l in np.arange(nlon):
412.                 line0 = str(hmi_LongI[l]) + '  ' + str(hmi_LatI[k]) + '  ' \
413.                     + str(hmi_BrMap[k,l]) + '  ' + str(hmi_BlonMap[k,l]) +'  '\
414.                     + str(hmi_BlatMap[k,l]) + '\n'
415.                 fid.write(line0)
416.         fid.close()
417.     return(IsPresentHMI,hmi_LongI,hmi_LatI,hmi_BrMap,hmi_BlonMap,hmi_BlatMap)
418. ##############################################################################
419. def FITS_RECOGNIZE(inputfile, IsSilent=True):
420.     """
421.     This function opens inputfile and tries to determine what type of
422.     magnetogram it is as well as the type of grid on which the datatype is 
423.     represented.  The magnetogram types and grid types are: 
424.       Hathaway Synchronic, regular
425.       ADAPT Synchronic, regular 
426.       GONG Synoptic, sin(lat)
427.       GONG Hourly updated, sin(lat)
428.       MDI Synoptic, sin(lat)
429.       HMI Synoptic and PoleFilled
430.       HMI SuperSynthia Maps (from D. Fouhey)
431.     This function returns all required details from the header to remap.
432.        """
433. 
434.     magnetogram_type = 'unknown'
435.     grid_type = 'unknown'
436.     map_data = 'unknown'
437.     g = fits.open(inputfile)
438.     header0 = g[0].header
439.     try:
440.         naxis=header0['NAXIS']
441.     except KeyError as er:
442.         naxis = -1
443. 
444.     if naxis == 0:
445.         header0=g[1].header
446.         d = g[1].data
447.         try:
448.             nlo = g[1].header['NAXIS1']
449.         except KeyError as er:
450.             nlo = 0
451.         try:
452.             nla = g[1].header['NAXIS2']
453.         except KeyError as er:
454.             nla =0
455.         g[0].header = g[1].header
456.     else:
457.         header0=g[0].header
458.         d = g[0].data
459. 
460.     # Print out the headers if needed
461.     if not IsSilent:
462.         g.info()
463.         # print("====================================================\n")
464.         # print("Primary Extension Header:\n")
465.         # print(repr(header0))
466.         # print("====================================================\n")
467.     
468.     # Which telescope & instrument
469.     try:
470.         telescope = g[0].header['TELESCOP'] #works for MDI, GONG, HMI, SS
471.     except KeyError as er:
472.         telescope = 'unknown'
473. 
474.     try:
475.         inst = g[0].header['INSTRUME'] #works for MDI, HMI, SS
476.     except KeyError as er:
477.         inst = 'unknown'
478. 
479.     try:
480.         ctyp = g[0].header['CTYPE2'] #works for MDI, GONG, HMI, SS
481.     except KeyError as er:
482.         ctyp = 'unknown'
483. 
484.     try:
485.         cunit = g[0].header['CUNIT2'] #works for MDI, GONG, HMI, SS
486.     except KeyError as er:
487.        cunit = 'unknown'
488. 
489.     try:
490.         model = g[0].header['MODEL'] #works for ADAPT
491.     except KeyError as err:
492.         model = 'unknown'
493. 
494.     try:
495.         sft = g[0].header['SFT_TYP'] #works for Hathaway
496.     except KeyError as er:
497.         sft = 'unknown'
498. 
499.     if naxis > 0:
500.         try :
501.             nlo = g[0].header['NAXIS1'] #works on GONG, ADAPT, Syn HMI, MDI
502.         except KeyError as er:
503.             nlo = 0
504.         try :
505.             nla = g[0].header['NAXIS2']
506.         except KeyError as er:
507.             nla =0
508. 
509.     if telescope.find('SOLO/PHI/FDT')>-1:
510.         magnetogram_type='SOLO'
511.         try:
512.             long0=g[0].header['CRLN_OBS']
513.         except KeyError as er:
514.             long0 = -1
515.         try :
516.             CR = g[0].header['CAR_ROT'] #works on GONG and MDI
517.             CRnumber = CR
518.         except KeyError as er:
519.             CR = 0
520.         try:
521.             mapdate = g[0].header['DATE-OBS'] #works for GONG
522.         except Keyerror as er:
523.             mapdate = '0000-00-00T00:00:00'
524.         grid_type='uniform'
525. 
526.     if telescope.find('NSO-GONG') > -1 :
527.         # long at left edge
528.         try:
529.             long0 = g[0].header['LONG0']
530.         except KeyError as er:
531.             long0 = - 1
532.         # CR number
533.         try :
534.             CR = g[0].header['CAR_ROT'] #works on GONG and MDI
535.         except KeyError as er:
536.             CR = 0
537.         # CR at center of map
538.         try :
539.             CRnumber = g[0].header['CRNOW'] #works on GONG
540.             magnetogram_type = 'NSO-GONG Hourly'
541.         except KeyError as er:
542.             if float(long0) > 0.:
543.                 # Something goes wrong: this is not synoptic map,
544.                 # however, the carrington time is not present
545.                 magnetogram_type = 'NSO-GONG Hourly'
546.                 CRnumber = 0
547.             else:
548.                magnetogram_type = 'NSO-GONG Synoptic'
549.                # The Carrington time is the midtime of
550.                # the Carrington rotation:
551.                CRnumber=str(float(CR)+0.5)
552.         #Date
553.         try:
554.             mapdate = g[0].header['DATE'] #works for GONG
555.         except Keyerror as er:
556.             mapdate = '0000-00-00T00:00:00'
557.         #grid
558.         if ctyp.find('CRLT-CEA') > -1:
559.             grid_type = 'sin(lat)'            
560.             map_data = 'GONG'
561.         else:
562.             print ("unknown NSO-GONG magnetogram type")
563.             return(-1)
564. 
565.     if ( (telescope.find('SOHO') > -1) or (telescope.find('SoHO') > -1)):
566.         if ( (inst.find('MDI') > -1) & (ctyp.find('Sine Latitude') > -1
567.                                         or cunit.find('Sine Latitude')) > -1 ):
568.             magnetogram_type = 'MDI Synoptic'
569.             grid_type = 'sin(lat)'
570.             map_data = 'MDI'
571.             # CR number
572.             try :
573.                 CR = str(g[0].header['CAR_ROT']) #works on GONG and MDI
574.             except KeyError as er:
575.                 CR = 0
576.             # CR at center of map
577.             try :
578.                 CRnumber = str(2*float(CR)-float(g[0].header['CRVAL1'])/360.0)
579.             except KeyError as er:
580.                 CRnumber = '0'
581.             # long at left edge
582.             try:
583.                 long0 = g[0].header['LONG0']
584.             except KeyError as er:
585.                 long0 = 360*float(CR)-float(g[0].header['LON_LAST'])-180.0/nlo
586.             # Date
587.             try :
588.                 mapdate = g[0].header['T_OBS']  #works for MDI, HMI
589.             except KeyError as er:
590.                 mapdate = '0000-00-00T00:00:00'
591.         else:
592.             print ("unknown SoHO/MDI magnetogram type")
593.             return(-1)
594. 
595.     if telescope.find('SDO/HMI') > -1 :  # not HMI Pole filled or SuperSyn
596.         # CR number
597.         try :
598.             CR = str(g[0].header['CAR_ROT']) #works on GONG and MDI
599.         except KeyError as er:
600.             CR = 0
601.         # CR at center of map
602.         try :
603.             CRnumber = str(2*float(CR)-float(g[0].header['CRVAL1'])/360.0)
604.         except KeyError as er:
605.             CRnumber = '0'
606.         # long at left edge
607.         try:
608.             long0 = g[0].header['LONG0']
609.         except KeyError as er:
610.             long0 = 0
611.         try:
612.             long_last = g[0].header['LON_LAST']
613.             long0 = 360*float(CR)-float(g[0].header['LON_LAST'])-180.0/nlo
614.         except KeyError as er:
615.             long0 = 0  # for SuperSynthia
616.         # Date
617.         try :
618.             mapdate = g[0].header['T_OBS']  #works for MDI, HMI
619.         except KeyError as er:
620.             mapdate = '0000-00-00T00:00:00'
621. 
622.         if ( (ctyp.find('CRLT-CEA') > -1) ):
623.             if ((cunit.find('Sine Latitude') > -1) or cunit.find('sin(latitude)') > -1):
624.                 magnetogram_type = 'HMI Synoptic'
625.                 grid_type = 'sin(lat)'
626.                 map_data = 'HMI'
627. 
628.             if naxis ==0 :
629.                 map_data = 'HMI PolFill'
630.                 magnetogram_type = 'HMI Syn PolFill'
631.                 grid_type = 'sin(lat)'
632.                 
633.         if naxis == 0 and inst == 'HMI_COMBINED':
634.             map_data = 'HMI SuperSynthia'
635.             magnetogram_type = 'HMI SuperSynthia'
636.             grid_type = 'uniform'
637.             CRnumber = '0'
638.         if map_data == 'unknown':
639.             print ("unknown SDO magnetogram type")
640.             return(-1)
641. 
642.     if model.find('ADAPT') > -1:
643.         magnetogram_type ='ADAPT Synchronic'
644.         try:
645.             adapt_grid = g[0].header['GRID']
646.         except KeyError as er:
647.             adapt_grid = -1.
648.         if adapt_grid == 1.:
649.             grid_type = 'uniform'
650.         else:
651.             print ("unknown ADAPT magnetogram type")
652.             return(-1)
653.         # data type
654.         try:
655.             map_data = str(g[0].header['MAPDATA']) #works for ADAPT
656.         except KeyError as er:
657.             map_data = ' '
658.         # CRcenter and CR
659.         try:
660.             CRnumber = str(g[0].header['MAPCR']) #works for ADAPT-Center of CM 
661.             CR = str(int(g[0].header['MAPCR']))  #works for ADAPT
662.         except KeyError as er:
663.             CRnumber = '0'
664.         # Long at left edge
665.         try :
666.             long0 = g[0].header['CRLNGEDG']   #works on ADAPT
667.         except KeyError as er:
668.             long0 = 0
669.         # Map date
670.         try:
671.             mapdate = g[0].header['MAPTIME']  #works for ADAPT
672.         except KeyError as er:
673.             mapdate = '0000-00-00T00:00:00'
674. 
675.     # Fits files from HMI have a header with limited number of keywords.
676.     # Those limited keywords are not sufficient enough to provide informatoins
677.     # that FITS_RECOGNIZE() wants to read.
678.     # Therefore you can manually set those necessay parameters in this if
679.     # statement
680.     if inputfile == 'hmi_test_fits':
681.         magnetogram_type = 'HMI Synoptic'
682.         map_data ='PolFill'
683.         grid_type = 'sin(lat)'
684.         nlo = 3600
685.         nla = 1440
686.         cunit = 'Sine Latitude'
687.         CRnumber = '2261'
688.         CR = '2261'
689.         long0 = '0.0'
690.         mapdate = '2022-09-05T16:00:00Z'
691.                     
692. ## Common for all
693. # Bunit
694.     try:
695.         bunit = g[0].header['BUNIT']  #works on GONG, MDI
696.     except KeyError as er:   #Hathaway and ADAPT don't list units
697.         bunit = 'Gauss'  #assume it's Gauss if you don't know
698. 
699.     if sft.find('Baseline / Assimilation') > -1:
700.         magnetogram_type = 'Hathaway Synchronic'
701.         grid_type = 'uniform'
702.         try :
703.             mapdate = g[0].header['MAP_DATE']  #works for Hathaway
704.         except KeyError as er:
705.             mapdate = '0000-00-00T00:00:00'
706. 
707.     if  ( (magnetogram_type == 'unknown') or (grid_type == 'unknown') ):
708.         print ("I don't recognize the type of this magnetogram.")
709.         return(-1)
710. 
711.     g.close()                
712. 
713.     if not IsSilent:
714.         print()
715.         if (naxis == -1):
716.             print ("I think this is a",magnetogram_type,"magnetogram on a",\
717.                    str(nla),"X",str(nlo),grid_type,"grid.")
718.         else:
719.             print ("I think this is a",magnetogram_type,"magnetogram on a",\
720.                    str(nla),"X",str(nlo),grid_type,"grid.")
721.             
722.     return( (magnetogram_type, grid_type, map_data, nlo, nla, CRnumber, CR, long0, bunit, mapdate) )
723. 
724. def read_bats(inputfile):
725.     """
726.     This function opens inputfile in the form it is produced by ModPlotFile
727.     and reads data and parameters in Python foormat.
728.     """
729.     f = open(inputfile,'r')
730.     # Header line
731.     StrHeader=f.readline()[:-1]
732.     print(StrHeader)
733.     # Second line
734.     string=f.readline()
735.     array=string.split()
736.     nDim = int(array[2])
737.     if nDim != 2:
738.         print('nDim = '+str(nDim)+' is not equal to 2, table cannot be read')
739.         exit()
740.     Time = float(array[1])
741.     print('Time = '+str(Time))
742.     nParam = int(float(array[3]))
743.     print('nParam = '+str(nParam))
744.     nVar = int(float(array[4]))
745.     print('nVar = '+str(nVar))
746.     # Third line
747.     string=f.readline()
748.     nIndex_I=[int(x) for  x in string.split()]
749.     print('nIndex_I = '+str(nIndex_I))
750.     # Fourth line
751.     string=f.readline()
752.     Param_I=[float(x) for  x in string.split()]
753.     print('Param_I = '+str(Param_I))
754.     # Fifth line
755.     NameVar=f.readline()[:-1]
756.     print(NameVar)
757.     # Allocate data arrays
758.     Coord1_I = np.zeros(nIndex_I[0])
759.     Coord2_I = np.zeros(nIndex_I[1])
760.     if  nVar ==1:
```

</details>


---

<sub>⏱️ 1m 59s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/get_magnetogram.py.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/get_magnetogram.py (lines 1-420)

<details>
<summary>108 lines</summary>

```
1. #!/usr/bin/env python3
2. ############ Prototype: make_submission.py by Maksym Petrenko
3. ############ CMERAL modification of make_submission.py
4. ############ 30/11/2022
5. ############ This python script correspond to a part of the make_submission.py
6. ############ that only download the latest GONG magnetogram for realtime
7. ############ simulation in the run directory as fitsfile.fits
8. ###############################################################################################################
9. 
10. from html.parser import HTMLParser
11. import requests
12. import re
13. import os
14. import shutil
15. import gzip
16. import argparse
17. 
18. ISWA_DATA_URL = 'https://iswaa-webservice1.ccmc.gsfc.nasa.gov/iswa_data_tree/observation/solar/gong/mrzqs/'
19. 
20. #modify to change the output directory (run_realtime directory used for realtime simulations)
21. OUTPUT_BASE_PATH = os.getcwd()
22. 
23. HEADERS = {"User-Agent":"Mozilla/5.0 (Macintosh Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"}
24. 
25. 
26. class LinkScrape(HTMLParser):
27.     def reset(self):
28.         super().reset()
29.         self.links = []
30.         self.in_link = False
31.     def handle_starttag(self, tag, attrs):
32.         self.in_link = False
33.         if tag == 'a':
34.             self.in_link = True
35.             for (name, value) in attrs:
36.                 if name == 'href':
37.                     self.links.append({'href': value})
38.     def handle_endtag(self, attrs):
39.         self.in_link = False
40.     def handle_data(self, data):
41.         if self.in_link: self.links[-1]['text'] = data
42.     def clean(self):
43.         self.links = []
44. 
45. def get_highest(page_url, pattern, datetime):
46.     response = requests.get(page_url)
47.     page_html = response.text
48.     link_parser = LinkScrape()
49.     link_parser.feed(page_html)
50.     links = link_parser.links
51.     link_parser.clean()
52. 
53. 
54.     last_match = ''
55.     lats_link = ''
56.     last_text = ''
57.     for link in links:
58.         original_url = link['href']
59.         text = link['text']
60.         matches = re.search(pattern, text)
61.         if (matches):
62.             if (matches.group(1) > last_match and matches.group(1)<=datetime):
63.                 last_match = matches.group(1)
64.                 lats_link = original_url
65.                 last_text = text
66.     return [last_match, last_text, lats_link]
67. 
68. def download_file(url, save_path):
69.     try:
70.         # Send GET request to the URL
71.         response = requests.get(url)
72.         # Check if the request was successful (status code 200)
73.         if response.status_code == 200:
74.             # Write the content of the response to a local file
75.             with open(save_path, 'wb') as file:
76.                 file.write(response.content)
77.             print(f"File downloaded successfully: {save_path}")
78.         else:
79.             print(f"Failed to download file. Status code: {response.status_code}")
80.     except Exception as e:
81.         print(f"Error: {e}")
82. 
83. if __name__ == '__main__':
84. 
85.     parser = argparse.ArgumentParser(description=
86.                                      "Use python3 get_magnetogram.py datetime")
87.     parser.add_argument('datetime', help=
88.                         "Date_Time in the format yymmdd't'hhmm")
89.     args = parser.parse_args()
90.     datetime = str(args.datetime)
91.     matches=re.search(r'(\d\d\d\d\d\dt\d\d\d\d)',datetime)
92.     year = '20'+matches.group(1)[0:2]
93.     month = matches.group(1)[2:4]
94.     month_url = ISWA_DATA_URL.rstrip('/')+'/'+\
95.         str(year)+'/'+str(month)+'/'
96.     [cr, text, link] = get_highest(
97.         month_url,r'(\d\d\d\d\d\dt\d\d\d\d)',matches.group(1))
98.     granule_url = month_url.rstrip('/') + '/' + link
99.     print("granule_url="+granule_url)
100.     # Adjust input files
101.     fits_file = os.path.join(OUTPUT_BASE_PATH, "fitsfile.fits")
102.     fits_file_gz = os.path.join(OUTPUT_BASE_PATH,str(link))
103.     download_file(granule_url,fits_file_gz)
104.     with gzip.open(fits_file_gz, 'rb') as f_in:
105.         with open(fits_file, 'wb') as f_out:
106.             shutil.copyfileobj(f_in, f_out)
107.     os.unlink(fits_file_gz)
108.
```

</details>


---

<sub>⏱️ 1m 59s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/download_ADAPT.py.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/download_ADAPT.py (lines 1-260)

<details>
<summary>101 lines</summary>

```
1. #!/usr/bin/env python3
2. 
3. from ftplib import FTP
4. import gzip
5. import shutil
6. import math
7. import sys
8. import datetime as dt
9. 
10. def download_ADAPT_magnetogram(timeIn, NameTypeMap='fixed'):
11.     '''
12.     This routine reads the date and type infomration from the command 
13.     line and download the corresponding ADAPT map.
14.     '''
15. 
16.     if NameTypeMap == 'fixed':
17.         StrTypeMap = '0'
18.     elif NameTypeMap == 'central':
19.         StrTypeMap = '1'
20.     else:
21.         raise ValueError('Unrecognized type of ADAPT map: '+NameTypeMap)
22. 
23.     # ADAPT maps only contains the hours for even numbers
24.     if timeIn.hour%2 != 0:
25.         timeIn = timeIn.replace(hour=math.floor(timeIn.hour/2)*2)
26.         print('Warning: Hour must be an even number. '
27.               +'The entered hour value is changed to ', timeIn.hour)
28. 
29.     # Go to the the ADAPT ftp server
30.     ftp=FTP('gong2.nso.edu')
31.     ftp.login()
32.     
33.     # Only ADAPT GONG is considered
34.     ftp.cwd('adapt/maps/gong')
35. 
36.     # Go to the specific year
37.     try:
38.         ftp.cwd(str(timeIn.year))
39.     except:
40.         sys.exit('******************************************************************\n' 
41.                  + 'Year not found on the ftp server: '+str(timeIn.year) + '.\n'
42.                  + 'Check ftp://gong2.nso.edu/adapt/maps/gong in the corresponding \n'
43.                  + 'year to see whether it provides a map.\n'
44.                  + '******************************************************************\n')
45. 
46.     # Only consider the public (4) Carrington Fixed (0) GONG (3) ADAPT maps
47.     patten = 'adapt4'+StrTypeMap+'3*' + str(timeIn.year).zfill(4) + \
48.         str(timeIn.month).zfill(2) + str(timeIn.day).zfill(2)     + \
49.         str(timeIn.hour).zfill(2)  + '*'
50.     
51.     filenames = ftp.nlst(patten)
52.     
53.     if len(filenames) < 1:
54.         sys.exit('******************************************************************\n' 
55.                  + 'File not found on the ftp server with the patten: '+patten + '.\n'
56.                  + 'Try another even hour within 24 hours range of the desired time.\n'
57.                  + 'Or check ftp://gong2.nso.edu/adapt/maps/gong in the corresponding \n'
58.                  + 'year/month/day to see whether it provides a map.\n'
59.                  + '******************************************************************\n')
60.     
61.     for ifile, filename in enumerate(filenames):
62.         # open the file locally
63.         fhandle=open(filename, 'wb')
64.         
65.         # try to download the magnetogram
66.         try:
67.             ftp.retrbinary('RETR '+ filename, fhandle.write)
68.         except:
69.             sys.exit('Cannot download '+filename)
70.         
71.         # close the file
72.         fhandle.close()
73. 
74.         #unzip the file
75.         if '.gz' in filename:
76.             filename_unzip = filename.replace('.gz','')
77.             with gzip.open(filename, 'rb') as s_file, \
78.                 open(filename_unzip, 'wb') as d_file:
79.                     shutil.copyfileobj(s_file, d_file, 65536)
80.             filenames[ifile]=filename_unzip
81.     
82.     ftp.quit()
83. 
84.     return filenames
85. 
86. if __name__ == '__main__':
87. 
88.     yyyy = int(input('Enter year: ' ))
89.     mm   = int(input('Enter month: '))
90.     dd   = int(input('Enter day: '  ))
91.     hh   = int(input('Enter hour: ' ))
92. 
93.     StrTime = str(yyyy).zfill(4)+'-'+str(mm).zfill(2)+'-' \
94.         +str(dd).zfill(2)+'T'+str(hh).zfill(2)
95. 
96.     timeIn = dt.datetime.strptime(StrTime,"%Y-%m-%dT%H")
97. 
98.     NameTypeMap = input('Type of ADAPT maps: fixed or central?  ')
99. 
100.     download_ADAPT_magnetogram(timeIn,NameTypeMap)
101.
```

</details>


---

<sub>⏱️ 1m 59s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py (lines 1-320)

<details>
<summary>225 lines</summary>

```
1. #!/usr/bin/env python3
2. 
3. import argparse
4. import datetime as dt
5. import sys
6. import subprocess
7. import warnings
8. import change_param
9. from remap_magnetogram import FITS_RECOGNIZE
10. import download_ADAPT
11. 
12. # -----------------------------------------------------------------------------
13. def change_param_local(time, map, pfss, scheme=2, poynting_flux=-1.0, new_params={},
14.                        DoUseMarker=0,DoRestart=0):
15. 
16.     params_pfss = ['CHANGEWEAKFIELD', 'BrFactor', 'BrMin', 'nHarmonics']
17. 
18.     if 'change' in new_params.keys():
19.         # need to turn on CHANGEWEAKFIELD if BrFactor and/or BrMin are changed
20.         if 'BrFactor' in new_params['change'].keys() or 'BrMin' in new_params['change'].keys():
21.             if 'add' in new_params.keys():
22.                 new_params['add']=new_params['add']+',CHANGEWEAKFIELD'
23.             else:
24.                 new_params['add']='CHANGEWEAKFIELD'
25. 
26.         # need to turn on FACTORB0 if FactorB0 is changed
27.         if 'FactorB0' in new_params['change'].keys():
28.             if 'add' in new_params.keys():
29.                 new_params['add']=new_params['add']+',FACTORB0'
30.             else:
31.                 new_params['add']='FACTORB0'
32. 
33.         # well, for 5th order scheme, there is a 0.02 thick layer above rMin for AWSoM-R
34.         if 'rMin_AWSoMR' in new_params['change'].keys():
35.             new_params['change']['rMaxLayer_AWSoMR'] = float(new_params['change']['rMin_AWSoMR']) + 0.02
36. 
37.     # set the PFSS solver, FDIPS or Harmonics
38.     # If it is HARAMONICS, no need to change as HARMONICS is the default
39.     if (pfss == 'FDIPS'):
40.         if 'add' in new_params.keys():
41.             new_params['add']=new_params['add']+',LOOKUPTABLE(FDIPS)'
42.         else:
43.             new_params['add']='LOOKUPTABLE(FDIPS)'
44.         if 'rm' in new_params.keys():
45.             new_params['rm'] =new_params['rm']+',HARMONICSFILE,HARMONICSGRID' 
46.         else:
47.             new_params['rm'] = 'HARMONICSFILE,HARMONICSGRID'
48.     elif pfss not in ['FDIPS','HARMONICS']:
49.         raise ValueError(pfss + ' must be either FDIPS')
50. 
51.     # for 5th order scheme
52.     if scheme == 5:
53.         if 'rm'in new_params.keys():
54.             new_params['rm'] =new_params['rm']+',END(END_2nd_scheme)'
55.         else:
56.             new_params['rm'] ='END(END_2nd_scheme)'
57. 
58.     new_params_pfss = {}
59. 
60.     # key1 could be change, add, rm, replace
61.     for key1 in list(new_params.keys()):
62.         if key1 in ['change','replace']:
63.             # another dict for ['change','replace']
64.             for key2 in list(new_params[key1].keys()):
65.                 if key2 in params_pfss:
66.                     if key1 not in new_params_pfss.keys():
67.                         new_params_pfss[key1]={key2:new_params[key1][key2]}
68.                     else:
69.                         new_params_pfss[key1][key2] = new_params[key1][key2]
70.                     # delete the entry found in params_pfss
71.                     new_params[key1].pop(key2,None)
72.         elif key1 in ['add','rm']:
73.             # a string for ['add','rm']
74.             commands_local = new_params[key1]
75.             commands_list_local = commands_local.split(',')
76.             commands_list_pfss  = []
77. 
78.             for i in range(len(commands_list_local)):
79.                 if commands_list_local[i] in params_pfss:
80.                     commands_list_pfss.append(commands_list_local[i])
81.                     commands_list_local[i] = ''
82. 
83.             # remove '' in the list
84.             if '' in commands_list_local:
85.                 commands_list_local.remove('')
86. 
87.             if len(commands_list_local) == 0:
88.                 # remove the key if the list of the string is empty (for PARAM.in)
89.                 new_params.pop(key1,None)
90.             else:
91.                 new_params[key1] = ','.join(commands_list_local)
92. 
93.             # if the list of the string for the pfss is not empty, add the entry
94.             if len(commands_list_pfss) > 0:
95.                 new_params_pfss[key1] = ','.join(commands_list_pfss)
96. 
97.     if time != 'MapTime':
98.         # TIME is given with the correct format
99.         time_input = dt.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")
100.         time_param = time.replace('-',',').replace('T',',').replace(':',',')
101. 
102.     if (map == 'NoMap'):
103.         if time != 'MapTime':
104.             # Download the ADAPT magnetogram if no map is pvoided
105.             # default 'fixed', note that the time_input is correctly set.
106.             filename_map = download_ADAPT.download_ADAPT_magnetogram(time_input)[0]
107.             print("download the map as: ", filename_map)
108.         else:
109.             raise ValueError('No map is provided. Please provide the time '
110.                              + 'by -t/--time to download the ADAPT map.')
111.     else:
112.         # The ADAPT map is provied
113.         filename_map = map
114.         
115.         map_local  = FITS_RECOGNIZE(map)
116.         time_map   = dt.datetime.strptime(map_local[9], "%Y-%m-%dT%H:%M:%S")
117. 
118.         # Very weird GONG Synoptic map, the map time is a few days after the end of the CR.
119.         # Use an approximation to get the time corresponding to the central meridian
120.         if (map_local[0] == 'NSO-GONG Synoptic'):
121.             CR_number = float(map_local[6])
122.             time_map = dt.datetime(1853, 11, 9) + dt.timedelta(days=27.2753*(CR_number-0.5))
123. 
124.         if time == 'MapTime':
125.             # if the user does not provide the time, then set the time based
126.             # on the time info from the ADAPT map.
127.             time_param = (str(time_map.year)   + ',' + str(time_map.month) + ',' +
128.                           str(time_map.day)    + ',' + str(time_map.hour)  + ',' +
129.                           str(time_map.minute) + ',' + str(time_map.second))
130. 
131.     # Need to add the msc
132.     time_param = time_param+',0.0'
133. 
134.     # set #STARTTIME
135.     if 'replace' in new_params.keys():
136.         new_params['replace']['STARTTIME']=time_param
137.     else:
138.         new_params['replace'] = {'STARTTIME':time_param}
139. 
140.     if DoRestart:
141.         if 'replace' in new_params.keys():
142.             if 'STARTTIME' in new_params['replace']:
143.                 new_params['replace'].pop('STARTTIME',None)
144. 
145.     if poynting_flux > 0:
146.         # set #POYNTINGFLUX
147.         if 'replace' in new_params.keys():
148.             new_params['replace']['POYNTINGFLUX']='{:<10.3e}'.format(poynting_flux)
149.         else:
150.             new_params['replace']={'POYNTINGFLUX':'{:<10.3e}'.format(poynting_flux)}
151. 
152.     if 'add' in new_params.keys():
153.         commands_add=new_params['add']
154.         change_param.add_commands(commands_add, DoUseMarker=DoUseMarker)
155. 
156.     if 'add' in new_params_pfss.keys():
157.         commands_add=new_params_pfss['add']
158.         change_param.add_commands(commands_add, DoUseMarker=DoUseMarker, filenameIn=pfss+'.in', filenameOut=pfss+'.in')
159. 
160.     if 'rm' in new_params.keys():
161.         commands_rm=new_params['rm']
162.         change_param.remove_commands(commands_rm, DoUseMarker=DoUseMarker)
163. 
164.     if 'rm' in new_params_pfss.keys():
165.         commands_rm=new_params_pfss['rm']
166.         change_param.remove_commands(commands_rm, DoUseMarker=DoUseMarker, filenameIn=pfss+'.in', filenameOut=pfss+'.in')
167. 
168.     if 'replace' in new_params.keys():
169.         DictReplace = new_params['replace']
170.         change_param.replace_commands(DictReplace, DoUseMarker=DoUseMarker)
171. 
172.     if 'replace' in new_params_pfss.keys():
173.         DictReplace = new_params_pfss['replace']
174.         change_param.replace_commands(DictReplace, DoUseMarker=DoUseMarker, filenameIn=pfss+'.in', filenameOut=pfss+'.in')
175. 
176.     if 'change' in new_params.keys():
177.         DictChange  = new_params['change']
178.         change_param.change_param_value(DictChange, DoUseMarker=DoUseMarker)
179. 
180.     if 'change' in new_params_pfss.keys():
181.         DictChange  = new_params_pfss['change']
182.         change_param.change_param_value(DictChange, DoUseMarker=DoUseMarker, filenameIn=pfss+'.in', filenameOut=pfss+'.in')
183. 
184.     # prepare each realization map.
185.     str_exe = str('Scripts/remap_magnetogram.py ' + filename_map)
186. 
187.     subprocess.call(str_exe, shell=True)
188. 
189. # =============================================================================
190. if __name__ == '__main__':
191. 
192.     # Program initiation
193.     PROG_DESCRIPTION = ('Script to change PARAM.in if needed and '
194.                         + ' automatically download the ADAPT map.')
195.     ARG_PARSER = argparse.ArgumentParser(description=PROG_DESCRIPTION)
196.     ARG_PARSER.add_argument('-p', '--poynting_flux',
197.                             help='(default: -1.0 J/m^2/s/T)',
198.                             type=float, default=-1)
199.     ARG_PARSER.add_argument('-t', '--time',
200.                             help='(default: MapTime)'
201.                             + 'Use if you want to overwrite PARAM.in time.'
202.                             + ' Format: yyyy-mm-ddThh:min:sec',
203.                             type=str, default='MapTime')
204.     ARG_PARSER.add_argument('-B0', '--pfss',
205.                             help='(default: HARMONICS.)'
206.                             + ' Use if you want to specify the PFSS solver.',
207.                             type=str, default='HARMONICS')
208.     ARG_PARSER.add_argument('-m', '--map',
209.                             help='(default: NoMap)'
210.                             + ' Use if you want to specify the ADAPT map.',
211.                             type=str, default='NoMap')
212.     ARG_PARSER.add_argument('-param', '--parameters',
213.                             help='(default: {})' +
214.                             ' Use if you want to change the values of the'
215.                             + ' parameters.',
216.                             type=list)
217.     ARG_PARSER.add_argument('--DoRestart',
218.                             help='(default: 0)' +
219.                             ' Use if it is a restart run.',
220.                             type=int)
221.     ARGS = ARG_PARSER.parse_args()
222. 
223.     change_param_local(time=ARGS.time, map=ARGS.map, pfss=ARGS.pfss,
224.                        poynting_flux=ARGS.poynting_flux, DoUseMarker=0, DoRestart=ARGS.DoRestart)
225.
```

</details>


---

<sub>⏱️ 2m 7s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/sub_runs.py.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/sub_runs.py (lines 1-420)

<details>
<summary>363 lines</summary>

```
1. #!/usr/bin/env python3
2. 
3. import sys
4. import array
5. import change_param
6. import change_awsom_param
7. import subprocess
8. import argparse
9. import os
10. import warnings
11. import re
12. import glob
13. import shutil
14. import shlex
15. 
16. # -----------------------------------------------------------------------------
17. def set_dict_params(list_params,NewParam,MAP,PFSS,TIME,MODEL,PARAM,SCHEME,strRealizations):
18. 
19.     for param in list_params:
20.         paramTmp = param.split('=')
21.         if paramTmp[0].lower()   == 'map':
22.             MAP  = paramTmp[1]
23.             if 'adapt' in MAP.lower():
24.                 REALIZATIONS = [x for x in range(1,13)]
25.                 TypeMap      = 'ADAPT'
26.             elif 'gong' in MAP.lower():
27.                 REALIZATIONS = [1]
28.                 TypeMap      = 'GONG'
29.             else:
30.                 raise ValueError(MAP, ': unknown map type.')
31.             if not strRealizations.strip():
32.                 ListStrRealizations = [str(iRealztion)
33.                                        for iRealztion in REALIZATIONS]
34.                 strRealizations = ",".join(ListStrRealizations)
35.         elif paramTmp[0].lower() == 'pfss':
36.             PFSS = paramTmp[1]
37.         elif paramTmp[0].lower() == 'time':
38.             TIME = paramTmp[1]
39.         elif paramTmp[0].lower() == 'model':
40.             MODEL= paramTmp[1]
41.         elif paramTmp[0].lower() == 'scheme':
42.             SCHEME = int(paramTmp[1])
43.         elif paramTmp[0].lower() == 'param':
44.             PARAM  = paramTmp[1]
45.         elif paramTmp[0].lower() == 'realization':
46.             strTmp  = paramTmp[1][1:-1]
47.             ListRealizationTmp = strTmp.split(',')
48.             REALIZATIONS = []
49.             for StrRealiaztion in ListRealizationTmp:
50.                 try:
51.                     # try to convert it to an integer
52.                     Realization = int(StrRealiaztion)
53.                     REALIZATIONS.append(Realization)
54.                 except:
55.                     # cannot convert to an integer as there is '-'
56.                     ListTmp = StrRealiaztion.split('-')
57.                     try:
58.                         REALIZATIONS.extend([x for x in range(int(ListTmp[0]),
59.                                                               int(ListTmp[1])+1)])
60.                     except Exception as error:
61.                         raise TypeError(error," wrong format: could only contain "
62.                                         + "integer, ',' and '-'.")
63.             ListStrRealizations = [str(iRealztion)
64.                                    for iRealztion in REALIZATIONS]
65.             strRealizations = ",".join(ListStrRealizations)
66.         elif paramTmp[0].lower() == 'realizations' or paramTmp[0].lower() == 'restartdir':
67.             continue
68.         elif paramTmp[0] == 'add' or paramTmp[0] == 'rm':
69.             if not paramTmp[0] in NewParam.keys():
70.                 NewParam[paramTmp[0]] = paramTmp[1]
71.             else:
72.                 NewParam[paramTmp[0]] = NewParam[paramTmp[0]]+','+paramTmp[1]
73.         elif paramTmp[1][0] == '[' and paramTmp[1][-1] == ']':
74.             if not 'replace' in NewParam.keys():
75.                 NewParam['replace'] = {paramTmp[0]:paramTmp[1][1:-1]}
76.             else:
77.                 NewParam['replace'][paramTmp[0]] = paramTmp[1][1:-1]
78.         else:
79.             if paramTmp[0] == 'GridResolution':
80.                 continue
81.             if not 'change' in NewParam.keys():
82.                 NewParam['change']  = {paramTmp[0]:paramTmp[1]}
83.             else:
84.                 NewParam['change'][paramTmp[0]] = paramTmp[1]
85. 
86.     return NewParam,MAP,PFSS,TIME,MODEL,PARAM,SCHEME,strRealizations
87. 
88. # -----------------------------------------------------------------------------
89. def set_restart_params(RestartDirIn,NewParam,MAP,PFSS,TIME,MODEL,PARAM,SCHEME,strRealizations):
90.     # use patten search to find, RestartDirIn does not need to be the full name
91.     filenameKeyparams = glob.glob('Results/' + RestartDirIn+'*/key_params.txt')[0]
92.     with open(filenameKeyparams, 'r') as file_keyparams:
93.         lines_keyparams = list(file_keyparams)
94. 
95.     for iLine, line in enumerate(lines_keyparams):
96.         # remove the /n in the .txt file...
97.         lines_keyparams[iLine] = line.strip()
98.         # the string for the realizations is saved...
99.         if 'realizations' in line.lower():
100.             strRealizationsRestart = line.strip().split('=')[1]
101.         else:
102.             strRealizationsRestart = ''
103.         if 'restartdir' in line.lower():
104.             # remove /n with strip() and then RestartDir is the second element after split
105.             RestartDirLocal  = line.strip().split('=')[1]
106.             NewParam,MAP,PFSS,TIME,MODEL,PARAM,SCHEME,strRealizations = \
107.                 set_restart_params(RestartDirLocal, NewParam,MAP,PFSS,TIME,MODEL,PARAM,SCHEME,strRealizations)
108. 
109.     # set the params based on the key_params.txt
110.     NewParam,MAP,PFSS,TIME,MODEL,PARAM,SCHEME,strRealizations = \
111.         set_dict_params(lines_keyparams,NewParam,MAP,PFSS,TIME,MODEL,PARAM,SCHEME,strRealizations)
112. 
113.     if strRealizationsRestart.strip():
114.         strRealizations=strRealizationsRestart
115. 
116.     return NewParam,MAP,PFSS,TIME,MODEL,PARAM,SCHEME,strRealizations
117.     
118. # -----------------------------------------------------------------------------
119. if __name__ == '__main__':
120. 
121.     PROG_DESCRIPTION = ('Script to submit jobs selected from a file.')
122.     ARG_PARSER = argparse.ArgumentParser(description=PROG_DESCRIPTION)
123.     ARG_PARSER.add_argument('-f', '--filename',
124.                             help='(default:param_list.txt)',
125.                             type=str, default='param_list.txt')
126.     ARG_PARSER.add_argument('-c', '--DoCompile',
127.                             help='(default: 1)'
128.                             + 'Use if you want to re-install and compile '
129.                             + 'the code.', 
130.                             type=int, default=1)
131.     ARG_PARSER.add_argument('-l', '--DoLink',
132.                             help='(default: 1)'
133.                             + 'Use if you want to link the restart '
134.                             + 'files only.',
135.                             type=int, default=0)
136.     ARG_PARSER.add_argument('-m', '--DoUseMarker',
137.                             help='(default: 1)'
138.                             + 'Use if you want to use the marker ^ for'
139.                             + 'changing the PARAM.in file.',
140.                             type=int, default=1)
141.     ARG_PARSER.add_argument('-r', '--DoSubRun',
142.                             help='(default: 1)'
143.                             + 'Use if you want to submit runs',
144.                             type=int, default=1)
145.     ARG_PARSER.add_argument('-t', '--ThresholdBrPoynting',
146.                             help='(default: -1.0)'
147.                             + 'Use if you want to set the Threshold for'
148.                             + 'BrFactor*PoyntingFlux',
149.                             type=float, default=-1.0)
150.     ARGS = ARG_PARSER.parse_args()
151. 
152.     # whether to reinstall the code
153.     DoInstall = True
154. 
155.     with open(ARGS.filename, 'rt') as events:
156.         lines = list(events)
157. 
158.     for iLine, line in enumerate(lines):
159.         if 'selected run IDs' in line[0:16]:
160.             iSelectedID=iLine
161.         if '#START' in line[0:6]:
162.             iParamStart=iLine+2
163.             break
164.         
165.     # find the location of =
166.     iChar  = lines[iSelectedID].find('=')
167. 
168.     # any character after = is considered to be the string containing 
169.     # run IDs.
170.     StrRunIDs = lines[iSelectedID][iChar+1:]
171. 
172.     # split the string
173.     List_StrRunIDs = StrRunIDs.split(',')
174. 
175.     RunIDs = []
176. 
177.     # loop through List_StrRunIDs to get the list of run IDs in an integer list
178.     for StrRunID in List_StrRunIDs:
179.         try:
180.             # try to convert it to an integer
181.             RunID = int(StrRunID)
182.             RunIDs.append(RunID)
183.         except:
184.             # cannot convert to an integer as there is '-'
185.             ListTmp = StrRunID.split('-')
186.             try:
187.                 RunIDs.extend([x for x in range(int(ListTmp[0]),
188.                                                 int(ListTmp[1])+1)])
189.             except Exception as error:
190.                 raise TypeError(error," wrong format: could only contain "
191.                                 + "integer, ',' and '-'.")
192. 
193.     params_I =[]
194. 
195.     for iLine, line in enumerate(lines[iParamStart:]):
196.         if line.strip():
197.             # preserve the white space within ''
198.             param_now = shlex.split(line.strip())
199.             # this will preserve the white space within []
200.             # param_now    = re.split(r'\s+(?![^[\]]*])', line.strip())
201. 
202.             # the first element is always an inter representing the run ID.
203.             param_now[0] = int(param_now[0])
204.             params_I.append(param_now)
205. 
206.     for iID, params in enumerate(params_I):
207.         # if the run ID is found in the selected run ID.
208. 
209.         if params[0] in RunIDs:
210.             RunID = params[0]
211. 
212.             # reset all the default values
213.             MAP   = 'NoMap'
214.             PFSS  = 'HARMONICS'
215.             TIME  = 'MapTime'
216.             MODEL = 'AWSoM'
217.             PARAM = 'Default'
218.             SCHEME= 2
219.             DoRestart = 0
220. 
221.             NewParam        = {}
222.             strRealizations = ''
223. 
224.             # check whether restartdir exists, if yes, set the params first.
225.             for param in params[1:]:
226.                 if 'restartdir=' in param.lower():
227.                     DoRestart   = 1
228.                     # remove /n with strip() and then RestartDir is the second element after split
229.                     RestartDir  = param.strip().split('=')[1]
230.                     NewParam,MAP,PFSS,TIME,MODEL,PARAM,SCHEME,strRealizations = \
231.                         set_restart_params(RestartDir,NewParam,MAP,PFSS,TIME,MODEL,PARAM,SCHEME,strRealizations)
232. 
233.             # the actual param starts from the 2nd element
234.             NewParam,MAP,PFSS,TIME,MODEL,PARAM,SCHEME,strRealizations = \
235.                 set_dict_params(params[1:],NewParam,MAP,PFSS,TIME,MODEL,PARAM,SCHEME,strRealizations)
236. 
237.             if ARGS.ThresholdBrPoynting > 0:
238.                 BrFactor_local     = float(NewParam['change']['BrFactor'])
239.                 PoyntingFlux_local = float(NewParam['change']['PoyntingFluxPerBSi'])
240.                 if BrFactor_local*PoyntingFlux_local > ARGS.ThresholdBrPoynting:
241.                     warnings.warn('For run ID: '+str(RunID).zfill(3) + '\n'
242.                                   +'BrFactor           ='+str(BrFactor_local)           + '\n'
243.                                   +'PoyntingFluxPerBSi ='+str(PoyntingFlux_local) + '\n'
244.                                   +'BrFactor*PoyntingFluxPerBSi ='+str(BrFactor_local*PoyntingFlux_local) + '\n'
245.                                   +'BrFactor*PoyntingFluxPerBSi >'+str(ARGS.ThresholdBrPoynting))
246.                     continue
247. 
248.             SIMDIR = ('run' + str(RunID).zfill(3) + '_' + MODEL)
249. 
250.             if DoRestart:
251.                 SIMDIR = SIMDIR+'_restart_'+RestartDir.replace('/','_')
252. 
253.             # if ARGS.DoLink, link the associated IH restart files and continue the loop.
254.             if ARGS.DoLink:
255.                 # check if the SIMDIR exists in Results
256.                 if os.path.isdir('Results/'+SIMDIR):
257.                     for dirTmp in os.listdir('Results/'+SIMDIR):
258.                         if os.path.isdir(os.path.join('Results/'+SIMDIR, dirTmp)):
259.                             linkSrc = os.path.join(os.getcwd(), 'Results/'+RestartDir, dirTmp, 'RESTART/IH')
260.                             linkDst = os.path.join(os.getcwd(), 'Results/'+SIMDIR,     dirTmp, 'RESTART/IH')
261.                             # check whether the IH restart files is linked or not, if yes, remove the link first.
262.                             if os.path.islink(linkDst):
263.                                 os.unlink(linkDst)
264.                             os.symlink(linkSrc, linkDst)
265.                             print('Created link from '+ linkSrc  + ' to ' + linkDst)
266.                 else:
267.                     print('Results/'+SIMDIR+' does not exist!!!!')
268.                 continue
269. 
270.             strPfssMake  ='PFSS='+PFSS
271.             strModelMake ='MODEL='+MODEL
272.             strParamMake ='PARAM='+PARAM
273. 
274.             strRealizationsMake = 'REALIZATIONS='+strRealizations
275. 
276.             strSimDirMake = 'SIMDIR='+SIMDIR
277. 
278.             # Compile the code if needed. AWSoM and AWSoM-R could not be 
279.             # selected at the same time
280.             if not MODEL in ['AWSoM','AWSoMR','AWSoM2T','AWSoMR_SOFIE']:
281.                 warnings.warn(MODEL+' may not be supported.')
282. 
283.             # If the corresponding MODEL.exe does not exist, need to re-compile the code.
284.             # If it exists, do not change ARGS.DoCompile, which default is 1 (to re-compile
285.             # the code for the first time when running the event list). However, the user
286.             # may still set it to 0, in which case the code will not be re-compiled.
287.             if not os.path.isfile('SWMF/bin/'+MODEL+'.exe'):
288.                 ARGS.DoCompile = 1
289. 
290.             if ARGS.DoCompile:
291.                 print('--------------------')
292.                 print('working on '+MODEL)
293.                 print('--------------------')
294.                 if DoInstall:
295.                     subprocess.call('make compile DOINSTALL=T MODEL='+MODEL, shell=True)
296.                 else:
297.                     subprocess.call('make compile DOINSTALL=F MODEL='+MODEL, shell=True)
298.                 DoInstall = False
299.             else:
300.                 print('--------------------')
301.                 print('no need to re-compile model = '+MODEL)
302.                 print('--------------------')
303. 
304.             # The code is compiled already, may not need to re-compile next time.
305.             ARGS.DoCompile = 0
306. 
307.             # backup previous results if needed
308.             strbackup_run = 'make backup_run ' + strSimDirMake
309.             subprocess.call(strbackup_run, shell=True)
310. 
311.             # copy the PARAM.in, HARMONICS.in and FDIPS.in files
312.             strCopy_param = 'make copy_param ' + strModelMake + ' ' + strParamMake
313.             subprocess.call(strCopy_param, shell=True)
314. 
315.             # change the PARAM.in file
316.             change_awsom_param.change_param_local(time=TIME, map=MAP, pfss=PFSS, 
317.                                                   new_params=NewParam,scheme=SCHEME,
318.                                                   DoUseMarker=ARGS.DoUseMarker,
319.                                                   DoRestart=DoRestart)
320.             
321.             # make run directories
322.             strRun_dir = ('make rundir_realizations ' + strSimDirMake + ' '
323.                           + strRealizationsMake + ' ' + strPfssMake + ' MODEL=' + MODEL)
324.             subprocess.call(strRun_dir, shell=True)
325. 
326.             file_output = open(SIMDIR+'/key_params.txt', 'w')
327.             file_output.write('model='+MODEL+'\n')
328.             for param in params[1:]:
329.                 if not 'realization' in param and not 'model' in param:
330.                     file_output.write(str(param)+'\n')
331.             file_output.write('realizations='+strRealizations+'\n')
332.             file_output.close()
333. 
334.             if DoRestart:
335.                 listRealizations = strRealizations.split(',')
336.                 # only consider the current realization list
337.                 for iRealization in listRealizations:
338.                     path_swmfsolar     = os.getcwd()
339.                     StrRealizationLocal=str(int(iRealization)).zfill(2)
340.                     # go to the realiztion dir in SIMDIR
341.                     os.chdir(SIMDIR+'/run'+StrRealizationLocal)
342.                     RestartDirFull = glob.glob(path_swmfsolar + '/Results/' + RestartDir
343.                                                + '*/run' + StrRealizationLocal+'/RESTART')
344.                     if len(RestartDirFull):
345.                         strLinkRestart = './Restart.pl -v -i ' + RestartDirFull[0]
346.                         subprocess.call(strLinkRestart, shell=True)
347.                         if os.path.exists(RestartDirFull[0]+'/../fdips_bxyz.out'):
348.                             shutil.copy2(RestartDirFull[0] +'/../fdips_bxyz.out', './SC/')
349.                         if os.path.exists(RestartDirFull[0]+'/../harmonics_bxyz.out'):
350.                             shutil.copy2(RestartDirFull[0] +'/../harmonics_bxyz.out', './SC/')
351.                     # go back to the SWMFSOLAR dir
352.                     os.chdir(path_swmfsolar)
353. 
354.             # clean the PARAM.in, HARMONICS.in, FDIPS.in and map_*.out files 
355.             # in the SWMFSOLAR folder
356.             subprocess.call('make clean_rundir_tmp', shell=True)
357. 
358.             # submit runs
359.             if ARGS.DoSubRun:
360.                 strRun = ('make run ' + strPfssMake + ' ' + strSimDirMake + ' '
361.                           + strRealizationsMake + ' JOBNAME=r'+str(RunID).zfill(2)+'_')
362.                 subprocess.call(strRun, shell=True)
363.
```

</details>


---

<sub>⏱️ 2m 7s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py (lines 1-220)

<details>
<summary>129 lines</summary>

```
1. #!/usr/bin/env python3
2. 
3. from ftplib import FTP
4. import gzip
5. import shutil
6. import math
7. import sys
8. import datetime as dt
9. 
10. def download_ADAPT_magnetogram(timeIn, NameTypeMap='fixed'):
11.     '''
12.     This routine reads the date and type infomration from the command 
13.     line and download the corresponding ADAPT map.
14.     '''
15. 
16.     if NameTypeMap == 'fixed':
17.         StrTypeMap = '0'
18.     elif NameTypeMap == 'central':
19.         StrTypeMap = '1'
20.     else:
21.         raise ValueError('Unrecognized type of ADAPT map: '+NameTypeMap)
22. 
23.     # ADAPT maps only contains the hours for even numbers
24.     if timeIn.hour%2 != 0:
25.         timeIn = timeIn.replace(hour=math.floor(timeIn.hour/2)*2)
26.         print('Warning: Hour must be an even number. '
27.               +'The entered hour value is changed to ', timeIn.hour)
28. 
29.     # Go to the the ADAPT ftp server
30.     ftp=FTP('gong2.nso.edu')
31.     ftp.login()
32.     
33.     # Only ADAPT GONG is considered
34.     ftp.cwd('adapt/maps/gong')
35. 
36.     # Go to the specific year
37.     try:
38.         ftp.cwd(str(timeIn.year))
39.     except:
40.         sys.exit('******************************************************************\n' 
41.                  + 'Year not found on the ftp server: '+str(timeIn.year) + '.\n'
42.                  + 'Check ftp://gong2.nso.edu/adapt/maps/gong in the corresponding \n'
43.                  + 'year to see whether it provides a map.\n'
44.                  + '******************************************************************\n')
45. 
46.     # Only consider the public (4) Carrington Fixed (0) GONG (3) ADAPT maps
47.     patten = 'adapt4'+StrTypeMap+'3*' + str(timeIn.year).zfill(4) + \
48.         str(timeIn.month).zfill(2) + str(timeIn.day).zfill(2)     + \
49.         str(timeIn.hour).zfill(2)  + '*'
50.     
51.     filenames = ftp.nlst(patten)
52. 
53.     timeMap = timeIn
54.     
55.     if len(filenames) < 1:
56.         iTry = 0
57.         timeLocal = timeIn
58.         while True:
59.             iTry += 1
60.             timeLocal   = timeLocal + dt.timedelta(hours=-1)
61.             pattenLocal = 'adapt4'+StrTypeMap+'3*' + str(timeLocal.year).zfill(4) + \
62.                 str(timeLocal.month).zfill(2) + str(timeLocal.day).zfill(2)       + \
63.                 str(timeLocal.hour).zfill(2)  + '*'
64.             if timeLocal.year != timeIn.year:
65.                 ftp=FTP('gong2.nso.edu')
66.                 ftp.login()
67.                 ftp.cwd('adapt/maps/gong')
68.                 try:
69.                     ftp.cwd(str(timeLocal.year))
70.                 except:
71.                     sys.exit('******************************************************************\n'
72.                              + 'Year not found on the ftp server: '+str(timeLocal.year) + '.\n'
73.                              + 'Check ftp://gong2.nso.edu/adapt/maps/gong in the corresponding \n'
74.                              + 'year to see whether it provides a map.\n'
75.                              + '******************************************************************\n')
76.             filenames = ftp.nlst(pattenLocal)
77.             if len(filenames) > 0:
78.                 timeMap = timeLocal
79.                 print('Warning: cannot find the specific year/month/day/hour.')
80.                 print('         But a map is found at '+ timeLocal.strftime("%Y-%m-%dT%H:00:00"))
81.                 break
82.             if iTry > 1000:
83.                 sys.exit('******************************************************************\n'
84.                          + 'Could not find any map with the specific time including prior 1000 \n'
85.                          + 'hours. Check ftp://gong2.nso.edu/adapt/maps/gong in the \n'
86.                          + 'corresponding year/month/day to see whether it provides a map.\n'
87.                          + '******************************************************************\n')
88.     
89.     for ifile, filename in enumerate(filenames):
90.         # open the file locally
91.         fhandle=open(filename, 'wb')
92.         
93.         # try to download the magnetogram
94.         try:
95.             ftp.retrbinary('RETR '+ filename, fhandle.write)
96.         except:
97.             sys.exit('Cannot download '+filename)
98.         
99.         # close the file
100.         fhandle.close()
101. 
102.         #unzip the file
103.         if '.gz' in filename:
104.             filename_unzip = 'adapt_' + timeMap.strftime('%Y%m%d%H') + '.fits'
105.             with gzip.open(filename, 'rb') as s_file, \
106.                 open(filename_unzip, 'wb') as d_file:
107.                     shutil.copyfileobj(s_file, d_file, 65536)
108.             filenames[ifile]=filename_unzip
109.     
110.     ftp.quit()
111. 
112.     return filenames
113. 
114. if __name__ == '__main__':
115. 
116.     yyyy = int(input('Enter year: ' ))
117.     mm   = int(input('Enter month: '))
118.     dd   = int(input('Enter day: '  ))
119.     hh   = int(input('Enter hour: ' ))
120. 
121.     StrTime = str(yyyy).zfill(4)+'-'+str(mm).zfill(2)+'-' \
122.         +str(dd).zfill(2)+'T'+str(hh).zfill(2)
123. 
124.     timeIn = dt.datetime.strptime(StrTime,"%Y-%m-%dT%H")
125. 
126.     NameTypeMap = input('Type of ADAPT maps: fixed or central?  ')
127. 
128.     download_ADAPT_magnetogram(timeIn,NameTypeMap)
129.
```

</details>


---

<sub>⏱️ 2m 7s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/HARMONICS.in.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/HARMONICS.in (lines 1-220)

<details>
<summary>23 lines</summary>

```
1. !  For ADAPT MAPS (HMI/GONG/VSM etc.)
2. 
3. ! This command reads the new fileformat with coordinates and header
4. 
5. ! Name of the input magnetogram ascii file
6. #MAGNETOGRAMFILE
7. map_1.out			NameFileIn
8. 3500.0				BrMax
9. 
10. CHANGEWEAKFIELD			^
11. 3.75                            BrFactor^
12. 5.0                             BrMin^
13. 
14. ! Default output file name is harmonics.dat
15. ! Name of the output file
16. #OUTPUT
17. harmonics_adapt.dat		NameFileOut
18. 
19. ! Default is the number of latitudes in the magnetogram but at most
20. ! MaxHarmonics = 180 (see ModMagHarmonics.f90)
21. #HARMONICS
22. 180				nHarmonics^
23.
```

</details>


---

<sub>⏱️ 2m 7s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/FDIPS.in.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/FDIPS.in (lines 1-220)

<details>
<summary>56 lines</summary>

```
1. ! Provide name of magnetogram file and specify maximum field strength
2. ! Defaults are "fitsfile.out" and 3500 G
3. ! Modifying for ADAPT maps
4. #MAGNETOGRAMFILE
5. map_1.out		NameFileIn
6. 3500.0			BrMax
7. 
8. ! Apply optional enhancement of the polar magnetic field with a factor
9. !  1 + (PolarFactor-1)*abs(sin(Latitude))^PolarExponent  
10. ! Not done for ADAPT maps
11. CHANGEPOLARFIELD
12. 3.0			PolarFactor
13. 2.0			PolarExponent
14. 
15. ! The observed magnetic field is increased
16. ! Br=sign(BrObserved)*min(BrFactor*|BrObserved|, BrMin + |BrObserved|)
17. ! Default BrFactor = 1.0, BrMin = 0.0 (no change)
18. CHANGEWEAKFIELD	     	  	^
19. 3.75				BrFactor^
20. 5.0				BrMin^
21. 
22. ! For a non-default domain size and/or logarithmic radial grid
23. #DOMAIN
24. 1.0			rMin         (default is 1)
25. 25			rMax         (default is 2.5) rSourceSurface^
26. T			UseLogRadius (default is F)
27. F			UseWedge
28. 
29. ! For Uniform Theta Transform from a sin-lat grid.
30. ! Default is true so the lookup table is more uniform and accurate.
31. 
32. #CHEBYSHEV
33. T			UseChebyshevNode
34. 
35. ! Grid for production run
36. #GRID
37. 400			nR      nR_pfss
38. 180			nTheta  nTheta_pfss
39. 360			nPhi    nPhi_pfss
40. 
41. ! nProcTheta*nProcPhi should agree with the number of procs FDIPS.exe uses
42. #PARALLEL
43. 0			nProcTheta
44. 0			nProcPhi
45. 
46. ! Standard solver (these are the defaults)
47. #SOLVER                 ! NO HYPRE
48. BiCGSTAB		NameSolver (BiCGSTAB)
49. ILU			NamePreconditioner (ILU or NONE)
50. 1e-10			Tolerance
51. 
52. #OUTPUT
53. bxyz			TypeOutput    (field, bxyz, potential, or tecplot)
54. fdips_bxyz.out		NameFileField
55. real4			TypeFileField (ascii, real4 or real8)
56.
```

</details>


---

<sub>⏱️ 2m 16s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/PARAM.XML**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "HARMONICSFILE|HARMONICSGRID|NEWHARMONICSFILE|MAGNETOGRAMFILE|CHANGEWEAKFIELD|CHANGEPOLARFIELD|FACTORB0|LOOKUPTABLE\\(FDIPS\\)|FDIPS",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/PARAM.XML",
  "output_mode": "content",
  "-n": true,
  "head_limit": 400
}
```

</details>

```
No matches found.
```


---

<sub>⏱️ 2m 16s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "read_magnetogram_param\\(|init_magnetogram_lookup_table|get_magnetogram_field|read_harmonics_file",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC",
  "output_mode": "content",
  "-n": true,
  "head_limit": 400
}
```

</details>

```
No matches found.
```


---

<sub>⏱️ 2m 16s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "ModMagnetogram|#HARMONICSFILE|#HARMONICSGRID|#FACTORB0|#MAGNETOGRAMFILE",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src",
  "output_mode": "content",
  "-n": true,
  "head_limit": 400
}
```

</details>

<details>
<summary>6 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src/ModCoronalHeating.f90:171:    use ModMagnetogram, ONLY: get_magnetogram_field
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src/ModSetParameters.f90:137:    use ModMagnetogram, ONLY: read_magnetogram_param
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src/ModSetParameters.f90:2800:       case("#HARMONICSFILE", "#NEWHARMONICSFILE", "#HARMONICSGRID", &
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src/ModSetParameters.f90:2801:            "#FACTORB0", "#MAGNETOGRAM") ! last one kept for compatibility only
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src/ModB0.f90:180:    use ModMagnetogram, ONLY: init_magnetogram_lookup_table, rMaxB0, &
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src/ModB0.f90:735:    use ModMagnetogram, ONLY: iTableB0, iTableB0New, get_magnetogram_field
```

</details>


---

<sub>⏱️ 2m 25s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "HARMONICSFILE|NEWHARMONICSFILE|HARMONICSGRID|MAGNETOGRAMFILE|CHANGEWEAKFIELD|CHANGEPOLARFIELD|FACTORB0",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF",
  "output_mode": "content",
  "-n": true,
  "glob": "**/PARAM.XML",
  "head_limit": 400
}
```

</details>

<details>
<summary>28 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:8416:if the radius of the B0 grid generated by #HARMONICSGRID command or by
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10524:<command name="FACTORB0">
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10527:#FACTORB0
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10537:<command name="HARMONICSGRID">
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10547:#HARMONICSGRID
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10556:#HARMONICSGRID
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10584:order present in the harmonics files read by #HARMONICSFILE and
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10585:#NEWHARMONICSFILE. If MaxOrder is less than the order present in the files,
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10595:<command name="HARMONICSFILE">
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10598:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10611:an additional B0NEW lookup table. See also the #NEWHARMONICSFILE command.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10616:<command name="NEWHARMONICSFILE">
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10619:#NEWHARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10653:This command is obsolete and has been replaced with the #HARMONICSFILE command.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/IH/BATSRUS/PARAM.XML:8416:if the radius of the B0 grid generated by #HARMONICSGRID command or by
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/IH/BATSRUS/PARAM.XML:10524:<command name="FACTORB0">
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/IH/BATSRUS/PARAM.XML:10527:#FACTORB0
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/IH/BATSRUS/PARAM.XML:10537:<command name="HARMONICSGRID">
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/IH/BATSRUS/PARAM.XML:10547:#HARMONICSGRID
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/IH/BATSRUS/PARAM.XML:10556:#HARMONICSGRID
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/IH/BATSRUS/PARAM.XML:10584:order present in the harmonics files read by #HARMONICSFILE and
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/IH/BATSRUS/PARAM.XML:10585:#NEWHARMONICSFILE. If MaxOrder is less than the order present in the files,
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/IH/BATSRUS/PARAM.XML:10595:<command name="HARMONICSFILE">
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/IH/BATSRUS/PARAM.XML:10598:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/IH/BATSRUS/PARAM.XML:10611:an additional B0NEW lookup table. See also the #NEWHARMONICSFILE command.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/IH/BATSRUS/PARAM.XML:10616:<command name="NEWHARMONICSFILE">
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/IH/BATSRUS/PARAM.XML:10619:#NEWHARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/IH/BATSRUS/PARAM.XML:10653:This command is obsolete and has been replaced with the #HARMONICSFILE command.
```

</details>


---

<sub>⏱️ 2m 25s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src/ModSetParameters.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src/ModSetParameters.f90 (lines 2760-2845)

<details>
<summary>86 lines</summary>

```
2760.           end if
2761. 
2762.        case("#THINCURRENTSHEET")
2763.           call read_var('DoThinCurrentSheet', DoThinCurrentSheet)
2764.           if(SignB_ > 1 .and. DoThinCurrentSheet)then
2765.              NameVar_V(SignB_) = 'SignB'
2766.              call set_namevar
2767.           end if
2768. 
2769.        case("#ALIGNBANDU")
2770.           call read_samhd_param
2771.           if(BperU_ > 1 .and. UseSaMhd)then
2772.              NameVar_V(BperU_) = 'BperU'
2773.              call set_namevar
2774.           end if
2775. 
2776.           ! OUTERHELIOSPHERE SPECIFIC COMMANDS
2777. 
2778.        case("#OHNEUTRALS")
2779.           call read_var('RhoNeuWindDim',  RhoNeuWindDim)
2780.           call read_var('TempNeuWindDim', TempNeuWindDim)
2781.           call read_var('UxNeuWindDim',   UxNeuWindDim)
2782.           call read_var('UyNeuWindDim',   UyNeuWindDim)
2783.           call read_var('UzNeuWindDim',   UzNeuWindDim)
2784.           call read_var('MassNeutralDim', MassNeutralDim)
2785. 
2786.        case("#OHBOUNDARY")
2787.           call read_var('DoOhNeutralBc', DoOhNeutralBc)
2788.           if(DoOhNeutralBc)then
2789.              do iFluid = nIonFluid+1, nFluid
2790.                 call read_var('RhoBcFactor', RhoBcFactor_I(iFluid))
2791.                 call read_var('uBcFactor', uBcFactor_I(iFluid))
2792.              end do
2793.           end if
2794. 
2795.        case("#PUIGRID")
2796.           call read_pui_param(NameCommand)
2797. 
2798.           ! CORONA SPECIFIC COMMANDS
2799. 
2800.        case("#HARMONICSFILE", "#NEWHARMONICSFILE", "#HARMONICSGRID", &
2801.             "#FACTORB0", "#MAGNETOGRAM") ! last one kept for compatibility only
2802.           call read_magnetogram_param(NameCommand)
2803. 
2804.        case('#LDEM')
2805.           call read_var('UseLdem',  UseLdem)
2806.           if(UseLdem) then
2807.              call read_var('NameLdemFile', NameLdemFile)
2808.              call read_var('iRadiusLdem', iRadiusLdem)
2809.              call read_ldem(NamePlotDir)
2810.           end if
2811. 
2812.        case("#CORONALHEATING", "#LONGSCALEHEATING", "#ACTIVEREGIONHEATING")
2813.           call read_coronal_heating_param(NameCommand)
2814. 
2815.        case("#HEATPARTITIONING", "#HIGHBETASTOCHASTIC",  "#ALIGNMENTANGLE", &
2816.             "#NONLINAWDISSIPATION", "#LIMITIMBALANCE", "#POYNTINGFLUX")
2817.           call read_turbulence_param(NameCommand)
2818. 
2819.        case("#RADIATIVECOOLING")
2820.           call read_var('UseRadCooling', UseRadCooling)
2821. 
2822.        case("#CHROMOSPHERE")
2823.           call read_chromosphere_param
2824. 
2825.        case("#TRANSITIONREGION")
2826.           call read_cooling_param
2827. 
2828.        case("#FIELDLINETHREAD", '#PLOTTHREADS', '#CHROMOEVAPORATION')
2829.           call read_thread_param(NameCommand, iSession)
2830. 
2831.        case("#THREADEDBC")
2832.           call read_threaded_bc_param
2833. 
2834.        case('#THREADRESTART')
2835.           call read_var('DoThreadRestart', DoThreadRestart)
2836. 
2837.        case("#ADVECTWAVES", "#ALFVENWAVES", "#WAVEPRESSURE", &
2838.             "#FREQUENCY", "#SPECTRUM", "#WAVEREFLECTION",    &
2839.             "#AWREPRESENTATIVE")
2840.           call read_waves_param(NameCommand)
2841. 
2842.        case("#LASERPULSE", "#LASERBEAM", "#LASERBEAMS", "#LASERBEAMPROFILE", &
2843.             "#LASERRAYTEST")
2844.           call read_laser_heating_param(NameCommand)
2845.
```

</details>


---

<sub>⏱️ 2m 25s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src/ModB0.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src/ModB0.f90 (lines 150-260)

<details>
<summary>111 lines</summary>

```
150. 
151.     case("#MONOPOLEB0")
152.        call read_var('MonopoleStrengthSi', MonopoleStrengthSi)
153. 
154.     case("#B0WAVE")
155.        call read_var('UseB0Wave', UseB0Wave)
156.        if(UseB0Wave)then
157.           call read_var('B0Wave0X', B0Wave0_D(1))
158.           call read_var('B0Wave0Y', B0Wave0_D(2))
159.           call read_var('B0Wave0Z', B0Wave0_D(3))
160.           call read_var('B0Wave1X', B0Wave1_D(1))
161.           call read_var('B0Wave1Y', B0Wave1_D(2))
162.           call read_var('B0Wave1Z', B0Wave1_D(3))
163.           call read_var(             'B0WaveLengthX', B0WaveNumber_D(1))
164.           if(nDim > 1) call read_var('B0WaveLengthY', B0WaveNumber_D(2))
165.           if(nDim > 2) call read_var('B0WaveLengthZ', B0WaveNumber_D(3))
166.           B0WaveNumber_D = max(0.0, cTwoPi/B0WaveNumber_D)
167.           call read_var('B0WavePhase', B0WavePhase)
168.           B0WavePhase = B0WavePhase*cDegToRad
169.        end if
170.     case default
171.        call stop_mpi(NameSub//': unknown command='//NameCommand)
172.     end select
173. 
174.     call test_stop(NameSub, DoTest)
175.   end subroutine read_b0_param
176.   !============================================================================
177.   subroutine init_mod_b0
178. 
179.     use SC_BATL_lib, ONLY: iComm, iProc
180.     use ModMagnetogram, ONLY: init_magnetogram_lookup_table, rMaxB0, &
181.          iTableB0, iTableB0local
182.     use SC_ModGeometry, ONLY: RadiusMax
183. 
184.     logical:: DoTest
185.     character(len=*), parameter:: NameSub = 'init_mod_b0'
186.     !--------------------------------------------------------------------------
187.     call test_start(NameSub, DoTest)
188. 
189.     !$omp parallel
190.     !$omp single
191.     if(.not.allocated(B0_DGB))then
192.        allocate(B0_DGB(MaxDim,MinI:MaxI,MinJ:MaxJ,MinK:MaxK,MaxBlock))
193.        B0_DGB = 0.0
194.        if(iTypeUpdate == UpdateOrig_)then
195.           allocate( &
196.                B0ResChangeX_DIIEB(MaxDim,nJ,nK,1:2,MaxBlock),    &
197.                B0ResChangeY_DIIEB(MaxDim,nI,nK,3:4,MaxBlock),    &
198.                B0ResChangeZ_DIIEB(MaxDim,nI,nJ,5:6,MaxBlock))
199.           B0ResChangeX_DIIEB = 0.0
200.           B0ResChangeY_DIIEB = 0.0
201.           B0ResChangeZ_DIIEB = 0.0
202.        end if
203.     end if
204.     !$omp end single
205. 
206.     if( .not.allocated(B0_DX) ) then
207.        if(UseConstrainB)then
208.           ! The current implementation of CT requires fluxes
209.           ! between ghost cells. Not a good solution.
210.           allocate( &
211.                B0_DX(MaxDim,nI+1,0:nJ+1,0:nK+1), &
212.                B0_DY(MaxDim,0:nI+1,nJ+1,0:nK+1), &
213.                B0_DZ(MaxDim,0:nI+1,0:nJ+1,nK+1))
214.        else
215.           allocate( &
216.                B0_DX(MaxDim,nI+1,nJ,nK), &
217.                B0_DY(MaxDim,nI,nJ+1,nK), &
218.                B0_DZ(MaxDim,nI,nJ,nK+1))
219.        end if
220.     end if
221. 
222.     !$omp end parallel
223. 
224.     call init_magnetogram_lookup_table(iComm)
225. 
226.     if(rCurrentFreeB0 < -1.0)then
227.        ! Set defaults if #CURLB0 was not used
228.        if(iTableB0Local > 0)then
229.           ! Non potential lookup table has non-zero curl B0
230.           UseCurlB0 = .true.
231.           rCurrentFreeB0 = 0.0
232.           if(iProc==0)write(*,*)NameSub, &
233.                ' Local B0, so UseCurlB0=T, rCurrentFreeB0=1'
234.        elseif(iTableB0 > 0) then
235.           if(rMaxB0 < RadiusMax)then
236.              ! J0 is finite above rMaxB0
237.              UseCurlB0 = .true.
238.              rCurrentFreeB0 = rMaxB0
239.              if(iProc==0)write(*,*)NameSub,&
240.                   ' UseCurlB0=T, rCurrentFreeB0 =', rCurrentFreeB0
241.           else if(UseCurlB0)then
242.              ! if rSourceSurface > SC boundary then UseCurlB0 is NOT required
243.              UseCurlB0 = .false.
244.              rCurrentFreeB0 = -1.0
245.              if(iProc==0)write(*,*)NameSub,&
246.                   ' UseCurlB0=F because source surface radius =', rMaxB0
247.           end if
248.        end if
249.     end if
250.     !$acc update device (UseCurlB0, rCurrentFreeB0)
251. 
252.     !$omp parallel
253. 
254.     if(UseB0Source .and. .not.allocated(DivB0_C)) &
255.          allocate(DivB0_C(nI,nJ,nK))
256. 
257.     if((UseCurlB0 .or. UseB0Source) .and. .not.allocated(CurlB0_DC)) &
258.          allocate(CurlB0_DC(3,nI,nJ,nK), B0MomentumSource_DC(3,nI,nJ,nK))
259. 
260.     !$omp end parallel
```

</details>


---

<sub>⏱️ 2m 25s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src/ModCoronalHeating.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src/ModCoronalHeating.f90 (lines 140-240)

<details>
<summary>101 lines</summary>

```
140.     use SC_ModPhysics, ONLY: Si2No_V, UnitEnergyDens_, UnitT_
141. 
142.     logical:: DoTest
143.     character(len=*), parameter:: NameSub = 'init_coronal_heating'
144.     !--------------------------------------------------------------------------
145.     call test_start(NameSub, DoTest)
146.     call init_turbulence
147.     if(.not.DoInit)then
148.        call test_stop(NameSub, DoTest)
149.        RETURN
150.     end if
151.     DoInit = .false.
152. 
153.     if(UseExponentialHeating)then
154.        HeatingAmplitude =  HeatingAmplitudeCgs*0.1 &
155.             *Si2No_V(UnitEnergyDens_)/Si2No_V(UnitT_)
156.     end if
157. 
158.     call test_stop(NameSub, DoTest)
159.   end subroutine init_coronal_heating
160.   !============================================================================
161.   subroutine get_coronal_heat_factor
162. 
163.     ! Integrate heat function with a unit factor, then multiply by
164.     ! the total heating and divide by volume
165.     ! With thus calculated factor, the integral of coronal heating
166.     ! function equals the prescribed (for example, stemming from
167.     ! the unsigned flux) total heating
168. 
169.     use SC_ModAdvance, ONLY: State_VGB, Bz_
170.     use SC_ModGeometry, ONLY: IsNoBody_B, TypeGeometry
171.     use ModMagnetogram, ONLY: get_magnetogram_field
172.     use SC_ModMain, ONLY: nI, nJ, nK, nBlock, Unused_B, tSimulation,z_
173.     use ModMpi, ONLY: MPI_REAL, MPI_SUM
174.     use ModNumConst, ONLY: cHalfPi, cTwoPi
175.     use SC_ModPhysics, ONLY: Si2No_V, No2Si_V, UnitX_, UnitT_, &
176.          UnitEnergyDens_, rBody
177.     use SC_BATL_lib, ONLY: CellFace_DB, CellVolume_GB, nProc, iComm, Used_GB
178. 
179.     integer :: i, j, k, iBlock
180.     integer :: iTheta, iPhi, iError
181.     real :: UnsignedFluxCgs, dAreaCgs
182.     real :: HeatFunction, HeatFunctionVolume, HeatFunctionVolumePe
183.     real :: x, y, z, Theta, Phi, SinTheta, CosTheta, SinPhi, CosPhi
184.     real :: B0_D(3), BrSi, BrCgs, SumUnsignedBrCgs
185.     real :: BzCgs_II(1:nI,1:nJ), SumUnsignedBzCgs, UnsignedFluxCgsPe
186.     real    :: TotalCoronalHeating = -1.0, TimeUpdateLast = -1.0
187.     logical :: DoFirst = .true.
188.     !$omp threadprivate(TotalCoronalHeating, TimeUpdateLast, DoFirst)
189. 
190.     integer, parameter:: nTheta = 72, nPhi=90
191.     real, parameter:: dSinTheta = 2.0/nTheta, dPhi = cTwoPi/nPhi
192.     real, parameter:: HeatExponent = 1.1488, HeatCoef = 89.4
193. 
194.     logical:: DoTest
195.     character(len=*), parameter:: NameSub = 'get_coronal_heat_factor'
196.     !--------------------------------------------------------------------------
197.     call test_start(NameSub, DoTest)
198. 
199.     if(DoFirst .and. DtUpdateFlux <= 0.0)then
200. 
201.        ! uniform cell area on sphere
202.        dAreaCgs = rBody**2*dSinTheta*dPhi*No2Si_V(UnitX_)**2*1e4
203.        SumUnsignedBrCgs = 0.0
204. 
205.        do iTheta = 0, nTheta
206. 
207.           Theta = cHalfPi - asin((real(iTheta) + 0.5)*dSinTheta - 1.0)
208.           SinTheta = sin(Theta)
209.           CosTheta = cos(Theta)
210.           do iPhi = 1, nPhi
211.              Phi=(real(iPhi)-0.5)*dPhi
212.              SinPhi = sin(Phi)
213.              CosPhi = cos(Phi)
214. 
215.              x = rBody*SinTheta*CosPhi
216.              y = rBody*SinTheta*SinPhi
217.              z = rBody*CosTheta
218. 
219.              call get_magnetogram_field(x, y, z, B0_D)
220.              BrSi = (x*B0_D(1) + y*B0_D(2) + z*B0_D(3))/rBody
221.              BrCgs = BrSi*1e4
222.              SumUnsignedBrCgs = SumUnsignedBrCgs + abs(BrCgs)
223. 
224.           end do
225.        end do
226. 
227.        UnsignedFluxCgs = SumUnsignedBrCgs*dAreaCgs
228. 
229.        TotalCoronalHeatingCgs = HeatCoef*UnsignedFluxCgs**HeatExponent
230. 
231.        TotalCoronalHeating = TotalCoronalHeatingCgs*1e-7 &
232.             *Si2No_V(UnitEnergyDens_)*Si2No_V(UnitX_)**3/Si2No_V(UnitT_)
233. 
234.        DoFirst = .false.
235. 
236.     elseif( DtUpdateFlux > 0.0 .and. &
237.          tSimulation - TimeUpdateLast > DtUpdateFlux ) then
238. 
239.        UnsignedFluxCgs = 0.0
240.        if(TypeGeometry == 'spherical')then
```

</details>


---

<sub>⏱️ 2m 25s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src/ModB0.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/src/ModB0.f90 (lines 700-790)

<details>
<summary>91 lines</summary>

```
700.                + B0_DZ(:,i,j,k+1)*sum(B0_DZ(:,i,j,k+1)*                 &
701.                FaceNormal_DDFB(:,3,i,j,k+1,iBlock))                     &
702.                - FaceNormal_DDFB(:,3,i,j,k+1,iBlock)*                   &
703.                sum(B0_DZ(:,i,j,k+1)**2)*0.50                            &
704.                - B0_DZ(:,i,j,k  )*sum(B0_DZ(:,i,j,k  )*                 &
705.                FaceNormal_DDFB(:,3,i,j,k  ,iBlock) )                    &
706.                + FaceNormal_DDFB(:,3,i,j,k  ,iBlock)*                   &
707.                sum(B0_DZ(:,i,j,k  )**2)*0.50
708. 
709.           ! Remove contribution from finite div(B0)
710.           B0MomentumSource_DC(:,i,j,k) =                                &
711.                B0MomentumSource_DC(:,i,j,k)/CellVolume_GB(i,j,k,iBlock) &
712.                - B0_DGB(:,i,j,k,iBlock)*DivB0_C(i,j,k)
713.        end do; end do; end do
714.     else
715.        do k = 1, nK; do j = 1, nJ; do i = 1, nI
716.           B0MomentumSource_DC(:,i,j,k) = cross_product(CurlB0_DC(:,i,j,k), &
717.                B0_DGB(:,i,j,k,iBlock))
718.        end do; end do; end do
719.     end if
720.     call test_stop(NameSub, DoTest, iBlock)
721. 
722.   end subroutine set_b0_source
723.   !============================================================================
724.   subroutine get_b0(Xyz_D, B0_D)
725.     !$acc routine seq
726. 
727.     ! Get B0 at location Xyz_D
728. 
729.     use SC_ModMain, ONLY: tSimulation, NameThisComp, &
730.          TypeCoordSystem
731.     use SC_ModPhysics, ONLY: Si2No_V, UnitB_, DipoleStrengthSi, &
732.          MonopoleStrength
733.     use CON_planet_field, ONLY: get_planet_field
734.     use SC_ModMain, ONLY: UseBody2, UseUserB0, IsTimeAccurate, StartTime
735.     use ModMagnetogram, ONLY: iTableB0, iTableB0New, get_magnetogram_field
736.     use ModConst, ONLY: CarringtonSynodicPeriod, tStartCarringtonRotation
737. 
738.     real, intent(in) :: Xyz_D(3)
739.     real, intent(out):: B0_D(3)
740. 
741.     real:: r, CarringtonNumber
742. 
743.     character(len=*), parameter:: NameSub = 'get_b0'
744.     !--------------------------------------------------------------------------
745.     if(iTableB0 > 0)then
746.        if(iTableB0New > 0 .and. IsTimeAccurate)then
747.           ! Interpolate to the current time expressed as CarringtonNumber
748.           CarringtonNumber = &
749.                (StartTime + tSimulation - tStartCarringtonRotation) &
750.                /CarringtonSynodicPeriod
751.           call get_magnetogram_field(Xyz_D, B0_D, CarringtonNumber)
752.        else
753.           call get_magnetogram_field(Xyz_D, B0_D)
754.        end if
755. 
756.        ! Convert from Tesla to normalized units.
757.        B0_D = B0_D*Si2No_V(UnitB_)
758. #ifndef _OPENACC
759.     elseif(UseB0Wave)then
760.        B0_D = B0Wave0_D &
761.             + B0Wave1_D*cos(B0WavePhase + sum(B0WaveNumber_D*Xyz_D))
762.     elseif(MonopoleStrength /= 0.0)then
763.        r = norm2(Xyz_D(1:nDim))
764.        B0_D = MonopoleStrength*Xyz_D/r**nDim
765.     elseif(DipoleStrengthSi == 0.0)then
766.        B0_D = 0.0
767.     elseif(NameThisComp=='GM' .and. nDim == 3)then
768.        call get_planet_field(tSimulation, Xyz_D, TypeCoordSystem//' NORM',&
769.             B0_D)
770.        B0_D = B0_D*Si2No_V(UnitB_)
771. #endif
772.     else
773.        ! dipole field
774.        call get_b0_dipole(Xyz_D, B0_D)
775.     end if
776. 
777. #ifndef _OPENACC
778.     if(UseBody2)call add_b0_body2(Xyz_D, B0_D)
779. 
780.     if(UseUserB0)call SC_user_get_b0(Xyz_D(1), Xyz_D(2), Xyz_D(3), B0_D)
781. #endif
782. 
783.   end subroutine get_b0
784.   !============================================================================
785.   subroutine get_b0_dipole(Xyz_D, B0_D, IsAligned)
786.     !$acc routine seq
787. 
788.     ! Provide magnetic field B0_D in normalized unit at location Xyz_D
789.     ! By default the coordinate system of BATSRUS is used.
790.     ! If IsAligned is present, then MAG/SMG coordinate system is assumed.
```

</details>


---

<sub>⏱️ 2m 33s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML (lines 10515-10645)

<details>
<summary>131 lines</summary>

```
10515. </command>
10516. 
10517. </commandgroup>
10518. 
10519. <commandgroup name="CORONA SPECIFIC COMMANDS">
10520. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
10521. !!!!!!!!!! CORONA SPECIFIC COMMANDS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
10522. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
10523. 
10524. <command name="FACTORB0">
10525.   <parameter name="FactorB0" type="real" min="0.0" default="1.0"/>
10526. 
10527. #FACTORB0
10528. 1e-4                    FactorB0  
10529. 
10530. FactorB0 is a multiplication factor for the magnetogram based potential
10531. field B0. It can be used to correct the magnetic field units
10532. (default is Gauss) or to change the strength of the field.
10533. 
10534. Default value is 1.
10535. </command>
10536. 
10537. <command name="HARMONICSGRID">
10538.   <parameter name="rMagnetogram"   type="real" min="0"  default="1"  />
10539.   <parameter name="rSourceSurface" type="real"          default="2.5"
10540. 	                                       min="$rMagnetogram"   />
10541.   <parameter name="IsLogRadius" type="logical"          default="F"  />
10542.   <parameter name="MaxOrder"    type="integer" min="1"  default="30" />
10543.   <parameter name="nR"          type="integer" min="10" default="30" />
10544.   <parameter name="nLon"        type="integer" min="10" default="72" />
10545.   <parameter name="nLat"        type="integer" min="10" default="30" />
10546. 
10547. #HARMONICSGRID
10548. 1.0			rMagnetogram
10549. 2.5			rSourceSurface
10550. F                       IsLogRadius
10551. 30                      MaxOrder
10552. 30                      nR
10553. 72                      nLon
10554. 30                      nLat
10555. 
10556. #HARMONICSGRID
10557. 1.0			rMagnetogram
10558. 25.0			rSourceSurface
10559. T                       IsLogRadius
10560. 180                     MaxOrder
10561. 400                     nR
10562. 180                     nLon
10563. 90                      nLat
10564. 
10565. This command determines the grid used in the B0 and B0New lookup tables
10566. generated from the spherical harmonics.
10567. 
10568. The radial grid goes from the inner boundary at rMagnetogram (typically 1)
10569. to the source surface radius rSourceSurface where B0 becomes radial.
10570. The longitude goes from 0 to 360 degrees, while the latitude from -90 to 90
10571. degrees. Both angular coordinates are uniform (no sine latitude grid).
10572. 
10573. Traditionally rSourceSurface is 2.5, but this may not be the best choice.
10574. Setting rSourceSurface to 25.0 eliminates the non-zero curl of B0
10575. inside the SC domain, so #CURLB0 command is not needed
10576. and numerical artifacts are minimized. In essense, B0 should capture
10577. the field near the active regions but it does not need to represent
10578. the helmet streamer or the heliospheric current sheet. Those features
10579. are best captured by the B1 field obtained from solving the MHD equations.
10580. When rSourceSurface is much larger than rMagnetogram, it is
10581. recommended to use a logarithmic radial grid with IsLogRadius set to true.
10582. 
10583. MaxOrder sets the maximum harmonics order used. This may get reduced to the
10584. order present in the harmonics files read by #HARMONICSFILE and
10585. #NEWHARMONICSFILE. If MaxOrder is less than the order present in the files,
10586. then the higher order harmonics are ignored.
10587. 
10588. nR, nLon and nLat give number of grid cells in the radial, longitudinal and
10589. latitudinal directions, respectively. The B0 field is stored on the grid
10590. (nR+1)*(nLon+1)*(nLat+1) grid nodes.
10591. 
10592. Default values are shown by the first example.
10593. </command>
10594. 
10595. <command name="HARMONICSFILE">
10596.   <parameter name="NameHarmonicsFile" type="string" length="$lLine" />
10597. 
10598. #HARMONICSFILE
10599. Param/CORONA/CR1935_WSO.dat           NameHarmonicsFile
10600. 
10601. NameHarmonicsFile is the name of the file containing the harmonics
10602. coefficients.
10603. 
10604. After reading the harmonics file, the B0 lookup table is generated and saved.
10605. By default this lookup table is saved into "harmonics_bxyz.out" file.
10606. The defaults can be changed with the #LOOKUPTABLE command. Once the
10607. lookup table file is created, it can be loaded directly and there is
10608. no need for this command.
10609. 
10610. The temporal evolution of the magnetogram can be captured by using
10611. an additional B0NEW lookup table. See also the #NEWHARMONICSFILE command.
10612. 
10613. By default there is no B0 lookup table.
10614. </command>
10615. 
10616. <command name="NEWHARMONICSFILE">
10617.   <parameter name="NameHarmonicsFileNew" type="string" length="$lLine"/>
10618. 
10619. #NEWHARMONICSFILE
10620. Param/CORONA/CR1936_WSO.dat    NameHarmonicsFileNew
10621. 
10622. NameHarmonicsFileNew is the name of the file containing the harmonics
10623. coefficients for the time at the end of the session.
10624. 
10625. After reading the harmonics file, the B0NEW lookup table is generated
10626. and saved into the "harmonics_bxyz_new.out" file.
10627. The default parameters of the lookup table can be changed with the
10628. #LOOKUPTABLE command. Once the lookup table file is created,
10629. it can be loaded directly and there is no need for this command.
10630. 
10631. The potential field contained in the B0 and B0NEW lookup tables
10632. will be interpolated in time during the session. 
10633. 
10634. By default there is no B0NEW lookup tables.
10635. </command>
10636. 
10637. <command name="MAGNETOGRAM">
10638.   <parameter name="UseMagnetogram" type="logical" default="F"	/>
10639.   <if expr="$UseMagnetogram">
10640.     <parameter name="rMagnetogram" type="real" default="1.0" />
10641.     <parameter name="rSourceSurface" type="real" default="2.5" />
10642.     <parameter name="HeightInnerBc" type="real" default="0.0" />
10643.     <parameter name="NameHarmonicsFile" type="string" length="$lLine" />
10644.   </if>
10645.
```

</details>


---

<sub>⏱️ 2m 33s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML (lines 8398-8435)

<details>
<summary>38 lines</summary>

```
8398. 2.5		rCurrentFreeB0    (read if UseCurlB0 is true)
8399. T		UseB0MomentumFlux (read if UseCurlB0 is true)
8400. 
8401. If UseCurlB0 is true, then the B0 field has non-zero curl.
8402. The B0 field of planets has zero curl, but the potential field source surface
8403. model (PFSS) for the corona has a finite curl beyond the source surface,
8404. where the field is forced to become radial.
8405. 
8406. The rCurrentFreeB0 parameter is set to the radius within which the B0 field
8407. has no curl (i.e. it is current free).
8408. 
8409. If UseB0MomentumFlux is true, the contribution from B0 field to momentum
8410. source is calculated as $div (B0 B0) - grad B0^2/2 - B0 div B0$
8411. otherwise as $curl B0 \times B0$. Although mathematically identical, 
8412. these expressions are numerically different.
8413. 
8414. If this command is not used, then the defaults are the following.
8415. The default is UseCurlB0 false in general, but it is set to true
8416. if the radius of the B0 grid generated by #HARMONICSGRID command or by
8417. FDIPS is less than the radius of the solar corona domain.
8418. In this case rCurrentFreeB0 is set to the radius of the B0 grid.
8419. If the local B0 lookup table is used, it is assumed to be non-potential,
8420. so the default becomes UseCurlB0 true and rCurrentFreeB0=0.
8421. 
8422. The default for UseB0MomentumFlux is false.
8423. </command>
8424. 
8425. <command name="LIGHTSPEED">
8426.   <parameter name="cLightDim"  type="real" min="0" default="3e5"/>
8427.   
8428. #LIGHTSPEED
8429. 10.0			cLightDim
8430. 
8431. Set speed of light used in the Maxwell equations. Reducing the speed of light
8432. artificially will allow larger explicit time steps. The speed of light
8433. should be larger than the typical wave speeds present in the problem.
8434. 
8435. Default is the true speed of light.
```

</details>


---

<sub>⏱️ 2m 33s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/harmonics.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/harmonics.f90 (lines 1-220)

<details>
<summary>19 lines</summary>

```
1. !  Copyright (C) 2002 Regents of the University of Michigan,
2. !  portions used with permission
3. !  For more information, see http://csem.engin.umich.edu/tools/swmf
4. program harmonics
5. 
6.   ! Transform raw magnetogram file into spherical harmonics file
7. 
8.   use ModMagHarmonics
9. 
10.   implicit none
11.   integer:: iError
12.   !----------------------------------------------------------------------------
13.   call read_harmonics_param
14.   call read_modified_magnetogram
15.   call calc_harmonics
16. 
17. end program harmonics
18. !==============================================================================
19.
```

</details>


---

<sub>⏱️ 2m 33s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90 (lines 1-220)

<details>
<summary>220 lines</summary>

```
1. !  Copyright (C) 2002 Regents of the University of Michigan,
2. !  portions used with permission
3. !  For more information, see http://csem.engin.umich.edu/tools/swmf
4. module ModB0Matvec
5. 
6.   use ModPotentialField, ONLY:  iComm, iProc, nProc, iProcTheta, iProcPhi, &
7.        nTheta, nPhi, &
8.        tmpXPhi0_II,tmpXPhipi_II, &
9.        nThetaLgr,nThetaSml,nPhiLgr,nPhiSml, &
10.        nProcThetaLgr,nProcThetaSml,nProcPhiLgr,nProcPhiSml, &
11.        nR, nTheta, nPhi, Radius_I, SinTheta_I, &
12.        dRadiusNode_I, dTheta_I, dCosTheta_I, dThetaNode_I, dPhiNode_I, &
13.        Br_II, set_boundary, &
14.        RadiusNode_I, Theta_I, SinThetaNode_I, dCosThetaNode_I, &
15.        iRTest, iThetaTest, iPhiTest, ThetaNode_I, Phi_I, PhiNode_I
16. 
17.   use ModReadMagnetogram, ONLY: UseCosTheta, nThetaAll, nPhiAll
18.   use ModMPI
19.   use ModUtilities, ONLY: flush_unit
20.   use ModIoUnit, ONLY: STDOUT_
21. 
22.   implicit none
23. 
24. contains
25.   !============================================================================
26. 
27.   subroutine matvec(x_C, y_C, n)
28. 
29.     use ModPotentialField, ONLY: B0_DF, UsePreconditioner, UseHypre, &
30.          nR, nTheta, d_I, e_I, e1_I, e2_I, f_I, f1_I, f2_I
31.     use ModLinearSolver, ONLY: Lhepta, Uhepta
32.     use ModHypre,        ONLY: hypre_preconditioner
33. 
34.     integer, intent(in) :: n
35.     real, intent(in)    :: x_C(n)
36.     real, intent(out)   :: y_C(n)
37.     !--------------------------------------------------------------------------
38. 
39.     ! Calculate y = laplace x in two steps
40.     call get_gradient(x_C, B0_DF)
41.     call get_divergence(B0_DF, y_C)
42. 
43.     if(UsePreconditioner)then
44.        if(UseHypre)then
45.           call hypre_preconditioner(n, y_C)
46.        else
47.           ! Preconditioning: y'= U^{-1}.L^{-1}.y
48.           call Lhepta(        n, 1, nR, nR*nTheta, y_C, d_I, e_I, e1_I, e2_I)
49.           call Uhepta(.true., n, 1, nR, nR*nTheta, y_C,      f_I, f1_I, f2_I)
50.        end if
51.     end if
52. 
53.   end subroutine matvec
54.   !============================================================================
55. 
56.   subroutine get_gradient(x_C, Grad_DG)
57. 
58.     real, intent(in):: x_C(nR,nTheta,nPhi)
59.     real, intent(out):: Grad_DG(3,nR+1,nTheta+1,nPhi+1)
60. 
61.     real, allocatable, save :: x_G(:,:,:)
62. 
63.     integer:: iR, iTheta, iPhi
64. 
65.     ! real:: r, GradExact_D(3)
66. 
67.     !--------------------------------------------------------------------------
68.     if(.not.allocated(x_G))then
69.        allocate(x_G(0:nR+1,0:nTheta+1,0:nPhi+1))
70.        ! Initialize so that corners are all set
71.        x_G = 0.0
72.     end if
73. 
74.     call set_boundary(x_C, x_G)
75. 
76.     ! This initialization is only for the corners
77.     Grad_DG = 0.0
78. 
79.     do iPhi = 1, nPhi
80.        do iTheta = 1, nTheta
81.           do iR = 1, nR+1
82.              Grad_DG(1,iR,iTheta,iPhi) = &
83.                   (x_G(iR,iTheta,iPhi) - x_G(iR-1,iTheta,iPhi)) &
84.                   / dRadiusNode_I(iR)
85.           end do
86.        end do
87.     end do
88. 
89.     if(UseCosTheta)then
90.        do iPhi = 1, nPhi
91.           do iTheta = 1, nTheta+1
92.              do iR = 1, nR
93.                 Grad_DG(2,iR,iTheta,iPhi) = &
94.                      (x_G(iR,iTheta,iPhi) - x_G(iR,iTheta-1,iPhi)) &
95.                      *SinThetaNode_I(iTheta) &
96.                      / (Radius_I(iR)*dCosThetaNode_I(iTheta))
97.              end do
98.           end do
99.        end do
100.     else
101.        do iPhi = 1, nPhi
102.           do iTheta = 1, nTheta+1
103.              do iR = 1, nR
104.                 Grad_DG(2,iR,iTheta,iPhi) = &
105.                      (x_G(iR,iTheta,iPhi) - x_G(iR,iTheta-1,iPhi)) &
106.                      / (Radius_I(iR)*dThetaNode_I(iTheta))
107.              end do
108.           end do
109.        end do
110.     end if
111. 
112.     do iPhi = 1, nPhi+1
113.        do iTheta = 1, nTheta
114.           do iR = 1, nR
115.              Grad_DG(3,iR,iTheta,iPhi) = &
116.                   (x_G(iR,iTheta,iPhi) - x_G(iR,iTheta,iPhi-1)) &
117.                   / (Radius_I(iR) &
118.                   *max(1e-10,SinTheta_I(iTheta))*dPhiNode_I(iPhi))
119.           end do
120.        end do
121.     end do
122. 
123.     ! Calculate discretization error for the l=m=1 harmonics
124.     ! iR = iRTest; iPhi = iPhiTest; iTheta = iThetaTest
125.     !
126.     ! r = Radius_I(iR)
127.     ! GradExact_D  = (/ &
128.     !     (1+2*rMax**3/RadiusNode_I(iR)**3)/(1+2*rMax**3) &
129.     !     *sin(Theta_I(iTheta))*cos(Phi_I(iPhi)), &
130.     !     (r-rMax**3/r**2)/(1+2*rMax**3)/r &
131.     !     *cos(ThetaNode_I(iTheta))*cos(Phi_I(iPhi)), &
132.     !     -(r-rMax**3/r**2)/(1+2*rMax**3)/r*sin(PhiNode_I(iPhi)) /)
133.     !
134.     ! write(*,*) 'magnetogram at test cell=', Br_II(iTheta,iPhi)
135.     ! do iDim = 1, 3
136.     !   write(*,*) 'Grad, Exact, Error=', &
137.     !        Grad_DG(iDim,iR,iTheta,iPhi), GradExact_D(iDim), &
138.     !        Grad_DG(iDim,iR,iTheta,iPhi) - GradExact_D(iDim)
139.     ! end do
140. 
141.   end subroutine get_gradient
142.   !============================================================================
143. 
144.   subroutine get_divergence(b_DG, DivB_C)
145. 
146.     use ModPotentialField, ONLY: nR, Radius_I, dRadius_I, &
147.          dPhi_I, SinTheta_I, dCosTheta_I, RadiusNode_I, &
148.          SinThetaNode_I, nTheta, nPhi
149. 
150.     real, intent(in) :: b_DG(3,nR+1,nTheta+1,nPhi+1)
151.     real, intent(out):: DivB_C(nR,nTheta,nPhi)
152. 
153.     ! real:: r, DivExact_D(3), Div_D(3)
154.     integer:: iR, iTheta, iPhi
155.     !--------------------------------------------------------------------------
156.     do iPhi = 1, nPhi
157.        do iTheta = 1, nTheta
158.           do iR = 1, nR
159.              DivB_C(iR,iTheta,iPhi) = &
160.                   ( RadiusNode_I(iR+1)**2*b_DG(1,iR+1,iTheta,iPhi)   &
161.                   - RadiusNode_I(iR)**2  *b_DG(1,iR  ,iTheta,iPhi) ) &
162.                   / (Radius_I(iR)**2 *dRadius_I(iR)) &
163.                   + &
164.                   ( SinThetaNode_I(iTheta+1)*b_DG(2,iR,iTheta+1,iPhi)   &
165.                   - SinThetaNode_I(iTheta)  *b_DG(2,iR,iTheta  ,iPhi) ) &
166.                   / (Radius_I(iR)*dCosTheta_I(iTheta)) &
167.                   + &
168.                   ( b_DG(3,iR,iTheta,iPhi+1) &
169.                   - b_DG(3,iR,iTheta,iPhi) ) &
170.                   / (Radius_I(iR)*max(1e-10,SinTheta_I(iTheta))*dPhi_I(iPhi))
171.           end do
172.        end do
173.     end do
174. 
175.     ! Calculate discretization error for the l=m=1 harmonics
176.     ! iR = iRTest; iPhi = iPhiTest; iTheta = iThetaTest
177.     ! r = Radius_I(iR)
178.     !
179.     ! Div_D(1) = ( RadiusNode_I(iR+1)**2*b_DG(1,iR+1,iTheta,iPhi)   &
180.     !     - RadiusNode_I(iR)**2  *b_DG(1,iR  ,iTheta,iPhi) ) &
181.     !     / (Radius_I(iR)**2 *dRadius_I(iR))
182.     !
183.     ! Div_D(2) = ( SinThetaNode_I(iTheta+1)*b_DG(2,iR,iTheta+1,iPhi)   &
184.     !     - SinThetaNode_I(iTheta)  *b_DG(2,iR,iTheta  ,iPhi) ) &
185.     !     / (Radius_I(iR)*dCosTheta_I(iTheta))
186.     !
187.     ! Div_D(3) = ( b_DG(3,iR,iTheta,iPhi+1) - b_DG(3,iR,iTheta,iPhi) ) &
188.     !     / (Radius_I(iR)*SinTheta_I(iTheta)*dPhi_I(iPhi))
189.     !
190.     ! DivExact_D = &
191.     !     (/ 2*SinTheta_I(iTheta), &
192.     !     (1-SinTheta_I(iTheta)**2)/SinTheta_I(iTheta), &
193.     !     - 1/SinTheta_I(iTheta) /)
194.     !
195.     ! DivExact_D = DivExact_D &
196.     !     *(r-rMax**3/r**2)/(1+2*rMax**3)/r**2*cos(Phi_I(iPhi))
197.     !
198.     ! do iDim = 1, 3
199.     !   write(*,*) 'Div_D, Exact, Error=', Div_D(iDim), DivExact_D(iDim), &
200.     !        Div_D(iDim) - DivExact_D(iDim)
201.     ! end do
202.     !
203.     ! write(*,*)'testlaplace=', DivB_C(iR,iTheta,iPhi)
204.     ! write(*,*)'location   =', maxloc(abs(DivB_C))
205.     ! write(*,*)'max laplace=', maxval(abs(DivB_C))
206.     ! write(*,*)'avg laplace=', sum(abs(DivB_C))/(nR*nThetaAll*nPhiAll)
207.     !
208.     ! stop
209. 
210.   end subroutine get_divergence
211.   !============================================================================
212. 
213. end module ModB0Matvec
214. !==============================================================================
215. 
216. program potential_field
217. 
218.   ! Solve 3D potential field with given Br at inner boundary,
219.   ! radial field at outer boundary.
220.
```

</details>


---

<sub>⏱️ 2m 33s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/Makefile.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/Makefile (lines 1-120)

<details>
<summary>65 lines</summary>

```
1. include ../../Makefile.def
2. 
3. check_src:
4. 	@(if([ ! -f src/Makefile ]); then \
5. 		echo "The src/Makefile is missing!"; \
6. 		echo "make SCBATSRUS"; \
7. 		exit 1; \
8. 	fi)
9. 
10. install:
11. 	@(if([ -f src/Makefile ]); then \
12. 		cp -f src/ModOptimizeParam_orig.f90 src/ModOptimizeParam.f90; \
13. 		cp -f srcBATL/BATL_size_orig.f90 srcBATL/BATL_size.f90; \
14. 	fi)
15. 
16. LIB: check_src
17. 	cd srcBATL; $(MAKE) LIB
18. 	cd src; $(MAKE) LIB
19. 	cd srcInterface; $(MAKE) LIB
20. 
21. test:
22. 	@echo SC/BATSRUS is tested in GM/BATSRUS
23. 
24. rundir: check_src
25. 	mkdir ${RUNDIR}/SC
26. 	cd ${RUNDIR}/SC; \
27. 		mkdir restartIN restartOUT IO2; \
28. 		ln -s IO2 plots; \
29. 		ln -s ${BINDIR}/PostIDL.exe .; \
30. 		ln -s ${BINDIR}/FDIPS.exe .; \
31. 		ln -s ${BINDIR}/HARMONICS.exe .; \
32. 		ln -s ${BINDIR}/CONVERTHARMONICS.exe .; \
33. 		ln -s ${BINDIR}/FRMAGNETOGRAM.exe .; \
34. 		ln -s ${BINDIR}/ELIMINATECMEBR.exe .; \
35. 		cp ${MAGNETOGRAMDIR}/HARMONICS.in.orig \
36. 		HARMONICS.in; \
37. 		cp ${MAGNETOGRAMDIR}/HARMONICSGRID.in.orig \
38. 		HARMONICSGRID.in; \
39. 		ln -s ${MAGNETOGRAMDIR}/remap_magnetogram.py .; \
40. 		ln -s ${MAGNETOGRAMDIR}/read_magnetogram.pro .; \
41. 		ln -s ${MAGNETOGRAMDIR}/readfits.pro .; \
42. 		ln -s ${MAGNETOGRAMDIR}/*SETUP*py .; \
43. 		ln -s ${MAGNETOGRAMDIR}/*SETUP*pro .; \
44. 		cp    ${DIR}/share/Scripts/pIDL .; \
45. 		cp    ${DIR}/GM/BATSRUS/Scripts/TEC/pTEC .; \
46. 		ln -s ${DIR}/GM/BATSRUS/Param/CORONA Param; \
47. 		ln -s ${DIR}/GM/BATSRUS/data/TRAJECTORY .
48. 
49. clean:  
50. 	@(if([ -f src/Makefile ]); then \
51. 	   cd src; make clean; cd ..; \
52. 	   cd srcBATL; make clean; cd ..; \
53. 	   cd srcInterface; make clean; \
54. 	fi)
55. 
56. distclean: 
57. 	./Config.pl -uninstall
58. 
59. allclean:
60. 	@(if([ -f Makefile.def ]); then \
61. 		cd srcInterface; make distclean; \
62. 	fi)
63. 	rm -rf src srcBATL srcUser srcEquation \
64. 		PARAM.XML RenameList.pl Config.pl *~
65.
```

</details>


---

<sub>⏱️ 2m 45s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90 (lines 216-360)

<details>
<summary>145 lines</summary>

```
216. program potential_field
217. 
218.   ! Solve 3D potential field with given Br at inner boundary,
219.   ! radial field at outer boundary.
220. 
221.   use ModPotentialField
222.   use ModB0Matvec, ONLY: get_gradient, get_divergence, matvec
223.   use ModLinearSolver, ONLY: bicgstab, prehepta
224.   use ModHypre,        ONLY: hypre_initialize, hypre_solver
225.   use ModPlotFile, ONLY: save_plot_file
226.   use ModUtilities, ONLY: flush_unit
227.   use ModIoUnit, ONLY: STDOUT_
228.   use ModMpi
229.   use ModReadMagnetogram, ONLY: UseCosTheta, nThetaAll, nPhiAll
230. 
231.   implicit none
232. 
233.   integer :: nIter=10000
234.   real    :: r, DivBMax, DivBMaxAll
235.   integer :: n, i, iError, iR, iPhi, iTheta
236.   !----------------------------------------------------------------------------
237. 
238.   call MPI_init(iError)
239.   call MPI_comm_rank(iComm,iProc,iError)
240.   call MPI_comm_size(iComm,nProc,iError)
241. 
242.   call read_fdips_param
243. 
244.   if(DoReadMagnetogram .and. iProc == 0) call read_modified_magnetogram
245. 
246. !  nThetaAll = nThetaCoarse
247. !  nPhiAll = nPhiCoarse
248. !  write(*,*)'nTHetaCoarse, nPhiCoarse in FDIPS.f90',nThetaAll, nPhiAll
249. 
250.   call MPI_bcast(UseCosTheta, 1, MPI_LOGICAL, 0, iComm, iError)
251.   call MPI_bcast(nThetaAll, 1, MPI_INTEGER, 0, iComm, iError)
252.   call MPI_bcast(nPhiAll,   1, MPI_INTEGER, 0, iComm, iError)
253.   if (.not. allocated(Br_II)) allocate(Br_II(nThetaAll,nPhiAll))
254. 
255.   call MPI_bcast(Br_II, nThetaAll*nPhiAll, MPI_REAL, 0,  iComm, iError)
256. 
257.   if(UseTiming) TimeStart = mpi_wtime()
258. 
259.   call init_potential_field
260.   if (IsProcIdle) then
261.     call MPI_FINALIZE(iError)
262.     STOP
263.   endif
264. 
265.   if(.not.DoReadMagnetogram)then
266.      allocate(Br_II(nThetaAll,nPhiAll))
267.      do iPhi = 1, nPhiAll; do iTheta = 1, nThetaAll;
268.         ! magnetogram proportional to the l=m=n harmonics
269.         n = 1 ! or 2
270.         Br_II(iTheta,iPhi) = sin(Theta_I(iTheta))**n *cos(n*Phi_I(iPhi))
271. 
272.         ! Exact solution
273.         do iR = 1, nR
274.            r = Radius_I(iR)
275.            Potential_C(iR,iTheta,iPhi) = Br_II(iTheta,iPhi) &
276.                 * (r**n - rMax**(2*n+1)/r**(n+1)) &
277.                 / (n    + (n+1)*rMax**(2*n+1))
278.         end do
279.      end do; end do
280. 
281.      write(*,*)'rTest    =',Radius_I(iRTest)
282.      write(*,*)'PhiTest  =',Phi_I(iPhiTest)
283.      write(*,*)'ThetaTest=',Theta_I(iThetaTest)
284.      write(*,*)'BrTest   =',Br_II(iThetaTest,iPhiTest)
285.      write(*,*)'PotTest  =',Potential_C(iRTest,iThetaTest,iPhiTest)
286. 
287.   end if
288. 
289.   n = nR*nTheta*nPhi
290.   ! write(*,*) 'iProc, n', iProc, n
291. 
292.   if(UsePreconditioner .or. UseHypre)then
293. 
294.      allocate(d_I(n), e_I(n), f_I(n), e1_I(n), f1_I(n), e2_I(n), f2_I(n))
295. 
296.      i = 0
297.      do iPhi = 1, nPhi; do iTheta = 1, nTheta; do iR = 1, nR
298. 
299.         i = i + 1
300.         e_I(i)  = RadiusNode_I(iR)**2 &
301.              /(Radius_I(iR)**2 * dRadiusNode_I(iR) * dRadius_I(iR))
302. 
303.         f_I(i)  = RadiusNode_I(iR+1)**2 &
304.              /(Radius_I(iR)**2 * dRadiusNode_I(iR+1) * dRadius_I(iR))
305. 
306.         if(UseCosTheta)then
307.            e1_I(i) = SinThetaNode_I(iTheta)**2 / &
308.                 (Radius_I(iR)**2 * dCosThetaNode_I(iTheta)  *dCosTheta_I(iTheta))
309. 
310.            f1_I(i) = SinThetaNode_I(iTheta+1)**2 /&
311.                 (Radius_I(iR)**2 * dCosThetaNode_I(iTheta+1)*dCosTheta_I(iTheta))
312.         else
313.            e1_I(i) = SinThetaNode_I(iTheta) / &
314.                 (Radius_I(iR)**2 * dThetaNode_I(iTheta)  *dCosTheta_I(iTheta))
315. 
316.            f1_I(i) = SinThetaNode_I(iTheta+1) /&
317.                 (Radius_I(iR)**2 * dThetaNode_I(iTheta+1)*dCosTheta_I(iTheta))
318.         end if
319. 
320.         ! e1_I(i) = 0.0
321. 
322.         ! f1_I(i) = 0.0
323. 
324.         e2_I(i) = 1/(Radius_I(iR)**2 * SinTheta_I(iTheta)**2 &
325.              * dPhiNode_I(iPhi) * dPhi_I(iPhi))
326. 
327.         ! e2_I(i) = 0.0
328. 
329.         f2_I(i) = 1/(Radius_I(iR)**2 * SinTheta_I(iTheta)**2 &
330.              * dPhiNode_I(iPhi+1) * dPhi_I(iPhi))
331. 
332.         ! f2_I(i) = 0.0
333. 
334.         d_I(i)  = -(e_I(i) + f_I(i) + e1_I(i) + f1_I(i) + e2_I(i) + f2_I(i))
335. 
336.         if(iR     == 1)      d_I(i)  = d_I(i) + e_I(i) ! inner BC
337.         if(iR     == 1)      e_I(i)  = 0.0
338.         if(iR     == nR)     d_I(i)  = d_I(i) - f_I(i) ! outer BC
339.         if(iR     == nR)     f_I(i)  = 0.0
340. 
341.         if (iProcTheta ==0) then
342.            if(iTheta == 1)      e1_I(i) = 0.0
343.         end if
344.         if (iProcTheta == nProcTheta-1) then
345.            if(iTheta == nTheta) f1_I(i) = 0.0
346.         end if
347. 
348.         if(.not.UseHypre)then
349.            if (iProcPhi == 0) then
350.               if(iPhi   == 1)   e2_I(i) = 0.0
351.            end if
352.            if (iProcPhi == nProcPhi-1) then
353.               if(iPhi   == nPhi)f2_I(i) = 0.0
354.            end if
355.         end if
356.      end do; end do; end do
357. 
358.      ! A -> LU
359.      if(.not.UseHypre)call prehepta(n, 1, nR, nR*nTheta, PrecondParam, &
360.           d_I, e_I, f_I, e1_I, f1_I, e2_I, f2_I)
```

</details>


---

<sub>⏱️ 2m 45s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "program\\s+potential_field|call\\s+read_fdips_param|call\\s+read_modified_magnetogram|call\\s+save_potential_field|call\\s+solve|call\\s+init_potential_field",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90",
  "output_mode": "content",
  "-n": true,
  "head_limit": 200
}
```

</details>

<details>
<summary>6 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90:216:program potential_field
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90:242:  call read_fdips_param
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90:244:  if(DoReadMagnetogram .and. iProc == 0) call read_modified_magnetogram
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90:259:  call init_potential_field
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90:437:    call save_potential_field
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90:442:end program potential_field
```

</details>


---

<sub>⏱️ 2m 45s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "subroutine\\s+read_harmonics_param|call\\s+read_magnetogram_param|#MAGNETOGRAMFILE|#OUTPUT|#HARMONICS",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90",
  "output_mode": "content",
  "-n": true,
  "head_limit": 260
}
```

</details>

<details>
<summary>6 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90:72:  subroutine read_harmonics_param
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90:90:       case("#HARMONICS")
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90:92:       case("#OUTPUT")
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90:94:       case("#MAGNETOGRAMFILE", "#CHEBYSHEV", '#CHANGEWEAKFIELD',&
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90:96:          call read_magnetogram_param(NameCommand)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90:104:  end subroutine read_harmonics_param
```

</details>


---

<sub>⏱️ 2m 45s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90 (lines 1-220)

<details>
<summary>220 lines</summary>

```
1. !  Copyright (C) 2002 Regents of the University of Michigan,
2. !  portions used with permission
3. !  For more information, see http://csem.engin.umich.edu/tools/swmf
4. module ModMagHarmonics
5. 
6.   use ModNumConst
7.   use ModUtilities, ONLY: CON_stop
8.   use ModReadMagnetogram, ONLY: dPhi, dTheta, dSinTheta
9. 
10.   implicit none
11. 
12.   ! **********************Choice of this parameter**********************
13.   ! *Sin(Latitude): WSO : http://wso.stanford.edu                      *
14.   ! *   MDI: see http://soi.stanford.edu/magnetic/index6.html          *
15.   ! *   SOLIS:http://solis.nso.edu/vsm/map_info.html                   *
16.   ! *   GONG: http://gong.nso.edu/data/magmap/index.html               *
17.   ! ********************************************************************
18. 
19.   ! This Module reads a raw (RADIAL, not LOS!!!) magnetogram data file and
20.   ! generates a magnetogram file in the form of spherical
21.   ! harmonics to be used by the SWMF.
22. 
23.   ! ************************ Data Links ********************************
24.   ! * MDI:   http://soi.stanford.edu/magnetic/index6.html              *
25.   ! * WSO:   http://wso.stanford.edu/forms/prgs.html                   *
26.   ! * GONG:  http://gong.nso.edu/data/magmap/QR/mqs/                   *
27.   ! * SOLIS: ftp://solis.nso.edu/synoptic/level3/vsm/merged/carr-rot   *
28.   ! * MWO:   ftp://howard.astro.ucla.edu/pub/obs/synoptic_charts       *
29.   ! ********************************************************************
30.   ! * Field in Gauss: MDI,GONG,SOLIS                                   *
31.   ! * Field in microTesla(0.01Gs): WSO, MWO                            *
32.   ! ********************************************************************
33. 
34.   ! Name of output file
35.   character (len=100):: NameFileOut='harmonics.dat'
36. 
37.   integer, public:: i,n,m,iTheta,iPhi,iR,mm,nn
38.   real, allocatable:: Br_II(:,:)
39.   real:: dR=1.0
40.   integer:: nPhi=72, nTheta=29
41. 
42.   integer, parameter:: MaxHarmonics = 1800
43.   integer:: nHarmonics = MaxHarmonics, nHarmonicsIn = MaxHarmonics
44. 
45.   real:: CosTheta,SinTheta
46.   real:: stuff1,stuff2,stuff3
47.   real:: Theta,Phi
48. 
49.   real :: SumArea,da
50.   real :: NormalizationFactor
51.   integer :: iUnit2, iNM
52.   real,allocatable,dimension(:) :: gArray, hArray
53.   integer,allocatable,dimension(:) :: nArray, mArray
54.   integer :: SizeOfnm, ArrPerProc,EndProc,SizeLastProc
55.   real, allocatable, dimension(:,:)   :: p_nm, CosMPhi_II,SinMPhi_II
56.   real, allocatable, dimension(:,:,:) :: PNMTheta_III
57. 
58.   real:: SinThetaM, SinThetaM1
59.   integer:: delta_m0
60.   real, allocatable:: FactRatio1(:)
61.   integer:: MaxInt
62.   real, allocatable:: Sqrt_I(:)
63. 
64.   real, allocatable, dimension(:) :: ChebyshevWeightE_I, ChebyshevWeightW_I
65.   ! For integrating on subgrid in Theta, should be even integer:
66.   integer :: nSubGrid = 1
67.   ! If subgrid is used the polar fix can be applied reducing the error in the
68.   ! polar domain
69. contains
70.   !============================================================================
71. 
72.   subroutine read_harmonics_param
73. 
74.     use ModReadParam
75.     use ModReadMagnetogram, ONLY: read_magnetogram_param
76.     use ModMpi,             ONLY: MPI_COMM_SELF
77. 
78.     character(len=lStringLine) :: NameCommand
79. 
80.     character(len=*), parameter:: NameSub = 'read_harmonics_param'
81.     !--------------------------------------------------------------------------
82.     call read_file('HARMONICS.in', iCommIn = MPI_COMM_SELF)
83.     call read_init
84.     call read_echo_set(.true.)
85. 
86.     do
87.        if(.not.read_line() ) EXIT
88.        if(.not.read_command(NameCommand)) CYCLE
89.        select case(NameCommand)
90.        case("#HARMONICS")
91.           call read_var('nHarmonics', nHarmonicsIn)
92.        case("#OUTPUT")
93.           call read_var('NameFileOut', NameFileOut)
94.        case("#MAGNETOGRAMFILE", "#CHEBYSHEV", '#CHANGEWEAKFIELD',&
95.             '#CHANGEPOLARFIELD','#USEMAGNETOGRAMDATE')
96.           call read_magnetogram_param(NameCommand)
97.        case("#SUBGRID")
98.           call read_var('nSubGrid', nSubGrid)
99.        case default
100.           call CON_stop(NameSub//': unknown command='//trim(NameCommand))
101.        end select
102.     end do
103. 
104.   end subroutine read_harmonics_param
105.   !============================================================================
106.   subroutine read_modified_magnetogram
107. 
108.     use ModReadMagnetogram, ONLY: read_orig_magnetogram, nTheta0, nPhi0, &
109.          nThetaorig, nPhiorig
110. 
111.     character(len=*), parameter:: NameSub = 'read_modified_magnetogram'
112.     !--------------------------------------------------------------------------
113.     call read_orig_magnetogram
114. 
115.     nTheta = nTheta0
116.     nPhi   = nPhi0
117.     write(*,*)NameSub,': Original nTheta, nPhi =', nThetaorig, nPhiorig
118.     write(*,*)NameSub,': Remeshed nTheta, nPhi =', nTheta0, nPhi0
119. 
120.     ! Setting the order on harmonics to be equal to the
121.     ! latitudinal resolution.
122.     if(nHarmonicsIn > 0 .and. nHarmonicsIn < MaxHarmonics)then
123.        nHarmonics = nHarmonicsIn
124.     else
125.        nHarmonics = min(nThetaorig, MaxHarmonics)
126.     endif
127.     write(*,*)'Order of harmonics: ',nHarmonics
128. 
129.     ! Allocate the harmonic coefficients arrays
130.     allocate( &
131.          p_nm(nHarmonics+1,nHarmonics+1), &
132.          FactRatio1(nHarmonics+1))
133. 
134.     p_nm = 0.0
135. 
136.   end subroutine read_modified_magnetogram
137.   !============================================================================
138.   subroutine calc_harmonics
139. 
140.     ! This subroutine calculates the spherical harmonics from the
141.     !  modified - remesed magnetogram data
142. 
143.     use ModPlotFile, ONLY: save_plot_file
144.     use ModReadMagnetogram, ONLY: Br0_II, nTheta0, nPhi0, UseChebyshevNode, &
145.          MagnetogramTimeCR, LongShift, UseCosTheta, nThetaOrig, nPhiorig, &
146.          ChebyshevWeightE_I, ChebyshevWeightW_I, dPhi, dTheta, dSinTheta, &
147.          StringMagHeader
148. 
149.     integer :: iTheta, iPhi, m,inm, nn, mm
150.     real    :: dThetaChebyshev, dLon = 0.0
151.     real    :: CRFraction, CRNumber
152.     real, allocatable:: Br_II(:,:), Coord_DII(:,:,:), Var_VI(:,:)
153.     ! Subgrid computations:
154.     real    :: PolarField
155.     integer :: iSubGrid, nSubGrid2
156.     !--------------------------------------------------------------------------
157.     write(*,*)'Calculating harmonic coefficients'
158. 
159.     allocate(Sqrt_I(nHarmonics**2))
160.     MaxInt = nHarmonics**2
161.     ! Calculate sqrt(integer) from 1 to 10000::
162.     do m=1,MaxInt
163.        Sqrt_I(m) = sqrt(real(m))
164.     end do
165. 
166.     ! Calculate the ratio sqrt(2m!)/(2^m*m!)::
167.     factRatio1(:) = 0.0; factRatio1(1) = 1.0
168.     do m=1,nHarmonics
169.        factRatio1(m+1) = factRatio1(m)*Sqrt_I(2*m-1)/Sqrt_I(2*m)
170.     enddo
171. 
172.     ! If Chebyshev is done then remeshed theta & phi are used, else
173.     ! original values are used.
174.     if(UseChebyshevNode) then
175.        nTheta = nTheta0
176.        nPhi   = nPhi0
177.     else
178.        nTheta = nThetaorig
179.        nPhi   = nPhiorig
180.     endif
181. 
182.     ! LongShift is the starting Carrington longitude of the magnetogram
183.     ! Add the longitude width of a half cell (=180/nPhi) for cell centers
184.     ! dLon rotates the longitude into actual HGR/Carrington longitude
185.     dLon = LongShift + 180.0/nPhi
186.     if(nSubGrid==2*(nSubGrid/2))then
187.        nTheta = nTheta*nSubGrid
188.        dSinTheta = dSinTheta/nSubGrid
189.        nSubGrid2 = nSubGrid/2
190.        allocate(Br_II(0:nPhi-1,0:nTheta-1))
191.        ! Fix Southern pole value:
192.        ! PolarField = sum(Br0_II(:,1),1)/nPhi
193.        do iSubGrid = 0, nSubGrid2 - 1
194.           Br_II(:,iSubGrid) = Br0_II(:,1)
195.           ! (  (0.50 + iSubgrid)*Br0_II(:,1) +&
196.           ! (nSubgrid2 -iSubgrid - 0.5)*PolarField ) / nSubgrid2
197.        end do
198.        do iTheta = 1, nThetaOrig-1
199.           do iSubGrid = 0, nSubGrid - 1
200.              Br_II(:,iTheta*nSubGrid - nSubGrid2 + iSubGrid) = (&
201.                   (0.50 + iSubgrid)*Br0_II(:,iTheta+1) + &
202.                   (nSubgrid - iSubgrid - 0.5)*Br0_II(:,iTheta))/nSubGrid
203.           end do
204.        end do
205.        ! Fix Northern pole value:
206.        ! PolarField = sum(Br0_II(:,nThetaOrig),1)/nPhi
207.        do iSubGrid = 0, nSubGrid2 - 1
208.           Br_II(:,nTheta-nSubGrid2+iSubGrid) = Br0_II(:,nThetaOrig)
209.           !((0.50 + iSubgrid)*PolarField &
210.           !+ (nSubgrid2 -iSubgrid - 0.5)*Br0_II(:,nThetaOrig))/nSubgrid2
211.        end do
212.     else
213.        allocate(Br_II(0:nPhi-1,0:nTheta-1))
214.        Br_II=Br0_II
215.     end if
216. 
217.     if(UseChebyshevNode) then
218.        allocate(PNMTheta_III(nHarmonics+1,nHarmonics+1,0:nTheta-1))
219.        PNMTheta_III = 0.0
220.        dThetaChebyshev = cPi/(nTheta-1)
```

</details>


---

<sub>⏱️ 2m 54s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90 (lines 360-455)

<details>
<summary>85 lines</summary>

```
360.           d_I, e_I, f_I, e1_I, f1_I, e2_I, f2_I)
361. 
362.   end if
363. 
364.   if(UseHypre)call hypre_initialize
365. 
366.   UseBr = .true.
367.   call matvec(Potential_C, Rhs_C, n)
368.   Rhs_C = -Rhs_C
369. 
370.   UseBr = .false.
371. 
372.   call flush_unit(STDOUT_)
373.   call mpi_barrier(iComm, iError)
374. 
375.   if(UseHypre .and. .not.UsePreconditioner)then
376.      call hypre_solver
377.   else
378.      call bicgstab(matvec, Rhs_C, Potential_C, .false., n, &
379.           Tolerance, 'rel', nIter, iError, DoTest=DoTestMe, iCommIn=iComm)
380.   end if
381. 
382.   UseBr = .true.
383. 
384.   if(UseTiming) TimeEnd = mpi_wtime()
385.   if(iProc == 0) &
386.        write(*,*)'nIter, Tolerance, iError=', nIter, Tolerance, iError
387. 
388.   ! report maximum divb
389.   call get_gradient(Potential_C, B0_DF)
390.   call get_divergence(B0_DF, DivB_C)
391.   DivbMax = maxval(abs(DivB_C))
392.   if(nProc > 1)then
393.      call MPI_reduce(DivBMax, DivBMaxAll, 1, MPI_REAL, MPI_MAX, 0, &
394.           iComm, iError)
395.      if(iProc==0) DivBMax = DivBMaxAll
396.   end if
397.   if(iProc ==0)then
398.      write(*,*) 'max(abs(divb)) = ', DivBMax
399.      write(*,*) 'nProcTheta, nProcPhi=', nProcTheta, nProcPhi
400.   end if
401.   if(UseTiming) write(*,*) 'running time=', TimeEnd - TimeStart
402. 
403.   if(DoSavePotential)then
404.      allocate(PlotVar_VC(6,nR,nTheta,nPhi))
405.      PlotVar_VC = 0.0
406.      PlotVar_VC(1,:,:,:) = Potential_C
407.      PlotVar_VC(2,:,:,:) = &
408.           0.5*(B0_DF(1,1:nR,1:nTheta,1:nPhi) + &
409.           B0_DF(1,2:nR+1,1:nTheta,1:nPhi))
410.      PlotVar_VC(3,:,:,:) = &
411.           0.5*(B0_DF(2,1:nR,1:nTheta,1:nPhi) + &
412.           B0_DF(2,1:nR,2:nTheta+1,1:nPhi))
413.      PlotVar_VC(4,:,:,:) = &
414.           0.5*(B0_DF(3,1:nR,1:nTheta,1:nPhi) + &
415.           B0_DF(3,1:nR,1:nTheta,2:nPhi+1))
416.      PlotVar_VC(5,:,:,:) = DivB_C
417.      PlotVar_VC(6,:,:,:) = Rhs_C
418. 
419.      ! Note the fake processor index to be used by redistribute.pl
420.      write(NameFile,'(a,2i2.2,a,i3.3,a)') &
421.           trim(NameFilePotential)//'_np01', nProcTheta, nProcPhi,'_', &
422.           iProcTheta + iProcPhi*nProcTheta, '.out'
423. 
424.      ! Save divb, potential and RHS for testing purposes
425.      call save_plot_file(NameFile, TypeFileIn=TypeFilePotential, &
426.           StringHeaderIn='potential field', &
427.           NameVarIn='r theta phi pot br btheta bphi divb rhs', &
428.           Coord1In_I=Radius_I(1:nR), &
429.           Coord2In_I=Theta_I(1:nTheta), &
430.           Coord3In_I=Phi_I(1:nPhi), &
431.           VarIn_VIII=PlotVar_VC)
432. 
433.      deallocate(PlotVar_VC)
434.   end if
435. 
436.   if (.not. IsProcIdle) then
437.     call save_potential_field
438.   endif
439. 
440.   call MPI_FINALIZE(iError)
441. 
442. end program potential_field
443. !==============================================================================
444.
```

</details>


---

<sub>⏱️ 2m 54s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "save_potential_field|NameFileBxyz|fdips_bxyz|harmonics_bxyz|LOOKUPTABLE",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram",
  "output_mode": "content",
  "-n": true,
  "head_limit": 300
}
```

</details>

<details>
<summary>35 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/TDSETUPAlg.py:450:      FileId.write("#LOOKUPTABLE \n")
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/TDSETUPAlg.py:453:      FileId.write("harmonics_bxyz.out	NameFile \n")
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/TDSETUPAlg.py:555:      FileId.write("#LOOKUPTABLE \n")
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/TDSETUPAlg.py:558:      FileId.write("harmonics_bxyz.out	NameFile \n")
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/fdips.ref:44:fdips_bxyz.out		NameFileField		NameFileBxyz
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90:437:    call save_potential_field
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP.py:202:      FileId.write("#LOOKUPTABLE \n")
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP.py:205:      FileId.write("harmonics_bxyz.out		NameFile \n")
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90:40:  character(len=100):: NameFileBxyz = 'potentialBxyz.out'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90:184:             call read_var('NameFileBxyz', NameFileBxyz)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90:508:  subroutine save_potential_field
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90:732:                  NameFileBxyz, TypeFileIn=TypeFileBxyz, &
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90:743:                  NameFileBxyz, TypeFileIn=TypeFileBxyz, &
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90:803:  end subroutine save_potential_field
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/fdips_hypre.ref:44:fdips_bxyz.out		NameFileField		NameFileBxyz
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/potential_field.f90:314:  subroutine save_potential_field
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/potential_field.f90:412:  end subroutine save_potential_field
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/potential_field.f90:792:  call save_potential_field
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModOpenClosedBoundary.f90:13:  character(len=100):: NameB0File = 'harmonics_bxyz.out'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.in.orig:100:! "bxyz" output file type using "#LOOKUPTABLE" "B0" and "B0NEW" in PARAM.in.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.in.orig:104:fdips_bxyz.out		NameFileField
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90:39:  character(len=100):: NameFileBxyz = 'potentialBxyz'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90:185:             call read_var('NameFileBxyz', NameFileBxyz)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90:188:             i = index(NameFileBxyz,'.out')
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90:189:             if(i>0) NameFileBxyz = NameFileBxyz(1:i-1)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90:484:  subroutine save_potential_field
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90:667:            trim(NameFileBxyz)//'_np01', nProcPhi, nProcTheta, '_', &
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90:778:  end subroutine save_potential_field
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/Makefile:265:		fdips_bxyz.out \
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/Makefile:266:		fdips_bxyz_ref.out.gz >> test_fdips.diff
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/README:106:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/README:109:SC/fdips_bxyz.out               NameFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/BOUNDARY.in:2:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/open_closed_boundary.f90:25:     case('#LOOKUPTABLE')
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagnetogram.f90:146:            NameFile    = 'harmonics_bxyz.out',    &
```

</details>


---

<sub>⏱️ 2m 54s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90 (lines 360-520)

<details>
<summary>161 lines</summary>

```
360.        write(*,*) 'Partitioning in nThetaAll gives: ', &
361.             nThetaLgr*nProcThetaLgr + nThetaSml*nProcThetaSml, &
362.             'Actual nThetaAll is: ', nThetaAll
363.        write(*,*) 'Partitioning in nPhiAll gives:   ', &
364.             nPhiLgr*nProcPhiLgr + nPhiSml*nProcPhiSml, &
365.             'Actual nPhiAll is:   ', nPhiAll
366.     end if
367. 
368.     ! Both iProcTheta and iProcPhi in the large region
369.     if (iProcTheta < nProcThetaLgr .and. iProcPhi < nProcPhiLgr) then
370.        nTheta = nThetaLgr
371.        nPhi   = nPhiLgr
372.        iTheta0 = iProcTheta* nThetaLgr
373.        iPhi0   = iProcPhi  * nPhiLgr
374.     end if
375. 
376.     ! Only iProcTheta in the large region
377.     if (iProcTheta < nProcThetaLgr .and. iProcPhi >= nProcPhiLgr) then
378.        nTheta = nThetaLgr
379.        nPhi   = nPhiSml
380.        iTheta0 = iProcTheta  * nThetaLgr
381.        iPhi0   = nProcPhiLgr * nPhiLgr + (iProcPhi - nProcPhiLgr)*nPhiSml
382.     end if
383. 
384.     ! Only iProcPhi in the large region
385.     if (iProcTheta >= nProcThetaLgr .and. iProcPhi < nProcPhiLgr) then
386.        nTheta  = nThetaSml
387.        nPhi    = nPhiLgr
388.        iTheta0 = nProcThetaLgr * nThetaLgr + &
389.             (iProcTheta - nProcThetaLgr)*nThetaSml
390.        iPhi0   = iProcPhi      * nPhiLgr
391.     end if
392. 
393.     ! Both iProcTheta and iProcPhi in the small region
394.     if (iProcTheta >= nProcThetaLgr .and. iProcPhi >= nProcPhiLgr) then
395.        nTheta = nThetaSml
396.        nPhi   = nPhiSml
397.        iTheta0 = nProcThetaLgr*nThetaLgr &
398.             + (iProcTheta - nProcThetaLgr)*nThetaSml
399.        iPhi0   = nProcPhiLgr  *nPhiLgr   &
400.             + (iProcPhi   - nProcPhiLgr)  *nPhiSml
401.     end if
402. 
403.     allocate( BrLocal_II(nTheta,nPhi), &
404.          Radius_I(0:nR+1), Theta_I(0:nTheta+1), Phi_I(0:nPhi+1), &
405.          dRadius_I(nR), dPhi_I(nPhi), &
406.          SinTheta_I(0:nTheta+1), dTheta_I(nTheta), dCosTheta_I(nTheta), &
407.          SinThetaNode_I(nTheta+1), dCosThetaNode_I(nTheta+1), &
408.          RadiusNode_I(nR+1), ThetaNode_I(nTheta+1), PhiNode_I(nPhi+1), &
409.          dRadiusNode_I(nR+1), dThetaNode_I(nTheta+1), dPhiNode_I(nPhi+1) , &
410.          Potential_C(nR,nTheta,nPhi), &
411.          Rhs_C(nR,nTheta,nPhi), &
412.          B0_DF(3,nR+1,nTheta+1,nPhi+1), &
413.          DivB_C(nR,nTheta,nPhi))
414. 
415.     ! Set BrLocal_II, this is used in set_boundary when UseBr is true
416.     BrLocal_II(:,:) = Br_II(iTheta0+1:iTheta0+nTheta,iPhi0+1:iPhi0+nPhi)
417. 
418.     ! nR is the number of mesh cells in radial direction
419.     ! cell centered radial coordinate
420. 
421.     if(UseLogRadius)then
422.        dLogR = log(rMax/rMin)/nR
423.        do iR = 0, nR+1
424.           Radius_I(iR) = rMin*exp( (iR - 0.5)*dLogR )
425.        end do
426.        ! node based radial coordinate
427.        do iR = 1, nR+1
428.           RadiusNode_I(iR) = rMin*exp( (iR - 1)*dLogR )
429.        end do
430. 
431.     else
432.        dR = (rMax - rMin)/nR
433.        do iR = 0, nR+1
434.           Radius_I(iR) = rMin + (iR - 0.5)*dR
435.        end do
436.        ! node based radial coordinate
437.        do iR = 1, nR+1
438.           RadiusNode_I(iR) = rMin + (iR - 1)*dR
439.        end do
440.     end if
441. 
442.     dRadius_I     = RadiusNode_I(2:nR+1) - RadiusNode_I(1:nR)
443.     dRadiusNode_I = Radius_I(1:nR+1) - Radius_I(0:nR)
444. 
445.     if(UseCosTheta)then
446.        dZ = 2.0/nThetaAll
447. 
448.        do iTheta = 0, nTheta+1
449.           z = max(-1.0, min(1.0, 1 - (iTheta + iTheta0 - 0.5)*dZ))
450.           Theta_I(iTheta) = acos(z)
451.        end do
452. 
453.        ! Set the boundary condition of Theta_I
454.        if (iProcTheta == 0) &
455.             Theta_I(0) = -Theta_I(1)
456.        if (iProcTheta == nProcTheta-1) &
457.             Theta_I(nTheta+1) = cTwoPi - Theta_I(nTheta)
458. 
459.        ! Set ThetaNode_I
460.        do iTheta = 1, nTheta + 1
461.           z = max(-1.0, min(1.0, 1 - (iTheta + iTheta0 -1)*dZ))
462.           ThetaNode_I(iTheta) = acos(z)
463.        end do
464.     else
465.        dTheta = (ThetaMax-ThetaMin)/nThetaAll
466.        ! Set Theta_I
467.        do iTheta = 0, nTheta+1
468.           Theta_I(iTheta) = ThetaMin + (iTheta  + iTheta0 - 0.5)*dTheta
469.        end do
470. 
471.        ! Set ThetaNode_I
472.        do iTheta = 1, nTheta+1
473.           ThetaNode_I(iTheta) = ThetaMin + (iTheta + iTheta0 - 1)*dTheta
474.        end do
475.     end if
476. 
477.     dTheta_I = ThetaNode_I(2:nTheta+1) - ThetaNode_I(1:nTheta)
478.     SinTheta_I = sin(Theta_I)
479.     SinThetaNode_I = sin(ThetaNode_I)
480. 
481.     if(UseCosTheta)then
482.        dCosTheta_I     = dZ
483.        dCosThetaNode_I = dZ
484.        dThetaNode_I    = Theta_I(1:nTheta+1) - Theta_I(0:nTheta)
485.     else
486.        dCosTheta_I(1:nTheta) = SinTheta_I(1:nTheta)*dTheta
487.        dCosThetaNode_I       = SinThetaNode_I*dTheta
488.        dThetaNode_I          = dTheta
489.     end if
490. 
491.     dPhi = (PhiMax-PhiMin)/nPhiAll
492.     ! Set Phi_I
493.     do iPhi = 0, nPhi+1
494.        ! Phi grid is Cell Centered
495.        Phi_I(iPhi) = PhiMin+(iPhi + iPhi0 - 0.5)*dPhi
496.     end do
497. 
498.     PhiNode_I = Phi_I(1:nPhi+1) - 0.5*dPhi
499.     dPhi_I = PhiNode_I(2:nPhi+1) - PhiNode_I(1:nPhi)
500.     dPhiNode_I = Phi_I(1:nPhi+1) - Phi_I(0:nPhi)
501. 
502.     Potential_C       =   0.0
503.     Rhs_C             =   0.0
504. 
505.   end subroutine init_potential_field
506.   !============================================================================
507. 
508.   subroutine save_potential_field
509. 
510.     use ModIoUnit,      ONLY: UnitTmp_
511.     use ModPlotFile,    ONLY: save_plot_file
512.     use ModCoordTransform, ONLY: rot_xyz_sph
513.     use ModReadMagnetogram, ONLY: nThetaAll, nPhiAll, StringMagHeader
514. 
515.     integer:: iR, jR, iTheta, iPhi, iLat, nLat
516.     real   :: r, CosTheta, SinTheta, CosPhi, SinPhi
517.     real   :: Br, Btheta, Bphi, XyzSph_DD(3,3)
518.     real   :: rI, rJ, rInv
519.     real, allocatable:: Lat_I(:), b_DX(:,:,:,:), b_DII(:,:,:)
520.     real, allocatable:: Bpole_DII(:,:,:), Btotal_DII(:,:,:)
```

</details>


---

<sub>⏱️ 2m 54s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/README.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/README (lines 1-260)

<details>
<summary>114 lines</summary>

```
1. #  Copyright (C) 2002 Regents of the University of Michigan, 
2. #  portions used with permission 
3. #  For more information, see http://csem.engin.umich.edu/tools/swmf
4. 
5. ##########################################################################
6. How to create input magnetogram files for the SWMF from a
7. raw magnetogram fits file (inlcuding ADAPT maps): 
8. 
9. These are the steps for creating a magnetogram file for SWMF from 
10. any raw magnetogram fits file.
11. 
12. The steps below require IDL or python to be installed on your machine.
13. 
14. 1. If the SWMF is already installed and compiled, skip to step 2. Otherwise,
15.    in the main SWMF path, type:
16. 
17.     ./Config.pl -install
18.     make
19. 
20.    To test if the codes work try:
21. 
22.    cd util/DATAREAD/srcMagnetogram
23.    make test_harmonics
24.    make test_fdips
25. 
26.    The resulting test_harmonics.diff and test_fdips.diff files should be empty.
27. 
28. 2. In the directory SWMF_path/util/DATAREAD/srcMagnetogram
29.    compile the HARMONICS.exe and/or FDIPS.exe executables:
30. 
31. 	make HARMONICS
32.         make FDIPS
33. 
34. 3. Convert the raw magnetogram file from FITS to ASCII format. 
35.    There are two ways to do this:
36. 
37. 3a. Run the python script 
38. 
39.    ./remap_magnetogram.py your_magnetogram_file.fits output_file.dat
40. 
41.   ------------------
42.    FOR ADAPT MAPS,
43.   ------------------
44.    Run the python script
45. 
46.    ./remap_magnetogram.py your_magnetogram_file.fits -istart 'startindex' -iend 'endindex'
47. 
48.    This produces map_'index'.out ascii files.
49.    'startindex' and 'endindex' are the map index numbers that are specified by the user.
50.     If unspecified, only the first adapt map realisation is remapped.
51.     istart < iend and lie between 1-12 (no. of adapt realisations).
52. 
53.    For example,
54.    -----------
55.    remap_magnetogram.py adapt40411_02e012_201708132000_i00020000n0.fts -istart 1 -iend 12
56.    converts all 12 realisations of the ADAPT-HMI map and saves 12 (map_1.out to map_12.out) ascii files.
57. 
58.    -grid can be used to specify the required grid (uniform/sinlat) of the output ascii file.
59.     If unspecified, the grid of output map is same as that of the input magnetogram.
60. 
61.    For more information on remap options use,
62.    -----------------------------------------
63.    remap_magnetogarm.py -h
64.    
65.    Once the magnetogram fits files are converted to ascii files, follow steps 4 and 5 to create the Harmonics file.
66. 
67. 3b. Use IDL to convert. Rename your magnetogram file and run the scripts
68. 
69.    cp your_magnetoram_file.fits fitsfile.fits
70.    idl run_fits_to_ascii.pro
71. 
72.    The idl routine generates four files:
73. 
74. 	fitsfile.H - the header of the original fits file with information 
75.                      about the magnetogram source.
76. 	fitsfile_tec.dat - a Tecplot file to display the original magnetogram.
77. 
78.         fitsfile_idl.out - the new ASCII file format to be used by 
79.                            HARMONICS.exe or FDIPS.exe
80. 
81. 4. Create and edit the input file HARMONICS.in and/or FDIPS.in:
82. 
83.    cp HARMONICS.in.orig HARMONICS.in
84.    emacs HARMONICS.in
85. 
86.    cp FDIPIS.in.orig FDIPS.in
87.    emacs FDIPS.in
88. 
89.    ---------------
90.    FOR ADAPT MAPS, 
91.    ---------------
92.    cp HARMONICS.in.ADAPT.orig HARMONICS.in
93.    emacs HARMONICS.in
94. 
95.    The original input files contain the documentation about all options.
96. 
97. 5. Run the executables HARMONICS.exe and/or FDIPS.exe
98. 
99.    ./HARMONICS.exe
100. 
101.    mpirun -np 4 ./FDIPS.exe
102. 
103. 6. Move the output file (bxyz type output for FDIPS) to the location where it is expected by the
104.    #HARMONICSFILE and/or the 
105. 
106. #LOOKUPTABLE
107. B0                      NameTable
108. load                    NameCommand
109. SC/fdips_bxyz.out               NameFile
110. real4                   TypeFile
111. 
112.   commands in the PARAM.in file.
113. 
114.
```

</details>


---

<sub>⏱️ 3m 7s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "if __name__ == '__main__'|argparse|istart|iend|map_",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py",
  "output_mode": "content",
  "-n": true,
  "head_limit": 260
}
```

</details>

<details>
<summary>29 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:27:import argparse
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:45:    My MATLAB code remap_mag.m uses the same algorithm but runs much faster.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:75:            map_data = cc[2]
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:303:                +str(imdex+1)+ '; InstrumentName = '+map_data+\
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:314:                +map_data+\
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:436:    map_data = 'unknown'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:560:            map_data = 'GONG'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:570:            map_data = 'MDI'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:626:                map_data = 'HMI'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:629:                map_data = 'HMI PolFill'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:634:            map_data = 'HMI SuperSynthia'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:638:        if map_data == 'unknown':
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:655:            map_data = str(g[0].header['MAPDATA']) #works for ADAPT
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:657:            map_data = ' '
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:682:        map_data ='PolFill'
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:722:    return( (magnetogram_type, grid_type, map_data, nlo, nla, CRnumber, CR, long0, bunit, mapdate) )
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:813:if __name__ == '__main__':
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:815:    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="""
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:816:    remap_magnetogram.py pre-processes the FITS format magnetograms 
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:837:    ./remap_magnetogram.py test.fits test.out
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:838:    ./remap_magnetogram.py test.fits test.out 180 360
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:839:    ./remap_magnetogram.py test.fits test.out -grid=uniform
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:868:    istart = 1
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:869:    iend   = 1
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:870:    map_local  = FITS_RECOGNIZE(args.inputfile,IsSilent=False)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:871:    if map_local[0] == 'ADAPT Synchronic':
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:872:        istart = 1
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:873:        iend   = 12
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py:874:        for i in range(istart,iend+1):
```

</details>


---

<sub>⏱️ 3m 7s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py (lines 920-1140)

<details>
<summary>5 lines</summary>

```diff

diff --git a/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py b/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py
index 0000000..0000000 100644
--- a/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py
+++ b/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py
@@ -920,221 +920,221 @@
```

</details>


---

<sub>⏱️ 3m 7s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Makefile.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Makefile (lines 1-220)

<details>
<summary>220 lines</summary>

```
1. SHELL=/bin/bash
2. 
3. # Include the link to the Makefile.def from the SWMF used
4. -include SWMF/Makefile.def
5. 
6. MYDIR  = $(shell echo `pwd -P`)
7. SIMDIR = Runs
8. RESDIR = Runs
9. IDLDIR = ${DIR}/share/IDL/Solar
10. PYDIR  = ${MYDIR}/Scripts
11. 
12. MODEL = AWSoM
13. PFSS  = HARMONICS
14. 
15. TIME = MapTime
16. MAP  = NoMap
17. 
18. EVTIME = none
19. DTEV   = -7
20. 
21. POYNTINGFLUX   = -1.0
22. 
23. PARAM = Default
24. 
25. REALIZATIONS    = 1,2,3,4,5,6,7,8,9,10,11,12
26. REALIZATIONLIST = $(foreach v, $(shell echo ${REALIZATIONS} | tr , ' '), $(shell printf '%02d' $(v)))
27. 
28. RESTART   = F
29. DOINSTALL = T
30. 
31. JOBNAME  = amap
32. 
33. SimDirList = $(sort $(dir $(wildcard run[0-9]*_*/)))
34. ResDirList = $(subst ${MYDIR}/Results/,,${FullResDirList})
35. FullResDirList = $(sort $(dir $(wildcard ${MYDIR}/Results/run[0-9]*_*/)))
36. 
37. FullResDir        = ${MYDIR}/Results/${RESDIR}
38. FullRunDirList    = $(sort $(dir $(wildcard ${MYDIR}/${SIMDIR}/run[01][0-9]/)))
39. FullResRunDirList = $(sort $(dir $(wildcard ${FullResDir}/run[01][0-9]/)))
40. 
41. help: 
42. 	@echo "*******************************************************************************"
43. 	@echo "This makefile uses pyfits (in SWMF/share/Python/. "
44. 	@echo "There is a link in SWMFSOLAR/Scripts to pyfits. "
45. 	@echo "Check the python version with python --version. Should be 3.7 or above."
46. 	@echo ""
47. 	@echo "On Pleiades, add 'module load python3/3.7.0' in the .cashrc or .bashrc file."
48. 	@echo "On Derecho, python packages are avail. via conda env, intel compiler is reloaded"
49. 	@echo "This is temp. fix to load the correct compiler while using Python, UCAR may fix it"
50. 	@echo "module load conda; conda activate npl, module load intel"
51. 	@echo "On Frontera, the default python is python2 and it is a link in /bin. "
52. 	@echo "Make a bin folder in your home folder and create a link to python3.7:"
53. 	@echo "  mkdir ~/bin; cd ~/bin/; ln -s `which python3.7` ~/bin/python"
54. 	@echo '  setenv PATH ~/bin/:$${PATH} # add it to the beginning of PATH in .cshrc'
55. 	@echo "*******************************************************************************"
56. 	@echo ""
57. 	@echo "Examples:"
58. 	@echo "  make adapt_run_w_compile MODEL=AWSoM  "
59. 	@echo "       (configure SWMF and run AWSoM with 12 ADAPT realizations with B0 "
60. 	@echo "        from Harmonics)"
61. 	@echo "  make adapt_run MODEL=AWSoM  "
62. 	@echo "       (run AWSoM   with 12 ADAPT realizations with B0 from Harmonics)"
63. 	@echo "  make adapt_run MODEL=AWSoMR "
64. 	@echo "       (run AWSoM-R with the 12 ADAPT realizations with B0 from Harmonics)"
65. 	@echo "  make adapt_run MODEL=AWSoM REALIZATIONS=1 MAP=hmi.dat PFSS=FDIPS"
66. 	@echo "       (run AWSoM with a single map named hmi.dat and use FDIPS)"
67. 	@echo ""
68. 	@echo "NOTE: "
69. 	@echo "  adapt_run does NOT re-configure/compile SWMF to save time!"
70. 	@echo "  adapt_run_w_compile will uninstall the SWMF, reinstall and compile the code."
71. 	@echo ""
72. 	@echo "After all simulations are finished post-process the results into Results/event1:"
73. 	@echo ""
74. 	@echo "  make check_postproc RESDIR=event1"
75. 	@echo ""
76. 	@echo "Comparing the simulations with observations is best to do on a local machine."
77. 	@echo "This requires SSWIDL and share/IDL/Solar has to be properly set up. Use"
78. 	@echo ""
79. 	@echo "  make check_compare RESDIR=event1 MODEL=AWSoMR"
80. 	@echo ""
81. 	@echo "to compare Results/event1 with observations saved into Results/obsdata."
82. 	@echo "MODEL is needed for plot legends."
83. 	@echo ""
84. 	@echo "Options:"
85. 	@echo " MODEL=AWSoM         - select model: 'AWSoM' (default) or 'AWSoMR' (case sensitive)"
86. 	@echo " SIMDIR=run01_test   - set name of simulation directory. Default is 'Runs'"
87. 	@echo " RESDIR=run01_test   - set name of result directory in Results/. Default is 'Runs'"
88. 	@echo " PFSS=HARMONICS      - set potential field solver: HARMONICS (default) or FDIPS"
89. 	@echo " TIME=2012-1-1T1:1:1 - set the start time of the simulation, format is "
90. 	@echo "                       YYYY-MM-DDTHH:MM:SC, default is MapTime (time of map)".
91. 	@echo " POYNTINGFLUX=1.0e6, - set the Poynting flux, default is in the PARAM.in file."
92. 	@echo " MAP=filename        - set the input map if desired. Default is 'NoMap'."
93. 	@echo " REALIZATIONS=1,2    - list the realizations. Default is '1,2,3,4,5,6,7,8,9,10,11,12'"
94. 	@echo " JOBNAME=amap        - set the job name. Default is 'amap' with "
95. 	@echo "                       realization appensed, e.g. 'amap01'"
96. 	@echo "                       Some systems limit the length of job name to 6 letters"
97. 	@echo ""
98. 	@echo "Notes:"
99. 	@echo "User can set either TIME or MAP, or BOTH. And the following will occur:"
100. 	@echo " 1. Both TIME and MAP are provided: use map and set start time to TIME. "
101. 	@echo " 2. Only TIME is provided: download ADAPT map based on TIME and set start time to TIME."
102. 	@echo " 3. Only MAP is provided: use MAP and set the start time based on map time."
103. 	@echo ""
104. 
105. ######################################################################################
106. 
107. adapt_run_w_compile:
108. 	@echo "Submitting AWSoM runs with a ADAPT map with re-compiling the code."
109. 	make compile
110. 	make rundir_local
111. 	make run
112. 	@echo "Finished submitting AWSoM runs with a ADAPT map."
113. 
114. adapt_run:
115. 	@echo "Submitting AWSoM runs with a ADAPT map without re-compiling the code."
116. 	make rundir_local
117. 	make run
118. 	@echo "Finished submitting AWSoM runs with a ADAPT map."
119. 
120. install:
121. 	-@(cp ${DIR}/util/DATAREAD/srcMagnetogram/remap_magnetogram.py ${MYDIR}/Scripts/;	\
122. 	if([ -L ${MYDIR}/Scripts/pyfits ]); then					\
123. 		rm -f ${MYDIR}/Scripts/pyfits; 						\
124. 	fi;										\
125. 	ln -s ${DIR}/share/Python/pyfits ${MYDIR}/Scripts/pyfits; 			\
126. 	)
127. 
128. compile:
129. 	-@(make install;								\
130. 	if [[ "${MODEL}" == "$(filter ${MODEL},AWSoM AWSoM2T AWSoMR AWSoMR_SOFIE)" ]]; then	\
131. 		cd ${DIR}; 								\
132. 		if [[ "${DOINSTALL}" == "T" ]]; then					\
133. 			rm -f ${DIR}/bin/*.exe;						\
134. 			./Config.pl -uninstall; 					\
135. 			./Config.pl -install; 						\
136. 			./Config.pl -v=Empty,SC/BATSRUS,IH/BATSRUS; 			\
137. 		fi;									\
138. 		if [[ "${MODEL}" == "AWSoM" ]]; then 					\
139. 			./Config.pl -o=SC:u=Awsom,e=AwsomAnisoPi,nG=3,g=6,8,8; 		\
140. 			./Config.pl -o=IH:u=Awsom,e=AwsomAnisoPi,nG=3,g=8,8,8; 		\
141. 		fi;									\
142. 		if [[ "${MODEL}" == "$(filter ${MODEL},AWSoM2T AWSoMR)" ]]; then	\
143. 			./Config.pl -o=SC:u=Awsom,e=Awsom,nG=3,g=6,8,8;                 \
144. 			./Config.pl -o=IH:u=Awsom,e=Awsom,nG=3,g=8,8,8;                 \
145. 		fi; 									\
146. 		if [[ "${MODEL}" == "AWSoMR_SOFIE" ]]; then 				\
147. 			./Config.pl -v=SP/MFLAMPA;				\
148. 			./Config.pl -o=SC:u=Awsom,e=AwsomSA,nG=2,g=6,8,8;             \
149. 			./Config.pl -o=IH:u=Awsom,e=AwsomSA,nG=2,g=8,8,8;             \
150. 			./Config.pl -o=SP:g=20000;                                      \
151. 		fi;									\
152. 		make -j SWMF PIDL; 							\
153. 		cp ${DIR}/bin/SWMF.exe ${DIR}/bin/${MODEL}.exe;				\
154. 		cd ${DIR}/util/DATAREAD/srcMagnetogram; 				\
155. 		make HARMONICS FDIPS; 							\
156. 	else										\
157. 		echo "MODEL = ${MODEL}";						\
158. 		echo "ERROR: MODEL must be either AWSoM, AWSoM2T, AWSoMR or AWSoMR_SOFIE.";	\
159. 	fi;										\
160. 	)
161. 
162. backup_run:
163. 	-@if([ -d ${MYDIR}/${SIMDIR}/run01 ]); then					\
164. 		rm -rf ${MYDIR}/${SIMDIR}/run_backup;					\
165. 		mkdir -p ${MYDIR}/${SIMDIR}/run_backup;                   		\
166. 		mv ${MYDIR}/${SIMDIR}/run[01]* ${MYDIR}/${SIMDIR}/run_backup/;          \
167. 	fi
168. 
169. copy_param:
170. 	-@(if [[ "${MODEL}" == "$(filter ${MODEL},AWSoM AWSoM2T AWSoMR AWSoMR_SOFIE)" ]]; then	\
171. 		if [[ "${MODEL}" == "AWSoMR" ]]; then					\
172. 			cp Param/PARAM.in.awsomr PARAM.in; 				\
173. 		fi; 									\
174. 		if [[ "${MODEL}" == "$(filter ${MODEL},AWSoM AWSoM2T)" ]]; then		\
175. 			cp Param/PARAM.in.awsom PARAM.in;				\
176. 		fi;									\
177. 		if [[ "${MODEL}" == "AWSoMR_SOFIE" ]]; then				\
178. 			cp Param/PARAM.in.sofie PARAM.in;				\
179. 		fi;									\
180. 		if [[ "${PARAM}" != "Default" ]]; then					\
181. 			cp Param/${PARAM} PARAM.in;					\
182. 		fi;									\
183. 		cp Param/HARMONICS.in Param/FDIPS.in .; 				\
184. 	else										\
185. 		echo "MODEL = ${MODEL}";						\
186. 		echo "ERROR: MODEL must be either AWSoM, AWSoM2T, AWSoMR or AWSoMR_SOFIE.";	\
187. 	fi;										\
188. 	)
189. 
190. clean_rundir_tmp:
191. 	-@(cd ${MYDIR};				\
192. 	rm -f PARAM.in HARMONICS.in FDIPS.in;	\
193. 	rm -f map_*.out; 			\
194. 	)
195. 
196. rundir_realizations:
197. 	-@for iRealization in ${REALIZATIONLIST}; do									\
198. 		cd ${DIR}; 												\
199. 		make rundir MACHINE=${MACHINE} RUNDIR=${MYDIR}/${SIMDIR}/run$${iRealization}; 				\
200. 		rm ${MYDIR}/${SIMDIR}/run$${iRealization}/SWMF.exe;			 				\
201. 		cp ${DIR}/bin/${MODEL}.exe ${MYDIR}/${SIMDIR}/run$${iRealization}/SWMF.exe;			 	\
202. 		cp ${MYDIR}/PARAM.in     ${MYDIR}/${SIMDIR}/run$${iRealization}; 					\
203. 		cp ${MYDIR}/HARMONICS.in ${MYDIR}/${SIMDIR}/run$${iRealization}/SC/; 					\
204. 		cp ${MYDIR}/FDIPS.in     ${MYDIR}/${SIMDIR}/run$${iRealization}/SC/; 					\
205. 		cp ${MYDIR}/JobScripts/job.${PFSS}.${MACHINE} ${MYDIR}/${SIMDIR}/run$${iRealization}/job.long;		\
206. 		mv ${MYDIR}/map_$${iRealization}.out ${MYDIR}/${SIMDIR}/run$${iRealization}/SC/;  			\
207. 		cd ${MYDIR}/${SIMDIR}/run$${iRealization}/SC/; 								\
208. 		if [[ "${PFSS}"  == "HARMONICS" ]]; then								\
209. 			perl -i -p -e "s/map_1/map_$${iRealization}/g" HARMONICS.in;					\
210. 			./HARMONICS.exe; 										\
211. 		fi; 													\
212. 		if [[ "${PFSS}"  == "FDIPS" ]]; then									\
213. 			perl -i -p -e "s/map_1/map_$${iRealization}/g" FDIPS.in;					\
214. 		fi; 													\
215. 	done
216. 
217. rundir_local:
218. 	@echo "Creating rundirs"
219. 	make backup_run
220. 	make copy_param
```

</details>


---

<sub>⏱️ 3m 7s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/README.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/README (lines 1-260)

<details>
<summary>43 lines</summary>

```
1. This repository contains scripts, param files and input files for running
2. AWSoM and AWSoM-R models. The param files in this repository mean PARAM.in, 
3. HARMONICS.in and FDIPS.in files. The input files mean the magneotgram files.
4. 
5. The SWMFSOLAR directory must be linked to an installed SWMF source code
6. directory and have access to the SWMF's Makefile.def file.
7. 
8. The Events directory contains some previous simulations, and associated param 
9. and input files.
10. 
11. The Param directory contains the latest param files.
12. 
13. The Scripts directory contains some Python scripts to change the param files.
14. 
15. USAGE:
16. To use SWMFSOLAR, first install the SWMF in the usual manner. Then enter the
17. SWMFSOLAR directory and type
18. 
19. make install
20. 
21. to install SWMFSOLAR (basically links all Python scripts in various places).
22. 
23. make help
24. 
25. to see the available options.
26. 
27. ---------------------------------------------------------------------
28. 
29. To submit multiple runs with the event_list:
30. 
31. *********************
32. It is required to have the symobolic link of SWMF to the installed SWMF.
33. *********************
34. 
35. Copy Events/event_list.txt to the SWMFSOLAR main directory, 
36. and modify it based on your need.
37. More information on editing and parameter options is listed within 
38. "Events/event_list.txt" .
39. Copy all the magnetogram files (corresponding to the selected events 
40. in events_list.txt) to the SWMFSOLAR main directory.
41. Execute "Scripts/sub_runs.py" to run the selected runs.
42. 
43. To be continued.
```

</details>


---

<sub>⏱️ 3m 12s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py (lines 800-930)

<details>
<summary>81 lines</summary>

```
800.                 line0 = '{0:14.6f} {1:14.6f}'.format(Coord1_I[l],Coord2_I[k])
801.                 line0 = line0+' {:14.6e}'.format(Data_IV[k,l]) + ' '
802.                 fid.write(line0 +' \n')
803.     else:
804.         for k in np.arange(nJ):
805.             for l in np.arange(nI):
806.                 line0 = '{0:14.6f} {1:14.6f}'.format(Coord1_I[l],Coord2_I[k])
807.                 for iw in np.arange(nVar):
808.                     line0 = line0+' {:14.6e}'.format(Data_IV[k,l,iw])
809.                 fid.write(line0 +' \n')
810.     fid.close()
811.     return(outputfile)
812. 
813. if __name__ == '__main__':
814. 
815.     parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="""
816.     remap_magnetogram.py pre-processes the FITS format magnetograms 
817.     into ASCII files that can by read by FDIPS.exe, BATSRUS.exe and SWMF.exe
818.     and IDL macros. The script can read the following types of magnetograms:
819. 
820.        Hathaway Synchronic
821.        ADAPT Synchronic
822.        GONG Synoptic
823.        GONG Hourly updated
824.        MDI Synoptic
825.        HMI PolFill, needs astropy (uncomment in the beginning)
826.        Solar Orbiter
827.     
828.     The code opens the .fits file and automatically recognizes the type of
829.     map it is, which determines whether it is on a sin(latitude) or regular
830.     spherical grid.  The output can be any desired resolution, on either a
831.     sin(latitude) or regular spherical grid.  If the output grid type is not
832.     specified, it will be the same as the original .fits file.  If the
833.     resolution is not specified, it will be the same as the original .fits
834.     file. The calling syntax from the command line is shown above.
835.     Some examples:
836. 
837.     ./remap_magnetogram.py test.fits test.out
838.     ./remap_magnetogram.py test.fits test.out 180 360
839.     ./remap_magnetogram.py test.fits test.out -grid=uniform
840.    
841.     Within Python, the remapping is done with the remap function contained
842.     in this file.
843.     
844.     The script uses the scipy and astropy packages that can be installed, 
845.     for example, with MacPorts.
846.     """)
847.     parser.add_argument('inputfile', help='Input FITS file name including path')
848.     parser.add_argument('outputfile', nargs='?', default="map", help='Output file name including path but without the map index and .out extension. Default name is "map".')
849.     parser.add_argument('nlat', nargs='?', type=int, default=-1, help='Number of latitude points in output. Default is same as input.')
850.     parser.add_argument('nlon', nargs='?', type=int, default=-1, help='Number of longitude points in output. Default is same as input.')
851.     parser.add_argument('-grid',choices=['uniform','sinlat'],help="type of latitude grid in the output. Default is same as input.")
852. 
853.     args = parser.parse_args()
854. 
855.     if args.nlat < -1:
856.         print ("nlat must be -1 or a postive integer.  No output.")
857.         quit()
858.     if args.nlon < -1:
859.         print ("nlon must be -1 or a postive integer.  No output.")
860.         quit()
861. 
862.     grid_type = 'unspecified'
863.     if args.grid == 'sinlat':
864.         grid_type = 'sin(lat)'
865.     elif args.grid == 'uniform':
866.         grid_type = 'uniform'
867. 
868.     istart = 1
869.     iend   = 1
870.     map_local  = FITS_RECOGNIZE(args.inputfile,IsSilent=False)
871.     if map_local[0] == 'ADAPT Synchronic':
872.         istart = 1
873.         iend   = 12
874.         for i in range(istart,iend+1):
875.             out=args.outputfile+'_'+str(i).zfill(2)+'.out'
876.             remap(args.inputfile, out, args.nlat, args.nlon, grid_type, i-1)
877.     else:
878.         out=args.outputfile+'_01.out'
879.         remap(args.inputfile, out, args.nlat, args.nlon, grid_type, 0)
880.
```

</details>


---

<sub>⏱️ 3m 12s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML (lines 10645-10710)

<details>
<summary>66 lines</summary>

```
10645. 
10646. #MAGNETOGRAM
10647. T			UseMagnetogram (rest of parameters read if true)
10648. 1.0			rMagnetogram
10649. 2.5			rSourceSurface
10650. 0.0			HeightInnerBc (not used)
10651. Param/CORONA/CR1935_WSO.dat    NameHarmonicsFile
10652. 
10653. This command is obsolete and has been replaced with the #HARMONICSFILE command.
10654. 
10655. If UseMagnetogram=T then read the harmonics file for the coronal
10656. magnetic field and use it to set B0 to the potential field solution.
10657. 
10658. rMagnetogram and rSourceSurface are the photosphere and source surface
10659. heliocentric radii, respectively. B0 becomes radial at rSourceSurface
10660. (typically taken to be 2.5 solar radii).
10661. 
10662. HeightInnerBc is the height above the photosphere of the boundary surface,
10663. non-zero values for this parameter are not recommended to unexperienced users.
10664. 
10665. NameHarmonicsFile is the name of the file containing the harmonics.
10666. 
10667. Default is UseMagnetogram=F.
10668. </command>
10669. 
10670. <command name="LDEM">
10671.   <parameter name="UseLdem" type="logical" default="F"	/>
10672.   <if expr="$UseLdem">    
10673.     <parameter name="NameLdemFile" type="string" length="$lLine" />
10674.     <parameter name="iRadiusLdem" type="integer" min="0" default="12" />
10675.   </if>
10676. 
10677. #LDEM
10678. F			UseLdem (rest of parameters read if true)
10679. LDEM_moments.out	NameLdemFile
10680. 1			iRadiusLdem
10681. 
10682. If UseLdem=T then read the LDEM moments file for the coronal density and temperature.
10683. 
10684. NameLdemFile is the name of the file containing the Ldem moments.
10685. 
10686. iRadiusLdem gives the index of the desired radius at which data is extracted.
10687. The Ldem moments data is ordered into concentric spherical shells of increasing
10688. radius,  ranging from 1.035Rs to 1.255Rs, in increaments of 0.01Rs. The user can
10689. select the desired radius by varying the iRadiusLdem parameter. The minimal accepted
10690. value of iRadiusLdem is 1, corresponding to 1.035Rs. iRadiusLdem=2 corresponds to
10691. 1.045Rs, and so forth.
10692. 
10693. Default is UseLdem=F, iRadiusLdem=1
10694. 
10695. </command>
10696. 
10697. <command name="EMPIRICALSW">
10698.   <parameter name="NameModelSW" type="string" input="select">
10699.     <option name="none" default="T"/>
10700.     <option name="WSA"/>
10701.   </parameter>
10702. 
10703. #EMPIRICALSW
10704. WSA             NameModelSW
10705. 
10706. Depending on the expansion factors, calculated using the magnetogram field,
10707. for NameModelSW=WSA the spatial distribution of varied gamma is calculated.
10708. Through the Bernoulli integral the solar wind at 1AU should fit the WSA
10709. solar wind semi-empirical model, with the prescribed distribution of the
10710. varied gamma. Default value is NameModelSW=none.
```

</details>


---

<sub>⏱️ 3m 12s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/HARMONICS.in.ADAPT.orig.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/HARMONICS.in.ADAPT.orig (lines 1-200)

<details>
<summary>17 lines</summary>

```
1. !  For ADAPT MAPS (HMI/GONG/VSM etc.)
2. 
3. ! Name of the input magnetogram ascii file. Set maximum for |B| in Gauss.
4. #MAGNETOGRAMFILE
5. map_1.out			NameFileIn
6. 3500.0				BrMax
7. 
8. ! Set name of output file. Default name is harmonics.dat
9. #OUTPUT
10. harmonics_adapt_ref.dat		NameFileOut
11. 
12. ! The maximum order of spherical harmonics is nOrder = min(nTheta, MaxOrder)
13. ! where nTheta is the number of latitude grid cells in the magnetogram,
14. ! while MaxOrder can be set below. Default value for MaxOrder is 180.
15. #HARMONICS
16. 180				MaxOrder
17.
```

</details>


---

<sub>⏱️ 3m 12s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.in.orig.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.in.orig (lines 1-180)

<details>
<summary>124 lines</summary>

```
1. ! Provide name of magnetogram file and specify maximum field strength
2. ! Defaults are "fitsfile.out" and 3500 G
3. #MAGNETOGRAMFILE
4. dipole11.out		NameFileIn
5. 3500.0			BrMax
6. 
7. ! Apply optional enhancement of the polar magnetic field with a factor
8. !  1 + (PolarFactor-1)*abs(sin(Latitude))^PolarExponent  
9. #CHANGEPOLARFIELD
10. 3.0			PolarFactor
11. 2.0			PolarExponent
12. 
13. ! The observed magnetic field is increased
14. ! Br=sign(BrObserved)*min(BrFactor*|BrObserved|, BrMin + |BrObserved|)
15. ! Default BrFactor = 1.0, BrMin = 0.0 (no change)
16. CHANGEWEAKFIELD
17. 3.75				BrFactor
18. 5.0				BrMin
19. 
20. ! For a non-default domain size and/or logarithmic radial grid
21. #DOMAIN
22. 1.0			rMin         (default is 1)
23. 25.0			rMax         (default is 2.5)
24. T			UseLogRadius (default is F)
25. F			UseWedge
26. 
27. ! Chebyshev transform simply interpolates to a uniform (co)latitude grid.
28. ! If the magnetometer grid is uniform to start with or was converted with
29. !    remap_magnetogram.py -grid uniform
30. ! then this command has no effect. If the magnetogram on a sin-lat grid,
31. ! then this is strongly recommended. To ensure that the grid resolution
32. ! nowhere gets degraded, the number of latitude grid points nTheta
33. ! is increased by a factor of pi/2 = 1.57 relative to the original grid
34. ! or the coarsened grid requested in the #GRID command.
35. ! Default is true so the lookup table is more uniform and accurate.
36. 
37. #CHEBYSHEV
38. T			UseChebyshevNode
39. 
40. ! In the Theta and Phi directions coarsening relative to the magnetogram 
41. ! resolution by an integer ratio is allowed. Refinement is not possible.
42. ! nTheta may be increased by the Chebyshev transform (see above).
43. 
44. ! Grid for testing only
45. #GRID
46. 20			nR
47. 20			nTheta
48. 20			nPhi
49. 
50. ! Reasonable grid for a production run
51. GRID
52. 400			nR     (number of cells in the radial direction)
53. 180			nTheta (set 0 to use the magnetogram resolution)
54. 180			nPhi   (set 0 to use the magnetogram resolution)
55. 
56. ! Switch off timing so that output does not change from run-to-run
57. #TIMING
58. F			UseTiming
59. 
60. TEST
61. -1			iProcTest
62. 
63. TESTIJK
64. 1			iRTest
65. 1			iPhiTest
66. 1			iThetaTest
67. 
68. ! nProcTheta*nProcPhi should agree with the number of procs FDIPS.exe uses
69. ! Default is a reasonably good decomposition, so this command is not needed
70. PARALLEL
71. 2			nProcTheta
72. 2			nProcPhi
73. 
74. ! Standard solver (these are the defaults)
75. #SOLVER                 ! NO HYPRE
76. BiCGSTAB		NameSolver (BiCGSTAB)
77. ILU			NamePreconditioner (ILU or NONE)
78. 1e-10			Tolerance
79. 
80. ! If configured with HYPRE the following solver can also be used
81. SOLVER                  ! HYPRE
82. GMRES			NameSolver (GMRES or AMG)
83. AMG			NamePreconditioner (AMG, MG or NONE)
84. 1e-10			Tolerance
85. 
86. ! Options for the AMG solver
87. HYPRE
88. 3			iVerboseAmg
89. 6			MaxRowElementsAmg
90. 10			iCoarsenAmg
91. 6			iRelaxAmg
92. 6			iInterpolateAmg
93. 0.5			StrongThresholdAmg
94. 0.3			TruncFactorAmg
95. T			UseSinglePart
96. 
97. ! Save up to four files containing the potential or the magnetic field.
98. 
99. ! The solar corona component of the SWMF can import FDIPS results from
100. ! "bxyz" output file type using "#LOOKUPTABLE" "B0" and "B0NEW" in PARAM.in.
101. 
102. #OUTPUT
103. bxyz			TypeOutput    Bx,By,Bz
104. fdips_bxyz.out		NameFileField
105. real4			TypeFileField (ascii, real4 or real8)
106. 
107. ! For plotting saving the spherical components may be useful
108. 
109. #OUTPUT
110. field			TypeOutput    Br,Blon,Blat
111. fdips_field.out		NameFileField
112. real4			TypeFileField (ascii, real4 or real8)
113. 
114. ! This output file contains the potential that is used for testing the solver
115. OUTPUT
116. potential		TypeOutput    Potential
117. fdips_potential.out	NameFilePotential
118. real8			TypeFilePotential
119. 
120. ! The tecplot output (that contains Bx, By, Bz) only works in serial mode. 
121. OUTPUT
122. tecplot			TypeOutput    Bx,By,Bz in tecplot format
123. fdips_field.dat		NameFilePotential
124.
```

</details>


---

<sub>⏱️ 3m 20s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "#LOOKUPTABLE|LOOKUPTABLE\\s+FDIPS|#HARMONICSFILE|NameHarmonicsFile|harmonics_bxyz|fdips_bxyz|map_1.out|#STARTTIME",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param",
  "output_mode": "content",
  "-n": true,
  "glob": "PARAM.in*",
  "head_limit": 300
}
```

</details>

<details>
<summary>105 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:44:#STARTTIME		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:87:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:90:SC/fdips_bxyz.out		NameFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:93:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:94:SC/harmonics_adapt.dat		NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:139:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:145:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:292:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:298:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:304:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA:310:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:33:#STARTTIME		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:85:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:88:SC/fdips_bxyz.out		NameFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:91:#HARMONICSFILE		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:92:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:132:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:138:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:292:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:298:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:304:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie:310:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:30:#STARTTIME		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:82:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:85:SC/fdips_bxyz.out		NameFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:88:#HARMONICSFILE		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:89:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:129:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:135:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:343:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:349:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:355:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr:361:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:43:#STARTTIME		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:87:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:90:SC/fdips_bxyz.out		NameFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:93:#HARMONICSFILE		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:94:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:125:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:363:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:369:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:375:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom_gpu:381:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CCMC:27:#STARTTIME
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CCMC:78:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CCMC:79:SC/mf.dat		NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CCMC:115:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CCMC:121:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:75:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:78:SC/fdips_bxyz.out		NameFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:81:#HARMONICSFILE		^		
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:82:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:127:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:133:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:323:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:329:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:335:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.sofie.CME:341:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:83:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:86:SC/fdips_bxyz.out		NameFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:89:#HARMONICSFILE		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:90:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:121:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:368:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:374:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:380:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME:386:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:85:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:88:SC/fdips_bxyz.out		NameFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:91:#HARMONICSFILE		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:92:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:123:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:371:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:377:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:383:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.CME_gpu:389:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.STITCH:35:#STARTTIME		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.STITCH:81:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.STITCH:84:SC/fdips_bxyz.out		NameFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.STITCH:88:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.STITCH:119:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.STITCH:338:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.STITCH:344:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.STITCH:350:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.STITCH:356:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:84:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:87:SC/fdips_bxyz.out		NameFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:90:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:91:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:122:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:128:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:272:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:278:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:284:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.CME:290:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:39:#STARTTIME		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:78:LOOKUPTABLE		FDIPS^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:81:SC/fdips_bxyz.out		NameFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:84:#HARMONICSFILE		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:85:SC/harmonics_adapt.dat	NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:116:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:353:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:359:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:365:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom:371:#LOOKUPTABLE
```

</details>


---

<sub>⏱️ 3m 20s</sub>

### ❌ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/Param/CORONA**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "#LOOKUPTABLE|NameTable|harmonics_bxyz|fdips_bxyz|NameFile",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/Param/CORONA",
  "output_mode": "content",
  "-n": true,
  "head_limit": 300
}
```

</details>

```
rg: /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/Param/CORONA: IO error for operation on /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/Param/CORONA: No such file or directory (os error 2)
```


---

<sub>⏱️ 3m 20s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Makefile**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "HARMONICS\\.exe|FDIPS\\.exe|map_\\$\\$\\{iRealization\\}|remap_magnetogram\\.py|change_awsom_param",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Makefile",
  "output_mode": "content",
  "-n": true,
  "head_limit": 200
}
```

</details>

<details>
<summary>6 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Makefile:121:	-@(cp ${DIR}/util/DATAREAD/srcMagnetogram/remap_magnetogram.py ${MYDIR}/Scripts/;	\
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Makefile:206:		mv ${MYDIR}/map_$${iRealization}.out ${MYDIR}/${SIMDIR}/run$${iRealization}/SC/;  			\
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Makefile:209:			perl -i -p -e "s/map_1/map_$${iRealization}/g" HARMONICS.in;					\
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Makefile:210:			./HARMONICS.exe; 										\
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Makefile:213:			perl -i -p -e "s/map_1/map_$${iRealization}/g" FDIPS.in;					\
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Makefile:221:	${MYDIR}/Scripts/change_awsom_param.py --map ${MAP} -t ${TIME} -B0 ${PFSS} -p ${POYNTINGFLUX}
```

</details>


---

<sub>⏱️ 3m 26s</sub>

### ✅ `glob`

**SWMF/**/Param/CORONA**

"SWMF/**/Param/CORONA"

```
No files matched the pattern.
```


---

<sub>⏱️ 3m 26s</sub>

### ✅ `glob`

**SWMF/**/PARAM.in*CORONA***

"SWMF/**/PARAM.in*CORONA*"

```
No files matched the pattern.
```


---

<sub>⏱️ 3m 26s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "#HARMONICSFILE|#LOOKUPTABLE|harmonics_bxyz|fdips_bxyz|#HARMONICSGRID",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA",
  "output_mode": "content",
  "-n": true,
  "head_limit": 260
}
```

</details>

<details>
<summary>26 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.1Dwedge:83:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom.GPU:41:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom.GPU:136:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/README_los:81:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/README_los:87:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/README_los:93:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.AwsomR:64:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.AwsomR:150:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.awsom.bvector:34:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.awsom.bvector:37:#HARMONICSGRID		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.awsom.bvector:53:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.awsom.bvector:89:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.2Dwedge:89:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/AIA_XRT:10:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.bvector:31:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.bvector:43:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.bvector:46:#HARMONICSGRID		^
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom:31:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom:126:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom.large.GPU:45:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom.large.GPU:140:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom.signb:39:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom.signb:134:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.STITCH:56:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.AwsomChargeState:41:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.AwsomChargeState:72:#LOOKUPTABLE
```

</details>


---

<sub>⏱️ 3m 33s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom (lines 20-170)

<details>
<summary>151 lines</summary>

```
20. 10000			DnSaveRestart
21. -1.0			DtSaveRestart
22. 
23. #COORDSYSTEM
24. HGR			TypeCoordSystem
25. 
26. #PLASMA
27. 1.0			FluidMass [amu]
28. 1.0			IonCharge [e]
29. 1.0			ElectronTemperatureRatio
30. 
31. #HARMONICSFILE
32. Param/CORONA/CR2077_GNG.dat		NameHarmonicsFile
33. 
34. HARMONICSGRID
35. 1.0			rMagnetogram
36. 25.0			rSourceSurface
37. T			IsLogRadius
38. 180			MaxOrder
39. 100			nR
40. 180			nLon
41. 90			nLat
42. 
43. #POYNTINGFLUX
44. 1e6			PoyntingFluxPerBSi
45. 
46. #CORONALHEATING
47. turbulentcascade		TypeCoronalHeating
48. 1.5e5			LperpTimesSqrtBSi
49. 0.0			rMinWaveReflection
50. F			UseReynoldsDecomposition
51. 
52. #HEATPARTITIONING
53. stochasticheating		TypeHeatPartitioning
54. 0.21			StochasticExponent
55. 0.18			StochasticAmplitude
56. 
57. #RADIATIVECOOLING
58. T			UseRadCooling
59. 
60. #USERSWITCH
61. +init +ic		StringSwitch
62. 
63. #COARSEAXIS
64. T			UseCoarseAxis
65. 2			nCoarseLayer
66. 
67. #USERINPUTBEGIN -----------------------------------
68. 
69. #CHROMOBC
70. 2e17			NchromoSi
71. 5e4			TchromoSi
72. 
73. #USERINPUTEND -------------------------------------
74. 
75. #TRANSITIONREGION
76. T			DoExtendTransitionRegion
77. 2.2e5			TeTransitionRegionSi
78. 1.0e1			DeltaTeModSi
79. 
80. #GRIDGEOMETRY
81. spherical_genr		TypeGeometry
82. Param/CORONA/grid_awsom.dat		NameGridFile
83. 
84. ! Use a true sphere, so box is made much larger
85. #GRID
86. 1			nRootBlock1
87. 2			nRootBlock2
88. 1			nRootBlock3
89. -100.0			xMin
90.  100.0			xMax
91. -100.0			yMin
92.  100.0			yMax
93. -100.0			zMin
94.  100.0			zMax
95. 
96. #GRIDBLOCKALL
97. 4000			MaxBlock
98. 
99. #LIMITRADIUS
100. 1.0			rMin
101. 24.0			rMax
102. 
103. #AMRREGION
104. InnerShell		NameRegion
105. shell0			StringShape
106. 1.0			RadiusInner
107. 1.7			Radius
108. 
109. #AMRCRITERIARESOLUTION
110. 3			nRefineCrit
111. dphi			StringRefine
112. 12.0			RefineTo
113. 6.0			CoarsenFrom
114. dphi Innershell		StringRefine
115. 1.5  			RefineTo
116. 0.75			CoarsenFrom
117. currentsheet		StringRefine
118. 0.5			CoarsenLimit
119. 0.5			RefineLimit
120. 1.5			MaxResolution
121. 
122. #GRIDRESOLUTION
123. 12.0			Resolution
124. initial			StringShape
125. 
126. #LOOKUPTABLE
127. radcool			NameTable
128. load			NameCommand
129. Param/CORONA/RadCoolCorona.dat		NameFile
130. ascii			TypeFile
131. 
132. #DOAMR
133. T			DoAmr
134. 40			DnAmr
135. -1			DtAmr
136. T			IsStrictAmr
137. 
138. #TIMESTEPPING
139. 2			nStage
140. 0.8			CflExpl
141. 
142. #SCHEME
143. 2			nOrder (1 or 2)
144. Linde			TypeFlux
145. mc3			TypeLimiter
146. 1.2			LimiterBeta
147. 
148. #LIMITER
149. T			UseLogRhoLimiter
150. T			UseLogPLimiter
151. F			UseRhoRatioLimiter
152. 
153. #MINIMUMTEMPERATURE
154. 5.0e4			TminDim
155. 5.0e4			TeMinDim
156. 
157. #MINIMUMPRESSURE
158. 1.0E-9			pMinDim
159. 1.0e-9			PeMinDim
160. 
161. #MINIMUMRADIALSPEED
162. T			UseSpeedMin
163. 10			rSpeedMin
164. 500			SpeedMinDim  ! 250km/s has no effect in this test
165. 10 h			TauSpeedMinDim
166. 
167. #NONCONSERVATIVE
168. T			UseNonConservative
169. 
170. #RESCHANGE
```

</details>


---

<sub>⏱️ 3m 33s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.AwsomR.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.AwsomR (lines 50-180)

<details>
<summary>131 lines</summary>

```
50. 2			nPlotFile 1
51. x=0 VAR idl		StringPlot
52. 20			DnSavePlot 5000
53. 10.0			DtSavePlot
54. -1.0			DxSavePlot
55. rho ux uy uz ti bx by bz I01 I02 p b1x b1y b1z		NameVars
56. {default}		NamePars
57. z=0 VAR idl		StringPlot
58. 20			DnSavePlot 5000
59. 10.0			DtSavePlot
60. -1.0			DxSavePlot
61. rho ux uy uz ti bx by bz I01 I02 p b1x b1y b1z 		NameVars
62. {default}		NamePars
63. 
64. #HARMONICSFILE
65. Param/CORONA/CR2077_GNG.dat		NameHarmonicsFile
66. 
67. #POYNTINGFLUX
68. 1e6			PoyntingFluxPerBSi
69. 
70. #CORONALHEATING
71. turbulentcascade		TypeCoronalHeating
72. 1.5e5			LperpTimesSqrtBSi
73. 0.0			rMinWaveReflection
74. F			UseReynoldsDecomposition
75. 
76. #HEATPARTITIONING
77. stochasticheating		TypeHeatPartitioning
78. 0.21			StochasticExponent
79. 0.18			StochasticAmplitude
80. 
81. #RADIATIVECOOLING
82. T			UseRadCooling
83. 
84. #USERSWITCH
85. +init +ic		StringSwitch
86. 
87. #COARSEAXIS
88. T			UseCoarseAxis
89. 2			nCoarseLayer
90. 
91. #USERINPUTBEGIN -----------------------------------
92. 
93. #CHROMOBC
94. 2e17			NchromoSi
95. 5e4			TchromoSi
96. 
97. #USERINPUTEND -------------------------------------
98. 
99. #TRANSITIONREGION
100. T			DoExtendTransitionRegion
101. 2.2e5			TeTransitionRegionSi
102. 1.0e1			DeltaTeModSi
103. 
104. #GRIDGEOMETRY
105. spherical_genr		TypeGeometry
106. Param/CORONA/grid_awsom.dat		NameGridFile
107. 
108. ! Use a true sphere, so box is made much larger
109. #GRID
110. 1			nRootBlock1
111. 2			nRootBlock2
112. 1			nRootBlock3
113. -100.0			xMin
114.  100.0			xMax
115. -100.0			yMin
116.  100.0			yMax
117. -100.0			zMin
118.  100.0			zMax
119. 
120. #GRIDBLOCKALL
121. 4000			MaxBlock
122. 
123. #LIMITRADIUS
124. 1.01			rMin
125. 24.0			rMax
126. 
127. #AMRREGION
128. InnerShell		NameRegion
129. shell0			StringShape
130. 1.0			RadiusInner
131. 1.7			Radius
132. 
133. #AMRCRITERIARESOLUTION
134. 3			nRefineCrit
135. dphi			StringRefine
136. 12.0			RefineTo
137. 6.0			CoarsenFrom
138. dphi Innershell		StringRefine
139. 1.5  			RefineTo
140. 0.75			CoarsenFrom
141. currentsheet		StringRefine
142. 0.5			CoarsenLimit
143. 0.5			RefineLimit
144. 1.5			MaxResolution
145. 
146. #GRIDRESOLUTION
147. 12.0			Resolution
148. initial			StringShape
149. 
150. #LOOKUPTABLE
151. radcool			NameTable
152. load			NameCommand
153. Param/CORONA/RadCoolCorona.dat		NameFile
154. ascii			TypeFile
155. 
156. #DOAMR
157. T			DoAmr
158. 40			DnAmr
159. -1			DtAmr
160. T			IsStrictAmr
161. 
162. #TIMESTEPPING
163. 2			nStage
164. 0.8			CflExpl
165. 
166. #SCHEME
167. 2			nOrder (1 or 2)
168. Linde			TypeFlux
169. mc3			TypeLimiter
170. 1.2			LimiterBeta
171. 
172. #LIMITER
173. T			UseLogRhoLimiter
174. T			UseLogPLimiter
175. F			UseRhoRatioLimiter
176. 
177. #MINIMUMTEMPERATURE
178. 5.0e4			TminDim
179. 5.0e4			TeMinDim
180.
```

</details>


---

<sub>⏱️ 3m 33s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "LOOKUPTABLE\\s+FDIPS|#HARMONICSFILE|NameHarmonicsFile|fdips_bxyz|harmonics_bxyz",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA",
  "output_mode": "content",
  "-n": true,
  "glob": "PARAM.in*",
  "head_limit": 300
}
```

</details>

<details>
<summary>14 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.AwsomR:64:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.AwsomR:65:Param/CORONA/CR2077_GNG.dat		NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom.signb:39:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom.signb:40:Param/CORONA/CR2077_GNG.dat		NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom.large.GPU:45:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom.large.GPU:46:Param/CORONA/CR2077_GNG.dat		NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.awsom.bvector:34:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.awsom.bvector:35:Param/CORONA/CR2157_HMI.dat		NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom.GPU:41:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom.GPU:42:Param/CORONA/CR2077_GNG.dat		NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom:31:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.Awsom:32:Param/CORONA/CR2077_GNG.dat		NameHarmonicsFile
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.bvector:43:#HARMONICSFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/GM/BATSRUS/Param/CORONA/PARAM.in.bvector:44:Param/CORONA/CR2157_HMI.dat		NameHarmonicsFile
```

</details>


---

<sub>⏱️ 3m 44s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP1.pro**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "read_magnetogram\\(|read_magnetogram,|UseBATS|FILE = input magnetogram file|readfits",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP1.pro",
  "output_mode": "content",
  "-n": true,
  "head_limit": 120
}
```

</details>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP1.pro:16:;   FILE = input magnetogram file (can be FITS or SWMF format).
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP1.pro:17:;   UseBATS = if set, will read BATS-R-US format (2D or 3D). Default
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP1.pro:26:  mag_info=read_magnetogram(file,PlotRadius,1)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP1.pro:129:  mag_info=read_magnetogram(file,PlotRadius,1)
```


---

<sub>⏱️ 3m 44s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP2.pro**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "read_magnetogram\\(|read_magnetogram,|UseBATS|FILE = input magnetogram file|readfits",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP2.pro",
  "output_mode": "content",
  "-n": true,
  "head_limit": 120
}
```

</details>

<details>
<summary>6 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP2.pro:1:pro GLSETUP2, FILE=FILE, UseBATS=UseBATS
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP2.pro:16:;   FILE = input magnetogram file (can be FITS or SWMF format).
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP2.pro:17:;   UseBATS = if set, will read BATS-R-US format (2D or 3D). Default
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP2.pro:26:  mag_info=read_magnetogram(file,PlotRadius,UseBATS)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP2.pro:50:  mag1_info=read_magnetogram('FRMagnetogram.out',PlotRadius,UseBATS)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP2.pro:73:     hmi_info = read_magnetogram('hmi_map.out',PlotRadius,UseBATS)
```

</details>


---

<sub>⏱️ 3m 44s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP1.pro.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP1.pro (lines 1-120)

<details>
<summary>120 lines</summary>

```
1. pro GLSETUP1, FILE=FILE
2. 
3. ;-----------------------------------------------------------------------
4. ; NAME:
5. ;   GLSETUP1
6. ;
7. ; OUTPUTS:
8. ;   user choise for stdout file
9. ;
10. ; SYSTEM REQUIREMENTS:
11. ; Mouse with left and right button
12. ;
13. ;
14. ; KEYWORDS: 
15. ;
16. ;   FILE = input magnetogram file (can be FITS or SWMF format).
17. ;   UseBATS = if set, will read BATS-R-US format (2D or 3D). Default
18. ;             will read FITS format.
19. 
20. ;Setup the color mode and a better IDL font.
21. 
22.   device,decomposed=0
23.   !p.font=1
24.   PlotRadius =1.
25. ;Read the magnetogram (fitsfile.out in BATSRUS format)
26.   mag_info=read_magnetogram(file,PlotRadius,1)
27.   nlat=mag_info.nlat
28.   nlon=mag_info.nlon
29.   longitude=mag_info.longitude
30.   latitude=mag_info.latitude
31.   br_field=mag_info.br_field
32.   neqpar =mag_info.neqpar
33.   eqpar  =mag_info.eqpar
34. 
35. ;Display the magnetogram and let user interactively select the CME source region. The
36. ;procedure to select is:
37. ; 1. Click the CME source region of positive polarity with 'left' button of mouse
38. ; 2. Click the CME source region of negative polarity with 'right' button of mouse
39. ;
40. ;Note that the user can click anywhere inside the active region. However, click closer
41. ;to the center of the positive/negative patterns is recommended.
42. ;
43. ;Note the solar latitude is expressed in pixel due to the non-uniform spacing. The latitude
44. ;is uniform in sin(latitude). This will be changed in the future to degree. 
45. 
46.   br_field_show=br_field
47.   index=where(br_field lt -20)
48.   br_field_show[index]=-20
49.   index=where(br_field gt 20)
50.   br_field_show[index]=20
51. 
52.   window,2,xs=1200,ys=1200.*float(nlat)/float(nlon)*4./3.
53.   loadct,0
54.   contour,br_field_show,min=-20,max=20,charsize=3,$
55.           title='SWMF Input Magnetogram (R ='$
56.           +strtrim(PlotRadius,2)+' Rs)',xtitle='Solar Longitude (Pixel)',$
57.           ytitle='Solar Latitude (Pixel)',/fill,nlevels=60,/iso,xstyle=1,ystyle=1
58.   
59.   loadct,39
60.   if(neqpar ge 2) then begin
61.      ;plot the Earth Carrington coordinate:
62.      if eqpar[1] gt 0 then begin
63.         ;eqpar[1] is the Carrington coordinate of the Earth
64.         ;eqpar[0] is the Carrington coordinate of the left margin
65.         MapLongEarth = 360*(1 - mag_info.time)  - eqpar[0]
66.         ;If the left margin of the map is in the next Carrington 
67.         ;rotation, add 360 deg:
68.         if MapLongEarth lt 0 then MapLongEarth = MapLongEarth +360
69.         ;Our plot coordinates are in pixels, not in degrees:
70.         PixelEarth = (MapLongEarth/360.)*nlon
71.         xEarthLine = findgen(nlat)*0.+PixelEarth
72.         yEarthLine = findgen(nlat)
73.         oplot,xEarthLine,yEarthLine,color=250,linestyle=5
74.      endif
75.   endif
76.   !MOUSE.button = 0
77.   while(!MOUSE.button ne 1) do begin
78.      cursor,xPositive,yPositive,/data,/down
79.      if br_field[xPositive,yPositive] lt 0 then begin
80.         print,'Negative Polarity! Please Select POSITIVE Polarity!'   
81.         !MOUSE.button=0
82.      endif else begin
83.         plots,xPositive,yPositive,/data,psym=-2,color=250 
84.      endelse
85.   endwhile
86.   while(!MOUSE.button ne 4) do begin
87.      cursor,xNegative,yNegative,/data,/down
88.      if br_field[xNegative,yNegative] gt 0 then begin
89.         print,'Positive Polarity! Please Select NEGATIVE Polarity!'   
90.         !MOUSE.button=0
91.      endif else begin
92.         plots,xNegative,yNegative,/data,psym=-2,color=100
93.      endelse
94.   endwhile
95.   print, '==='
96.   print, xPositive,yPositive,xNegative,yNegative
97.   !mouse.button=0
98.   wait,2
99.   wdelete,2
100.   exit
101. end
102. 
103. pro TDSETUP1, FILE=FILE
104. 
105. ;-----------------------------------------------------------------------
106. ; NAME:
107. ;   GLSETUP1
108. ;
109. ; OUTPUTS:
110. ;   user choise for stdout file
111. ;
112. ; SYSTEM REQUIREMENTS:
113. ; Mouse with left and right button
114. ;
115. ;
116. ; KEYWORD: 
117. ;
118. ;   FILE = input zoomed magnetogram file
119. ; color 250 - positive Br (center of the spot, footpoint)
120. ; color 100 - negative Br (center of the spot, footpoint)
```

</details>


---

<sub>⏱️ 3m 44s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP2.pro.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/GLSETUP2.pro (lines 1-120)

<details>
<summary>120 lines</summary>

```
1. pro GLSETUP2, FILE=FILE, UseBATS=UseBATS
2. 
3. ;-----------------------------------------------------------------------
4. ; NAME:
5. ;   GLSETUP2
6. ;
7. ; OUTPUTS:
8. ;   user choise for stdout file
9. ;
10. ; SYSTEM REQUIREMENTS:
11. ; Mouse with left and right button
12. ;
13. ;
14. ; KEYWORDS: 
15. ;
16. ;   FILE = input magnetogram file (can be FITS or SWMF format).
17. ;   UseBATS = if set, will read BATS-R-US format (2D or 3D). Default
18. ;             will read FITS format.
19. 
20. ;Setup the color mode and a better IDL font.
21.   device,decomposed=0
22.   !p.font=1
23.   PlotRadius =1.
24. 
25. ;Read the magnetogram
26.   mag_info=read_magnetogram(file,PlotRadius,UseBATS)
27.   nlat=mag_info.nlat
28.   nlon=mag_info.nlon
29.   longitude=mag_info.longitude
30.   latitude=mag_info.latitude
31.   br_field=mag_info.br_field
32.   sizemap_p= mag_info.blon_field
33.   sizemap_n= mag_info.blat_field
34.   occPos = mag_info.occPos
35.   occNeg = mag_info.occNeg
36. 
37.   neqpar = mag_info.neqpar
38.   eqpar  = mag_info.eqpar
39. 
40.   xPositive = eqpar[2]
41.   yPositive = eqpar[3]
42.   xNegative = eqpar[4]
43.   yNegative = eqpar[5]
44.   XyARCenter_D = [eqpar[6],eqpar[7]]
45.   nPIL = (neqpar - 8)/2
46.   xPIL_I = eqpar[8:7+nPIL]
47.   yPIL_I = eqpar[8+nPIL:7+2*nPIL]
48. 
49.   ;Read the magnetogram
50.   mag1_info=read_magnetogram('FRMagnetogram.out',PlotRadius,UseBATS)
51.   gl_bradfield = mag1_info.br_field
52.   gl_blonfield = mag1_info.blon_field
53.   gl_blatfield = mag1_info.blat_field
54. 
55.   br_field_show=br_field ; from AfterGlSETUP.out
56.   index=where(br_field lt -20)
57.   br_field_show[index]=-20
58.   index=where(br_field gt 20)
59.   br_field_show[index]=20
60.   
61.   inPos = where(occPos gt 0)
62.   inNeg = where(occNeg gt 0)
63.   occPos_show = occPos
64.   occPos_show[inPos] = 20
65.   occNeg_show = occNeg
66.   occNeg_show[inNeg] = 20
67.   ;Read the HMI vector field components (Blat & Blon) to overplot
68.   ;on the original magnetogram field Br
69.   cp =fltarr(nPIL)
70.   hmi_file = file_search('hmi_map.out',count=count)
71.   if (count eq 1) then begin
72.      IsPresentHMI = 1
73.      hmi_info = read_magnetogram('hmi_map.out',PlotRadius,UseBATS)
74.      hmi_Brad = hmi_info.br_field
75.      hmi_Blon = hmi_info.blon_field
76.      hmi_Blat = hmi_info.blat_field
77.      for i = 0, nPIL -1 do begin
78.         cp[i] = (longitude[xPIL_I(i)] * hmi_Blat[xPIL_I(i),yPIL_I(i)] - $
79.                  latitude[yPIL_I(i)] * hmi_Blon[xPIL_I(i),yPIL_I(i)])
80.      endfor
81.   endif else begin
82.      print, 'No HMI output found'
83.      IsPresentHMI = 0
84.   endelse
85. 
86.   window,2,xs=1200,ys=1200.*float(nlat)/float(nlon)*4./3.
87.   loadct,0
88.   contour,br_field_show,min=-20,max=20,charsize=3,$
89.           title='SWMF Input Magnetogram (R ='$
90.           +strtrim(PlotRadius,2)+' Rs)',xtitle='Solar Longitude (Pixel)',$
91.           ytitle='Solar Latitude (Pixel)',/fill,nlevels=60,/iso,xstyle=1,$
92.           ystyle=1
93.   
94.   loadct,39
95.   if(neqpar ge 2) then begin
96.      ;plot the Earth Carrington coordinate:
97.      if eqpar[1] gt 0 then begin
98.         ;eqpar[1] is the Carrington coordinate of the Earth
99.         ;eqpar[0] is the Carrington coordinate of the left margin
100.         MapLongEarth = 360*(1 - mag_info.time) - eqpar[0]
101.         ;If the left margin of the map is in the next Carrington 
102.         ;rotation, add 360 deg:
103.         if MapLongEarth lt 0 then MapLongEarth = MapLongEarth +360
104.         ;Our plot coordinates are in pixels, not in degrees:
105.         PixelEarth = (MapLongEarth/360.)*nlon
106.         xEarthLine = findgen(nlat)*0.+PixelEarth
107.         yEarthLine = findgen(nlat)
108.         oplot,xEarthLine,yEarthLine,color=250,linestyle=5
109.      endif
110.   endif
111.   plots,xPositive,yPositive,/data,psym=-2,color=250
112.   plots,xNegative,yNegative,/data,psym=-2,color=100
113. ;plot center of the flux rope 
114.   plots,XyARCenter_D[0],XyARCenter_D[1],/data,psym=-2,color=150
115. ;show PIL
116.   for i=0, nPIL-1 do begin
117.      plots,xPIL_I(i),yPIL_I(i),psym=-1,color=210
118.   endfor
119. ; Showing positive and negative spots
120.   contour,sizemap_p,/overplot,c_color=100
```

</details>


---

<sub>⏱️ 4m 5s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsom (lines 70-100)

<details>
<summary>31 lines</summary>

```
70. #RESTARTOUTFILE
71. one			StringRestartOutFile
72. 
73. #PLASMA
74. 1.0			FluidMass [amu]
75. 1.0			IonCharge [e]
76. 1.0			ElectronTemperatureRatio
77. 
78. LOOKUPTABLE		FDIPS^
79. B0			NameTable
80. load			NameCommand
81. SC/fdips_bxyz.out		NameFile
82. real4			TypeFile
83. 
84. #HARMONICSFILE		^
85. SC/harmonics_adapt.dat	NameHarmonicsFile
86. 
87. #HARMONICSGRID		^
88. 1.0			rMagnetogram
89. 25			rSourceSurface^
90. T			IsLogRadius^
91. 180			MaxOrder
92. 400			nR
93. 180			nLon
94. 90			nLat
95. 
96. FACTORB0		^
97. 1.0			FactorB0^
98. 
99. #POYNTINGFLUX
100. 1.0e6			PoyntingFluxPerBSi^ [J/m^2/s/T]
```

</details>


---

<sub>⏱️ 4m 5s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Param/PARAM.in.awsomr (lines 74-98)

<details>
<summary>25 lines</summary>

```
74. T			DoConvergenceCheck
75. limited			TypeBc
76. 
77. #FIELDLINETHREAD
78. T			UseFieldLineThreads
79. 200			nPointThreadMax
80. 2.0e-3			DsThreadMin
81. 
82. LOOKUPTABLE		FDIPS^
83. B0			NameTable
84. load			NameCommand
85. SC/fdips_bxyz.out		NameFile
86. real4			TypeFile
87. 
88. #HARMONICSFILE		^
89. SC/harmonics_adapt.dat	NameHarmonicsFile
90. 
91. #HARMONICSGRID		^
92. 1.0			rMagnetogram
93. 25			rSourceSurface^
94. T			IsLogRadius^
95. 180			MaxOrder
96. 400			nR
97. 180			nLon
98. 90			nLat
```

</details>


---

<sub>⏱️ 4m 5s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py (lines 96-210)

<details>
<summary>115 lines</summary>

```
96. 
97.     if time != 'MapTime':
98.         # TIME is given with the correct format
99.         time_input = dt.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")
100.         time_param = time.replace('-',',').replace('T',',').replace(':',',')
101. 
102.     if (map == 'NoMap'):
103.         if time != 'MapTime':
104.             # Download the ADAPT magnetogram if no map is pvoided
105.             # default 'fixed', note that the time_input is correctly set.
106.             filename_map = download_ADAPT.download_ADAPT_magnetogram(time_input)[0]
107.             print("download the map as: ", filename_map)
108.         else:
109.             raise ValueError('No map is provided. Please provide the time '
110.                              + 'by -t/--time to download the ADAPT map.')
111.     else:
112.         # The ADAPT map is provied
113.         filename_map = map
114.         
115.         map_local  = FITS_RECOGNIZE(map)
116.         time_map   = dt.datetime.strptime(map_local[9], "%Y-%m-%dT%H:%M:%S")
117. 
118.         # Very weird GONG Synoptic map, the map time is a few days after the end of the CR.
119.         # Use an approximation to get the time corresponding to the central meridian
120.         if (map_local[0] == 'NSO-GONG Synoptic'):
121.             CR_number = float(map_local[6])
122.             time_map = dt.datetime(1853, 11, 9) + dt.timedelta(days=27.2753*(CR_number-0.5))
123. 
124.         if time == 'MapTime':
125.             # if the user does not provide the time, then set the time based
126.             # on the time info from the ADAPT map.
127.             time_param = (str(time_map.year)   + ',' + str(time_map.month) + ',' +
128.                           str(time_map.day)    + ',' + str(time_map.hour)  + ',' +
129.                           str(time_map.minute) + ',' + str(time_map.second))
130. 
131.     # Need to add the msc
132.     time_param = time_param+',0.0'
133. 
134.     # set #STARTTIME
135.     if 'replace' in new_params.keys():
136.         new_params['replace']['STARTTIME']=time_param
137.     else:
138.         new_params['replace'] = {'STARTTIME':time_param}
139. 
140.     if DoRestart:
141.         if 'replace' in new_params.keys():
142.             if 'STARTTIME' in new_params['replace']:
143.                 new_params['replace'].pop('STARTTIME',None)
144. 
145.     if poynting_flux > 0:
146.         # set #POYNTINGFLUX
147.         if 'replace' in new_params.keys():
148.             new_params['replace']['POYNTINGFLUX']='{:<10.3e}'.format(poynting_flux)
149.         else:
150.             new_params['replace']={'POYNTINGFLUX':'{:<10.3e}'.format(poynting_flux)}
151. 
152.     if 'add' in new_params.keys():
153.         commands_add=new_params['add']
154.         change_param.add_commands(commands_add, DoUseMarker=DoUseMarker)
155. 
156.     if 'add' in new_params_pfss.keys():
157.         commands_add=new_params_pfss['add']
158.         change_param.add_commands(commands_add, DoUseMarker=DoUseMarker, filenameIn=pfss+'.in', filenameOut=pfss+'.in')
159. 
160.     if 'rm' in new_params.keys():
161.         commands_rm=new_params['rm']
162.         change_param.remove_commands(commands_rm, DoUseMarker=DoUseMarker)
163. 
164.     if 'rm' in new_params_pfss.keys():
165.         commands_rm=new_params_pfss['rm']
166.         change_param.remove_commands(commands_rm, DoUseMarker=DoUseMarker, filenameIn=pfss+'.in', filenameOut=pfss+'.in')
167. 
168.     if 'replace' in new_params.keys():
169.         DictReplace = new_params['replace']
170.         change_param.replace_commands(DictReplace, DoUseMarker=DoUseMarker)
171. 
172.     if 'replace' in new_params_pfss.keys():
173.         DictReplace = new_params_pfss['replace']
174.         change_param.replace_commands(DictReplace, DoUseMarker=DoUseMarker, filenameIn=pfss+'.in', filenameOut=pfss+'.in')
175. 
176.     if 'change' in new_params.keys():
177.         DictChange  = new_params['change']
178.         change_param.change_param_value(DictChange, DoUseMarker=DoUseMarker)
179. 
180.     if 'change' in new_params_pfss.keys():
181.         DictChange  = new_params_pfss['change']
182.         change_param.change_param_value(DictChange, DoUseMarker=DoUseMarker, filenameIn=pfss+'.in', filenameOut=pfss+'.in')
183. 
184.     # prepare each realization map.
185.     str_exe = str('Scripts/remap_magnetogram.py ' + filename_map)
186. 
187.     subprocess.call(str_exe, shell=True)
188. 
189. # =============================================================================
190. if __name__ == '__main__':
191. 
192.     # Program initiation
193.     PROG_DESCRIPTION = ('Script to change PARAM.in if needed and '
194.                         + ' automatically download the ADAPT map.')
195.     ARG_PARSER = argparse.ArgumentParser(description=PROG_DESCRIPTION)
196.     ARG_PARSER.add_argument('-p', '--poynting_flux',
197.                             help='(default: -1.0 J/m^2/s/T)',
198.                             type=float, default=-1)
199.     ARG_PARSER.add_argument('-t', '--time',
200.                             help='(default: MapTime)'
201.                             + 'Use if you want to overwrite PARAM.in time.'
202.                             + ' Format: yyyy-mm-ddThh:min:sec',
203.                             type=str, default='MapTime')
204.     ARG_PARSER.add_argument('-B0', '--pfss',
205.                             help='(default: HARMONICS.)'
206.                             + ' Use if you want to specify the PFSS solver.',
207.                             type=str, default='HARMONICS')
208.     ARG_PARSER.add_argument('-m', '--map',
209.                             help='(default: NoMap)'
210.                             + ' Use if you want to specify the ADAPT map.',
```

</details>


---

<sub>⏱️ 4m 5s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Makefile.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Makefile (lines 217-280)

<details>
<summary>64 lines</summary>

```
217. rundir_local:
218. 	@echo "Creating rundirs"
219. 	make backup_run
220. 	make copy_param
221. 	${MYDIR}/Scripts/change_awsom_param.py --map ${MAP} -t ${TIME} -B0 ${PFSS} -p ${POYNTINGFLUX}
222. 	make rundir_realizations
223. 	make clean_rundir_tmp
224. 
225. run:
226. 	@echo "Submitting jobs"
227. 	-@for iRealization in ${REALIZATIONLIST}; do              	        		\
228. 		cd ${MYDIR}/${SIMDIR}/run$${iRealization}; 					\
229. 		if [[ "${MACHINE}" == "frontera" ]];						\
230. 			then perl -i -p -e "s/amap01/${JOBNAME}$${iRealization}/g" job.long;  	\
231. 			sbatch job.long;							\
232. 		fi;										\
233. 		if [[ "${MACHINE}" == "pfe" ]];                         			\
234. 			then ./qsub.pfe.pbspl.pl job.long ${JOBNAME}$${iRealization};      	\
235. 		fi; 										\
236. 		if [[ "${MACHINE}" == "derecho" ]];						\
237. 			then perl -i -p -e "s/amap01/${JOBNAME}$${iRealization}/g" job.long;  	\
238. 			qsub job.long;								\
239. 		fi;										\
240. 	done
241. 
242. #########################################################################################
243. 
244. check_postproc:
245. 	@if([ ! -d ${MYDIR}/Results/${RESDIR} ]); then                   			\
246. 		rm -f error_postproc.log; 							\
247. 		echo "Post processing simulation results to Results/${RESDIR}";			\
248. 		mkdir -p ${MYDIR}/Results/${RESDIR}; 						\
249. 		cp ${MYDIR}/${SIMDIR}/key_params.txt ${MYDIR}/Results/${RESDIR}/; 		\
250. 		for RunDir in ${FullRunDirList};  do                              		\
251. 			echo "processing rundir = $${RunDir}";					\
252. 			cd $${RunDir};                                    			\
253. 			if([ -f SWMF.SUCCESS ]); then                              		\
254. 				mkdir -p ${FullResDir}/$${RunDir: -6:5};                      	\
255. 				if([ ! -d RESULTS ]); then ./PostProc.pl -l=IH RESULTS; fi;   	\
256. 				cp SC/map_*out ${FullResDir}/$${RunDir: -6:5}/;			\
257. 				mv RESULTS/* ${FullResDir}/$${RunDir: -6:5}/;			\
258. 				if [[ -f SC/fdips_bxyz.out ]]; then          			\
259. 					mv SC/fdips_bxyz.out SC/FDIPS.in 			\
260. 						${FullResDir}/$${RunDir: -6:5}/; 		\
261. 				fi;								\
262. 				if [[ -f SC/harmonics_adapt.dat ]]; then			\
263. 					cp SC/harmonics_adapt.dat SC/HARMONICS.in 	 	\
264. 						${FullResDir}/$${RunDir: -6:5}/ ;		\
265. 					mv harmonics_bxyz.out ${FullResDir}/$${RunDir: -6:5}/ ; \
266. 				fi;								\
267. 			else									\
268. 				echo "$${RunDir} crashed" >> ${MYDIR}/error_postproc.log;	\
269. 			fi; 									\
270. 		done;										\
271. 	else                                                            			\
272. 		echo "${RESDIR} already exists; skip post processing.";				\
273. 	fi
274. 
275. #########################################################################################
276. 
277. check_compare:
278. 	make check_compare_insitu
279. 	make check_compare_remote
280.
```

</details>


---

<sub>⏱️ 4m 18s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "call\\s+read_orig_magnetogram|call\\s+read_magnetogram_param\\(|use\\s+ModReadMagnetogram",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram",
  "output_mode": "content",
  "-n": true,
  "head_limit": 300
}
```

</details>

<details>
<summary>24 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90:17:  use ModReadMagnetogram, ONLY: UseCosTheta, nThetaAll, nPhiAll
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.f90:229:  use ModReadMagnetogram, ONLY: UseCosTheta, nThetaAll, nPhiAll
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90:107:    use ModReadMagnetogram, ONLY: read_magnetogram_param
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90:155:          call read_magnetogram_param(NameCommand)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90:229:    use ModReadMagnetogram, ONLY: read_orig_magnetogram, Br0_II,  &
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90:237:    call read_orig_magnetogram(IsPhiThetaOrder, UseWedge, DoRemoveMonopole, &
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90:267:    use ModReadMagnetogram, ONLY: UseCosTheta, nThetaAll, nPhiAll
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90:513:    use ModReadMagnetogram, ONLY: nThetaAll, nPhiAll, StringMagHeader
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module.f90:808:    use ModReadMagnetogram, ONLY: nPhiAll
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90:109:    use ModReadMagnetogram, ONLY: read_magnetogram_param
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90:156:          call read_magnetogram_param(NameCommand)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90:241:    use ModReadMagnetogram, ONLY: read_orig_magnetogram, Br0_II,  &
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90:249:    call read_orig_magnetogram(IsPhiThetaOrder, UseWedge, DoRemoveMonopole, &
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90:279:    use ModReadMagnetogram, ONLY: UseCosTheta, nThetaAll, nPhiAll
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90:489:    use ModReadMagnetogram, ONLY: nThetaAll, nPhiAll, StringMagHeader
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_module_twoghostcells.f90:783:    use ModReadMagnetogram, ONLY: nPhiAll
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS_hypre.f90:8:  use ModReadMagnetogram, ONLY: nThetaAll, nPhiAll
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90:8:  use ModReadMagnetogram, ONLY: dPhi, dTheta, dSinTheta
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90:75:    use ModReadMagnetogram, ONLY: read_magnetogram_param
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90:96:          call read_magnetogram_param(NameCommand)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90:108:    use ModReadMagnetogram, ONLY: read_orig_magnetogram, nTheta0, nPhi0, &
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90:113:    call read_orig_magnetogram
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/ModMagHarmonics.f90:144:    use ModReadMagnetogram, ONLY: Br0_II, nTheta0, nPhi0, UseChebyshevNode, &
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/convert_harmonics.f90:26:        call read_magnetogram_param(NameCommand)
```

</details>


---

<sub>⏱️ 4m 18s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "download_ADAPT_magnetogram\\(|FITS_RECOGNIZE\\(|remap\\(|map_\\d+|ADAPT Synchronic|NSO-GONG",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts",
  "output_mode": "content",
  "-n": true,
  "head_limit": 300
}
```

</details>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py:10:def download_ADAPT_magnetogram(timeIn, NameTypeMap='fixed'):
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/download_ADAPT.py:128:    download_ADAPT_magnetogram(timeIn,NameTypeMap)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:106:            filename_map = download_ADAPT.download_ADAPT_magnetogram(time_input)[0]
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:115:        map_local  = FITS_RECOGNIZE(map)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMFSOLAR/Scripts/change_awsom_param.py:120:        if (map_local[0] == 'NSO-GONG Synoptic'):
```


---

<sub>⏱️ 4m 18s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.in.orig**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "#MAGNETOGRAMFILE|read_magnetogram_param|#CHEBYSHEV|#CHANGEWEAKFIELD",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.in.orig",
  "output_mode": "content",
  "-n": true,
  "head_limit": 200
}
```

</details>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.in.orig:3:#MAGNETOGRAMFILE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/FDIPS.in.orig:37:#CHEBYSHEV
```


---

<sub>⏱️ 4m 26s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/convert_harmonics.f90.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/convert_harmonics.f90 (lines 1-140)

<details>
<summary>37 lines</summary>

```
1. !  Copyright (C) 2002 Regents of the University of Michigan,
2. !  portions used with permission
3. !  For more information, see http://csem.engin.umich.edu/tools/swmf
4. program convert_harmonics
5. 
6.   ! Transform spherical harmonics file into 3D lookup table  for B0  field
7.   use ModMagnetogram
8.   use ModMpi, ONLY: MPI_init, MPI_Finalize, MPI_COMM_WORLD
9.   use ModReadParam
10.   use ModUtilities
11.   implicit none
12.   character(len=lStringLine) :: NameCommand
13.   integer :: iError
14.   character(len=*), parameter:: NameSub = 'convert_harmonics'
15.   !----------------------------------------------------------------------------
16.   call MPI_init(iError)
17.   call read_file('HARMONICSGRID.in',iCommIn = MPI_COMM_WORLD)
18.   call read_init
19.   call read_echo_set(.false.)
20. 
21.   do
22.      if(.not.read_line() ) EXIT
23.      if(.not.read_command(NameCommand)) CYCLE
24.      select case(NameCommand)
25.      case("#FACTORB0", "#HARMONICSGRID", "#HARMONICSFILE")
26.         call read_magnetogram_param(NameCommand)
27.      case("#END")
28.         EXIT
29.      case default
30.         call CON_stop(NameSub//' invalid NameCommand='//NameCommand)
31.      end select
32.   end do
33.   call init_magnetogram_lookup_table(MPI_COMM_WORLD)
34.   call MPI_finalize(iError)
35. end program convert_harmonics
36. !==============================================================================
37.
```

</details>


---

<sub>⏱️ 4m 26s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/convert_harmonics.f90**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "program|read_magnetogram_param|#MAGNETOGRAMFILE|#CHANGEWEAKFIELD",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/convert_harmonics.f90",
  "output_mode": "content",
  "-n": true,
  "head_limit": 160
}
```

</details>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/convert_harmonics.f90:4:program convert_harmonics
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/convert_harmonics.f90:26:        call read_magnetogram_param(NameCommand)
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/util/DATAREAD/srcMagnetogram/convert_harmonics.f90:35:end program convert_harmonics
```


---

<sub>⏱️ 4m 26s</sub>

### ✅ `rg`

**/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML**

<details>
<summary>Arguments</summary>

```json
{
  "pattern": "#LOOKUPTABLE|B0\\s+NameTable|fdips_bxyz|harmonics_bxyz",
  "path": "/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML",
  "output_mode": "content",
  "-n": true,
  "head_limit": 260
}
```

</details>

<details>
<summary>8 lines</summary>

```
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:5538:lines in the PARAM.in file. This follows the #LOOKUPTABLE command
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:5541:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:5547:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:9447:#LOOKUPTABLE
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10605:By default this lookup table is saved into "harmonics_bxyz.out" file.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10606:The defaults can be changed with the #LOOKUPTABLE command. Once the
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10626:and saved into the "harmonics_bxyz_new.out" file.
/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML:10628:#LOOKUPTABLE command. Once the lookup table file is created,
```

</details>


---

<sub>⏱️ 4m 31s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML (lines 5528-5565)

<details>
<summary>38 lines</summary>

```
5528. For line-of-sight Extreme Ultraviolet (EUV) and Soft X-Ray (SXR) plots,
5529. the same parametes are read as for the wl and pb plots (above) but now
5530. the integration is carried out to the surface of the sun so rOccult should
5531. be set to zero. MuLimbDarkening has no effect but needs to be included.
5532. Also, for line-of-sight (los) EUV images from STEREO-A/B and SDO/AIA using
5533. the response function table both 'ins' and 'INS' give the same dimensional
5534. output.
5535. Additionally, because EUV and SXR plots are configured to read in a response
5536. table specific to the EUV or SXR instument (e.g. SOHO EIT, STEREO EUVI,
5537. Yohkoh SXT) the tables for the response need to be read in by additional
5538. lines in the PARAM.in file. This follows the #LOOKUPTABLE command
5539. syntax e.g:
5540. \begin{verbatim}
5541. #LOOKUPTABLE
5542. euv                     NameTable
5543. load                    NameCommand
5544. SC/Param/los_Eit.dat    NameFile
5545. ascii                   TypeFile
5546. 
5547. #LOOKUPTABLE
5548. sxr                     NameTable
5549. load                    NameCommand
5550. SC/Param/los_Sxt.dat    NameFile
5551. ascii                   TypeFile
5552. \end{verbatim}
5553. The possible values for NameVars with PlotArea 'los'
5554. are listed in subroutine set_plotvar_los in write_plot_los.f90.
5555. 
5556. The line-of-site (PlotArea 'los') plots have an option to use 'ins'/'INS',
5557. which will fill the ObsPosX, ObsPosY, ObsPosZ, rSizeImage, xOffset, yOffset,
5558. rOccult, MuLimbDarkening, nPix for SOME supported instruemts. An example is:
5559. 
5560. \begin{verbatim}
5561. los ins idl_real4       StringPlot ! line of sight plot using table
5562. -1			DnSavePlot
5563. 100.			DtSavePlot
5564. soho:c3 sta:euvi stb:cor2	StringsInstrument
5565. \end{verbatim}
```

</details>


---

<sub>⏱️ 4m 31s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML (lines 9436-9470)

<details>
<summary>35 lines</summary>

```
9436.   <if expr="$NameCommand =~ /make|save|use/">
9437.     <parameter name="StringDescription" type="string" length="$lLine"/>
9438.     <parameter name="NameVar"           type="string" length="$lLine"/>
9439.     <parameter name="nIndex"            type="integer" min="1"/>
9440.     <for name="i" from="1" to="$nIndex">
9441.       <parameter name="nIndex$i" type="integer" min="2"/>
9442.       <parameter name="Index${i}Min" type="real"/>
9443.       <parameter name="Index${i}Max" type="real"/>
9444.     </for>
9445.   </if>
9446. 
9447. #LOOKUPTABLE
9448. p(rho,e)			NameTable
9449. use param			NameCommand (use, load, save, make, param)
9450. table1.out			NameFile (read this if use/load/save)
9451. real4				TypeFile (read this unless "param")
9452. zXe zBe nPl			NameTableParam (if NameCommand has "param")
9453. 54.0				TableParam number of protons in Xenon
9454. 4.0				TableParam number of protons in Beryllium
9455. 4.0				TableParam number of elements in plastic
9456. p(rho,e) for ionized plasma	Description (read this and rest unless "load")
9457. logrho logp pXe pBe pPl		NameVar
9458. 2      	    	    		nIndex
9459. 100				nIndex1
9460. 1e-6				Index1Min
9461. 1e+6				Index1Max
9462. 50				nIndex2
9463. 0.001				Index2Min
9464. 100.0				Index2Max
9465. 
9466. Lookup tables allow interpolating one or more variables from a discrete
9467. table. For sake of efficiency, lookup tables should have uniform indexes,
9468. but non-uniform tables are also supported.
9469. Tables with up to 5 indexes are supported.
9470. Lookup tables are in the same format as structured "IDL" plotfiles.
```

</details>


---

<sub>⏱️ 4m 31s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/SWMF/SC/BATSRUS/PARAM.XML (lines 10600-10634)

<details>
<summary>35 lines</summary>

```
10600. 
10601. NameHarmonicsFile is the name of the file containing the harmonics
10602. coefficients.
10603. 
10604. After reading the harmonics file, the B0 lookup table is generated and saved.
10605. By default this lookup table is saved into "harmonics_bxyz.out" file.
10606. The defaults can be changed with the #LOOKUPTABLE command. Once the
10607. lookup table file is created, it can be loaded directly and there is
10608. no need for this command.
10609. 
10610. The temporal evolution of the magnetogram can be captured by using
10611. an additional B0NEW lookup table. See also the #NEWHARMONICSFILE command.
10612. 
10613. By default there is no B0 lookup table.
10614. </command>
10615. 
10616. <command name="NEWHARMONICSFILE">
10617.   <parameter name="NameHarmonicsFileNew" type="string" length="$lLine"/>
10618. 
10619. #NEWHARMONICSFILE
10620. Param/CORONA/CR1936_WSO.dat    NameHarmonicsFileNew
10621. 
10622. NameHarmonicsFileNew is the name of the file containing the harmonics
10623. coefficients for the time at the end of the session.
10624. 
10625. After reading the harmonics file, the B0NEW lookup table is generated
10626. and saved into the "harmonics_bxyz_new.out" file.
10627. The default parameters of the lookup table can be changed with the
10628. #LOOKUPTABLE command. Once the lookup table file is created,
10629. it can be loaded directly and there is no need for this command.
10630. 
10631. The potential field contained in the B0 and B0NEW lookup tables
10632. will be interpolated in time during the session. 
10633. 
10634. By default there is no B0NEW lookup tables.
```

</details>


---

<sub>⏱️ 4m 54s</sub>

### 💬 Copilot

I found **five primary magnetogram-ingestion paths** spanning `SWMF` and `SWMFSOLAR`:

1. **SWMFSOLAR orchestration (download/map selection → remap → run setup)**  
   `SWMFSOLAR/Scripts/sub_runs.py` → `change_awsom_param.py` → `download_ADAPT.py` (optional ADAPT fetch) → `Scripts/remap_magnetogram.py` (called from change script) → `SWMFSOLAR/Makefile:rundir_realizations` (moves `map_##.out`, switches `map_1` placeholder, runs `HARMONICS.exe` for harmonic mode, prepares `FDIPS.in` for FDIPS mode).  
   Key controls are in `SWMFSOLAR/Param/PARAM.in.*` (`LOOKUPTABLE FDIPS`, `#HARMONICSFILE`, `#HARMONICSGRID`).

2. **Core FITS recognition/remap pipeline (SWMF utility layer)**  
   `SWMF/util/DATAREAD/srcMagnetogram/remap_magnetogram.py` is the central FITS ingester: `FITS_RECOGNIZE()` detects ADAPT/GONG/MDI/HMI/etc and grid type, `remap()` does flux-conserving remeshing, writes `map_01.out` (or ADAPT realizations `map_01..map_12.out`).  
   Related download helpers: `download_ADAPT.py` (ADAPT FTP) and `get_magnetogram.py` (realtime GONG download path).

3. **HARMONICS PFSS preprocessing path**  
   `HARMONICS.exe` (`harmonics.f90`) → `ModMagHarmonics.read_harmonics_param()` → `ModReadMagnetogram.read_magnetogram_param()/read_orig_magnetogram()` (reads `#MAGNETOGRAMFILE`, applies `#CHANGEWEAKFIELD/#CHANGEPOLARFIELD/#CHEBYSHEV`) → `calc_harmonics()` writes harmonics coefficients (`harmonics*.dat`).

4. **FDIPS PFSS preprocessing path**  
   `FDIPS.exe` (`FDIPS.f90`, `ModPotentialField`) → `read_fdips_param()` (delegates magnetogram commands to `ModReadMagnetogram`) → `read_modified_magnetogram()`/`read_orig_magnetogram()` → potential solve → `save_potential_field()` producing `fdips_bxyz.out` (consumed later through `#LOOKUPTABLE B0 load ...`).

5. **Runtime SC/BATSRUS B0 ingestion path**  
   `SC/BATSRUS/src/ModSetParameters.f90` reads `#HARMONICSFILE/#NEWHARMONICSFILE/#HARMONICSGRID/#FACTORB0` via `ModMagnetogram.read_magnetogram_param()`.  
   `ModB0.init_mod_b0()` calls `init_magnetogram_lookup_table()`; `ModB0.get_b0()` and `ModCoronalHeating` call `get_magnetogram_field()` during simulation.  
   This supports either harmonic-file-driven table generation or loading prebuilt lookup tables (e.g., FDIPS outputs) via `#LOOKUPTABLE`.

There is also an **IDL interactive path** (`GLSETUP1.pro`, `GLSETUP2.pro` + `read_magnetogram.pro`/`readfits.pro`) used by setup tools to ingest FITS or BATS-R-US magnetogram files directly.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
