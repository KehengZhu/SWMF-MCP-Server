# Shipped PARAM template index

Each `swmf-replicate` archetype names a **set** of shipped PARAM files the
agent must read before authoring its own PARAM.in. The set surfaces
convention variance ("template A uses Linde+mc3, template B uses Sokolov+minmod,
template C uses Roe — pick by archetype + paper"). The agent reads the
shipped files directly via `Read`; there are no forked YAML copies here.

Discovery is not exhaustive — see `discovery.md` for the search recipe the
agent runs after the static list below.

## Layout

```
<archetype>:
  primary:  the canonical shipped PARAM for this archetype (read first)
  surveys:  additional precedents from anywhere under SWMF that the agent
            reads to observe convention variance
```

## Static index

```yaml
awsom_steady_sc:
  primary:
    - SWMFSOLAR/Param/PARAM.in.awsom
  surveys:
    - SWMFSOLAR/Param/PARAM.in.awsom.STITCH
    - SC/BATSRUS/Param/PARAM.in.SCstandalone
    - SC/BATSRUS/Test_SCIH_AWSoM/PARAM.in
    - SC/BATSRUS/Test_SC_AwsomFluids/PARAM.in
    - SC/BATSRUS/Param/AWSoMR/PARAM.in.start

awsom_steady_sc_only:
  primary:
    - SWMFSOLAR/Param/PARAM.in.awsom
  surveys:
    - SWMFSOLAR/Param/PARAM.in.awsom.STITCH
    - SC/BATSRUS/Param/PARAM.in.SCstandalone
    - SC/BATSRUS/Test_SC_AwsomFluids/PARAM.in
  notes: >
    SC-only variant of awsom_steady_sc; surveys excludes any template that
    expands into IH (the recipe explicitly drops IH-only commands).

awsom_cme_eruption:
  primary:
    - SWMFSOLAR/Param/PARAM.expand.restart
  surveys:
    - SWMFSOLAR/Param/PARAM.expand.start
    - SC/BATSRUS/Test_SC_CME/PARAM.in
    - SC/BATSRUS/Test_SCIH_CME/PARAM.in

sofie_mflampa_cme:
  primary:
    - SWMFSOLAR/Param/PARAM.sofie.restart
  surveys:
    - SWMFSOLAR/Param/PARAM.sofie.start
    - SP/MFLAMPA/Param/PARAM.in.test
    - SC/BATSRUS/Test_SCIH_AWSoM/PARAM.in

geospace_gm_ie_im:
  primary:
    - SWMFSOLAR/Param/PARAM.geospace
  surveys:
    - GM/BATSRUS/Test_GM_IE/PARAM.in
    - GM/BATSRUS/Test_GM_IE_IM/PARAM.in
    - IM/RCM2/Param/PARAM.in.coupling
```

## Why a *set* and not a single template

The Liu et al. 2026 replication failure showed the danger of structural
anchoring on one template. `PARAM.in.awsom` omits `#CURLB0`; if the agent
only reads that one file, it misses the entire `#CURLB0`/FDIPS-B0 path.
Reading 3–5 precedents surfaces the alternative.

The archetype recipe (`case_recipes/<archetype>.md`) also describes the
variance the agent should expect to see across the set — e.g. "templates
disagree on TypeFlux between Linde and Sokolov; pick per the paper, or per
the convention in `conventions.yaml`."
