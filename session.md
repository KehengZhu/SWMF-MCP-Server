# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `31d7da7a-a2ae-4ff0-9644-5ec1d0726141`  
> - **Started:** 4/24/2026, 3:08:41 PM  
> - **Duration:** 5m 16s  
> - **Exported:** 4/24/2026, 3:13:57 PM  

---

<sub>⏱️ 0s</sub>

### ℹ️ Info

Environment loaded: 1 custom instruction, 8 skills, 2 MCP servers, Visual Studio Code connected

---

<sub>⏱️ 31s</sub>

### 👤 User

lot the beginning, intermediate and last frames of IH z=0 cut. plot func U. save them as separate images. results are in Run_Max_RP_CME3

---

<sub>⏱️ 48s</sub>

### ✅ `skill`

**swmf-analyze**

<details>
<summary>Arguments</summary>

```json
{
  "skill": "swmf-analyze"
}
```

</details>

```
Skill "swmf-analyze" loaded successfully. Follow the instructions in the skill context.
```


---

<sub>⏱️ 58s</sub>

### 💬 Copilot

I’ll inspect the run directory first to confirm available IH outputs and then wire an IDL plotting script for the three requested frames.

---

<sub>⏱️ 1m 4s</sub>

### ✅ `swmf-prototype-inspect_artifact`

**/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01**

<details>
<summary>Arguments</summary>

```json
{
  "artifact_type": "run_dir",
  "path": "/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01"
}
```

</details>

```
{"ok":true,"artifact_type":"run_dir","path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01","question":"","summary":"Run directory '/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01': 13 items. Status: prepared_or_running. Logs: 5. Job scripts: 1.","findings":[{"kind":"directory_inventory","location":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01","description":"13 top-level items in run directory.","items":[".DS_Store","HARMONICS.in","IH/","PARAM.in","SC/","harmonics_adapt.dat","harmonics_bxyz.out","job.frontera","map_01.out","runlog_2603121545","runlog_2603142021","runlog_2603151352","runlog_2603161512"]},{"kind":"artifact_presence","location":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01","description":"Run status: prepared_or_running. Key artifacts detected.","artifact_presence":{"PARAM.in":true,"RESTART.in":false,"RESTART.out":false,"SWMF.SUCCESS":false,"SWMF.DONE":false,"SWMF.KILLED":false},"run_status":"prepared_or_running"},{"kind":"log_discovery","location":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/runlog_2603121545","description":"Primary log: runlog_2603121545 (528 lines). First error at line 235.","log_files":["/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/runlog_2603121545","/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/runlog_2603142021","/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/runlog_2603151352","/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/runlog_2603161512","/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/harmonics_bxyz.out"],"primary_log":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/runlog_2603121545","first_error":{"found":true,"line_number":235,"line":"Error in component SC in session  1","context_before":["SC:SC/Param/TR.dat\t\tNameFile","SC:ascii\t\t\tTypeFile"],"context_after":[" ERROR: aborting execution on processor          54  with message:","ERROR: Error reading missing variable StringPlot from line="]}},{"kind":"job_scripts","location":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/job.frontera","description":"1 job script(s) found. Scheduler: slurm. SWMF nproc: 1624.","job_scripts":["/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/job.frontera"],"job_layout":{"scheduler":"slurm","machine_hint":"frontera","nodes":30,"tasks_per_node":56,"swmf_executable":null,"swmf_nproc":1624}},{"kind":"output_subdirs","location":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01","description":"Component output subdirectories found: SC/, IH/","subdirs":["SC/","IH/"]},{"kind":"component_output_files","location":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH","description":"IH output directory has 312 .out file(s), 0 .outs file(s), and 4 time-snapshot group(s).","component":"IH","patterns":{"z=0*.out":{"count":95,"samples":["z=0_var_3_t00020000_n00005000.out","z=0_var_3_t00030000_n00005120.out","z=0_var_3_t00040000_n00005240.out","z=0_var_3_t00050000_n00005360.out","z=0_var_3_t00060000_n00005480.out","z=0_var_3_t00070000_n00005600.out","z=0_var_3_t00080000_n00005720.out","z=0_var_3_t00090000_n00005840.out"]},"z=0*.outs":{"count":0,"samples":[]},"x=0*.out":{"count":95,"samples":["x=0_var_1_t00020000_n00005000.out","x=0_var_1_t00030000_n00005120.out","x=0_var_1_t00040000_n00005240.out","x=0_var_1_t00050000_n00005360.out","x=0_var_1_t00060000_n00005480.out","x=0_var_1_t00070000_n00005600.out","x=0_var_1_t00080000_n00005720.out","x=0_var_1_t00090000_n00005840.out"]},"y=0*.out":{"count":95,"samples":["y=0_var_2_t00020000_n00005000.out","y=0_var_2_t00030000_n00005120.out","y=0_var_2_t00040000_n00005240.out","y=0_var_2_t00050000_n00005360.out","y=0_var_2_t00060000_n00005480.out","y=0_var_2_t00070000_n00005600.out","y=0_var_2_t00080000_n00005720.out","y=0_var_2_t00090000_n00005840.out"]},"*.out":{"count":312,"samples":["shl_var_4_t00180000_n00006800.out","shl_var_4_t00210000_n00006980.out","shl_var_4_t00240000_n00007160.out","shl_var_4_t00270000_n00007340.out","shl_var_4_t00300000_n00007522.out","shl_var_4_t00330000_n00007705.out","shl_var_4_t00360000_n00007888.out","shl_var_4_t00390000_n00008071.out"]},"*.outs":{"count":0,"samples":[]},"*.log":{"count":2,"samples":["log_n005000.log","log_n006560.log"]},"PARAM.in":{"count":0,"samples":[]}},"snapshot_groups":[{"base":"shl_var_4","pattern":"shl_var_4_t*_n*.out","count":27,"samples":["shl_var_4_t00180000_n00006800.out","shl_var_4_t00210000_n00006980.out","shl_var_4_t00240000_n00007160.out","shl_var_4_t00270000_n00007340.out","shl_var_4_t00300000_n00007522.out"],"first_frame":"shl_var_4_t00180000_n00006800.out","middle_frame":"shl_var_4_t00570000_n00009169.out","last_frame":"shl_var_4_t00960000_n00011548.out","first_frame_path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/shl_var_4_t00180000_n00006800.out","middle_frame_path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/shl_var_4_t00570000_n00009169.out","last_frame_path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/shl_var_4_t00960000_n00011548.out","expected_outs":"shl_var_4.outs","combined_outs":"shl_var_4.outs","combined_outs_exists":false},{"base":"x=0_var_1","pattern":"x=0_var_1_t*_n*.out","count":95,"samples":["x=0_var_1_t00020000_n00005000.out","x=0_var_1_t00030000_n00005120.out","x=0_var_1_t00040000_n00005240.out","x=0_var_1_t00050000_n00005360.out","x=0_var_1_t00060000_n00005480.out"],"first_frame":"x=0_var_1_t00020000_n00005000.out","middle_frame":"x=0_var_1_t00490000_n00008681.out","last_frame":"x=0_var_1_t00960000_n00011548.out","first_frame_path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/x=0_var_1_t00020000_n00005000.out","middle_frame_path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/x=0_var_1_t00490000_n00008681.out","last_frame_path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/x=0_var_1_t00960000_n00011548.out","expected_outs":"x=0_var_1.outs","combined_outs":"x=0_var_1.outs","combined_outs_exists":false},{"base":"y=0_var_2","pattern":"y=0_var_2_t*_n*.out","count":95,"samples":["y=0_var_2_t00020000_n00005000.out","y=0_var_2_t00030000_n00005120.out","y=0_var_2_t00040000_n00005240.out","y=0_var_2_t00050000_n00005360.out","y=0_var_2_t00060000_n00005480.out"],"first_frame":"y=0_var_2_t00020000_n00005000.out","middle_frame":"y=0_var_2_t00490000_n00008681.out","last_frame":"y=0_var_2_t00960000_n00011548.out","first_frame_path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/y=0_var_2_t00020000_n00005000.out","middle_frame_path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/y=0_var_2_t00490000_n00008681.out","last_frame_path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/y=0_var_2_t00960000_n00011548.out","expected_outs":"y=0_var_2.outs","combined_outs":"y=0_var_2.outs","combined_outs_exists":false},{"base":"z=0_var_3","pattern":"z=0_var_3_t*_n*.out","count":95,"samples":["z=0_var_3_t00020000_n00005000.out","z=0_var_3_t00030000_n00005120.out","z=0_var_3_t00040000_n00005240.out","z=0_var_3_t00050000_n00005360.out","z=0_var_3_t00060000_n00005480.out"],"first_frame":"z=0_var_3_t00020000_n00005000.out","middle_frame":"z=0_var_3_t00490000_n00008681.out","last_frame":"z=0_var_3_t00960000_n00011548.out","first_frame_path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/z=0_var_3_t00020000_n00005000.out","middle_frame_path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/z=0_var_3_t00490000_n00008681.out","last_frame_path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/z=0_var_3_t00960000_n00011548.out","expected_outs":"z=0_var_3.outs","combined_outs":"z=0_var_3.outs","combined_outs_exists":false}]}],"evidence":[],"provenance":{"artifact_type":"run_dir","path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01"},"uncertainty":{"known_unknowns":["Only static filesystem scan; no runtime context or process state consulted.","Log first-error is from primary log only; component-specific logs not scanned."]},"swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked environment SWMF_ROOT: /Users/zkeheng/SWMFSoftware/SWMF","Resolved from SWMF_ROOT environment variable."]}
```


---

<sub>⏱️ 1m 12s</sub>

### ✅ `swmf-prototype-get_evidence`

**plot_data**

<details>
<summary>Arguments</summary>

```json
{
  "query": "plot_data",
  "mode": "keyword",
  "goal": "IDL procedure signature and usage"
}
```

</details>

````
{"ok":true,"query":"plot_data","mode":"keyword","scope":[],"top_k":8,"goal":"IDL procedure signature and usage","task_type":"lookup","module":null,"summary":"1 deterministic IDL evidence item(s) and 2 supporting evidence item(s) found for 'plot_data'","evidence":[{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_data: pro plot_data\ncategory: plotting\n==============================================================================","score":1,"name":"plot_data","kind":"pro","start_line":738,"metadata":{"kind":"idl_procedure_signature","relative_path":"share/IDL/General/procedures.pro","why_relevant":"Exact IDL procedure match from the deterministic IDL catalog.","category":"plotting","params":[],"keywords":[]}},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/support/swmf-postproc/IDL_VISUALIZATION.md","snippet":"### Usage questions\nExamples:\n- \"how do I plot func U\"\n- \"how do I use plot_func for SC z=0\"\n\nFirst tool:\n```\nget_evidence(mode=\"keyword\", query=<procedure_name>, goal=\"IDL procedure signature and usage\")\n```\nPrecision follow-up:\n- `get_evidence(mode=\"keyword\", goal=\"IDL procedure signature and usag…","score":null,"name":"Usage questions","kind":"doc_section","component":"","start_line":38},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/support/swmf-postproc/SKILL.md","snippet":"## Tool Protocol\n\nFor output inventory:\n```\ninspect_artifact(artifact_type=\"run_dir\", path=<run_dir>)\n```\n\nFor IDL procedures:\n```\nget_evidence(mode=\"keyword\", goal=\"IDL procedure signature and usage\")\n```\nPrecision follow-up:\n```\nget_evidence(mode=\"keyword\", goal=\"IDL procedure detail or category n…","score":null,"name":"Tool Protocol","kind":"doc_section","component":"","start_line":38}],"provenance":{"mode_used":"keyword","scope":[]},"uncertainty":{"known_unknowns":["Runtime behavior for the current case not inspected."]},"swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked environment SWMF_ROOT: /Users/zkeheng/SWMFSoftware/SWMF","Resolved from SWMF_ROOT environment variable."]}
````


---

<sub>⏱️ 1m 12s</sub>

### ✅ `swmf-prototype-get_evidence`

**func U**

<details>
<summary>Arguments</summary>

```json
{
  "query": "func U",
  "mode": "keyword",
  "goal": "IDL visualization manual detail"
}
```

</details>

```
{"ok":true,"query":"func U","mode":"keyword","scope":[],"top_k":8,"goal":"IDL visualization manual detail","task_type":"lookup","module":null,"summary":"8 deterministic IDL evidence item(s) and 0 supporting evidence item(s) found for 'func U'","evidence":[{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md","snippet":"parameter, which is a list of ’y’ and ’n’ characters, each referring to the respective\nfunction. If you set ’n’ for any of the variables, the fmin and fmax arrays have\nto be set, e.g.\nfmin=[1. ,-1.]\nfmax=[1.1, 1.]\nIDL remembers the previous setting and uses it, unless the number of functions\nare changed. You can always set fmin=0, fmax=0, and let IDL prompt you for\nthe values.\n\n\n9     Function names in string func\nThe function names listed in the func string can be any of the variable names\nlisted in the string array wnames, which is read from the header of the file,\nor any of the function name strings shown in the functiondef array at the\nbeginning of funcdef.pro (see section 16), or any expression using the standard\nvariable, coordinate and scalar parameter names and various constants:\nx y z r\nrho p ux uy uz uu u bx by bz bb b\nxSI gamma gammae Mi Me Qi Qe clight rbody\nmu0 mu0A c0 op0 o...","score":1,"name":"func","kind":"manual_section","start_line":422,"metadata":{"kind":"idl_manual_section","relative_path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md","why_relevant":"func strings, variables, funcdef names, expressions, vector pairs","topic":"func","line_start":422,"line_end":455}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/funcdef.pro","snippet":"mxB = rho*ux+(bb*ux-(ux*bx+uy*by+uz*bz)*bx)/c0^2\nmyB = rho*uy+(bb*uy-(ux*bx+uy*by+uz*bz)*by)/c0^2\nmzB = rho*uz+(bb*uz-(ux*bx+uy*by+uz*bz)*bz)/c0^2\nmx = rho*ux\nmy = rho*uy\nmz = rho*uz\nuH = uH0*sqrt({jx}^2+{jy}^2+{jz}^2)/rho\nuHx = uH0*{jx}/rho\nuHy = uH0*{jy}/rho\nuHz = uH0*{jz}/rho\nuex = ux-uH0*{jx}/rho\nuey = uy-uH0*{jy}/rho\nuez = uz-uH0*{jz}/rho\nue = sqrt({uex}^2+{uey}^2+{uez}^2)\nur = (x*ux+y*uy+z*uz)/r\nuxrot = ux+y*xSI*omegaSunSI/uSI\nuyrot = uy-x*xSI*omegaSunSI/uSI\nuphi = (uy*x-ux*y)/r\nulon = -sin(Lon)*ux+cos(Lon)*uy\nulat = -sin(Lat)*(cos(Lon)*ux+sin(Lon)*uy)+cos(Lat)*uz","score":1,"name":"funcdef","kind":"funcdef_inventory","metadata":{"kind":"idl_funcdef_inventory","relative_path":"share/IDL/General/funcdef.pro","why_relevant":"Parsed function names and expressions from share/IDL/General/funcdef.pro.","functions":[{"name":"mxB","expression":"rho*ux+(bb*ux-(ux*bx+uy*by+uz*bz)*bx)/c0^2"},{"name":"myB","expression":"rho*uy+(bb*uy-(ux*bx+uy*by+uz*bz)*by)/c0^2"},{"name":"mzB","expression":"rho*uz+(bb*uz-(ux*bx+uy*by+uz*bz)*bz)/c0^2"},{"name":"mx","expression":"rho*ux"},{"name":"my","expression":"rho*uy"},{"name":"mz","expression":"rho*uz"},{"name":"uH","expression":"uH0*sqrt({jx}^2+{jy}^2+{jz}^2)/rho"},{"name":"uHx","expression":"uH0*{jx}/rho"},{"name":"uHy","expression":"uH0*{jy}/rho"},{"name":"uHz","expression":"uH0*{jz}/rho"},{"name":"uex","expression":"ux-uH0*{jx}/rho"},{"name":"uey","expression":"uy-uH0*{jy}/rho"},{"name":"uez","expression":"uz-uH0*{jz}/rho"},{"name":"ue","expression":"sqrt({uex}^2+{uey}^2+{uez}^2)"},{"name":"ur","expression":"(x*ux+y*uy+z*uz)/r"},{"name":"uxrot","expression":"ux+y*xSI*omegaSunSI/uSI"},{"name":"uyrot","expression":"uy-x*xSI*omegaSunSI/uSI"},{"name":"uphi","expression":"(uy*x-ux*y)/r"},{"name":"ulon","expression":"-sin(Lon)*ux+cos(Lon)*uy"},{"name":"ulat","expression":"-sin(Lat)*(cos(Lon)*ux+sin(Lon)*uy)+cos(Lat)*uz"}],"function_count_sampled":40}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"show_data: pro show_data\ncategory: plotting","score":0.95,"name":"show_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_data: pro plot_data\ncategory: plotting","score":0.95,"name":"plot_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_log_data: pro plot_log_data\ncategory: plotting","score":0.95,"name":"plot_log_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_func: pro plot_func\ncategory: plotting","score":0.95,"name":"plot_func","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/geopack.pro","snippet":"geigse: pro geigse,xgei,ygei,zgei,xgse,ygse,zgse,j,epoch\ncategory: plotting","score":0.95,"name":"geigse","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/geopack.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"getvectors: pro getvectors, nvector, vectors\ncategory: plotting","score":0.95,"name":"getvectors","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}}],"provenance":{"mode_used":"keyword","scope":[]},"uncertainty":{"known_unknowns":["Runtime behavior for the current case not inspected."]},"swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked environment SWMF_ROOT: /Users/zkeheng/SWMFSoftware/SWMF","Resolved from SWMF_ROOT environment variable."]}
```


---

<sub>⏱️ 1m 12s</sub>

### ✅ `swmf-prototype-get_evidence`

**postprocessing**

<details>
<summary>Arguments</summary>

```json
{
  "query": "postprocessing",
  "task_type": "analysis",
  "goal": "postprocessing"
}
```

</details>

```
{"ok":true,"query":"postprocessing","mode":"hybrid","scope":[],"top_k":8,"goal":"postprocessing","task_type":"analysis","module":null,"summary":"0 workflow evidence item(s), 0 IDL catalog evidence item(s), and 8 supporting evidence item(s) found for 'postprocessing'","evidence":[{"type":"code","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/Scripts/PostProc.pl","snippet":"Known analysis entrypoint: PostProc.pl","score":1,"metadata":{"kind":"script","relative_path":"share/Scripts/PostProc.pl","why_relevant":"Known analysis entrypoint: PostProc.pl"}},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/swmf-analyze/SKILL.md","snippet":"## Evidence order\n\n1. `inspect_artifact(artifact_type=\"run_dir\", path=<run_dir>)`\n   — output file inventory and layout\n2. `get_evidence(mode=\"keyword\", goal=\"output format or field definition\")`\n   — field semantics, output variable definitions\n3. `get_evidence(query=\"postprocessing\", task_type=\"an…","score":null,"name":"Evidence order","kind":"doc_section","component":"","start_line":22,"metadata":{"kind":"doc_section","relative_path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/swmf-analyze/SKILL.md","why_relevant":"Supporting analysis evidence from search"}},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/support/swmf-postproc/SKILL.md","snippet":"## Purpose\n\nProvide specialized postprocessing knowledge that entry skills need but do not\nown directly.","score":null,"name":"Purpose","kind":"doc_section","component":"","start_line":12,"metadata":{"kind":"doc_section","relative_path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/support/swmf-postproc/SKILL.md","why_relevant":"Supporting analysis evidence from search"}},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/swmf-analyze/SKILL.md","snippet":"---\nname: swmf-analyze\ndescription: \"Use when the user wants to interpret SWMF outputs: what results mean, diagnostics from output files, field interpretation, or postprocessing discovery.\"\n---","score":null,"name":"__preamble__","kind":"doc_section","component":"","start_line":1,"metadata":{"kind":"doc_section","relative_path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/swmf-analyze/SKILL.md","why_relevant":"Supporting analysis evidence from search"}},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/support/swmf-postproc/SKILL.md","snippet":"---\nname: swmf-postproc\ntype: support\ndescription: \"Support skill. Provides deep postprocessing knowledge: IDL visualization, coupling architecture, output artifact inspection. Called by swmf-analyze and swmf-compare.\"\n---","score":null,"name":"__preamble__","kind":"doc_section","component":"","start_line":1,"metadata":{"kind":"doc_section","relative_path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/support/swmf-postproc/SKILL.md","why_relevant":"Supporting analysis evidence from search"}},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/support/swmf-postproc/SKILL.md","snippet":"## Scope\n\n* IDL procedure discovery and usage guidance\n* coupling architecture explanation and Mermaid diagrams\n* output artifact layout and interpretation context\n* postprocessing failure triage (before handing off to `swmf-debug`)\n\nNot in scope: general failure diagnosis, PARAM semantics, build/ru…","score":null,"name":"Scope","kind":"doc_section","component":"","start_line":17,"metadata":{"kind":"doc_section","relative_path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/support/swmf-postproc/SKILL.md","why_relevant":"Supporting analysis evidence from search"}},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/swmf-analyze/SKILL.md","snippet":"## When to use\n- \"What do these output files contain?\"\n- \"How do I plot the result?\"\n- \"What does this field value mean?\"\n- \"How do I run the postprocessing?\"\n- \"Are my results physically reasonable?\"\n- Any task about reading, interpreting, or processing simulation outputs","score":null,"name":"When to use","kind":"doc_section","component":"","start_line":8,"metadata":{"kind":"doc_section","relative_path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/swmf-analyze/SKILL.md","why_relevant":"Supporting analysis evidence from search"}},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/swmf-analyze/SKILL.md","snippet":"## Outputs\n\n* what output artifacts were found (from `inspect_artifact`)\n* field/variable definitions cited from evidence\n* postprocessing workflow evidence from `get_evidence(task_type=\"analysis\")`\n* workflow metadata on returned items:\n  * `metadata.kind`\n  * `metadata.relative_path`\n  * `metadata…","score":null,"name":"Outputs","kind":"doc_section","component":"","start_line":36,"metadata":{"kind":"doc_section","relative_path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/swmf-analyze/SKILL.md","why_relevant":"Supporting analysis evidence from search"}}],"provenance":{"mode_used":"keyword","scope":[]},"uncertainty":{"known_unknowns":["Runtime behavior for the current case not inspected."]},"swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked environment SWMF_ROOT: /Users/zkeheng/SWMFSoftware/SWMF","Resolved from SWMF_ROOT environment variable."]}
```


---

<sub>⏱️ 1m 19s</sub>

### ✅ `swmf-prototype-inspect_artifact`

**/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/z=0_var_3_t00020000_n00005000.out**

<details>
<summary>Arguments</summary>

```json
{
  "artifact_type": "result",
  "path": "/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/z=0_var_3_t00020000_n00005000.out"
}
```

</details>

```
{"ok":true,"artifact_type":"result","path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/z=0_var_3_t00020000_n00005000.out","question":"","summary":"SWMF IDL plot file 'z=0_var_3_t00020000_n00005000.out': REAL4, ndim=2, nw=20, variables: Rho, Ux, Uy, Uz, Bx, By, Bz, Ehot, I01, I02, Pe, P.","findings":[{"kind":"idl_plot_file_header","format":"binary","location":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/z=0_var_3_t00020000_n00005000.out","description":"SWMF IDL binary plot-file header detected (REAL4).","filetype":"REAL4","npictinfile":1,"headline":"2024-08-01T02:04:00; R R R g/cm3 km/s km/s km/s G G G erg/cm3 erg/cm3 erg/cm3 dyne/cm^2 dyne/cm^2 uA/m2 uA/m2 uA/m2 G G G K K","it":5000,"time":7200,"gencoord":1,"ndim":2,"neqpar":4,"nw":20,"nx":[281152,1],"coord_names":["x","y"],"variable_names":["Rho","Ux","Uy","Uz","Bx","By","Bz","Ehot","I01","I02","Pe","P","jx","jy","jz","b1x","b1y","b1z","te","ti"],"parameter_names":["xSI","r","g","cutz"],"header_length":500}],"evidence":[],"provenance":{"artifact_type":"result","path":"/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/z=0_var_3_t00020000_n00005000.out"},"uncertainty":{"known_unknowns":["Binary files cannot be inspected without specialized tools (IDL, netCDF, etc.).","SWMF output format detection is heuristic; may misclassify custom outputs."]},"swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked environment SWMF_ROOT: /Users/zkeheng/SWMFSoftware/SWMF","Resolved from SWMF_ROOT environment variable."]}
```


---

<sub>⏱️ 1m 27s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/support/swmf-postproc/IDL_VISUALIZATION.md.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/support/swmf-postproc/IDL_VISUALIZATION.md

<details>
<summary>300 lines</summary>

```
1. # IDL Visualization Playbook
2. 
3. Use this playbook only as a support policy for `swmf-analyze` or
4. `swmf-compare`. The entry skill owns the final answer; this file defines how to
5. gather and normalize IDL visualization evidence.
6. 
7. ## Supported Intents
8. 
9. - IDL setup and startup path guidance
10. - snapshot reading with `read_data`
11. - quick read-and-plot workflows with `show_data`
12. - plotting loaded snapshots with `plot_data`
13. - animation or multi-snapshot workflows with `animate_data`
14. - log and satellite plotting with `read_log_data`, `plot_log_data`, or `show_log_data`
15. - `func` selection, derived quantities, vector pairs, and `funcdef.pro` lookup
16. - `plotmode` selection for 1D, 2D scalar, vector, stream, contour, polar, and overplot modes
17. - non-regular grid handling, regular-grid transforms, slices, cuts, and graphics export
18. - listing IDL plotting procedures and separating entrypoints from helpers
19. 
20. ## Not In Scope
21. 
22. - diagnosing failed IDL execution beyond basic artifact observations
23. - changing SWMF output configuration; hand back to `swmf-configure`
24. - comparing two completed plots or runs; use `swmf-compare`
25. - inventing IDL function definitions without evidence from `funcdef.pro` or docs
26. 
27. ## Evidence Order
28. 
29. 1. If a run directory or output file is named:
30.    `inspect_artifact(artifact_type="run_dir"|"result", path=<path>)`
31. 2. Normalize the prompt before retrieval:
32.    - named procedure or workflow: `plot_data`, `show_data`, `read_data`, `animate_data`, `plot_log_data`, `read_log_data`
33.    - inventory request: `list IDL plotting procedures`
34.    - manual detail: `func`, `plotmode`, `transform`, `slice`, `export`
35.    - if the prompt is broad, do not pass it through unchanged to `get_evidence`
36. 3. For named procedures or procedure inventories:
37.    `get_evidence(query=<normalized procedure-or-inventory-task>, mode="keyword", goal="IDL procedure signature and usage")`
38.    - for animations, normalize to
39.      `get_evidence(query="animate_data", mode="keyword", goal="IDL procedure signature and usage")`
40. 4. For `func`, `plotmode`, transform, slicing, animation, log plotting, or export details:
41.    `get_evidence(query=<normalized specific-term>, mode="keyword", goal="IDL visualization manual detail")`
42. 5. For postprocessing entrypoints:
43.    `get_evidence(query="IDL postprocessing", task_type="analysis", goal="IDL visualization entrypoints")`
44. 6. Direct file reads are allowed only for files named by evidence, normally:
45.    `share/IDL/General/procedures.pro`, `share/IDL/General/funcdef.pro`,
46.    examples under `share/IDL/**`, or `docs/idl.md`.
47. 
48. ## MCP Evidence Contract
49. 
50. IDL evidence from MCP must stay factual:
51. 
52. - procedure name, kind, signature, keywords, category, source path, and line
53. - run-directory inventory and result-file type
54. - documentation snippets for `read_data`, `plot_data`, `show_data`, `animate_data`, `func`, `plotmode`, transforms, and export
55. - example file paths and exact snippets
56. - uncertainty such as missing IDL catalog, missing output path, or uninspected runtime behavior
57. 
58. If a vague request arrives, the support skill should first rewrite it into one
59. of the normalized retrieval forms above. If the normalized query still returns
60. no IDL evidence, fall back to the artifact name, a term from the file header, or
61. an exact procedure name mentioned in docs.
62. 
63. MCP must not emit recommended workflows, next tools, or plotting advice. The
64. agent infers the workflow from this playbook and the evidence.
65. 
66. ## Decision Matrix
67. 
68. - Quick single plot: `show_data`.
69. - Controlled single snapshot: `read_data` followed by `plot_data`.
70. - Controlled single snapshot export: generated `.pro` script with `read_data`, `set_device`, `plot_data`, and `close_device`.
71. - Multiple selected snapshot exports: generated `.pro` script that loops over files with `read_data`, `set_device`, `plot_data`, and `close_device`.
72. - Multiple frames or files: `animate_data`.
73. - Multiple frames, full frame series, or movies: generated `.pro` script with `animate_data`.
74. - Logfile columns: `read_log_data` followed by `plot_log_data`, or `show_log_data`.
75. - Derived logfile quantities: read the log as 1D data with `read_data`, then use `plot_data`.
76. - Structured 3D slice scan: `read_data`, configure `func`/`plotmode`, then `slice_data`.
77. 
78. ## IDL-First Execution Ladder
79. 
80. For requests that ask Codex to create a plot, image, movie, or export artifact,
81. use IDL as the renderer by default and use SWMF IDL macros before custom
82. graphics:
83. 
84. 1. Inspect the named run directory or result file with MCP. Use the evidence only
85.    to identify the artifact, variables, frame groups, and first/middle/last
86.    frames; do not manually reconstruct the plotted data unless IDL cannot run.
87. 2. Retrieve deterministic IDL evidence for the chosen SWMF entrypoint and for
88.    `func`, `plotmode`, and `export`.
89. 3. Create an `analysis/` directory next to the relevant output files and write a
90.    case-local `.pro` command script there. Put local plot choices near the top:
91.    `workdir`, `files`, `func`, `plotmode`, `plottitle`, `outbase`,
92.    `autorange`, `showxtitle`, and `showytitle`.
93.    The script should be a macro driver that sets documented variables and then
94.    calls `read_data`, `plot_data`, `show_data`, `animate_data`,
95.    `plot_log_data`, or `slice_data`.
96. 4. Execute the script with `idl`, capturing the transcript as
97.    `analysis/<outbase>.idl.log`, for example:
98.    `printf '@analysis/z0_u_bxy_export\nexit\n' | idl > analysis/z0_u_bxy_export.idl.log 2>&1`
99. 5. Verify expected `.ps`, `.eps`, `.pdf`, `.png`, or movie outputs exist before
100.    presenting them as completed artifacts.
101. 6. Only use Python, SVG, manual Fortran-record plotting, or hand-written IDL
102.    direct graphics (`contour`, `vector`, `triangulate`, `tvrd`, custom readers)
103.    as a last resort after IDL macro execution fails or evidence shows the SWMF
104.    macros cannot express the requested output, and the user explicitly accepts
105.    that fallback. Do not check for Python plotting libraries before trying the
106.    IDL path.
107. 
108. Assume `idl` is the preferred deployed renderer for IDL visualization tasks. Do
109. not spend the main workflow proving IDL installation up front; if execution
110. fails, inspect the log and then check `IDL_PATH`, `IDL_STARTUP`, and `idlrc`.
111. 
112. ## Workflow Policy
113. 
114. For IDL environment and startup setup:
115. 
116. 1. If you can find idl executable, then run idl. 
117. 2. If you cannot find idl, write the script as .pro file and give commands for user
118.    to execute them manually.
119. 
120. For artifact triage:
121. 
122. 1. Distinguish snapshot plot files from time-series logs:
123.    - `.out` is normally one snapshot, unless the header says otherwise.
124.    - `.outs` is a concatenated multi-snapshot plot file suitable for `animate_data`.
125.    - `.log` and `.sat` are log/satellite time series for log workflows.
126. 2. Inspect result files before naming variables. SWMF IDL plot files may be ASCII,
127.    `real4`, `real8`, or long-header `REAL4`/`REAL8`; use header fields for
128.    `headline`, `it`, `time`, `gencoord`, `ndim`, `neqpar`, `nw`, `nx`, coordinate
129.    names, variable names, and parameter names.
130. 3. Treat `.out` files that cannot be decoded as IDL plot files as generic result
131.    files; state the uncertainty instead of inventing variables.
132. 
133. For a snapshot plot:
134. 
135. 1. Establish the target artifact: run directory, `*.out`, `*.outs`, `*.idl`, or log/satellite file.
136. 2. Confirm the IDL entrypoint:
137.    - use `read_data` then `plot_data` when data is already chosen or multiple settings matter
138.    - use `show_data` for quick read-or-reread-and-plot
139.    - use `animate_data` for multiple frames, movies, or time evolution
140.    - use log procedures for `.log` or satellite time-series data
141. 3. Map the requested quantity to `func`:
142.    - raw variable names come from the plot-file header
143.    - predefined names must be confirmed in `funcdef.pro` or `docs/idl.md`
144.    - expressions are acceptable if grounded in available variables and scalar parameters
145.    - vector pairs use semicolon syntax such as `ux;uy` or `bx;bz`
146. 4. Select `plotmode` from data dimensionality and grid constraints:
147.    - 1D: `plot`, `plot_io`, `plot_oi`, `plot_oo`
148.    - 2D scalar: contour, filled contour, colorbar, polar, `tv`, surface, or shade modes
149.    - 2D vector: stream, vector, arrow, or velovect modes
150.    - irregular or generalized grids: prefer contour, filled contour, stream, or vector unless evidence shows a regular transform
151. 5. Add transform or slice setup only when the user asks for it or the artifact requires it.
152. 6. Add graphics export setup only when the user asks for saved files.
153. 
154. For log and satellite data:
155. 
156. 1. Use `read_log_data` when the task is selecting existing log columns by name.
157. 2. Use `plot_log_data` after `read_log_data`, or `show_log_data` for quick
158.    read-and-plot behavior.
159. 3. Use `read_data` on a log only when the user needs derived quantities,
160.    expressions, or normal `plot_data` behavior for 1D data.
161. 4. Ground log function names in `wlognames`, `show_log_data` prompts, or artifact
162.    evidence; do not assume a column exists.
163. 
164. For an animation from many single-snapshot plot files:
165. 
166. 1. Distinguish `*.out` from `*.outs`: a `*.out` file is one snapshot, while a
167.    `*.outs` file is the multi-snapshot input expected by `animate_data`.
168. 2. Locate the component output directory and select the desired cut pattern, for
169.    example `IH/z=0_var_3_t*.out`.
170. 3. If multiple matching `*.out` files are found and no matching `*.outs` file
171.    exists, propose concatenating them first:
172.     `cat z=0_var_3_t*.out > z=0_var_3.outs`
173. 4. Then generate a `.pro` file and run `animate_data` with
174.    `filename='z=0_var_3.outs'`.
175. 5. For non-interactive export, set `showmovie='n'`. Use `savemovie='ps'` for
176.    robust frame export, or `savemovie='png'` only when IDL image output is known
177.    to work in the environment.
178. 
179. For transforms and non-regular grids:
180. 
181. 1. A negative `ndim` or `gencoord=1` signals generalized/unstructured grid handling.
182. 2. Use `transform='regular'`, `transform='polar'`, `transform='unpolar'`,
183.    `transform='sphere'`, or `transform='my'` only when supported by manual evidence
184.    and the requested plot mode benefits from regular coordinates.
185. 3. Configure regular-grid transforms with `nxreg`, `xreglimits`, and
186.    `dotransform`; use `wreg`/`xreg` when plotting transformed data.
187. 4. If two files must be compared after transform, keep separate arrays such as
188.    `x1`, `w1`, `xreg1`, `wreg1` and form differences like `w=w1-w0` or
189.    `wreg=wreg1-wreg0`. If resolutions differ, use `coarsen` only when evidence
190.    supports the dimensions.
191. 
192. For domain selection, cuts, and vectors:
193. 
194. 1. For flat 2D plots, `!x.range` and `!y.range` are the broadest domain limits;
195.    reset them with `!x.range=0` and `!y.range=0`.
196. 2. For transformed regular grids, use `xreglimits` to limit the transformed
197.    domain.
198. 3. For structured grids, use `cut=grid(...)`; use `triplet(...)` or
199.    `quadruplet(...)` to coarsen and subset index ranges.
200. 4. For vector and streamline placement, use `velpos` and `velvector`; reset with
201.    `velpos=0` to return to random positions.
202. 5. Use `rcut` to remove data inside a circular/spherical inner radius; `body` in
203.    `plotmode` only covers that region visually.
204. 
205. For structured 3D slicing:
206. 
207. 1. Read the snapshot first with `read_data`; then configure `func`, `plotmode`,
208.    `slicedir`, `firstslice`, `dslice`, and `nslicemax`.
209. 2. Use `slice_data` to animate or scan slices.
210. 3. If slicing aborts and overwrites `x`/`w`, use `slice_data_restore`.
211. 
212. For comparison and multi-file plotting:
213. 
214. 1. Use `animate_data` when comparing multiple plot files or frames with common
215.    `func`, `plotmode`, and `plottitle` settings.
216. 2. Use per-file arrays such as `filename`, `func_file`, `plotmode_file`, and
217.    `plottitle_file` when files require different rendering.
218. 3. Use the IDL `compare` workflow or explicit differences (`w=w1-w0`,
219.    `wreg=wreg1-wreg0`) only after the files have compatible variables and grids.
220. 
221. For multiplot, overplot, and animation storage:
222. 
223. 1. Use `multiplot` to control subplot rows, columns, fill order, and starting
224.    slot; use `showxtitle`/`showytitle` when axis labels must appear on all panels.
225. 2. Use the `over` plotmode modifier, such as `streamover`, `vectorover`, or
226.    `arrowover`, to draw a later function on an earlier scalar plot.
227. 3. Use `nplotstore` with `max` or `mean` plotmode modifiers when the task asks for
228.    stored-frame maxima or averages.
229. 
230. For export:
231. 
232. 1. For a single plot, wrap `plot_data` or a one-frame `animate_data` call with
233.    `set_device,'file.eps'` and `close_device`; use `close_device,/pdf` or
234.    `close_device,pdf='convert',/delete` only when the conversion tool exists.
235. 2. For animation frames, set `savemovie='ps'`, `'png'`, `'tiff'`, `'jpeg'`, or
236.    `'bmp'`.
237. 3. For video export, set `savemovie='mp4'`, `'mov'`, or `'avi'`, and optionally
238.    `videofile` and `videorate`, before `animate_data`.
239. 4. When the user asks for PNG output and IDL generates PostScript, convert after
240.    IDL succeeds:
241.    `magick -density 180 input.ps -background white -alpha remove input.png`
242.    Use `convert` only if `magick` is unavailable.
243. 5. Keep the IDL transcript in `analysis/<outbase>.idl.log` and report failed IDL
244.    execution from that log instead of switching silently to another renderer.
245. 
246. For reusable IDL scripts:
247. 
248. 1. Use `@script` for command scripts that run in the current IDL session.
249. 2. Use `.r script` to compile a `.pro` file containing procedures/functions.
250. 3. Write a true `pro name` routine when arguments, local variables, or reuse
251.    matter; keep case-local filenames and plot choices near the top.
252. 
253. State that `u` is the IDL speed function from `funcdef`, while `Bx` and `By`
254. are header variables from the IH z=0 files. Mention
255. `plotmode='contbar ovelovect'` only as a denser vector alternative.
256. For three selected frames, prefer the `files` loop with `read_data` and
257. `plot_data`; for a full series, use the `.outs` file with `animate_data`.
258. 
259. ## Required Answer Shapes
260. 
261. For `idl_inventory`, include:
262. 
263. - `authority_level`
264. - `entry_points`
265. - `helpers_or_supporting_routines`
266. - `source_paths`
267. - `verification_note`
268. 
269. For `idl_usage_guidance`, include:
270. 
271. - `authoritative_procedure`
272. - `artifact_assumptions`
273. - `function_definition_evidence`
274. - `plotmode_evidence`
275. - `copy_paste_ready_example`
276. - `uncertainty`
277. 
278. For `idl_plot_workflow`, include:
279. 
280. - `target_artifact`
281. - `read_step`
282. - `func_choice`
283. - `plotmode_choice`
284. - `optional_transform_or_slice`
285. - `generated_pro_script`
286. - `idl_execution_command`
287. - `export_files`
288. - `copy_paste_ready_example`
289. - `known_unknowns`
290. 
291. ## Guardrails
292. 
293. - Do not treat helper routines as the main plotting interface.
294. - Do not state a variable exists in the output unless it came from artifact inspection, file header evidence, or explicit user input.
295. - Do not claim IDL is installed or runnable unless the environment was inspected.
296. - Do not substitute Python/SVG/manual binary plotting for IDL unless IDL failed
297.   and the user accepted that fallback.
298. - Prefer commands that can be pasted into an IDL session; label shell setup separately.
299. - If evidence conflicts, say what is deterministic and what is inferred.
300.
```

</details>


---

<sub>⏱️ 1m 35s</sub>

### ✅ `swmf-prototype-get_evidence`

**read_data**

<details>
<summary>Arguments</summary>

```json
{
  "query": "read_data",
  "mode": "keyword",
  "goal": "IDL procedure signature and usage"
}
```

</details>

````
{"ok":true,"query":"read_data","mode":"keyword","scope":[],"top_k":8,"goal":"IDL procedure signature and usage","task_type":"lookup","module":null,"summary":"1 deterministic IDL evidence item(s) and 2 supporting evidence item(s) found for 'read_data'","evidence":[{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"read_data: pro read_data\ncategory: data_reading\n==============================================================================","score":1,"name":"read_data","kind":"pro","start_line":568,"metadata":{"kind":"idl_procedure_signature","relative_path":"share/IDL/General/procedures.pro","why_relevant":"Exact IDL procedure match from the deterministic IDL catalog.","category":"data_reading","params":[],"keywords":[]}},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/support/swmf-postproc/IDL_VISUALIZATION.md","snippet":"### Usage questions\nExamples:\n- \"how do I plot func U\"\n- \"how do I use plot_func for SC z=0\"\n\nFirst tool:\n```\nget_evidence(mode=\"keyword\", query=<procedure_name>, goal=\"IDL procedure signature and usage\")\n```\nPrecision follow-up:\n- `get_evidence(mode=\"keyword\", goal=\"IDL procedure signature and usag…","score":null,"name":"Usage questions","kind":"doc_section","component":"","start_line":38},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/agent_assets/skills/support/swmf-postproc/SKILL.md","snippet":"## Tool Protocol\n\nFor output inventory:\n```\ninspect_artifact(artifact_type=\"run_dir\", path=<run_dir>)\n```\n\nFor IDL procedures:\n```\nget_evidence(mode=\"keyword\", goal=\"IDL procedure signature and usage\")\n```\nPrecision follow-up:\n```\nget_evidence(mode=\"keyword\", goal=\"IDL procedure detail or category n…","score":null,"name":"Tool Protocol","kind":"doc_section","component":"","start_line":38}],"provenance":{"mode_used":"keyword","scope":[]},"uncertainty":{"known_unknowns":["Runtime behavior for the current case not inspected."]},"swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked environment SWMF_ROOT: /Users/zkeheng/SWMFSoftware/SWMF","Resolved from SWMF_ROOT environment variable."]}
````


---

<sub>⏱️ 1m 35s</sub>

### ✅ `swmf-prototype-get_evidence`

**plotmode**

<details>
<summary>Arguments</summary>

```json
{
  "query": "plotmode",
  "mode": "keyword",
  "goal": "IDL visualization manual detail"
}
```

</details>

```
{"ok":true,"query":"plotmode","mode":"keyword","scope":[],"top_k":8,"goal":"IDL visualization manual detail","task_type":"lookup","module":null,"summary":"8 deterministic IDL evidence item(s) and 0 supporting evidence item(s) found for 'plotmode'","evidence":[{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md","snippet":"You may combine two function names with the ; character representing two\ncomponents of a vector, e.g. ux;uy or bx;bz, which can either be plotted as a\nvectorfield by the velovect, vector and arrow plot modes, or as streamlines\nor fieldlines, using\n                p the stream plotting modes. For other plotting modes the\nabsolute value ux2 + uy 2 is plotted. You can also put a minus sign in front of\nany function or variable name, which will simply multiply the value of the rest\nof the string by −1. For example ’-Ti’ plots (−1)*temperature of ions. This is\njust a shorthand for the general syntax ’-Ti’.\n\n\n10     Plotting modes in string plotmode\nThere are many plotting modes available. These can be listed in the plotmode\nstring for each function separated by spaces. If the number of plotting modes is\nless than the number of functions, the last plotting mode is applied for the rest\nof the fu...","score":1,"name":"plotmode","kind":"manual_section","start_line":456,"metadata":{"kind":"idl_manual_section","relative_path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md","why_relevant":"plotmode strings for 1D, scalar 2D, vector, overplot, modifiers","topic":"plotmode","line_start":456,"line_end":585}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"show_data: pro show_data\ncategory: plotting","score":0.95,"name":"show_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_data: pro plot_data\ncategory: plotting","score":0.95,"name":"plot_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_log_data: pro plot_log_data\ncategory: plotting","score":0.95,"name":"plot_log_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_func: pro plot_func\ncategory: plotting","score":0.95,"name":"plot_func","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/geopack.pro","snippet":"geigse: pro geigse,xgei,ygei,zgei,xgse,ygse,zgse,j,epoch\ncategory: plotting","score":0.95,"name":"geigse","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/geopack.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"getvectors: pro getvectors, nvector, vectors\ncategory: plotting","score":0.95,"name":"getvectors","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_color_bar: pro plot_color_bar, position, a, format=format, title=title\ncategory: plotting","score":0.95,"name":"plot_color_bar","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}}],"provenance":{"mode_used":"keyword","scope":[]},"uncertainty":{"known_unknowns":["Runtime behavior for the current case not inspected."]},"swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked environment SWMF_ROOT: /Users/zkeheng/SWMFSoftware/SWMF","Resolved from SWMF_ROOT environment variable."]}
```


---

<sub>⏱️ 1m 35s</sub>

### ✅ `swmf-prototype-get_evidence`

**set_device close_device**

<details>
<summary>Arguments</summary>

```json
{
  "query": "set_device close_device",
  "mode": "keyword",
  "goal": "IDL visualization manual detail"
}
```

</details>

```
{"ok":true,"query":"set_device close_device","mode":"keyword","scope":[],"top_k":8,"goal":"IDL visualization manual detail","task_type":"lookup","module":null,"summary":"2 deterministic IDL evidence item(s) and 6 supporting evidence item(s) found for 'set_device close_device'","evidence":[{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/set_device.pro","snippet":"set_device: pro set_device, psfile, port=port, land=land, square=square, eps=eps, $\ncategory: utility\nCopyright (C) 2002 Regents of the University of Michigan,\nportions used with permission\nFor more information, see http://csem.engin.umich.edu/tools/swmf\n^CFG COPYRIGHT UM","score":1,"name":"set_device","kind":"pro","start_line":5,"metadata":{"kind":"idl_procedure_signature","relative_path":"share/IDL/General/set_device.pro","why_relevant":"Exact IDL procedure match from the deterministic IDL catalog.","category":"utility","params":["psfile","$"],"keywords":["port","land","square","eps"]}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/close_device.pro","snippet":"close_device: pro close_device, pdf=pdf, png=png, delete=delete, verbose=verbose\ncategory: utility\nCopyright (C) 2002 Regents of the University of Michigan,\nportions used with permission\nFor more information, see http://csem.engin.umich.edu/tools/swmf","score":1,"name":"close_device","kind":"pro","start_line":4,"metadata":{"kind":"idl_procedure_signature","relative_path":"share/IDL/General/close_device.pro","why_relevant":"Exact IDL procedure match from the deterministic IDL catalog.","category":"utility","params":[],"keywords":["pdf","png","delete","verbose"]}},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/SWMF/PT/AMPS/srcEarth/gridless/test/README_density_tests.md","snippet":"## 8. Files\n\n| File | Description |\n|------|-------------|\n| `test_density_dipole_4pts.in`  | AMPS input file — all 4 test points, DIPOLE field, energy channels |\n| `test_density_analytic.py`     | Python comparison script — density, total flux, per-channel flux |\n| `README_density_tests.md`      | …","score":null,"name":"8. Files","kind":"doc_section","component":"","start_line":276},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/SWMF/PT/AMPS/srcEarth/gridless/test/README_density_tests.md","snippet":"### 9.5 Test logic in test_density_analytic.py\n\nFor each test point and each channel:\n\n| Channel status | Test criterion | Rationale |\n|---------------|---------------|-----------|\n| E1 > E_cut (fully above cutoff) | \\|F_model − F_analytic\\| / F_analytic < 5% | T = T_geo exactly; analytic formula is…","score":null,"name":"9.5 Test logic in test_density_analytic.py","kind":"doc_section","component":"","start_line":381},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/SWMF/UA/MGITM/srcDoc/set_inputs.tex","snippet":"\\subsubsection{ALTITUDE}\n\\label{altitude.sec}\n\nThe upper and lower altitude limits (in kilometers) may be specified here.  These values default to 500 km and 95 km, respectively.  Setting the altitude limits above or below these values may result in unstable model runs.\n\nUseStretchedAltitude may als…","score":null,"name":"ALTITUDE","kind":"doc_section","component":"UA","start_line":801},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/SWMF/UA/MGITM/srcDoc/set_inputs.tex","snippet":"\\subsubsection{AMIEFILES}\n\\label{amiefiles.sec}\n\nThis option allows the user to specify the electrodynamic state of the polar regions using the Assimilative Mapping of Ionospheric Electrodynamics (AMIE) model~\\citep{ridley:2004aa}.  Input files separately specify the conditions at the northern and s…","score":null,"name":"AMIEFILES","kind":"doc_section","component":"UA","start_line":578},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/SWMF/GM/BATSRUS/Doc/Tex/introduction.tex","snippet":"\\section{Acknowledgments}\n\n\\BATSRUS\\ was developed at the University of Michigan starting in 1996\nwith funding under the NASA High Performance Computing and Communications (HPCC)\nEarth and Space Sciences (ESS) program (NASA ESS Cooperative Agreement \nNumber: NCCS5-146).  Continued work is funded by …","score":null,"name":"Acknowledgments","kind":"doc_section","component":"GM","start_line":66},{"type":"doc","path":"/Users/zkeheng/SWMFSoftware/SWMF/doc/Tex/SWMF_introduction.tex","snippet":"\\section{Acknowledgments}\n\nThe first version of the SWMF was developed at the Center for \nSpace Environment Modeling (CSEM) of the University of Michigan under \nthe NASA Earth Science Technology Office (ESTO) \nComputational Technologies (CT) Project (NASA\nCAN NCC5-614). The project was entitled as `…","score":null,"name":"Acknowledgments","kind":"doc_section","component":"","start_line":43}],"provenance":{"mode_used":"keyword","scope":[]},"uncertainty":{"known_unknowns":["Runtime behavior for the current case not inspected."]},"swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked environment SWMF_ROOT: /Users/zkeheng/SWMFSoftware/SWMF","Resolved from SWMF_ROOT environment variable."]}
```


---

<sub>⏱️ 1m 35s</sub>

### ✅ `swmf-prototype-get_evidence`

**u speed function funcdef**

<details>
<summary>Arguments</summary>

```json
{
  "query": "u speed function funcdef",
  "mode": "keyword",
  "goal": "IDL visualization manual detail"
}
```

</details>

```
{"ok":true,"query":"u speed function funcdef","mode":"keyword","scope":[],"top_k":8,"goal":"IDL visualization manual detail","task_type":"lookup","module":null,"summary":"8 deterministic IDL evidence item(s) and 0 supporting evidence item(s) found for 'u speed function funcdef'","evidence":[{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md","snippet":"slicedir (1, 2, or 3)? 3\nIf the grid size is e.g. 50∗100∗60, then there are 60 slices to plot. The number\nof animated slices can be reduced: at most nslicemax slices are shown starting\n\n\n                                         22\n\nfrom firstslice, and only every dslice-th slice is shown. The plots can be further\nreduced by setting the cut array, however, now indices in cut refer to a single\nslice. The grid2d index array (generated by the first slice data, in this case it\nis a 50∗100 array) can be used, e.g.\n\ncut=grid2d(*,30:70)\nFor plotmode=’vector’ the vectors are not advected with the flow (i.e. vel-\nspeed=0) since it does not make sense for the slices.\n    The x and w arrays are overwritten with the 2D cuts during the slicing, and\nonly restored to the 3D arrays at the end. If the slicing failed for any reason,\nuse\nslice_data_restore\nto restore the arrays.\n\n\n16     Function definition...","score":1,"name":"funcdef","kind":"manual_section","start_line":958,"metadata":{"kind":"idl_manual_section","relative_path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md","why_relevant":"funcdef.pro function definition rules","topic":"funcdef","line_start":958,"line_end":1005}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/funcdef.pro","snippet":"mxB = rho*ux+(bb*ux-(ux*bx+uy*by+uz*bz)*bx)/c0^2\nmyB = rho*uy+(bb*uy-(ux*bx+uy*by+uz*bz)*by)/c0^2\nmzB = rho*uz+(bb*uz-(ux*bx+uy*by+uz*bz)*bz)/c0^2\nmx = rho*ux\nmy = rho*uy\nmz = rho*uz\nuH = uH0*sqrt({jx}^2+{jy}^2+{jz}^2)/rho\nuHx = uH0*{jx}/rho\nuHy = uH0*{jy}/rho\nuHz = uH0*{jz}/rho\nuex = ux-uH0*{jx}/rho\nuey = uy-uH0*{jy}/rho\nuez = uz-uH0*{jz}/rho\nue = sqrt({uex}^2+{uey}^2+{uez}^2)\nur = (x*ux+y*uy+z*uz)/r\nuxrot = ux+y*xSI*omegaSunSI/uSI\nuyrot = uy-x*xSI*omegaSunSI/uSI\nuphi = (uy*x-ux*y)/r\nulon = -sin(Lon)*ux+cos(Lon)*uy\nulat = -sin(Lat)*(cos(Lon)*ux+sin(Lon)*uy)+cos(Lat)*uz","score":1,"name":"funcdef","kind":"funcdef_inventory","metadata":{"kind":"idl_funcdef_inventory","relative_path":"share/IDL/General/funcdef.pro","why_relevant":"Parsed function names and expressions from share/IDL/General/funcdef.pro.","functions":[{"name":"mxB","expression":"rho*ux+(bb*ux-(ux*bx+uy*by+uz*bz)*bx)/c0^2"},{"name":"myB","expression":"rho*uy+(bb*uy-(ux*bx+uy*by+uz*bz)*by)/c0^2"},{"name":"mzB","expression":"rho*uz+(bb*uz-(ux*bx+uy*by+uz*bz)*bz)/c0^2"},{"name":"mx","expression":"rho*ux"},{"name":"my","expression":"rho*uy"},{"name":"mz","expression":"rho*uz"},{"name":"uH","expression":"uH0*sqrt({jx}^2+{jy}^2+{jz}^2)/rho"},{"name":"uHx","expression":"uH0*{jx}/rho"},{"name":"uHy","expression":"uH0*{jy}/rho"},{"name":"uHz","expression":"uH0*{jz}/rho"},{"name":"uex","expression":"ux-uH0*{jx}/rho"},{"name":"uey","expression":"uy-uH0*{jy}/rho"},{"name":"uez","expression":"uz-uH0*{jz}/rho"},{"name":"ue","expression":"sqrt({uex}^2+{uey}^2+{uez}^2)"},{"name":"ur","expression":"(x*ux+y*uy+z*uz)/r"},{"name":"uxrot","expression":"ux+y*xSI*omegaSunSI/uSI"},{"name":"uyrot","expression":"uy-x*xSI*omegaSunSI/uSI"},{"name":"uphi","expression":"(uy*x-ux*y)/r"},{"name":"ulon","expression":"-sin(Lon)*ux+cos(Lon)*uy"},{"name":"ulat","expression":"-sin(Lat)*(cos(Lon)*ux+sin(Lon)*uy)+cos(Lat)*uz"}],"function_count_sampled":40}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"show_data: pro show_data\ncategory: plotting","score":0.95,"name":"show_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_data: pro plot_data\ncategory: plotting","score":0.95,"name":"plot_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_log_data: pro plot_log_data\ncategory: plotting","score":0.95,"name":"plot_log_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_func: pro plot_func\ncategory: plotting","score":0.95,"name":"plot_func","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/geopack.pro","snippet":"geigse: pro geigse,xgei,ygei,zgei,xgse,ygse,zgse,j,epoch\ncategory: plotting","score":0.95,"name":"geigse","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/geopack.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"getvectors: pro getvectors, nvector, vectors\ncategory: plotting","score":0.95,"name":"getvectors","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}}],"provenance":{"mode_used":"keyword","scope":[]},"uncertainty":{"known_unknowns":["Runtime behavior for the current case not inspected."]},"swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked environment SWMF_ROOT: /Users/zkeheng/SWMFSoftware/SWMF","Resolved from SWMF_ROOT environment variable."]}
```


---

<sub>⏱️ 1m 50s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/set_device.pro.**

/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/set_device.pro

<details>
<summary>155 lines</summary>

```
1. ;  Copyright (C) 2002 Regents of the University of Michigan, 
2. ;  portions used with permission 
3. ;  For more information, see http://csem.engin.umich.edu/tools/swmf
4. ;^CFG COPYRIGHT UM
5. pro set_device, psfile, port=port, land=land, square=square, eps=eps, $
6.                 psfont=psfont, xratio=xratio, yratio=yratio
7. 
8.   ; Parameter defaults and conversions
9. 
10.   if not keyword_set(psfile) then psfile = 'idl.ps'
11.   common SETDEVICE, NameFile
12.   NameFile = psfile
13. 
14.   orientation = 'normal'
15.   if keyword_set(land)   then orientation='land'
16.   if keyword_set(port)   then orientation='port'
17.   if keyword_set(square) then orientation='square'
18. 
19.   if not keyword_set(xratio) then xratio = 1.0
20.   if not keyword_set(yratio) then yratio = 1.0
21. 
22.   if n_elements(psfont) eq 0  then psfont = 28
23. 
24.   ; If file extension is .eps it is an EPS file for sure
25.   if stregex(NameFile,'.eps$',/b) then eps = 1
26. 
27.   ; Set sizes and offsets
28.   case (orientation) of
29.      'normal': begin
30.         xs   = 10*xratio
31.         ys   =  7*yratio
32.         xoff = 11*xratio - (11*xratio - xs)/1.5
33.         yoff = (8.5*yratio - ys)/2.0
34.         land=0
35.      end
36.      'land': begin
37.         xs   = 10*xratio
38.         ys   = 7*yratio
39.         xoff = (8.5*yratio-ys)/2.0
40.         yoff = 11*xratio-(11*xratio-xs)/1.5
41.         land=1
42.      end
43.      'port': begin
44.         xs = 7.5*xratio
45.         ys = 9.5*yratio
46.         xoff = (8.5*xratio-xs)/2.0
47.         yoff = (11*yratio-ys)/2.0
48.         land=0
49.      end
50.      'square': begin
51.         xs = 7.5*xratio
52.         ys = 7.5*yratio
53.         xoff = (8.5*xratio-xs)/2.0
54.         yoff = (8.5*yratio-ys)/2.0
55.         land=0
56.      end
57.   endcase
58. 
59.   set_plot, 'PS', /copy, /interpolate
60. 
61.   !p.font = 0
62. 
63.   case (psfont) of
64.        -1  : device, file = psfile, encapsulated=eps, /color, bits=8,         $
65.                 /inches, landscape=land, xsize = xs, ysize = ys, $
66.                xoff = xoff, yoff = yoff
67. 
68. 	0  : device, file = psfile, encapsulated=eps, /color, bits=8,	      $
69. 		/inches, landscape=land, xsize = xs, ysize = ys, $
70. 		xoff = xoff, yoff = yoff,  $
71. 		/Courier 
72. 	1  : device, file = psfile, encapsulated=eps, /color, bits=8,	      $
73. 		/inches, landscape=land, xsize = xs, ysize = ys, $
74. 		xoff = xoff, yoff = yoff,  $
75. 		/Courier, /Bold 
76.     	2  : device, file = psfile, encapsulated=eps, /color, bits=8,	      $
77. 		/inches, landscape=land, xsize = xs, ysize = ys, $
78. 		xoff = xoff, yoff = yoff,  $
79. 		/Courier, /Oblique 
80. 	3  : device, file = psfile, encapsulated=eps, /color, bits=8,	      $
81. 		/inches, landscape=land, xsize = xs, ysize = ys, $
82. 		xoff = xoff, yoff = yoff,  $
83. 		/Courier, /Bold, /Oblique
84.        	4  : device, file = psfile, encapsulated=eps, /color, bits=8,	      $
85. 		/inches, landscape=land, xsize = xs, ysize = ys, $
86. 		xoff = xoff, yoff = yoff,  $
87. 		/Helvetica
88.       	5  : device, file = psfile, encapsulated=eps, /color, bits=8,	      $
89. 		/inches, landscape=land, xsize = xs, ysize = ys, $
90. 		xoff = xoff, yoff = yoff,  $
91. 		/Helvetica, /Bold
92.     	6  : device, file = psfile, encapsulated=eps, /color, bits=8,	      $
93. 		/inches, landscape=land, xsize = xs, ysize = ys, $
94. 		xoff = xoff, yoff = yoff,  $
95. 		/Helvetica, /Oblique
96.        	8  : device, file = psfile, encapsulated=eps, /color, bits=8,         $
97. 		/inches, landscape=land, xsize = xs, ysize = ys, $
98. 		xoff = xoff, yoff = yoff,  $
99. 		/Helvetica, /Bold, /Oblique 
100.     	12 : device, file = psfile, encapsulated=eps, /color, bits=8,	      $
101. 		/inches, landscape=land, xsize = xs, ysize = ys, $
102. 		xoff = xoff, yoff = yoff,  $
103. 		/Avantgarde, /Book 
104.      	13 : device, file = psfile, encapsulated=eps, /color, bits=8,	      $
105. 		/inches, landscape=land, xsize = xs, ysize = ys, $
106. 		xoff = xoff, yoff = yoff,  $
107. 		/Avantgarde, /Book, /Oblique
108. 	14 : device, file = psfile, encapsulated=eps, /color, bits=8,	$
109. 		/inches, landscape=land, xsize = xs, ysize = ys, $
110. 		xoff = xoff, yoff = yoff,  $
111. 		/Avantgarde, /Demi 
112.       	15 : device, file = psfile, encapsulated=eps, /color, bits=8,	      $
113. 		/inches, landscape=land, xsize = xs, ysize = ys, $
114. 		xoff = xoff, yoff = yoff,  $
115. 		/Avantgarde, /Demi, /Oblique
116.        	20 : device, file = psfile, encapsulated=eps, /color, bits=8, $
117. 		/inches, landscape=land, xsize = xs, ysize = ys, $
118. 		xoff = xoff, yoff = yoff,  $
119. 		/Schoolbook
120.    	21 : device, file = psfile, encapsulated=eps, /color, bits=8,$
121. 		/inches, landscape=land, xsize = xs, ysize = ys, $
122. 		xoff = xoff, yoff = yoff,  $
123. 		/Schoolbook, /Bold
124.       	22 : device, file = psfile, encapsulated=eps, /color, bits=8,$
125. 		/inches, landscape=land, xsize = xs, ysize = ys, $
126. 		xoff = xoff, yoff = yoff,  $
127. 		/Schoolbook, /Italic
128.        	23 : device, file = psfile, encapsulated=eps, /color, bits=8,	$
129. 		/inches, landscape=land, xsize = xs, ysize = ys, $
130. 		xoff = xoff, yoff = yoff,  $
131. 		/Schoolbook, /Bold, /Italic 
132. 	28 : device, file = psfile, encapsulated=eps, /color, bits=8,	$
133. 		/inches, landscape=land, xsize = xs, ysize = ys, $
134. 		xoff = xoff, yoff = yoff,  $
135. 		/Times, font_index=5
136. 	29 : device, file = psfile, encapsulated=eps, /color, bits=8,	$
137. 		/inches, landscape=land, xsize = xs, ysize = ys, $
138. 		xoff = xoff, yoff = yoff,  $
139. 		/Times, /Bold
140. 	30 : device, file = psfile, encapsulated=eps, /color, bits=8,	$
141. 		/inches, landscape=land, xsize = xs, ysize = ys, $
142. 		xoff = xoff, yoff = yoff,  $
143. 		/Times, /Italic
144. 	31 : device, file = psfile, encapsulated=eps, /color, bits=8,	$
145. 		/inches, landscape=land, xsize = xs, ysize = ys, $
146. 		xoff = xoff, yoff = yoff,  $
147. 		/Times, /Bold, /Italic
148. 
149.     endcase
150. 
151.   return
152. 
153. end
154. 
155.
```

</details>


---

<sub>⏱️ 1m 51s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/close_device.pro.**

/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/close_device.pro

<details>
<summary>36 lines</summary>

```
1. ;  Copyright (C) 2002 Regents of the University of Michigan,
2. ;  portions used with permission 
3. ;  For more information, see http://csem.engin.umich.edu/tools/swmf
4. pro close_device, pdf=pdf, png=png, delete=delete, verbose=verbose
5. 
6.   if !d.name ne 'PS' then return
7.   device, /close
8.   set_plot, 'X'
9.   !p.font=-1
10. 
11.   if not keyword_set(pdf) and not keyword_set(png) then return
12. 
13.   ;; Convert PS/EPS file to PDF or PNG and remove original if required
14.   common SETDEVICE, NameFile
15.   OutFile = NameFile
16.   i = strpos(OutFile,'.',/reverse_search)
17.   OutFile = strmid(OutFile, 0, i)
18. 
19.   if keyword_set(pdf) then begin
20.      ;; Use value of pdf or the default conversion command
21.      if typename(pdf) eq "STRING" then Convert = pdf else Convert = 'epspdf'
22.      OutFile += '.pdf'
23.   endif else begin
24.      if typename(png) eq "STRING" then Convert = png else Convert = 'convert'
25.      OutFile += '.png'
26.   endelse
27.   Command = Convert + ' ' + NameFile + ' ' + OutFile
28. 
29.   if keyword_set(delete) then Command = Command + '; /bin/rm ' + NameFile
30. 
31.   if keyword_set(verbose) then print,'Command = ', Command
32. 
33.   spawn, Command
34. 
35. end
36.
```

</details>


---

<sub>⏱️ 1m 53s</sub>

### ❌ `view`

**view the file at /Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/read_data.pro.**

/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/read_data.pro

```
Path does not exist
```


---

<sub>⏱️ 1m 52s</sub>

### ❌ `view`

**view the file at /Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/plot_data.pro.**

/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/plot_data.pro

```
Path does not exist
```


---

<sub>⏱️ 1m 59s</sub>

### ✅ `rg`

**^\s*pro\s+(read_data|plot_data|show_data|animate_data)\b**

"^\s*pro\s+(read_data|plot_data|show_data|animate_data)\b" in *.pro (~/SWMFSoftware/SWMF/share/IDL)

```
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:568:pro read_data
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:738:pro plot_data
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:860:pro show_data
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:867:pro animate_data
```


---

<sub>⏱️ 2m 2s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro.**

/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro (lines 520-760)

<details>
<summary>241 lines</summary>

```
520. ; measure of the minimum distance between two curves measured as
521. ; the averaged minimum of the sum of distances in the X and Y directions.
522. 
523.   n1 = n_elements(x1)
524.   n2 = n_elements(x2)
525.   d1 = 0d0
526.   d2 = 0d0
527.   for i = 0, n1-1 do d1 += min( abs(x1(i) - x2) + abs(y1(i) - y2) )
528.   for i = 0, n2-1 do d2 += min( abs(x2(i) - x1) + abs(y2(i) - y1) )
529.   d = (d1/n1 + d2/n2)/2
530.   return, d
531. end
532. ;==============================================================================
533. function curve_int_distance, x1, y1, x2, y2
534. 
535. ; Evaluates the distance between two curves (data & model results)
536. ; independent of the coordinate system so that errors in x and y
537. ; coordinates are treated equally.
538. ; (x1,y1) & (x2,y2) represent the x,y coordinates curves 1 and 2 respectively
539. ; d1 is the average of the minimum distance between the two curves 
540. ; integrated along curve 1 and d2 is integrated along curve 2
541. ; Function returns the error (distance) d, which is a symmetric
542. ; function of the two curves.
543. 
544.   n1 = n_elements(x1)
545.   n2 = n_elements(x2)
546.   d1=0d0
547.   d2=0d0
548. 
549.   x1c= (x1(1:n1-1) + x1(0:n1-2))/2
550.   x2c= (x2(1:n2-1) + x2(0:n2-2))/2
551.   y1c= (y1(1:n1-1) + y1(0:n1-2))/2
552.   y2c= (y2(1:n2-1) + y2(0:n2-2))/2
553. 
554.   d1c = sqrt( (x1(1:n1-1) - x1(0:n1-2))^2 + (y1(1:n1-1) - y1(0:n1-2))^2 )
555.   d2c = sqrt( (x2(1:n2-1) - x2(0:n2-2))^2 + (y2(1:n2-1) - y2(0:n2-2))^2 )
556. 
557.   len1 = total(d1c)
558.   len2 = total(d2c)
559. 
560.   for i = 0, n1-2 do $
561.      d1 += d1c(i)*min( sqrt( (x1c(i) - x2c)^2 + (y1c(i) - y2c)^2 ) )
562.   for i = 0, n2-2 do $
563.      d2 += d2c(i)*min( sqrt( (x2c(i) - x1c)^2 + (y2c(i) - y1c)^2 ) )
564.   d = (d1/len1 + d2/len2)/2
565.   return, d
566. end
567. ;==============================================================================
568. pro read_data
569. 
570. ;    Read the npict-th snapshot from an ascii or binary data file into
571. ;    the x (coordinates) and w (data) arrays. 
572. ;    If dotransfrom='y' the data is transformed according to 
573. ;    the transformation parameters, potentially into xreg, wreg.
574. ;
575. ;    Usage: 
576. ;
577. ; filename='...' ; set file to read from (optional)
578. ; npict=...      ; set snapshot index (optional)
579. ; read_data
580. ;
581. ;    read_data will prompt you for "filename(s)" and "npict"
582. ;    unless they are already set. Previous settings can be erased by 
583. ;
584. ; set_default_values
585. ;
586. ;    or modified explicitly, e.g.:
587. ;
588. ; filename='data/example.ini'
589. ; npict=1
590. ;
591. ;    The "x" and "w" arrays and the header info will be read from the file. 
592. ;
593. ;    If a file is read with generalized coordinates, "gencoord=1" is set,
594. ;    and the original data is transformed according to the "transform"
595. ;    string variable into "xreg" and "wreg".
596. ;
597. ;    The same npict-th snapshot can be read from up to 10 files by e.g. setting
598. ;
599. ; filename='data/file1.ini data/file2.out'
600. ;
601. ;    In this case the data is read into x0,w0 and x1,w1 for the two files,
602. ;    and possibly transformeed into wreg0,wreg1.
603. ;
604. ;    To plot a variable with IDL functions, type e.g.:
605. ;
606. ; plot, x(*,0), w(*,5,2)
607. ;
608. ;    or use the procedure
609. ;
610. ; plot_data
611. 
612.   common debug_param & on_error, onerror
613. 
614.   common ask_param, doask
615.   common getpict_param
616.   common animate_param
617.   common plot_data
618.   common file_head
619.   common transform_param
620. 
621.   nfile = 0
622.   askstr, 'filename(s)   ', filename, doask
623.   string_to_array, filename, filenames, nfile, /wildcard
624. 
625.   if not keyword_set(filenames) then begin
626.      print, 'Error in read_data: no matching filename was found.'
627.      retall
628.   endif
629. 
630.   if nfile gt 10 then begin
631.      print,'Error in read_data: cannot handle more than 10 files.'
632.      print,'nfile     = ', nfile
633.      print,'filenames = ', filenames
634.      retall
635.   endif
636.   get_file_types
637.   print, 'filetype(s)   =', filetypes
638.   print, 'npictinfile(s)=', npictinfiles
639.   ;; If all files have a single snapshot or all files are log files
640.   if max(npictinfiles) eq 1 or min(filetypes eq 'log') eq 1 then npict = 1
641.   asknum, 'npict', npict, doask
642.   print
643. 
644.   for ifile = 0, nfile - 1 do begin
645. 
646.      ;; Read data from file ifile
647. 
648.      print
649. 
650.      open_file, 10, filenames(ifile), filetypes(ifile)
651.      if n_elements(firstpict) eq nfile $
652.         and max(firstpict) ne min(firstpict) then npict=firstpict[ifile]
653.      get_pict, 10, filenames(ifile), filetypes(ifile), $
654.                npict<npictinfiles(ifile), error
655. 
656.      show_head, ifile
657. 
658.      if nfile gt 1 then begin
659.         case ifile of
660.            0: begin
661.               w0 = w
662.               x0 = x
663.               help, x0, w0
664.            end
665.            1: begin
666.               w1 = w
667.               x1 = x
668.            end
669.            2: begin
670.               w2 = w
671.               x2 = x
672.            end
673.            3: begin
674.               w3 = w
675.               x3 = x
676.            end
677.            4: begin
678.               w4 = w
679.               x4 = x
680.            end
681.            5: begin
682.               w5 = w
683.               x5 = x
684.            end
685.            6: begin
686.               w6 = w
687.               x6 = x
688.            end
689.            7: begin
690.               w7 = w
691.               x7 = x
692.            end
693.            8: begin
694.               w8 = w
695.               x8 = x
696.            end
697.            9: begin
698.               w9 = w
699.               x9 = x
700.            end
701.         endcase
702.         print,'Read x', ifile,' and w', ifile, FORMAT='(a,i1,a,i1)'
703.      endif else print,'Read x and w'
704. 
705.      read_transform_param
706. 
707.      do_transform
708. 
709.      if usereg then begin
710.         if nfile eq 1 then $
711.            print,'...transform to xreg and wreg' $
712.         else print,'...transform to xreg and wreg',ifile,FORMAT='(a,i1)'
713. 
714.         if nfile gt 1 then case ifile of
715.            0: wreg0 = wreg
716.            1: wreg1 = wreg
717.            2: wreg2 = wreg
718.            3: wreg3 = wreg
719.            4: wreg4 = wreg
720.            5: wreg5 = wreg
721.            6: wreg6 = wreg
722.            7: wreg7 = wreg
723.            8: wreg8 = wreg
724.            9: wreg9 = wreg
725.         endcase
726.      endif
727.   endfor
728.   close,10
729. 
730.   ;; Produce a wnames from the last file
731.   wnames = variables(ndim:ndim+nw-1)
732. 
733.   ;; Store type of the last file
734.   filetype = filetypes[-1]
735. 
736. end
737. ;==============================================================================
738. pro plot_data
739. 
740. ;    Use the x and w arrays (usually read by read_data or animate_data) and
741. ;    plot one or more functions of w using different plotting routines. 
742. ;    The functions are defined in the "Idl/funcdef.pro" file.
743. ;
744. ;    For generalized coordinates the variables are interpolated from the 
745. ;    irregular grid onto a regular one.
746. ;
747. ;    A subset can be cut from the grid by using the "cut" index array, e.g.:
748. ;    cut=grid(10:30,*), where "grid" contains the full index array.
749. ;    for the regular grid. The grid array is only defined after animate ran.
750. ;
751. ;    Usage:
752. ;
753. ; w=w2 & x=x2    ; set x and w (optional)
754. ; func='....'    ; function(s) to plot (optional)
755. ; plotmode='...' ; plot mode(s) (optional)
756. ; plot_data
757. ;
758. ;    Output can be directed to PS, EPS and/or PDF files:
759. ;
760. ; set_device,'filename.eps'
```

</details>


---

<sub>⏱️ 2m 2s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro.**

/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro (lines 760-980)

<details>
<summary>221 lines</summary>

```
760. ; set_device,'filename.eps'
761. ; plot_data
762. ; close_device,/pdf
763. ;
764. ;==============================================================================
765. 
766.   common debug_param & on_error, onerror
767. 
768.   common getpict_param
769.   common plot_param
770.   common plotfunc_param
771.   common file_head
772.   common plot_store
773. 
774.   if not keyword_set(nfile) then read_data
775. 
776.   if nfile gt 1 then begin
777.      print,'More than one files were read...'
778.      print,'Probably w is from file ',filenames(nfile-1)
779.      nfile=1
780.   endif
781. 
782.   print,'======= CURRENT PLOTTING PARAMETERS ================'
783.   print,'colorlevel=',colorlevel,', contourlevel=',contourlevel,$
784.         ', velvector=',velvector,', velspeed (0..5)=',velspeed,$
785.         FORMAT='(a,i3,a,i3,a,i4,a,i2)'
786.   print,'multiplot=',multiplot
787.   print,'axistype (coord/cells)=',axistype,', fixaspect= ',fixaspect,$
788.         FORMAT='(a,a,a,i1)'
789.   print,'bottomline=',bottomline,', headerline=',headerline,$
790.         FORMAT='(a,i1,a,i1)'
791. 
792.   if keyword_set(cut) then help,cut
793.   if keyword_set(velpos) then help,velpos
794.   velpos0=velpos
795.   ;; Read plotting and transforming parameters
796. 
797.   print,'======= PLOTTING PARAMETERS ========================='
798.   print,'wnames                     =',wnames
799. 
800.   read_plot_param
801. 
802.   help,nx
803. 
804.   read_transform_param
805. 
806.   do_transform
807. 
808.   print,'======= DETERMINE PLOTTING RANGES ==================='
809. 
810.   read_limits
811. 
812.   if noautorange eq 0 then begin
813.      get_limits, 1
814. 
815.      print
816.      for ifunc=0,nfunc-1 do $
817.         print,'Min and max value for ',funcs(ifunc),':',fmin(ifunc),fmax(ifunc)
818.   endif
819. 
820.   ;; do plotting in multixl*multiy subplots
821. 
822.   if keyword_set(multiplot) then begin
823.      if n_elements(multiplot) eq 1 then begin
824.         if multiplot gt 0 then       !p.multi=[0,multiplot,1 ,0,1] $
825.         else if multiplot eq -1 then !p.multi=[0,1,nplot     ,0,1] $
826.         else                         !p.multi=[0,1,-multiplot,0,1]
827.      endif else if n_elements(multiplot) eq 4 then $
828.         !p.multi = [multiplot(0)*multiplot(1)-multiplot(3), $
829.                     multiplot(0:1),0,multiplot(2)] $
830.      else $
831.         !p.multi=[0,multiplot(0:1),0,multiplot(2)]
832.      multix=!p.multi(1)
833.      multiy=!p.multi(2)
834.   endif else begin
835.      multix=long(sqrt(nplot-1)+1)
836.      multiy=long((nplot-1)/multix+1)
837.      !p.multi=[0,multix,multiy,0,0]
838.   endelse
839. 
840.   if not noerase then erase
841. 
842.   if velrandom then velpos=0
843. 
844.   if !d.name eq 'X' and !d.window ge 0 then wshow
845. 
846.   plot_func
847. 
848.   putbottom,1,1,0,0,bottomline,nx,it,time,npict
849.   putheader,1,1,0,0,headerline,headline,nx
850. 
851.   print
852.   !p.multi=0
853.   !p.title=''
854. 
855.   ;; Restore velpos array
856.   velpos=velpos0 & velpos0=0
857. 
858. end
859. ;==============================================================================
860. pro show_data
861.   common debug_param & on_error, onerror
862.   ;; read data and plot it
863.   read_data
864.   plot_data
865. end
866. ;==============================================================================
867. pro animate_data
868. 
869. ;    Written by G. Toth for the Versatile Advection Code.
870. ;
871. ;    Read pictures from one or more ascii or binary data files and 
872. ;    plot or animate one or more functions of w using different plotting 
873. ;    routines. The functions are defined in the "Idl/funcdef.pro" file.
874. ;
875. ;    For generalized coordinates the variables can be interpolated from the 
876. ;    irregular grid onto a regular one, or to polar coordinates.
877. ;
878. ;    A subset can be cut from the grid by using the "cut" index array, e.g.:
879. ;    cut=grid(10:30,*), where "grid" contains the full index array.
880. ;    for the regular grid. The grid array is only defined after animate ran.
881. ;
882. ;    Usage:
883. ; 
884. ; filename='... ; files to read (optional)
885. ; func='...     ; functions to plot (optional)
886. ; animate_data
887. ;
888. ;==============================================================================
889. 
890.   common debug_param & on_error, onerror
891. 
892.   common animate_param
893.   common getpict_param
894.   common file_head
895.   common ask_param
896.   common plot_param
897.   common plot_data
898.   common plotfunc_param
899.   common colors
900. 
901.   ;; Initialize storage for running maxima and averages
902.   iplotstore = 0
903.   plotstore  = 0
904.   timestore  = 0
905. 
906.   videosave = savemovie eq 'mp4' or savemovie eq 'avi' or savemovie eq 'mov'
907. 
908.   print,'======= CURRENT ANIMATION PARAMETERS ================'
909.   print,'firstpict=', firstpict,', dpict=', dpict,', npictmax=', npictmax, $
910.         FORMAT='(a,'+string(n_elements(firstpict))+'i4,a,' $
911.         +string(n_elements(dpict))+'i4,a,i4)'
912.   print,'savemovie (n/avi/mp4/mov/ps/png/tiff/bmp/jpeg)=',savemovie
913.   if videosave then print,'videofile=', videofile,'(.', savemovie, ')', $
914.                           ', videorate=', videorate
915.   print, 'colorlevel=', colorlevel,', contourlevel=', contourlevel, $
916.          ', velvector=', velvector,', velspeed (0..5)=', velspeed, $
917.         FORMAT='(a,i3,a,i3,a,i4,a,i2)'
918.   if keyword_set(multiplot) then begin
919.      print,'multiplot= ', multiplot,', axistype (coord/cells)=', axistype, $
920.            ', fixaspect= ', fixaspect, $
921.            FORMAT='(a,"[",i2,",",i2,",",i2,"]",a,a,a,i1)'
922.   endif else $
923.      print,'multiplot= 0 (default), axistype (coord/cells)=', axistype, $
924.            ', fixaspect= ', fixaspect, $
925.            FORMAT='(a,a,a,i1)'
926.   print,'bottomline=', bottomline,', headerline=', headerline, $
927.         FORMAT='(a,i1,a,i1)'
928. 
929.   if keyword_set(cut) then help, cut
930.   if keyword_set(wsubtract) then help, wsubtract
931.   if keyword_set(velpos) then help, velpos
932.   velpos0 = velpos
933. 
934.   print,'======= FILE DESCRIPTION ============================'
935.   nfile=0
936.   if filename eq '' or doask then $
937.      askstr,'filename(s)   ',filename,doask
938. 
939.   string_to_array, filename, filenames, nfile, /wildcard
940. 
941.   get_file_types
942. 
943.   print, 'filenames     =', filenames
944.   print, 'filetype(s)   =', filetypes
945.   print, 'npictinfile(s)=', npictinfiles
946. 
947.   ;; Extend firstpict and dpict into arrays of size nfile
948.   arr2arr, firstpict, nfile
949.   arr2arr, dpict, nfile
950. 
951.   ;; open file(s) and read and print header(s)
952.   anygencoord=0
953.   for ifile = 0, nfile-1 do begin
954.      open_file, 10, filenames(ifile), filetypes(ifile)
955.      get_file_head, 10, filenames(ifile), filetypes(ifile)
956.      anygencoord = anygencoord or gencoord
957.      print,         'headline                  =', strtrim(headline,2)
958.      print, FORMAT='("variables                 =",100(a," "),$)', variables
959.      print, FORMAT='(" (ndim=",i1,", nw=",i2,")")', ndim, nw
960.   endfor
961. 
962.   print,'======= PLOTTING PARAMETERS ========================='
963.   if keyword_set(func_file) then begin
964.      nfunc_file = intarr(nfile)
965.      nplot_file = intarr(nfile)
966.      for ifile = 0, nfile-1 do begin
967.         open_file, 10, filenames(ifile), filetypes(ifile)
968.         get_file_head, 10, filenames(ifile), filetypes(ifile)
969.         close, 10
970.         func = func_file[ifile]
971.         if keyword_set(plotmode_file) then plotmode = plotmode_file[ifile]
972.         if keyword_set(plottitle_file) then plottitle = plottitle_file[ifile]
973.         read_plot_param
974.         nfunc_file[ifile] = nfunc
975.         nplot_file[ifile] = nplot
976.      endfor
977.      nfuncmax = max(nfunc_file)
978.      nfuncall = total(nfunc_file,/int)
979.      nplotmax = max(nplot_file)
980.      nplotall = total(nplot_file,/int)
```

</details>


---

<sub>⏱️ 2m 2s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro.**

/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro (lines 980-1160)

<details>
<summary>181 lines</summary>

```
980.      nplotall = total(nplot_file,/int)
981.      if n_elements(fmin_file) ne nfuncall then fmin_file = dblarr(nfuncall)
982.      if n_elements(fmax_file) ne nfuncall then fmax_file = dblarr(nfuncall)
983.   endif else begin
984.      read_plot_param
985.      nfuncmax = nfunc
986.      nfuncall = nfunc
987.      nplotmax = nplot
988.      nplotall = nplot
989.   endelse 
990. 
991.   read_transform_param
992. 
993.   print,'======= DETERMINE PLOTTING RANGES ==================='
994. 
995.   read_limits
996. 
997.   ;; if all files are log files then there is no animation
998.   if min(filetypes eq 'log') then maxpict = 1 else maxpict = npictmax
999.   if noautorange then begin
1000.      npict = min( (npictinfiles - firstpict)/dpict + 1 )
1001.      if npict gt maxpict then npict = maxpict
1002.      if npict lt 0 then npict = 0
1003.   endif else begin
1004.      npict = 0
1005.      for ifile=0,nfile-1 do $
1006.         open_file, ifile+10, filenames(ifile), filetypes(ifile)
1007.      error = 0
1008.      while npict lt maxpict and not error do begin
1009.         for ifile = 0, nfile-1 do begin
1010. 
1011.            if npict eq 0 then nextpict=firstpict(ifile) $
1012.            else               nextpict=dpict(ifile)
1013. 
1014.            get_pict, ifile+10, filenames(ifile), filetypes(ifile), $
1015.                      nextpict, err
1016. 
1017.            if keyword_set(wsubtract) then w=w-wsubtract
1018. 
1019.            if keyword_set(timediff) then begin
1020.               if npict eq 0 then begin
1021.                  timeprev = time
1022.                  itprev   = it
1023.                  wprev = w
1024.                  w = 0.0*w
1025.               endif else begin
1026.                  dt = time - timeprev
1027.                  if dt eq 0 then dt = it - itprev
1028.                  w = (w - wprev)/dt
1029.                  wprev = wprev + w*dt
1030.                  timeprev = time
1031.                  itprev   = it
1032.               endelse
1033.            endif
1034. 
1035.            if keyword_set(pictdiff) then begin
1036.               if npict eq 0 then begin
1037.                  wprev  = w
1038.                  w      = 0.0*w
1039.               endif else begin
1040.                  w     = w - wprev
1041.                  wprev = wprev + w
1042.               endelse
1043.            endif
1044.            
1045.            wnames=variables(ndim:ndim+nw-1)
1046.            error=err or error
1047. 
1048.            if not error then begin
1049.               do_transform,ifile
1050.               if keyword_set(func_file) then begin
1051.                  func = func_file[ifile]
1052.                  if keyword_set(plotmode_file) then $
1053.                     plotmode = plotmode_file[ifile]
1054.                  if keyword_set(plottitle_file) then $
1055.                     plottitle = plottitle_file[ifile]
1056.                  read_plot_param, /quiet
1057.                  first = npict eq 0
1058.                  if ifile eq 0 then ifunc = 0 $
1059.                  else ifunc = total(nfunc_file[0:ifile-1],/int)
1060.                  fmin = fmin_file(ifunc:ifunc+nfunc-1)
1061.                  fmax = fmax_file(ifunc:ifunc+nfunc-1)
1062.                  get_limits, first
1063.                  fmin_file(ifunc:ifunc+nfunc-1) = fmin
1064.                  fmax_file(ifunc:ifunc+nfunc-1) = fmax
1065.               endif else begin
1066.                  first= npict eq 0 and ifile eq 0
1067.                  get_limits, first
1068.               endelse
1069.               if ifile eq nfile-1 then begin
1070.                  if npict eq 0 then print,FORMAT='("ipict:    ",$)'
1071.                  npict=npict+1
1072.                  print,FORMAT='(i5,$)',npict
1073.               endif
1074.            endif
1075.         endfor
1076.      endwhile
1077. 
1078.      print
1079.      for ifunc=0,nfunc-1 do $
1080.         print,'Min and max value for ',funcs(ifunc),':',fmin(ifunc),fmax(ifunc)
1081. 
1082.   endelse
1083.   print, 'npict=', npict
1084.   if npict eq 0 then begin
1085.      print,'There are no frames to animate! Check the following settings:'
1086.      print,'   npictinfiles=', npictinfiles
1087.      print,'   firstpict   =', firstpict
1088.      print,'   dpict       =', dpict
1089.      print,'   npictmax    =', npictmax
1090.      if min(npictinfiles - firstpict) lt 0 then $
1091.         print,'   firstpict is larger than npictinfiles for some files!' 
1092.      retall
1093.   endif
1094. 
1095.   ;; do animation in multix * multiy subplots
1096.   if keyword_set(multiplot) then begin
1097.      ;; scalar multiplot value is converted to a row (+) or a column (-)
1098.      if size(multiplot,/n_dim) eq 0 then begin
1099.         if multiplot gt 0 then       multiplot = [multiplot,1,1] $
1100.         else if multiplot eq -1 then multiplot = [1,nplotall,1] $
1101.         else                         multiplot = [1,-multiplot,1]
1102.      endif
1103.      multix   = multiplot(0)
1104.      multiy   = multiplot(1)
1105.      multidir = multiplot(2)
1106.      npict1=(multix*multiy)/(nplotmax*nfile)
1107.      if npict1 eq 0 then npict1=1
1108.   endif else if nfile eq 1 then begin
1109.      multix = long(sqrt(nplot-1)+1)
1110.      multiy = long((nplot-1)/multix+1)
1111.      multidir = 0
1112.      npict1 = 1
1113.   endif else begin
1114.      multix = nfile
1115.      multiy = nplotmax
1116.      multidir = 1
1117.      npict1 = 1
1118.   endelse
1119. 
1120.   if !d.name eq 'X' and savemovie ne 'ps' then begin
1121.      ;; open X window to get the size
1122.      if !d.window lt 0 then window
1123.      wshow
1124.   endif
1125. 
1126.   devicenameorig = !d.name
1127.   if videosave then begin
1128.      videoobject = IDLffVideoWrite(videofile+'.'+savemovie)
1129.      videostream = videoobject.AddVideoStream(!d.x_size,!d.y_size,videorate)
1130.   endif else begin
1131.      if savemovie ne 'n' then spawn,'/bin/mkdir -p '+moviedir
1132.      if savemovie eq 'ps' then begin
1133.         set_plot,'PS',/INTERPOLATE
1134.         if blackbackground then black_background
1135.      endif
1136.   endelse
1137. 
1138.   doanimate= npict gt npict1 and !d.name eq 'X' and showmovie eq 'y'
1139.   if doanimate then begin
1140.     if xregistered("XInterAnimate") then xinteranimate, /close
1141.     xinteranimate,set=[!d.x_size,!d.y_size,(npict-1)/npict1+1]
1142.   endif
1143. 
1144.   ipict = 0
1145.   ipict1 = 0
1146.   iplot = 0
1147.   for ifile = 0, nfile-1 do $
1148.      open_file, ifile+10, filenames(ifile), filetypes(ifile)
1149.   error = 0
1150.   while ipict lt npict and not error do begin
1151.      if ipict1 eq 0 then begin
1152.         if not keyword_set(noerase) then erase
1153.         !p.multi=[0,multix,multiy,0,multidir]
1154.         if savemovie eq 'ps' then begin
1155.            device, $
1156.               filename=moviedir+'/'+string(FORMAT='(i4.4)',iplot+1)+'.ps', $
1157.               XSIZE=24, YSIZE=18, /LANDSCAPE, /COLOR, BITS=8
1158.            if blackbackground then black_background
1159.         endif
1160.      endif
```

</details>


---

<sub>⏱️ 2m 8s</sub>

### ✅ `rg`

**^\s*pro\s+set_default_values\b|^\s*pro\s+swmf_plot_init\b|common ask_param**

"^\s*pro\s+set_default_values\b|^\s*pro\s+swmf_plot_init\b|common ask_param" (~/SWMFSoftware/SWMF/share/IDL/General/procedures.pro)

<details>
<summary>13 matches</summary>

```
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:71:pro set_default_values
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:84:  common ask_param, doask
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:614:  common ask_param, doask
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:895:  common ask_param
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:1339:  common ask_param
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:1601:  common ask_param
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:1652:  common ask_param
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:2011:  common ask_param
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:2535:  common ask_param, doask
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:2609:  common ask_param
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:2730:  common ask_param, doask
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:2763:   common ask_param, doask
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro:2793:  common ask_param, doask
```

</details>


---

<sub>⏱️ 2m 10s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro.**

/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro (lines 1-240)

<details>
<summary>240 lines</summary>

```
1. ;  Copyright (C) 2002 Regents of the University of Michigan, 
2. 
3. ;  For more information, see http://csem.engin.umich.edu/tools/swmf
4. ;
5. ; Written by G. Toth for the Versatile Advection Code and BATSRUS/SWMF
6. ; Some improvements by Aaron Ridley.
7. ;
8. ; Main procedures to (re)set defaults and to read, plot, animate and slice data
9. ;   set_default_values
10. ;   read_data, plot_data, show_data, animate_data, slice_data
11. ;   read_log_data, plot_log_data, show_log_data
12. ;
13. ; Procedures for
14. ;
15. ; fixing things if animate or slice crashes
16. ;   reset_axis, slice_data_restore
17. ; reading ascii and binary data produced by VAC, BATSRUS, PWOM, FLEKS etc:
18. ;    open_file, get_file_types, get_file_head, get_pict, 
19. ;    get_pict_asc, get_pict_bin, get_pict_log, get_log, read_log_line
20. ; showing / overwriting information read from last file:
21. ;    show_head, show_units, set_units
22. ; saving ascii and binary data in the same format as used for input:
23. ;    save_pict, save_log
24. ; reading numbers and strings from input:
25. ;    asknum, askstr, string_to_array, arr2arr, read_plot_param, read_limits
26. ; transforming initial data:
27. ;    read_transform_param, do_transform, do_my_transform, 
28. ;    make_regular_grid, make_polar_grid, make_unpolar_grid,
29. ;    make_sphere_grid
30. ;    getaxes
31. ;    interpol_logfiles, interpol_log
32. ; calculating functions of the data
33. ;    get_func, get_limits
34. ; plotting
35. ;    plot_func, plot_grid, plot_log
36. ; calculating cell corners and cell volumes for general 2D grids
37. ;    gengrid
38. ; comparing two w,x or wlog arrays for relative differences
39. ;    compare, rms_logfiles, rel_error, rel_errors
40. ; checking index ranges for functions quadruplet and triplet
41. ;    checkdim
42. ; procedure "quit" as an alias for "exit"
43. ;    quit
44. ;
45. ; Functions for
46. ;
47. ; calculating correlation between two functions
48. ;    corr2, pvalue
49. ; calculating first derivative in 1D
50. ;    diff1
51. ; calculating derivatives in 2D for Cartesian grids to 2nd,3rd,4th order
52. ;    diff2,diff3,diff4
53. ; calculating the laplace on 1D or 2D Cartesian grids
54. ;    laplace
55. ; calculating minmod limited slope
56. ;    minmod
57. ; calculating symmetric differences with respect to some mirror plane
58. ;    symmdiff
59. ; calculating derivatives in 2D for general grids
60. ;    grad_2d,div,curl,grad_rz,div_rz,curl_rz, filledge,intedge,intedge_rz
61. ; taking a part of an array or coarsen an array
62. ;    triplet, quadruplet, coarsen
63. ; eliminating degenerate dimensions from an array
64. ;    reform2
65. ; converting logfile time or date+time into hours, getting other functions
66. ;    log_time, log_func, convert_date
67. ; limiting changes in a time series
68. ;    limit_change, limit_growth
69. 
70. ;==============================================================================
71. pro set_default_values
72. 
73.   ;; Definitions and default values for variables in common blocks
74. 
75.   ;; System variables that can get corrupted if an animation is interrupted
76.   !x.tickname   = strarr(60)
77.   !y.tickname   = strarr(60)
78.   !x.tickformat = strarr(10)
79. 
80.   ;; Format date labels
81.   dummy = LABEL_DATE(DATE_FORMAT=['%H:%I!c%M %D %Y'])
82. 
83.   ;; Confirmation for set parameters
84.   common ask_param, doask
85.   doask = 0
86.   
87.   ;; behavior on error: 0: stop in the unit (for debug), 2=return to main
88.   common debug_param, onerror
89.   onerror = 2
90. 
91.   common fits_param, noresize
92.   noresize=0                    ; Keep original size of fits image
93. 
94.   ;; Parameters for read_data
95.   common getpict_param, $
96.      filename, nfile, filenames, filetypes, npictinfiles, npict, filetype
97.   filename=''          ; space separated list of filenames. May contain *, []
98.   nfile=0              ; number of files
99.   filenames=0          ; array of filenames
100.   filetypes=''         ; file types (real4, real8, ascii, log ...)
101.   npictinfiles=0       ; number of pictures in each file
102.   npict=0              ; index of snapshot to be read
103.   filetype=''          ; type of current file
104. 
105.   ;; Parameters for plot_data
106.   common plotfunc_param, $
107.      func, func_file, nfunc, nfuncall, funcs, funcs1, funcs2, $
108.      plotmode, plotmode_file, plotmodes, nplot, $
109.      plottitle, plottitle_file, plottitles, $
110.      timetitle, timetitleunit, timetitlestart, $
111.      xrange_file, yrange_file, $
112.      autorange, autoranges, noautorange, fmin, fmax, fmin_file, fmax_file, $
113.      axistype, bottomline, headerline
114.   func = ''            ; space separated list of functions to be plotted
115.   nfunc = 0            ; number of functions to be plotted
116.   funcs = ''           ; array of function names
117.   funcs1 = ''          ; array of first  components of vectors functions
118.   funcs2 = ''          ; array of second components of vectors functions
119.   plotmode = 'default' ; space separated list of plot modes
120.   plotmodes = ''       ; array of plot modes
121.   nplot = 0            ; number of subplots (overplot functions count as 1)
122.   plottitle = 'default'; semicolon separated list of titles
123.   plottitles = ''      ; array of plot titles
124.   plottitles_file = '' ; array of plottitle strings per file
125.   timetitle = ''       ; format string to plot time as title for time series
126.   timetitleunit  = 0   ; number of seconds in time unit
127.   timetitlestart = 0   ; initial time to be subtracted (in above units)
128.   xrange_file = 0      ; different xrange for different files
129.   yrange_file = 0      ; different yrange for different files
130.   autorange = 'y'      ; function ranges set automatically or by fmin/fmax
131.   autoranges = ''      ; array of autorange values
132.   noautorange = 0      ; true if all autoranges are 'n'
133.   fmin = 0             ; array of minimum values for each function
134.   fmax = 0             ; array of maximum values for each function
135.   fmin_file = 0        ; array of minimum values for each function and file
136.   fmax_file = 0        ; array of maximum values for each function and file
137.   axistype = 'coord'   ; 'cells' or 'coord'
138.   headerline = 0       ; Number of items to show at the top
139.   bottomline = 3       ; Number of items or a string to show at the bottom
140. 
141.   ;; Animation parameters for the movie
142.   common animate_param, $
143.      firstpict, dpict, npictmax, savemovie, showmovie, moviedir, $
144.      wsubtract, timediff, pictdiff, $
145.      videosave, videofile, videorate, videoobject, videostream, videotime
146.   firstpict=1        ; a scalar or array (per file) of the index of first frame
147.   dpict=1            ; a scalar or array (per file) of distance between frames
148.   npictmax=500       ; maximum number of frames in an animation
149.   showmovie='y'      ; show movie with Xinteranimate if possible
150.   savemovie='n'      ; save animation frames into ps/png/tiff/bmp/jpeg files
151.                                 ; or into a 'mov/mp4/avi' video file.
152.   moviedir="Movie"   ; directory where individual movie frames are saved to
153.   wsubtract=0        ; Array subtracted from w during animation
154.   timediff=0         ; take time derivative of w during animation if timediff=1
155.   pictdiff=0         ; running difference in w (w-wprev) during animation
156.                      ; independent of dt or iteration if pictdiff=1
157.   videosave=0        ; save video?
158.   videofile='movie'  ; name of video file with extension .savemovie
159.   videorate=10       ; number of frames per second
160.   videoobject=0      ; video object
161.   videostream=0      ; video stream object
162.   videotime=0        ; length of video
163. 
164.   ;; Parameters for slice_data
165.   common slice_param, $
166.      firstslice, dslice, nslicemax, slicedir, dyslicelabel, $
167.      x3d, w3d, var3d, rbody3d, grid2d
168.   firstslice=1                  ; index of first slice
169.   dslice=1                      ; stride between slices
170.   nslicemax=500                 ; maximum number of slices shown
171.   slicedir=0                    ; 
172.   dyslicelabel=0.98             ; position of bottom label (?)
173.   x3d=0                         ; 3D coordinates saved
174.   w3d=0                         ; 3D state saved
175.   var3d=0                       ; 3D variable names saved
176.   rbody3d=0.0                   ; 3D rBody value saved
177.   grid2d=0                      ; grid indexes for the slice
178. 
179.   ;; Transformation parameters for irregular grids 
180.   common transform_param, $
181.      usereg, dotransform, transform, nxreg, xreglimits, wregpad, $
182.      nxreg_old, xreglimits_old, triangles, symmtri
183. 
184.   usereg=0         ; use wreg and xreg instead of w and x
185.   dotransform='n'  ; do transform with plot_data?
186.   transform='n'    ; values: none,regular,my,polar,unpolar,sphere,angle
187.   nxreg=[0,0]      ; size of transformed grid
188.   xreglimits=0     ; transformed grid limits [xmin, ymin, xmax, ymax]
189.   wregpad=0        ; array of values used in "padding" the regular arrays
190.   nxreg_old=0      ; previous transformation grid
191.   xreglimits_old=0 ; previous limits of transform grid
192.   triangles=0      ; triangulation saved from previous transform
193.   symmtri=0        ; use symmetric triangulation during transformation?
194. 
195.   common vector_param, $
196.      nvector, vectors
197.   nvector=0                     ; number of vector variables
198.   vectors=0                     ; index of first components of vector variables
199. 
200.   ;; Parameters for read_log_data
201.   common getlog_param, $
202.      logfilename, logfilenames
203.   logfilename=''       ; space separated string of filenames. May contain *, []
204.   logfilenames=0                ; array of log filenames
205. 
206.   common log_data, $
207.      timeunit, timeunitsc, $
208.      wlog , logtime , wlognames , $
209.      wlog1, logtime1, wlognames1, $
210.      wlog2, logtime2, wlognames2, $
211.      wlog3, logtime3, wlognames3, $
212.      wlog4, logtime4, wlognames4, $
213.      wlog5, logtime5, wlognames5, $
214.      wlog6, logtime6, wlognames6, $
215.      wlog7, logtime7, wlognames7, $
216.      wlog8, logtime8, wlognames8, $
217.      wlog9, logtime9, wlognames9, $
218.      wlogrownames
219. 
220.   wlog=0                        ; data array from logfile
221.   logtime=0                     ; time array from logfile
222.   wlognames=''                  ; array of log data column names
223.   wlogrownames=''               ; array of log data row names (if present)
224.   timeunit='h' ; set to '1' (unitless), 's' (second), 'm' (minute), 'h' (hour) 
225.                                 ;        'millisec', 'microsec', 'ns' (nanosec)
226. 
227.   ;; Parameters for plot_log_data
228.   common plotlog_param, $
229.      log_spacex,log_spacey, logfunc, title, xtitle, ytitles, $
230.      xrange, yranges, timeshifts, $
231.      colors, linestyles, symbols, smooths, dofft, legends, legendpos
232. 
233.   log_spacex = 5 ; horizontal distance around log plots (in character size)
234.   log_spacey = 5 ; vertical distance between log plots (in character size)
235.   logfunc = ''   ; space separated list of log variables in wlogname(s)
236.   title = ''     ; set to a string with the title
237.   xtitle = 0     ; set to a string with the time title
238.   ytitles = 0    ; set to a string array with the function names
239.   xrange = 0     ; set to a [min,max] array for the time range
240.   yranges = 0    ; set to a [[min1,max1], [min2,max2] ...] for function ranges
```

</details>


---

<sub>⏱️ 2m 16s</sub>

### ✅ `swmf-prototype-get_evidence`

**IDL postprocessing**

<details>
<summary>Arguments</summary>

```json
{
  "query": "IDL postprocessing",
  "task_type": "analysis",
  "goal": "IDL visualization entrypoints"
}
```

</details>

```
{"ok":true,"query":"IDL postprocessing","mode":"hybrid","scope":[],"top_k":8,"goal":"IDL visualization entrypoints","task_type":"analysis","module":null,"summary":"0 workflow evidence item(s), 8 IDL catalog evidence item(s), and 0 supporting evidence item(s) found for 'IDL postprocessing'","evidence":[{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"show_data: pro show_data\ncategory: plotting","score":0.95,"name":"show_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_data: pro plot_data\ncategory: plotting","score":0.95,"name":"plot_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_log_data: pro plot_log_data\ncategory: plotting","score":0.95,"name":"plot_log_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_func: pro plot_func\ncategory: plotting","score":0.95,"name":"plot_func","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/geopack.pro","snippet":"geigse: pro geigse,xgei,ygei,zgei,xgse,ygse,zgse,j,epoch\ncategory: plotting","score":0.95,"name":"geigse","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/geopack.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"getvectors: pro getvectors, nvector, vectors\ncategory: plotting","score":0.95,"name":"getvectors","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_color_bar: pro plot_color_bar, position, a, format=format, title=title\ncategory: plotting","score":0.95,"name":"plot_color_bar","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_grid: pro plot_grid, x, y, lines=lines, xstyle=xstyle, ystyle=ystyle, $\ncategory: plotting","score":0.95,"name":"plot_grid","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}}],"provenance":{"mode_used":"keyword","scope":[]},"uncertainty":{"known_unknowns":["Runtime behavior for the current case not inspected."]},"swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked environment SWMF_ROOT: /Users/zkeheng/SWMFSoftware/SWMF","Resolved from SWMF_ROOT environment variable."]}
```


---

<sub>⏱️ 2m 16s</sub>

### ✅ `swmf-prototype-get_evidence`

**IDL_STARTUP startup script SWMF**

<details>
<summary>Arguments</summary>

```json
{
  "query": "IDL_STARTUP startup script SWMF",
  "mode": "keyword",
  "goal": "IDL visualization manual detail"
}
```

</details>

```
{"ok":true,"query":"IDL_STARTUP startup script SWMF","mode":"keyword","scope":[],"top_k":8,"goal":"IDL visualization manual detail","task_type":"lookup","module":null,"summary":"8 deterministic IDL evidence item(s) and 0 supporting evidence item(s) found for 'IDL_STARTUP startup script SWMF'","evidence":[{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md","snippet":"2     IDL path and startup file\nIt is necessary to let IDL know about the existence of the macros. You can\ndefine the search path for IDL, for example\n\nsetenv IDL_PATH \"${HOME}/SWMF/share/IDL/General:<IDL_DEFAULT>\"\nfor the csh or tcsh shell. You can also make IDL to read the idlrc file automat-\nically upon start up with\nsetenv IDL_STARTUP idlrc\n\nThese environment settings can be put into your ˜/.login or ˜/.cshrc files. The\nabove is valid for the csh and tcsh UNIX shells.\n   For other UNIX shells (bash, ksh, zsh), use\nexport IDL_PATH=\"${HOME}/BATSRUS/share/IDL/General:<IDL_DEFAULT>\"\nexport IDL_STARTUP=idlrc\n\nin the ˜/.profile or similar file.\n\n\n3     Running IDL\nIf the IDL PATH and the IDL STARTUP variables are set, simply start IDL\nfrom the directory where the *.out IDL plot files and the *.log logfiles are, e.g.\ncd run/IO2\nidl\nIf IDL STARTUP is not set, type\n\n@idlrc\n\n\n\n\n               ...","score":1,"name":"startup","kind":"manual_section","start_line":72,"metadata":{"kind":"idl_manual_section","relative_path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md","why_relevant":"IDL setup, IDL_PATH, IDL_STARTUP, idlrc, retall","topic":"startup","line_start":72,"line_end":118}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md","snippet":"the /delete argument is present as well, the original PS or EPS file is removed.\n    You can use animate data instead of plot data (e.g. for multiple files or\nfor time series) in combination with set device and close device, but make\nsure that only one plot is produced by setting npictmax=1, and use first-\npict to select the snapshot. Here is an example showing many of the optional\narguments:\nnpictmax=1\nfirstpict=12\nset_device,’figure2.eps’, /port, xratio=0.8, psfont=8\nanimate_data\nclose_device,pdf=’convert’,/delete\nThis will produce a ’figure2.pdf’ in portrait format with Helvetica font, using\nthe convert program to convert to PDF.\n   To save all frames of an animation into a series of Postscript files, do not use\nset device but set\nsavemovie=’ps’\nThis will produce files Movie/0001.ps,Movie/0002.ps,... in the Movie di-\nrectory, which is created automatically if it does not exist. The Po...","score":1,"name":"script","kind":"manual_section","start_line":1248,"metadata":{"kind":"idl_manual_section","relative_path":"/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md","why_relevant":"IDL script and procedure reuse","topic":"script","line_start":1248,"line_end":1295}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"show_data: pro show_data\ncategory: plotting","score":0.95,"name":"show_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_data: pro plot_data\ncategory: plotting","score":0.95,"name":"plot_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_log_data: pro plot_log_data\ncategory: plotting","score":0.95,"name":"plot_log_data","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"plot_func: pro plot_func\ncategory: plotting","score":0.95,"name":"plot_func","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/geopack.pro","snippet":"geigse: pro geigse,xgei,ygei,zgei,xgse,ygse,zgse,j,epoch\ncategory: plotting","score":0.95,"name":"geigse","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/geopack.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}},{"type":"idl","path":"/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/procedures.pro","snippet":"getvectors: pro getvectors, nvector, vectors\ncategory: plotting","score":0.95,"name":"getvectors","kind":"pro","metadata":{"kind":"idl_procedure_catalog_row","relative_path":"share/IDL/General/procedures.pro","why_relevant":"IDL procedure catalog row in category 'plotting'.","category":"plotting"}}],"provenance":{"mode_used":"keyword","scope":[]},"uncertainty":{"known_unknowns":["Runtime behavior for the current case not inspected."]},"swmf_root_resolved":"/Users/zkeheng/SWMFSoftware/SWMF","resolution_notes":["Checked environment SWMF_ROOT: /Users/zkeheng/SWMFSoftware/SWMF","Resolved from SWMF_ROOT environment variable."]}
```


---

<sub>⏱️ 2m 25s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md (lines 420-570)

<details>
<summary>151 lines</summary>

```
420. 
421. 
422. 9     Function names in string func
423. The function names listed in the func string can be any of the variable names
424. listed in the string array wnames, which is read from the header of the file,
425. or any of the function name strings shown in the functiondef array at the
426. beginning of funcdef.pro (see section 16), or any expression using the standard
427. variable, coordinate and scalar parameter names and various constants:
428. x y z r
429. rho p ux uy uz uu u bx by bz bb b
430. xSI gamma gammae Mi Me Qi Qe clight rbody
431. mu0 mu0A c0 op0 oc0 rg0 di0 ld0
432. Here ”uu” and ”bb” are the velocity and magnetic field squared, while ”u”
433. and ”b” are the velocity and magnetic field magnitudes, respectively. Note
434. that ”x ... b” are arrays, while ”gamma” is a scalar. For example the maximum
435. Alfvén speed could be given as func=’b/sqrt(rho*mu0A)’, but this is already
436. defined in funcdef.pro as ’calfven’. However, for a multifluid data file, one can
437. use a different density, e.g.
438. func=’b/sqrt({OpRho}*mu0A)’
439. where mu0A is the vacuum permeability together with the unit conversion fac-
440. tors. Note that the OpRho variable (density of O+ ion) is not among the
441. standard arrays, but it can still be used by enclosing it with the curly brackets.
442. 
443. 
444.                                          11
445.     You may combine two function names with the ; character representing two
446. components of a vector, e.g. ux;uy or bx;bz, which can either be plotted as a
447. vectorfield by the velovect, vector and arrow plot modes, or as streamlines
448. or fieldlines, using
449.                 p the stream plotting modes. For other plotting modes the
450. absolute value ux2 + uy 2 is plotted. You can also put a minus sign in front of
451. any function or variable name, which will simply multiply the value of the rest
452. of the string by −1. For example ’-Ti’ plots (−1)*temperature of ions. This is
453. just a shorthand for the general syntax ’-Ti’.
454. 
455. 
456. 10     Plotting modes in string plotmode
457. There are many plotting modes available. These can be listed in the plotmode
458. string for each function separated by spaces. If the number of plotting modes is
459. less than the number of functions, the last plotting mode is applied for the rest
460. of the functions.
461.     For 1D plots the following plotting modes are available:
462. Plotmode   Horizontal axis     Vertical axis
463. -------------------------------------------------------
464. plot       linear              linear
465. plot_io    linear              logarithmic
466. plot_oi    logarithmic         linear
467. plot_oo    logarithmic         logarithmic
468. The default value for plotmode is ’plot’, which uses linear axes. The names of
469. these plotting modes are identical with the corresponding IDL procedures.
470.    For 2D data there are many more possibilities. For scalar functions the main
471. plotting modes are
472. Plotmode   Parameters                Description
473. ----------------------------------------------------------------------
474. contour    contourlevel/colorlevel   contourlines
475. cont       contourlevel/colorlevel   contourlines or color map
476. lonlatn    contourlevel/colorlevel   lon-lat grid for north polar cap
477. lonlatd    contourlevel/colorlevel   lon-lat grid for south polar cap
478. polar      contourlevel/colorlevel   polar plot
479. scatter                              scatter plot
480. shade      ax az                     shaded surface, height proportional to value
481. surface    ax az                     surface mesh, height proportional to value
482. tv                                   grid cells colored by value
483. The parameters ax and az define the viewing angle, while the contourlevel
484. and contourlevel parameters determines the number of contourlevel and col-
485. ors, respectively. The ’tv’,’surface’ and ’shade’ plotting modes can be used for
486. Cartesian grids only (or grids transformed to Cartesian).
487.     For functions with two components (e.g. ’bx;bz’) the following plotting
488. modes are available
489. 
490. 
491.                                        12
492. Plotmode Parameters Description
493. -----------------------------------------------------------------
494. stream    velvector   stream/fieldlines at random/selected points
495.           velpos
496.           velrandom
497. 
498. arrow       velvector      arrows of fixed length at random/selected positions
499.             velpos
500.             velrandom
501. 
502. vector      velvector      vectors at random/selected positions
503.             velpos
504.             velspeed
505.             velrandom
506. 
507. velovect                   vectors at every grid point
508. 
509. ovelovect                  vectors at every grid point (for overplot)
510. The velvector parameter determines the number of arrows or stream/fieldlines
511. shown. By default the position of arrows/streamlines is random. The posi-
512. tions can be fixed with the velpos array (see section 11 for details). During
513. an animation the arrows can move from their initial position parallel to the
514. local velocity at a speed proportional to the magnitude of the velocity and the
515. velspeed parameter. The maximum value is the default velspeed=5, while
516. velspeed=0 does not allow the arrows to move. When the arrows move, it may
517. be necessary to reinitialize them with a random position periodically, otherwise
518. the arrows may converge to a small part of the domain. Setting velrandom to
519. a small positive integer value (e.g. 5) will reinitialize the position of every 5th
520. vector every 5 picture of the animation.
521.     The ’velovect’ and ’ovelovect’ plotting modes can be used for Cartesian grids
522. only.
523.     The following options can be added to any of the above plotting modes:
524. 
525. Option Description
526. ---------------------------------------------------------------------
527. log     show the 10 based logarithm of the function if it is positive
528. over    overplot the previous function
529. noaxis do not show the axes
530. #ctNNN use color table NNN (NNN is an integer from 0 to 999)
531. #cNNN   use color NNN       (NNN is an integer from 0 to 255)
532. max     plot maximum of the last "nplotstore" snapshots
533. mean    plot average of the last "nplotstore" snapshots
534.    For 1D plots:
535. 
536. Option    Description
537. 
538. 
539.                                         13
540. ---------------------------------------------------------------------
541. dash    dashed line style
542. dot     dotted line style
543. time    vertical dashed line at current time (for log/sat files)
544. 
545.    For 2D plots:
546. Option Description
547. ---------------------------------------------------------------------
548. bar     fill contour plot and show colorbar (also for "tv")
549. fill    fill contour plot without colorbar
550. label   contour plot with labels
551. deg     angle in degrees for plolar plots
552. rad     angle in radians for polar plots
553. hour    angle in hour for polar plots
554. lgx     logarithmic X axis
555. lgy     logarithmic Y axis
556. body    show the spherical body with radius rBody as a black circle
557. grid    show grid points with plus signs
558. mesh    show the mesh (lines connecting grid points) for structured grid
559. map     draw a world map under the plot
560. usa     draw the USA map under the plot
561. irr     force triangulation for irregular (non-Cartesian) grid
562. white   draw vectors, stream lines and the grid/mesh with white lines
563. Note that it makes no sense to overplot the grid for the surface plotting mode,
564. on the other hand plotmode=’shademesh’ will plot the shaded surface together
565. with the mesh of ’surface’. The radius of the body rBody is usueally read
566. from the scalar parameter named ’r’ or ’rbody’ in the data file, or it can be set
567. manually.
568.    Here is an example for some more complex plotmode strings:
569. plotmode=’contbargridlog streamwhiteoverbody’
570. will show the 10 based logarithm of the first scalar quantity with a color bar and
```

</details>


---

<sub>⏱️ 2m 26s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md (lines 1200-1295)

<details>
<summary>82 lines</summary>

```
1200. and close device procedures.
1201. set_device,’myfile.eps’
1202. loadct,3
1203. plot_data
1204. close_device
1205. The first optional argument of the set device procedure is the filename. If it is
1206. not given, the default filename ’idl.ps’ is used. There are several keyword argu-
1207. ments too. Layout is set by /port for portrait, /land for landscape (this is the
1208. default, but in some cases it is needed) and /square for a square shaped figure.
1209. 
1210. 
1211.                                        28
1212. The xratio and yratio options can be used to shrink figure relative to the page
1213. size (default values are 1). The /eps option selects encapsulated postscript for-
1214. mat (which is also default if the file extension is .eps). The psfont=12 argument
1215. can be used to select a specific font.
1216.     With no arguments, the close device procedure simply closes the postscript
1217. device, and opens the ’X’ device. If the optional /pdf argument is present, the
1218. output PostScript or EPS file is converted to PDF using either the default
1219. ps2pdf program or the programname given as a value, e.g. pdf=’convert’. If
1220. the /delete argument is present as well, the original PS or EPS file is removed.
1221.     You can use animate data instead of plot data (e.g. for multiple files or
1222. for time series) in combination with set device and close device, but make
1223. sure that only one plot is produced by setting npictmax=1, and use first-
1224. pict to select the snapshot. Here is an example showing many of the optional
1225. arguments:
1226. npictmax=1
1227. firstpict=12
1228. set_device,’figure2.eps’, /port, xratio=0.8, psfont=8
1229. animate_data
1230. close_device,pdf=’convert’,/delete
1231. This will produce a ’figure2.pdf’ in portrait format with Helvetica font, using
1232. the convert program to convert to PDF.
1233.    To save all frames of an animation into a series of Postscript files, do not use
1234. set device but set
1235. savemovie=’ps’
1236. This will produce files Movie/0001.ps,Movie/0002.ps,... in the Movie di-
1237. rectory, which is created automatically if it does not exist. The PostScript files
1238. are best suited for printing. You can also save the frames in PNG, TIFF, JPEG
1239. or BMP formats, e.g. by setting
1240. savemovie=’png’
1241. The frames can be put together into a movie by some program like mpeg encode
1242. or ImageMagick’s convert, or Apple’s QuicktimePro7, but there is a simpler
1243. approach. To save the animation into a video file directly, use the ’mov’, ’avi’
1244. or ’mp4’ format. The name of the video file can be set with ’videofile’ (default
1245. name is ’movie’) and the number of frames per second with ’videorate’ (default
1246. is 10), for example
1247. savemovie=’mp4’
1248. videofile=’waterwaves’
1249. videorate=24
1250. animate_data
1251. will create ’waterwaves.mp4’ file with 20 frames per second.
1252.     If you do not wish to use Xinteranimate, then set
1253. 
1254. 
1255.                                         29
1256. showmovie=’n’
1257. The default is ’y’, so Xinteranimate is used if there are multiple frames.
1258. 
1259. 
1260. 21       IDL scripts and procedures
1261. All the IDL commands can be collected into a script file, for example
1262. IDL_mine/myfig.pro
1263. which can be run from IDL by
1264. 
1265. @myfig
1266. This is a convenient way to store the commands for producing complicated
1267. figures. An example can be found in EXAMPLE.pro. There are some restric-
1268. tions on scripts, however. Loops and other multi-line structures cannot be used
1269. in a script. If loops are needed, simply add an end statement to the end, and
1270. call it as
1271. .r myfig
1272. For even more complicated cases a true procedure can be written. The common
1273. variables can be imported through common blocks. This can be called as any
1274. other procedure, for example
1275. my_fig, inputfile=’test.out’, outputfile=’test.eps’
1276. 
1277. 
1278. 
1279. 
1280.                                        30
1281.
```

</details>


---

<sub>⏱️ 2m 27s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md.**

/Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/idl.md (lines 72-130)

<details>
<summary>59 lines</summary>

```
72. define the search path for IDL, for example
73. 
74. setenv IDL_PATH "${HOME}/SWMF/share/IDL/General:<IDL_DEFAULT>"
75. for the csh or tcsh shell. You can also make IDL to read the idlrc file automat-
76. ically upon start up with
77. setenv IDL_STARTUP idlrc
78. 
79. These environment settings can be put into your ˜/.login or ˜/.cshrc files. The
80. above is valid for the csh and tcsh UNIX shells.
81.    For other UNIX shells (bash, ksh, zsh), use
82. export IDL_PATH="${HOME}/BATSRUS/share/IDL/General:<IDL_DEFAULT>"
83. export IDL_STARTUP=idlrc
84. 
85. in the ˜/.profile or similar file.
86. 
87. 
88. 3     Running IDL
89. If the IDL PATH and the IDL STARTUP variables are set, simply start IDL
90. from the directory where the *.out IDL plot files and the *.log logfiles are, e.g.
91. cd run/IO2
92. idl
93. If IDL STARTUP is not set, type
94. 
95. @idlrc
96. 
97. 
98. 
99. 
100.                                         3
101. at the IDL> prompt, so that the commands in the idlrc file are executed: the
102. procedures in procedures.pro, funcdef.pro and vector.pro are compiled and
103. the script set defaults is executed to set some common block variables to their
104. default values. You can customize the startup of IDL by editing idlrc, e.g. you
105. can compile your own IDL procedures.
106.     If an error occurs, the code usually returns to the main level, so one can fix
107. the settings and try again. The corresponds to the default setting
108. onerror=2
109. For debugging purposes, it may be useful to set
110. onerror=0
111. so that variables can be written out inside the macro where the error occurred.
112. In this case, or in general if you get trapped by an error inside some IDL routine,
113. typing
114. retall
115. will return to the main level. To exit IDL type
116. exit
117. The alternative ’quit’ command is also defined for convenience.
118. 
119. 
120. 4      Reading a snapshot with read data
121. To read a snapshot from a file, type at the ”IDL>” prompt of IDL
122. read_data
123. The procedure will prompt you for the filename, and it determines the file-
124. types and npictinfiles (the number of snapshots in the file) automatically.
125. Then it asks for the frame-number npict (1, 2,... npictinfiles) of the snapshot
126. to be read from the file. When npictinfiles=1, the frame number is set to 1
127. automatically:
128. filename(s)    ? example1.out
129. filetype(s)    = binary
130. npictinfile(s)=       1
```

</details>


---

<sub>⏱️ 2m 30s</sub>

### ✅ `glob`

****/idlrc**

"**/idlrc" in ~/SWMFSoftware/SWMF/share/IDL

```
/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/idlrc
```


---

<sub>⏱️ 2m 33s</sub>

### 💬 Copilot

I found the exact IH z=0 frame files and IDL plotting/export entrypoints; next I’ll run an IDL script to generate the three `func='u'` images.

---

<sub>⏱️ 2m 42s</sub>

### ✅ `bash`

**Check IDL and conversion tools**

$ set -euo pipefail && command -v idl || true && printf 'IDL_PATH=%s\n' "${IDL_PATH-}" && printf 'IDL_STARTUP=%s\n' "${IDL_STARTUP-}" && (command -v magick || true) && (command -v convert || true)

```
IDL_PATH=+/Users/zkeheng/SWMFSoftware/SWMF/share/IDL:+/Applications/NV5/idl92/lib:+/Applications/NV5/idl92/lib/utilities
IDL_STARTUP=idlrc
/opt/homebrew/bin/magick
/opt/homebrew/bin/convert
<exited with exit code 0>
```


---

<sub>⏱️ 2m 49s</sub>

### ✅ `bash`

**Check common IDL executable paths**

$ set -euo pipefail && for p in /Applications/NV5/idl92/bin/idl /usr/local/bin/idl /opt/homebrew/bin/idl; do if [ -x "$p" ]; then echo "$p"; fi; done

```
/Applications/NV5/idl92/bin/idl
<exited with exit code 0>
```


---

<sub>⏱️ 3m 4s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH.**

/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH

<details>
<summary>316 lines</summary>

```
log_n005000.log
log_n006560.log
sat_earth_n00005000.sat
sat_earth_n00006560.sat
shl_var_4_t00180000_n00006800.out
shl_var_4_t00210000_n00006980.out
shl_var_4_t00240000_n00007160.out
shl_var_4_t00270000_n00007340.out
shl_var_4_t00300000_n00007522.out
shl_var_4_t00330000_n00007705.out
shl_var_4_t00360000_n00007888.out
shl_var_4_t00390000_n00008071.out
shl_var_4_t00420000_n00008254.out
shl_var_4_t00450000_n00008437.out
shl_var_4_t00480000_n00008620.out
shl_var_4_t00510000_n00008803.out
shl_var_4_t00540000_n00008986.out
shl_var_4_t00570000_n00009169.out
shl_var_4_t00600000_n00009352.out
shl_var_4_t00630000_n00009535.out
shl_var_4_t00660000_n00009718.out
shl_var_4_t00690000_n00009901.out
shl_var_4_t00720000_n00010084.out
shl_var_4_t00750000_n00010267.out
shl_var_4_t00780000_n00010450.out
shl_var_4_t00810000_n00010633.out
shl_var_4_t00840000_n00010816.out
shl_var_4_t00870000_n00010999.out
shl_var_4_t00900000_n00011182.out
shl_var_4_t00930000_n00011365.out
shl_var_4_t00960000_n00011548.out
x=0_var_1_t00020000_n00005000.out
x=0_var_1_t00030000_n00005120.out
x=0_var_1_t00040000_n00005240.out
x=0_var_1_t00050000_n00005360.out
x=0_var_1_t00060000_n00005480.out
x=0_var_1_t00070000_n00005600.out
x=0_var_1_t00080000_n00005720.out
x=0_var_1_t00090000_n00005840.out
x=0_var_1_t00100000_n00005960.out
x=0_var_1_t00110000_n00006080.out
x=0_var_1_t00120000_n00006200.out
x=0_var_1_t00130000_n00006320.out
x=0_var_1_t00140000_n00006440.out
x=0_var_1_t00150000_n00006560.out
x=0_var_1_t00160000_n00006680.out
x=0_var_1_t00170000_n00006740.out
x=0_var_1_t00180000_n00006800.out
x=0_var_1_t00190000_n00006860.out
x=0_var_1_t00200000_n00006920.out
x=0_var_1_t00210000_n00006980.out
x=0_var_1_t00220000_n00007040.out
x=0_var_1_t00230000_n00007100.out
x=0_var_1_t00240000_n00007160.out
x=0_var_1_t00250000_n00007220.out
x=0_var_1_t00260000_n00007280.out
x=0_var_1_t00270000_n00007340.out
x=0_var_1_t00280000_n00007400.out
x=0_var_1_t00290000_n00007461.out
x=0_var_1_t00300000_n00007522.out
x=0_var_1_t00310000_n00007583.out
x=0_var_1_t00320000_n00007644.out
x=0_var_1_t00330000_n00007705.out
x=0_var_1_t00340000_n00007766.out
x=0_var_1_t00350000_n00007827.out
x=0_var_1_t00360000_n00007888.out
x=0_var_1_t00370000_n00007949.out
x=0_var_1_t00380000_n00008010.out
x=0_var_1_t00390000_n00008071.out
x=0_var_1_t00400000_n00008132.out
x=0_var_1_t00410000_n00008193.out
x=0_var_1_t00420000_n00008254.out
x=0_var_1_t00430000_n00008315.out
x=0_var_1_t00440000_n00008376.out
x=0_var_1_t00450000_n00008437.out
x=0_var_1_t00460000_n00008498.out
x=0_var_1_t00470000_n00008559.out
x=0_var_1_t00480000_n00008620.out
x=0_var_1_t00490000_n00008681.out
x=0_var_1_t00500000_n00008742.out
x=0_var_1_t00510000_n00008803.out
x=0_var_1_t00520000_n00008864.out
x=0_var_1_t00530000_n00008925.out
x=0_var_1_t00540000_n00008986.out
x=0_var_1_t00550000_n00009047.out
x=0_var_1_t00560000_n00009108.out
x=0_var_1_t00570000_n00009169.out
x=0_var_1_t00580000_n00009230.out
x=0_var_1_t00590000_n00009291.out
x=0_var_1_t00600000_n00009352.out
x=0_var_1_t00610000_n00009413.out
x=0_var_1_t00620000_n00009474.out
x=0_var_1_t00630000_n00009535.out
x=0_var_1_t00640000_n00009596.out
x=0_var_1_t00650000_n00009657.out
x=0_var_1_t00660000_n00009718.out
x=0_var_1_t00670000_n00009779.out
x=0_var_1_t00680000_n00009840.out
x=0_var_1_t00690000_n00009901.out
x=0_var_1_t00700000_n00009962.out
x=0_var_1_t00710000_n00010023.out
x=0_var_1_t00720000_n00010084.out
x=0_var_1_t00730000_n00010145.out
x=0_var_1_t00740000_n00010206.out
x=0_var_1_t00750000_n00010267.out
x=0_var_1_t00760000_n00010328.out
x=0_var_1_t00770000_n00010389.out
x=0_var_1_t00780000_n00010450.out
x=0_var_1_t00790000_n00010511.out
x=0_var_1_t00800000_n00010572.out
x=0_var_1_t00810000_n00010633.out
x=0_var_1_t00820000_n00010694.out
x=0_var_1_t00830000_n00010755.out
x=0_var_1_t00840000_n00010816.out
x=0_var_1_t00850000_n00010877.out
x=0_var_1_t00860000_n00010938.out
x=0_var_1_t00870000_n00010999.out
x=0_var_1_t00880000_n00011060.out
x=0_var_1_t00890000_n00011121.out
x=0_var_1_t00900000_n00011182.out
x=0_var_1_t00910000_n00011243.out
x=0_var_1_t00920000_n00011304.out
x=0_var_1_t00930000_n00011365.out
x=0_var_1_t00940000_n00011426.out
x=0_var_1_t00950000_n00011487.out
x=0_var_1_t00960000_n00011548.out
y=0_var_2_t00020000_n00005000.out
y=0_var_2_t00030000_n00005120.out
y=0_var_2_t00040000_n00005240.out
y=0_var_2_t00050000_n00005360.out
y=0_var_2_t00060000_n00005480.out
y=0_var_2_t00070000_n00005600.out
y=0_var_2_t00080000_n00005720.out
y=0_var_2_t00090000_n00005840.out
y=0_var_2_t00100000_n00005960.out
y=0_var_2_t00110000_n00006080.out
y=0_var_2_t00120000_n00006200.out
y=0_var_2_t00130000_n00006320.out
y=0_var_2_t00140000_n00006440.out
y=0_var_2_t00150000_n00006560.out
y=0_var_2_t00160000_n00006680.out
y=0_var_2_t00170000_n00006740.out
y=0_var_2_t00180000_n00006800.out
y=0_var_2_t00190000_n00006860.out
y=0_var_2_t00200000_n00006920.out
y=0_var_2_t00210000_n00006980.out
y=0_var_2_t00220000_n00007040.out
y=0_var_2_t00230000_n00007100.out
y=0_var_2_t00240000_n00007160.out
y=0_var_2_t00250000_n00007220.out
y=0_var_2_t00260000_n00007280.out
y=0_var_2_t00270000_n00007340.out
y=0_var_2_t00280000_n00007400.out
y=0_var_2_t00290000_n00007461.out
y=0_var_2_t00300000_n00007522.out
y=0_var_2_t00310000_n00007583.out
y=0_var_2_t00320000_n00007644.out
y=0_var_2_t00330000_n00007705.out
y=0_var_2_t00340000_n00007766.out
y=0_var_2_t00350000_n00007827.out
y=0_var_2_t00360000_n00007888.out
y=0_var_2_t00370000_n00007949.out
y=0_var_2_t00380000_n00008010.out
y=0_var_2_t00390000_n00008071.out
y=0_var_2_t00400000_n00008132.out
y=0_var_2_t00410000_n00008193.out
y=0_var_2_t00420000_n00008254.out
y=0_var_2_t00430000_n00008315.out
y=0_var_2_t00440000_n00008376.out
y=0_var_2_t00450000_n00008437.out
y=0_var_2_t00460000_n00008498.out
y=0_var_2_t00470000_n00008559.out
y=0_var_2_t00480000_n00008620.out
y=0_var_2_t00490000_n00008681.out
y=0_var_2_t00500000_n00008742.out
y=0_var_2_t00510000_n00008803.out
y=0_var_2_t00520000_n00008864.out
y=0_var_2_t00530000_n00008925.out
y=0_var_2_t00540000_n00008986.out
y=0_var_2_t00550000_n00009047.out
y=0_var_2_t00560000_n00009108.out
y=0_var_2_t00570000_n00009169.out
y=0_var_2_t00580000_n00009230.out
y=0_var_2_t00590000_n00009291.out
y=0_var_2_t00600000_n00009352.out
y=0_var_2_t00610000_n00009413.out
y=0_var_2_t00620000_n00009474.out
y=0_var_2_t00630000_n00009535.out
y=0_var_2_t00640000_n00009596.out
y=0_var_2_t00650000_n00009657.out
y=0_var_2_t00660000_n00009718.out
y=0_var_2_t00670000_n00009779.out
y=0_var_2_t00680000_n00009840.out
y=0_var_2_t00690000_n00009901.out
y=0_var_2_t00700000_n00009962.out
y=0_var_2_t00710000_n00010023.out
y=0_var_2_t00720000_n00010084.out
y=0_var_2_t00730000_n00010145.out
y=0_var_2_t00740000_n00010206.out
y=0_var_2_t00750000_n00010267.out
y=0_var_2_t00760000_n00010328.out
y=0_var_2_t00770000_n00010389.out
y=0_var_2_t00780000_n00010450.out
y=0_var_2_t00790000_n00010511.out
y=0_var_2_t00800000_n00010572.out
y=0_var_2_t00810000_n00010633.out
y=0_var_2_t00820000_n00010694.out
y=0_var_2_t00830000_n00010755.out
y=0_var_2_t00840000_n00010816.out
y=0_var_2_t00850000_n00010877.out
y=0_var_2_t00860000_n00010938.out
y=0_var_2_t00870000_n00010999.out
y=0_var_2_t00880000_n00011060.out
y=0_var_2_t00890000_n00011121.out
y=0_var_2_t00900000_n00011182.out
y=0_var_2_t00910000_n00011243.out
y=0_var_2_t00920000_n00011304.out
y=0_var_2_t00930000_n00011365.out
y=0_var_2_t00940000_n00011426.out
y=0_var_2_t00950000_n00011487.out
y=0_var_2_t00960000_n00011548.out
z=0_var_3_t00020000_n00005000.out
z=0_var_3_t00030000_n00005120.out
z=0_var_3_t00040000_n00005240.out
z=0_var_3_t00050000_n00005360.out
z=0_var_3_t00060000_n00005480.out
z=0_var_3_t00070000_n00005600.out
z=0_var_3_t00080000_n00005720.out
z=0_var_3_t00090000_n00005840.out
z=0_var_3_t00100000_n00005960.out
z=0_var_3_t00110000_n00006080.out
z=0_var_3_t00120000_n00006200.out
z=0_var_3_t00130000_n00006320.out
z=0_var_3_t00140000_n00006440.out
z=0_var_3_t00150000_n00006560.out
z=0_var_3_t00160000_n00006680.out
z=0_var_3_t00170000_n00006740.out
z=0_var_3_t00180000_n00006800.out
z=0_var_3_t00190000_n00006860.out
z=0_var_3_t00200000_n00006920.out
z=0_var_3_t00210000_n00006980.out
z=0_var_3_t00220000_n00007040.out
z=0_var_3_t00230000_n00007100.out
z=0_var_3_t00240000_n00007160.out
z=0_var_3_t00250000_n00007220.out
z=0_var_3_t00260000_n00007280.out
z=0_var_3_t00270000_n00007340.out
z=0_var_3_t00280000_n00007400.out
z=0_var_3_t00290000_n00007461.out
z=0_var_3_t00300000_n00007522.out
z=0_var_3_t00310000_n00007583.out
z=0_var_3_t00320000_n00007644.out
z=0_var_3_t00330000_n00007705.out
z=0_var_3_t00340000_n00007766.out
z=0_var_3_t00350000_n00007827.out
z=0_var_3_t00360000_n00007888.out
z=0_var_3_t00370000_n00007949.out
z=0_var_3_t00380000_n00008010.out
z=0_var_3_t00390000_n00008071.out
z=0_var_3_t00400000_n00008132.out
z=0_var_3_t00410000_n00008193.out
z=0_var_3_t00420000_n00008254.out
z=0_var_3_t00430000_n00008315.out
z=0_var_3_t00440000_n00008376.out
z=0_var_3_t00450000_n00008437.out
z=0_var_3_t00460000_n00008498.out
z=0_var_3_t00470000_n00008559.out
z=0_var_3_t00480000_n00008620.out
z=0_var_3_t00490000_n00008681.out
z=0_var_3_t00500000_n00008742.out
z=0_var_3_t00510000_n00008803.out
z=0_var_3_t00520000_n00008864.out
z=0_var_3_t00530000_n00008925.out
z=0_var_3_t00540000_n00008986.out
z=0_var_3_t00550000_n00009047.out
z=0_var_3_t00560000_n00009108.out
z=0_var_3_t00570000_n00009169.out
z=0_var_3_t00580000_n00009230.out
z=0_var_3_t00590000_n00009291.out
z=0_var_3_t00600000_n00009352.out
z=0_var_3_t00610000_n00009413.out
z=0_var_3_t00620000_n00009474.out
z=0_var_3_t00630000_n00009535.out
z=0_var_3_t00640000_n00009596.out
z=0_var_3_t00650000_n00009657.out
z=0_var_3_t00660000_n00009718.out
z=0_var_3_t00670000_n00009779.out
z=0_var_3_t00680000_n00009840.out
z=0_var_3_t00690000_n00009901.out
z=0_var_3_t00700000_n00009962.out
z=0_var_3_t00710000_n00010023.out
z=0_var_3_t00720000_n00010084.out
z=0_var_3_t00730000_n00010145.out
z=0_var_3_t00740000_n00010206.out
z=0_var_3_t00750000_n00010267.out
z=0_var_3_t00760000_n00010328.out
z=0_var_3_t00770000_n00010389.out
z=0_var_3_t00780000_n00010450.out
z=0_var_3_t00790000_n00010511.out
z=0_var_3_t00800000_n00010572.out
z=0_var_3_t00810000_n00010633.out
z=0_var_3_t00820000_n00010694.out
z=0_var_3_t00830000_n00010755.out
z=0_var_3_t00840000_n00010816.out
z=0_var_3_t00850000_n00010877.out
z=0_var_3_t00860000_n00010938.out
z=0_var_3_t00870000_n00010999.out
z=0_var_3_t00880000_n00011060.out
z=0_var_3_t00890000_n00011121.out
z=0_var_3_t00900000_n00011182.out
z=0_var_3_t00910000_n00011243.out
z=0_var_3_t00920000_n00011304.out
z=0_var_3_t00930000_n00011365.out
z=0_var_3_t00940000_n00011426.out
z=0_var_3_t00950000_n00011487.out
z=0_var_3_t00960000_n00011548.out
```

</details>


---

<sub>⏱️ 3m 34s</sub>

### ✅ `apply_patch`

<details>
<summary>Arguments</summary>

```json
"*** Begin Patch\n*** Add File: /Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/analysis/plot_ih_z0_u_3frames.pro\n+; Case-local IDL command script for exporting three IH z=0 frames of func='u'\n+set_default_values\n+doask = 0\n+\n+workdir = '/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH'\n+files = [ $\n+  'z=0_var_3_t00020000_n00005000.out', $\n+  'z=0_var_3_t00490000_n00008681.out', $\n+  'z=0_var_3_t00960000_n00011548.out'  $\n+]\n+\n+func = 'u'\n+plotmode = 'contbar'\n+autorange = 'y'\n+showxtitle = 'y'\n+showytitle = 'y'\n+\n+cd, workdir\n+\n+filename = files[0]\n+npict = 1\n+plottitle = 'IH z=0 cut: U (beginning frame)'\n+read_data\n+set_device, 'analysis/ih_z0_u_beginning.eps', /port\n+plot_data\n+close_device, png='magick -density 180 -background white -alpha remove', /delete\n+\n+filename = files[1]\n+npict = 1\n+plottitle = 'IH z=0 cut: U (middle frame)'\n+read_data\n+set_device, 'analysis/ih_z0_u_middle.eps', /port\n+plot_data\n+close_device, png='magick -density 180 -background white -alpha remove', /delete\n+\n+filename = files[2]\n+npict = 1\n+plottitle = 'IH z=0 cut: U (last frame)'\n+read_data\n+set_device, 'analysis/ih_z0_u_last.eps', /port\n+plot_data\n+close_device, png='magick -density 180 -background white -alpha remove', /delete\n*** End Patch\n"
```

</details>

```
Added 1 file(s): /Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/analysis/plot_ih_z0_u_3frames.pro
```


---

<sub>⏱️ 3m 56s</sub>

### ✅ `bash`

**Run IDL script to export three IH z=0 U plots**

$ set -euo pipefail && cd /Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH && export IDL_STARTUP=/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/idlrc && /Applications/NV5/idl92/bin/idl > analysis/plot_ih_z0_u_3frames.idl.log 2>&1 <<'EOF'
@analysis/plot_ih_z0_u_3frames
exit
EOF

```

<exited with exit code 0>
```


---

<sub>⏱️ 4m 2s</sub>

### ✅ `bash`

**List generated images and show IDL log tail**

$ set -euo pipefail && cd /Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH && ls -1 analysis && echo '---' && ls -1 analysis/*.png && echo '---' && tail -n 40 analysis/plot_ih_z0_u_3frames.idl.log

```
plot_ih_z0_u_3frames.idl.log
plot_ih_z0_u_3frames.pro
---
ls: analysis/*.png: No such file or directory
<exited with exit code 1>
```


---

<sub>⏱️ 4m 4s</sub>

### 💬 Copilot

IDL ran but didn’t emit PNGs, so I’m reading the log and fixing the script accordingly.

---

<sub>⏱️ 4m 5s</sub>

### ✅ `view`

**view the file at /Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/analysis/plot_ih_z0_u_3frames.idl.log.**

/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/analysis/plot_ih_z0_u_3frames.idl.log

<details>
<summary>290 lines</summary>

```
1. IDL 9.2.0 (darwin arm64 m64).
2. (c) 2025, NV5 Geospatial Solutions, Inc.
3. 
4. Want an IDL Workbench alternative? Check out "IDL for VSCode" for a new user experience.
5. https://marketplace.visualstudio.com/items?itemName=IDL.idl-for-vscode
6.  
7. Licensed for use by: University of Michigan (MAIN)
8. License: 770385
9. % Compiled module: SET_DEFAULT_VALUES.
10. % Compiled module: LIMIT_CHANGE.
11. % Compiled module: LIMIT_GROWTH.
12. % Compiled module: CURVE_DISTANCE.
13. % Compiled module: CURVE_INT_DISTANCE.
14. % Compiled module: READ_DATA.
15. % Compiled module: PLOT_DATA.
16. % Compiled module: SHOW_DATA.
17. % Loaded DLM: VIDEO.
18. % Compiled module: ANIMATE_DATA.
19. % Compiled module: SLICE_DATA.
20. % Compiled module: SLICE_DATA_RESTORE.
21. % Compiled module: READ_LOG_DATA.
22. % Compiled module: PLOT_LOG_DATA.
23. % Compiled module: SHOW_LOG_DATA.
24. % Compiled module: REFORM2.
25. % Compiled module: DATE_TO_JULDAY.
26. % Compiled module: LOG_TIME.
27. % Compiled module: LOG_FUNC.
28. % Compiled module: BLACK_BACKGROUND.
29. % Compiled module: WHITE_BACKGROUND.
30. % Compiled module: OPEN_FILE.
31. % Compiled module: GET_FILE_TYPES.
32. % Compiled module: SHOW_HEAD.
33. % Compiled module: GET_FILE_HEAD.
34. % Compiled module: GET_PICT.
35. % Compiled module: GET_PICT_LOG.
36. % Compiled module: GET_PICT_ASC.
37. % Compiled module: GET_PICT_BIN.
38. % Compiled module: GET_PICT_REAL.
39. % Compiled module: ASKNUM.
40. % Compiled module: ASKSTR.
41. % Compiled module: STRING_TO_ARRAY.
42. % Compiled module: ARR2ARR.
43. % Compiled module: READ_PLOT_PARAM.
44. % Compiled module: READ_TRANSFORM_PARAM.
45. % Compiled module: GETVECTORS.
46. % Compiled module: DO_MY_TRANSFORM.
47. % Compiled module: DO_TRANSFORM.
48. % Compiled module: READ_LIMITS.
49. % Compiled module: GET_LIMITS.
50. % Compiled module: GET_GRID_DATA.
51. % Compiled module: MAKE_REGULAR_GRID.
52. % Compiled module: SYMM_TRIANGLES.
53. % Compiled module: FIT_TRIANGLES.
54. % Compiled module: AVERAGE_TRIANGLES.
55. % Compiled module: MAKE_POLAR_GRID.
56. % Compiled module: MAKE_POLAR_GRID2.
57. % Compiled module: MAKE_POLAR_GRID3.
58. % Compiled module: MAKE_SPHERE_GRID.
59. % Compiled module: MAKE_ANGLE_GRID.
60. % Compiled module: MAKE_UNPOLAR_GRID.
61. % Compiled module: MAKE_UNPOLAR_GRID2.
62. % Compiled module: MAKE_UNPOLAR_GRID3.
63. % Compiled module: GETAXES.
64. % Compiled module: SET_UNITS.
65. % Compiled module: SHOW_UNITS.
66. % Compiled module: GET_FUNC.
67. % Compiled module: PLOT_FUNC.
68. % Compiled module: PUTBOTTOM.
69. % Compiled module: PUTHEADER.
70. % Compiled module: PVALUE.
71. % Compiled module: CORR2.
72. % Compiled module: DIFF1.
73. % Compiled module: LAPLACE.
74. % Compiled module: LAPLACE2.
75. % Compiled module: LAPLACE3.
76. % Compiled module: DIFF2.
77. % Compiled module: DIFF2AVG.
78. % Compiled module: DIFF4.
79. % Compiled module: DIFF3.
80. % Compiled module: MINMOD.
81. % Compiled module: SYMMDIFFREG.
82. % Compiled module: SYMMDIFF.
83. % Compiled module: FILLEDGE.
84. % Compiled module: GENGRID.
85. % Compiled module: INTEDGE.
86. % Compiled module: INTEDGE_RZ.
87. % Compiled module: GRAD_2D.
88. % Compiled module: GRAD_RZ.
89. % Compiled module: DIV3.
90. % Compiled module: DIV.
91. % Compiled module: DIV_RZ.
92. % Compiled module: CURL.
93. % Compiled module: CURL_RZ.
94. % Compiled module: QUADRUPLET.
95. % Compiled module: TRIPLET.
96. % Compiled module: COARSEN.
97. % Compiled module: CHECKDIM.
98. % Compiled module: PLOT_GRID.
99. % Compiled module: COMPARE.
100. % Compiled module: REL_ERROR.
101. % Compiled module: REL_ERRORS.
102. % Compiled module: READ_LOG_LINE.
103. % Compiled module: GET_LOG.
104. % Compiled module: PLOT_LOG.
105. % Compiled module: RMS_LOGFILES.
106. % Compiled module: INTERPOL_LOGFILES.
107. % Compiled module: INTERPOL_LOG.
108. % Compiled module: QUIT.
109. % Compiled module: SET_SPACE.
110. % Compiled module: SET_POSITION.
111. % Compiled module: PLOT_COLOR_BAR.
112. % Compiled module: LOADCT_BW.
113. % Compiled module: MAKECT.
114. % Compiled module: SAVE_PICT.
115. % Compiled module: SAVE_LOG.
116. % Compiled module: RESET_AXIS.
117. % Compiled module: SCATTER_PLOT.
118. % Compiled module: PLOT_MAP.
119. % Compiled module: $MAIN$.
120. % Compiled module: LABEL_DATE.
121. % Compiled module: STREAMLINE.
122. % Compiled module: VECTOR.
123. % Compiled module: FUNCDEF.
124. % LOADCT: Loading table Rainbow + white
125. % Program caused arithmetic error: Floating overflow
126. filename(s)   =z=0_var_3_t00020000_n00005000.out
127. filetype(s)   = REAL4
128. npictinfile(s)=       1
129. npict=       1
130. 
131. 
132. filename   = z=0_var_3_t00020000_n00005000.out
133. filetype   = REAL4
134. headline   = 2024-08-01T02:04:00; R R R g/cm3 km/s km/s km/s G G G erg/cm3 erg/cm3 erg/cm3 dyne/cm^2 dyne/cm^2 uA/m2 uA/m2 uA/m2 G G G K K
135. it         =     5000
136. time       =       7200.0000
137. gencoord   =        1
138. ndim       =        2
139. neqpar     =        4
140. nw         =       20
141. nx         =   281152       1
142. parameters =   6.9600000e+08      19.000000      1.6666700      0.0000000
143. coord names= x y
144. var   names= Rho Ux Uy Uz Bx By Bz Ehot I01 I02 Pe P jx jy jz b1x b1y b1z te ti
145. param names= xSI r g cutz
146. Read x and w
147. transform (p=polar/s=sphere/u=unpolar/m=my/n=none/a=angle)=n
148. GRID (PLOT_DATA)
149.                 LONG      = Array[281152]
150. % Compiled module: SET_DEVICE.
151. ======= CURRENT PLOTTING PARAMETERS ================
152. colorlevel= 30, contourlevel= 30, velvector= 200, velspeed (0..5)= 5
153. multiplot=       0
154. axistype (coord/cells)=coord, fixaspect= 1
155. bottomline=3, headerline=0
156. ======= PLOTTING PARAMETERS =========================
157. wnames                     = Rho Ux Uy Uz Bx By Bz Ehot I01 I02 Pe P jx jy jz
158. b1x b1y b1z te ti
159. func(s) (e.g. rho p ux;uz bx+by -T) =u
160. 2D plotmode: shade/surface/cont/tv/polar/lonlatn/lonlats/velovect/vector/stream/scatter
161. 2D +options: degree/radian/hour
162. 2D +options: bar,body,extra,fill,grid,irr,label,max,mean,log,lgx,lgy
163. 2D +options: map,mesh,noaxis,over,usa,white,#c999,#ct999
164. plotmode(s)                =contbar
165. plottitle(s) (e.g. B [G];J)=IH z=0 cut: U (beginning frame)
166. autorange(s) (y/n)         =y
167. NX (FILE_HEAD)  LONG      = Array[2]
168. transform (p=polar/s=sphere/u=unpolar/m=my/n=none/a=angle)=none
169. GRID (PLOT_DATA)
170.                 LONG      = Array[281152]
171. ======= DETERMINE PLOTTING RANGES ===================
172. 
173. Min and max value for u:       0.0000000       441.88239
174. % Type conversion error: Unable to convert given STRING to Float.
175. % Detected at: PLOT_FUNC        4102 /Users/zkeheng/SWMFSoftware/SWMF/share/IDL
176.   /General/procedures.pro
177. % Operation illegal with strings.
178. % Execution halted at: $MAIN$          
179. % Program caused arithmetic error: Floating divide by 0
180. % Compiled module: CLOSE_DEVICE.
181. magick: no images found for operation `-alpha' at CLI arg 5 @ error/operation.c/CLIOption/5481.
182. filename(s)   =z=0_var_3_t00490000_n00008681.out
183. filetype(s)   = REAL4
184. npictinfile(s)=       1
185. npict=       1
186. 
187. 
188. filename   = z=0_var_3_t00490000_n00008681.out
189. filetype   = REAL4
190. headline   = 2024-08-03T01:04:00; R R R g/cm3 km/s km/s km/s G G G erg/cm3 erg/cm3 erg/cm3 dyne/cm^2 dyne/cm^2 uA/m2 uA/m2 uA/m2 G G G K K
191. it         =     8681
192. time       =       176400.00
193. gencoord   =        1
194. ndim       =        2
195. neqpar     =        4
196. nw         =       20
197. nx         =   281152       1
198. parameters =   6.9600000e+08      19.000000      1.6666700      0.0000000
199. coord names= x y
200. var   names= Rho Ux Uy Uz Bx By Bz Ehot I01 I02 Pe P jx jy jz b1x b1y b1z te ti
201. param names= xSI r g cutz
202. Read x and w
203. transform (p=polar/s=sphere/u=unpolar/m=my/n=none/a=angle)=none
204. GRID (PLOT_DATA)
205.                 LONG      = Array[281152]
206. ======= CURRENT PLOTTING PARAMETERS ================
207. colorlevel= 30, contourlevel= 30, velvector= 200, velspeed (0..5)= 5
208. multiplot=       0
209. axistype (coord/cells)=coord, fixaspect= 1
210. bottomline=3, headerline=0
211. ======= PLOTTING PARAMETERS =========================
212. wnames                     = Rho Ux Uy Uz Bx By Bz Ehot I01 I02 Pe P jx jy jz
213. b1x b1y b1z te ti
214. func(s) (e.g. rho p ux;uz bx+by -T) =u
215. 2D plotmode: shade/surface/cont/tv/polar/lonlatn/lonlats/velovect/vector/stream/scatter
216. 2D +options: degree/radian/hour
217. 2D +options: bar,body,extra,fill,grid,irr,label,max,mean,log,lgx,lgy
218. 2D +options: map,mesh,noaxis,over,usa,white,#c999,#ct999
219. plotmode(s)                =contbar
220. plottitle(s) (e.g. B [G];J)=IH z=0 cut: U (middle frame)
221. autorange(s) (y/n)         =y
222. NX (FILE_HEAD)  LONG      = Array[2]
223. transform (p=polar/s=sphere/u=unpolar/m=my/n=none/a=angle)=none
224. GRID (PLOT_DATA)
225.                 LONG      = Array[281152]
226. ======= DETERMINE PLOTTING RANGES ===================
227. 
228. Min and max value for u:       0.0000000       634.95557
229. % Type conversion error: Unable to convert given STRING to Float.
230. % Detected at: PLOT_FUNC        4102 /Users/zkeheng/SWMFSoftware/SWMF/share/IDL
231.   /General/procedures.pro
232. % Operation illegal with strings.
233. % Execution halted at: $MAIN$          
234. % Program caused arithmetic error: Floating divide by 0
235. magick: no images found for operation `-alpha' at CLI arg 5 @ error/operation.c/CLIOption/5481.
236. filename(s)   =z=0_var_3_t00960000_n00011548.out
237. filetype(s)   = REAL4
238. npictinfile(s)=       1
239. npict=       1
240. 
241. 
242. filename   = z=0_var_3_t00960000_n00011548.out
243. filetype   = REAL4
244. headline   = 2024-08-05T00:04:00; R R R g/cm3 km/s km/s km/s G G G erg/cm3 erg/cm3 erg/cm3 dyne/cm^2 dyne/cm^2 uA/m2 uA/m2 uA/m2 G G G K K
245. it         =    11548
246. time       =       345600.00
247. gencoord   =        1
248. ndim       =        2
249. neqpar     =        4
250. nw         =       20
251. nx         =   281152       1
252. parameters =   6.9600000e+08      19.000000      1.6666700      0.0000000
253. coord names= x y
254. var   names= Rho Ux Uy Uz Bx By Bz Ehot I01 I02 Pe P jx jy jz b1x b1y b1z te ti
255. param names= xSI r g cutz
256. Read x and w
257. transform (p=polar/s=sphere/u=unpolar/m=my/n=none/a=angle)=none
258. GRID (PLOT_DATA)
259.                 LONG      = Array[281152]
260. ======= CURRENT PLOTTING PARAMETERS ================
261. colorlevel= 30, contourlevel= 30, velvector= 200, velspeed (0..5)= 5
262. multiplot=       0
263. axistype (coord/cells)=coord, fixaspect= 1
264. bottomline=3, headerline=0
265. ======= PLOTTING PARAMETERS =========================
266. wnames                     = Rho Ux Uy Uz Bx By Bz Ehot I01 I02 Pe P jx jy jz
267. b1x b1y b1z te ti
268. func(s) (e.g. rho p ux;uz bx+by -T) =u
269. 2D plotmode: shade/surface/cont/tv/polar/lonlatn/lonlats/velovect/vector/stream/scatter
270. 2D +options: degree/radian/hour
271. 2D +options: bar,body,extra,fill,grid,irr,label,max,mean,log,lgx,lgy
272. 2D +options: map,mesh,noaxis,over,usa,white,#c999,#ct999
273. plotmode(s)                =contbar
274. plottitle(s) (e.g. B [G];J)=IH z=0 cut: U (last frame)
275. autorange(s) (y/n)         =y
276. NX (FILE_HEAD)  LONG      = Array[2]
277. transform (p=polar/s=sphere/u=unpolar/m=my/n=none/a=angle)=none
278. GRID (PLOT_DATA)
279.                 LONG      = Array[281152]
280. ======= DETERMINE PLOTTING RANGES ===================
281. 
282. Min and max value for u:       0.0000000       642.23352
283. % Type conversion error: Unable to convert given STRING to Float.
284. % Detected at: PLOT_FUNC        4102 /Users/zkeheng/SWMFSoftware/SWMF/share/IDL
285.   /General/procedures.pro
286. % Operation illegal with strings.
287. % Execution halted at: $MAIN$          
288. % Program caused arithmetic error: Floating divide by 0
289. magick: no images found for operation `-alpha' at CLI arg 5 @ error/operation.c/CLIOption/5481.
290.
```

</details>


---

<sub>⏱️ 4m 21s</sub>

### ✅ `apply_patch`

<details>
<summary>Arguments</summary>

```json
"*** Begin Patch\n*** Update File: /Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/analysis/plot_ih_z0_u_3frames.pro\n@@\n func = 'u'\n plotmode = 'contbar'\n autorange = 'y'\n-showxtitle = 'y'\n-showytitle = 'y'\n@@\n close_device, png='magick -density 180 -background white -alpha remove', /delete\n@@\n close_device, png='magick -density 180 -background white -alpha remove', /delete\n@@\n close_device, png='magick -density 180 -background white -alpha remove', /delete\n*** End Patch\n"
```

</details>

```
Modified 1 file(s): /Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/analysis/plot_ih_z0_u_3frames.pro
```


---

<sub>⏱️ 4m 32s</sub>

### ✅ `apply_patch`

<details>
<summary>Arguments</summary>

```json
"*** Begin Patch\n*** Update File: /Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/analysis/plot_ih_z0_u_3frames.pro\n@@\n-close_device, png='magick -density 180 -background white -alpha remove', /delete\n+close_device, png='magick -density 180', /delete\n@@\n-close_device, png='magick -density 180 -background white -alpha remove', /delete\n+close_device, png='magick -density 180', /delete\n@@\n-close_device, png='magick -density 180 -background white -alpha remove', /delete\n+close_device, png='magick -density 180', /delete\n*** End Patch\n"
```

</details>

```
Modified 1 file(s): /Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH/analysis/plot_ih_z0_u_3frames.pro
```


---

<sub>⏱️ 4m 46s</sub>

### ✅ `bash`

**Re-run IDL script after fixing plotting options**

$ set -euo pipefail && cd /Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH && export IDL_STARTUP=/Users/zkeheng/SWMFSoftware/SWMF/share/IDL/General/idlrc && /Applications/NV5/idl92/bin/idl > analysis/plot_ih_z0_u_3frames.idl.log 2>&1 <<'EOF'
@analysis/plot_ih_z0_u_3frames
exit
EOF

```

<exited with exit code 0>
```


---

<sub>⏱️ 4m 48s</sub>

### ✅ `bash`

**Verify generated PNG images**

$ set -euo pipefail && cd /Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH && ls -1 analysis && echo '---' && ls -1 analysis/*.png

<details>
<summary>10 lines</summary>

```
ih_z0_u_beginning.png
ih_z0_u_last.png
ih_z0_u_middle.png
plot_ih_z0_u_3frames.idl.log
plot_ih_z0_u_3frames.pro
---
analysis/ih_z0_u_beginning.png
analysis/ih_z0_u_last.png
analysis/ih_z0_u_middle.png
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 54s</sub>

### 💬 Copilot

Done — I generated and saved the three IH z=0 `func='u'` plots as separate PNGs:

- `Run_Max_RP_CME3/run01/IH/analysis/ih_z0_u_beginning.png`
- `Run_Max_RP_CME3/run01/IH/analysis/ih_z0_u_middle.png`
- `Run_Max_RP_CME3/run01/IH/analysis/ih_z0_u_last.png`

I used the IH `z=0_var_3` frame group (first/middle/last files from `run01/IH`), confirmed the result-file header/variables for that artifact, and rendered via IDL using `read_data + plot_data` with `func='u'` and `plotmode='contbar'`. Script and log are saved at `Run_Max_RP_CME3/run01/IH/analysis/plot_ih_z0_u_3frames.pro` and `.idl.log`. **Uncertainty:** each frame used autorange, so color scales may differ between images; if strict visual comparison matters, fix `fmin/fmax` across all three.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
