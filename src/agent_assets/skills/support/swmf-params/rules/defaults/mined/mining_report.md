# Corpus mining report

Threshold (fraction of files for command to count as required): **0.80**

## Archetype coverage

| Archetype | Files | File names |
| --- | ---: | --- |
| `awsom_steady_sc_only` | 2 | PARAM.in.restart.SC.plot_los, PARAM.in.test.SC |
| `awsom_anisopi_steady_sc_ih` | 3 | PARAM.in.awsom, PARAM.in.awsom.eclipse2024, PARAM.in.test.start.SCIH |
| `awsom_anisopi_cme` | 6 | PARAM.in.awsom.CME, PARAM.in.awsom.CME_gpu, PARAM.in.test.cme.SCIH, PARAM.in.test.cme.SCIH_gpu, PARAM.in.test.restart.SCIH, PARAM.in.test.restart.SCIH_gpu |
| `awsomr_steady` | 5 | PARAM.in.awsomr, PARAM.in.realtime.SCIH_threadbc, PARAM.in.realtime.restart.SCIH_threadbc, PARAM.in.test.SCIH_threadbc, PARAM.in.test.restart.SCIH_threadbc |
| `awsomr_cme` | 1 | PARAM.in.awsomr.CME |
| `awsom_sc_only_legacy` | 1 | PARAM.in.awsom.STITCH |
| `sofie_steady` | 4 | PARAM.in.sofie, PARAM.in.sofie.CCMC, PARAM.in.test.SCIHSP, PARAM.in.test.restart.SCIHSP |
| `sofie_cme` | 1 | PARAM.in.sofie.CME |
| `sofie_mflampa_cme` | 1 | PARAM.in.sofie.MFLAMPA |
| `ee_corona` | 2 | PARAM.in.test.EE, PARAM.in.test.EE.3D |
| `outer_helio` | 0 | *(none)* |
| `geospace_gm_only` | 0 | *(none)* |
| `geospace_gm_ie_im` | 1 | PARAM.in.test.GMIEHEIDI |

## Unmatched PARAMs

These were enumerated but no archetype matched. Either extend `archetypes.yaml` or accept that they fall outside the catalog.

- `PARAM.in.test.CZ`:
  - unmatched: components=['CZ'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.EESC`:
  - filename hint 'PARAM.in.test.EESC' suggested awsom_steady_sc_only but tuple mismatch: ["components ['EE', 'SC'] != ['SC']"]
  - filename hint 'PARAM.in.test.EE' suggested ee_corona but tuple mismatch: ["components ['EE', 'SC'] != ['EE']"]
  - unmatched: components=['EE', 'SC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=True, models={}
- `PARAM.in.test.FLEKS.AMR.LightWave.3D`:
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMIEIMUA`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'IE', 'IM', 'UA'] != ['GM']"]
  - unmatched: components=['GM', 'IE', 'IM', 'UA'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMIEPW`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'IE', 'PW'] != ['GM']"]
  - unmatched: components=['GM', 'IE', 'PW'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.3D.start`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.FLEKS.2D.2steps`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.FLEKS.2D.4steps`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.FLEKS.2D.adapt`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.FLEKS.2D.periodic`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.FLEKS.2D.restart`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.FLEKS.3D`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.FLEKS.AMR.FASTWAVE.2D`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.FLEKS.AMR.FASTWAVE.3D`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.FLEKS.periodic`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.aniso.AMPS`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.aniso.AMPS.2step`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.aniso.AMPS.2step.restart`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.aniso.AMPS.corr`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.aniso.AMPS.dynamic`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.aniso.AMPS.fluxrope`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.restart.2step.aniso`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.start`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.start.2step.aniso`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPC.start.aniso`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PC'] != ['GM']"]
  - filename hint 'PARAM.in.test.GMPC' suggested geospace_gm_ie_im but tuple mismatch: ["components ['GM', 'PC'] != ['GM', 'IE', 'IM']"]
  - unmatched: components=['GM', 'PC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPT`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PT'] != ['GM']"]
  - unmatched: components=['GM', 'PT'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMPT.Europa`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'PT'] != ['GM']"]
  - unmatched: components=['GM', 'PT'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.GMUA.MGITM`:
  - filename hint 'PARAM.in.test.GM' suggested geospace_gm_only but tuple mismatch: ["components ['GM', 'UA'] != ['GM']"]
  - unmatched: components=['GM', 'UA'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.IHGM`:
  - unmatched: components=['GM', 'IH'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.IHOH.CoupleSphToXyz`:
  - unmatched: components=['IH', 'OH'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.OHPT`:
  - filename hint 'PARAM.in.test.OH' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - unmatched: components=['OH', 'PT'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.OHPT.FLEKS.outerhelio.4neu.couple`:
  - filename hint 'PARAM.in.test.OH' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - filename hint 'outerhelio' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - unmatched: components=['OH', 'PT'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.OHPT.FLEKS.outerhelio.4neu.start`:
  - filename hint 'PARAM.in.test.OH' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - filename hint 'outerhelio' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - unmatched: components=['OH', 'PT'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.OHPT.FLEKS.outerhelio.pui.4neu.couple`:
  - filename hint 'PARAM.in.test.OH' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - filename hint 'outerhelio' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - unmatched: components=['OH', 'PT'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.OHPT.FLEKS.outerhelio.pui.4neu.start`:
  - filename hint 'PARAM.in.test.OH' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - filename hint 'outerhelio' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - unmatched: components=['OH', 'PT'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.OHPT.FLEKS.outerhelio.swh`:
  - filename hint 'PARAM.in.test.OH' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - filename hint 'outerhelio' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - unmatched: components=['OH', 'PT'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.OHPT.FLEKS.outerhelio.swhpui`:
  - filename hint 'PARAM.in.test.OH' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - filename hint 'outerhelio' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - unmatched: components=['OH', 'PT'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.OHPT.FLEKS.shocktube`:
  - filename hint 'PARAM.in.test.OH' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - unmatched: components=['OH', 'PT'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.OHPTpui`:
  - filename hint 'PARAM.in.test.OH' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - unmatched: components=['OH', 'PT'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.OHPTpuishocktube`:
  - filename hint 'PARAM.in.test.OH' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - unmatched: components=['OH', 'PT'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.OHPTshocktube`:
  - filename hint 'PARAM.in.test.OH' suggested outer_helio but tuple mismatch: ["components ['OH', 'PT'] != ['OH']"]
  - unmatched: components=['OH', 'PT'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.PS`:
  - unmatched: components=['PS'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.PW`:
  - unmatched: components=['PW'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.SC.TDEquil`:
  - filename hint 'PARAM.in.test.SC' suggested awsom_steady_sc_only but tuple mismatch: ['has_CME True != False']
  - unmatched: components=['SC'], has_CME=True, has_MFLAMPA=False, has_threaded_gap=False, models={'SC': 'Mhd'}
- `PARAM.in.test.SCGM`:
  - filename hint 'PARAM.in.test.SC' suggested awsom_steady_sc_only but tuple mismatch: ["components ['GM', 'SC'] != ['SC']"]
  - unmatched: components=['GM', 'SC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=True, models={'SC': 'Awsom'}
- `PARAM.in.test.SCIHOHSP`:
  - filename hint 'PARAM.in.test.SC' suggested awsom_steady_sc_only but tuple mismatch: ["components ['IH', 'OH', 'SC', 'SP'] != ['SC']"]
  - unmatched: components=['IH', 'OH', 'SC', 'SP'], has_CME=False, has_MFLAMPA=True, has_threaded_gap=True, models={}
- `PARAM.in.test.SCIHPT`:
  - filename hint 'PARAM.in.test.SC' suggested awsom_steady_sc_only but tuple mismatch: ["components ['IH', 'PT', 'SC'] != ['SC']"]
  - unmatched: components=['IH', 'PT', 'SC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=True, models={}
- `PARAM.in.test.SCIHSP_single`:
  - filename hint 'PARAM.in.test.SC' suggested awsom_steady_sc_only but tuple mismatch: ["components [] != ['SC']"]
  - unmatched: components=[], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.SCIH_streamaligned`:
  - filename hint 'PARAM.in.test.SC' suggested awsom_steady_sc_only but tuple mismatch: ["components ['IH', 'SC'] != ['SC']"]
  - filename hint 'PARAM.in.test.SCIH_streamaligned' suggested awsom_anisopi_steady_sc_ih but tuple mismatch: ['has_threaded_gap True != False']
  - unmatched: components=['IH', 'SC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=True, models={'SC': 'AwsomSA', 'IH': 'AwsomSA'}
- `PARAM.in.test.SP`:
  - unmatched: components=['SP'], has_CME=False, has_MFLAMPA=True, has_threaded_gap=False, models={}
- `PARAM.in.test.restart.GMIEIMUA`:
  - unmatched: components=['GM', 'IE', 'IM', 'UA'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.restart.OHPT`:
  - unmatched: components=['OH', 'PT'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={}
- `PARAM.in.test.restart.SCIHOHSP`:
  - unmatched: components=['IH', 'OH', 'SC', 'SP'], has_CME=False, has_MFLAMPA=True, has_threaded_gap=True, models={}
- `PARAM.in.test.start.SCIH_gpu`:
  - unmatched: components=['IH', 'SC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={'SC': 'Awsom', 'IH': 'Awsom'}
- `PARAM.in.test.start.SP`:
  - unmatched: components=['SP'], has_CME=False, has_MFLAMPA=True, has_threaded_gap=False, models={}
- `PARAM.in.test.stubs`:
  - unmatched: components=['IH', 'SP'], has_CME=False, has_MFLAMPA=True, has_threaded_gap=False, models={}
- `PARAM.in.awsom_gpu`:
  - filename hint 'PARAM.in.awsom' suggested awsom_anisopi_steady_sc_ih but tuple mismatch: ["model {'Awsom'} != AwsomAnisoPi*"]
  - filename hint 'PARAM.in.awsom_gpu' suggested awsom_anisopi_steady_sc_ih but tuple mismatch: ["model {'Awsom'} != AwsomAnisoPi*"]
  - unmatched: components=['IH', 'SC'], has_CME=False, has_MFLAMPA=False, has_threaded_gap=False, models={'SC': 'Awsom', 'IH': 'Awsom'}
