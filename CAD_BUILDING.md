# CAD type dispatch and per-part output selection

## SolidCraft startup and failures

Run `python working_solidcraft.py` from the project folder to build populated, enabled parts using the helper Python configured in `solidcraft/config.json`. Ordinary native generation supports SolidCraft CLI 0.22.0 and 0.30.0; untested releases are still rejected. No AI session is needed to run the build.

The shared helper owns backend compatibility and launch/error handling in `components/mcp`, `components/backend`, `components/pipeline` and `components/project_launcher`. Projects load these through the configured helper root, so fixes do not need to be copied into their editable recipes. Keep geometry in `working_solidcraft.py`.

Build failures include the underlying error and failed part/mode directly in the exception, plus the attempt manifest and `build/solidcraft/runs/latest_run.json` paths. For example, an untested CLI release is reported by version instead of only showing a generic generation failure. Actual backend versions are recorded in successful build manifests and build keys.

## Reset generated SolidCraft outputs

Run `action_delete_solidcraft_files.bat` to clear the generated true/3dpr SolidCraft files and their STEP, native STL, PNG and metadata companions from part folders. The next build regenerates all selected native files. Use `action_delete_solidcraft_files.bat -DryRun` to preview targets.

SCAD outputs, part definitions, custom/manual files, sealed parts and build history are preserved. Cleanup refuses to run while a SolidCraft writer holds the build lock. The batch file works from any current directory; its implementation is in `components/solidcraft_cleanup/working.ps1`.

## Develop in working_scad and generate native SolidCraft

`run_solidcraft` now accepts three values:

| Value | Behavior |
| --- | --- |
| `True` | Generate native CAD using the separate `working_solidcraft.py` recipe. |
| `False` | Disable SolidCraft generation. |
| `"working_scad"` | Generate native CAD from the `get_<oobb_type>` definitions in `working_scad.py`. |

Both `action_make_all.py` and `action_make_solidcraft.py` now default to SCAD definitions as the SolidCraft source:

```python
kwargs.setdefault("run_solidcraft", "working_scad")
```

You can also call `action_make_all.main(run_solidcraft="working_scad")`. This selects the shared source for every enabled part while preserving per-part `run_solidcraft=False`. `run_scad=False` only disables the separate SCAD output; it does not prevent native generation from SCAD definitions.

For individual parts, set `option["run_solidcraft"] = "working_scad"` during population. With the ordinary project-wide `True` switch, each such part uses its SCAD recipe; other enabled parts retain their separate native recipes. An explicit project source override takes precedence over per-part source selection. The make-action default is `"working_scad"`. Pass `run_solidcraft=True` to use the independent native recipes, or `False` to disable SolidCraft.

For direct generation without population or other actions:

```powershell
python working_solidcraft.py --recipe-source working_scad --extras --stl
```

Keep geometry in `working_scad.get_<type>(thing, **kwargs)`. The helper adapts OOBB imports to the native components in memory on every run, retaining constants, helper functions and source tracebacks. It generates editable `.solidcraft` files and selected STEP/PNG/STL exports directly from these definitions. No duplicate recipe code is maintained automatically, and the independent native recipe file remains the launcher for direct generation. Missing `get_<type>` functions fail clearly against the selected source.

The shared source uses the same supported native components, arbitrary project details, finite hole depths, red `m="#"` highlights and optional verification. `scad_help.prepare_base_for_print` uses the native print helper in this mode. The manifest records the original SCAD source path/hash and `builder.recipe_source: working_scad`. Legacy SCAD-only output remains independent.

## Regenerate SolidCraft on every run

SolidCraft rebuilds every selected, enabled part/mode from the current recipe on every run, just like SCAD. Existing `.solidcraft`, STEP, PNG and STL files do not skip generation. There is no need to delete outputs after editing a recipe or changing dimensions.

`action_make_all.py` and `action_make_solidcraft.py` regenerate native CAD, STEP, PNG and STL by default. Outputs in `parts/<part-id>/` are `<mode>.solidcraft`, `<mode>.step`, `<mode>_solidcraft.png` and `<mode>_solidcraft.stl`, for `true` and `3dpr`. Requested outputs are replaced after each successful build. A failed build reports its error and leaves that mode's previous published files available. Sealed parts, imported-library parts, disabled routes and filters keep their existing behavior.

Direct `python working_solidcraft.py` rebuilds native CAD only by default. Use `python working_solidcraft.py --extras --stl` to rebuild native CAD and STEP/PNG/STL without running population, SCAD, SVG or other actions. Explicit `export_extras=False` and `export_stl=False` remain supported by both make actions; unrequested export formats are preserved.

Successful runs update `<mode>_solidcraft_manifest.json` with current recipe provenance and artifact hashes. The former missing-exports-only route is no longer used by builds. Verification remains independently controlled by `--verify` / `verify_solidcraft=True`, and now runs on each requested rebuild when enabled.

Raw `shape="cylinder"` components require `h` for the height (for example, `p3["h"] = depth_side`). The OOBB wrapper `shape="oobb_cylinder"` accepts `depth`.

Inherited `diameter` metadata is accepted on expanded primitives, including screw heads, shafts, nuts, overhangs and slicing cubes. It does not override their explicit dimensions, so a reel diameter in grid units can pass through the shared details dictionary without changing fastener sizes. Raw circular primitive dimensions still use `radius`, `r` or `d` in millimetres. This handling is shared through the helper's `components/primitive_contract/working.py`.

## Red SolidCraft highlights

Set the familiar modifier on any component before appending it:

```python
p3["m"] = "#"
oobb.append_full(thing, **p3)
```

Both positive components and negative cutters are shown in translucent red in the saved `.solidcraft` file and native PNG preview. Their normal add/cut behavior is preserved. Negative geometry remains visible as a display copy after subtraction. Remove `m`, or set `p3["m"] = ""`, to turn off highlighting on the next rebuild.

This also propagates through OOBB hole arrays and transformed groups. The native Browser lists display copies as `__oobb_highlight_###`. Generated STEP/STL files and physical geometry checks exclude those copies. For manual exports in SolidCraft, select the finished physical body. The shared helper owns this behavior in `components/highlight`, `components/recipe`, `components/compiler` and `components/backend`, so this project and `project_base` use the same implementation.

## Optional SolidCraft verification

Verification defaults to **off**, separately from export selection. Both make action scripts declare:

```python
kwargs["verify_solidcraft"] = kwargs.get("verify_solidcraft", False)
```

Change that default to True, pass `verify_solidcraft=True` to the action's `main()`, or use `python working_solidcraft.py --verify`. `working.run()` extracts the ordinary kwarg before other actions receive it. Direct native scripts also declare `VERIFY_SOLIDCRAFT = False`.

With verification off, requested SolidCraft/STEP/STL/PNG files still generate and publish immediately. Reference geometry, measurement comparisons, reopened-file checks, edited variants and STEP reimport are skipped. Command errors and native structural health still fail the build. Manifests explicitly record `verify_solidcraft: false` and `verification.status: not_requested`.

With verification on, native-only runs check reference measurements and saved-file reopening; runs with extras additionally perform the existing STEP comparisons, parameter edits and reimport checks. `--extras` selects exports only; it no longer enables verification implicitly.

## Default native output (updated)

`action_make_all.py` and `action_make_solidcraft.py` enable native SolidCraft, STEP, PNG and STL outputs by default. They set ordinary `kwargs["export_extras"]` and `kwargs["export_stl"]` to True when not supplied. `working.run()` extracts these flags into the internal SolidCraft options before calling other actions; absent flags default to False. Explicit flat kwargs take precedence over legacy context values, and filters/modes are preserved. This differs intentionally from running `working_solidcraft.py` directly.

`python working_solidcraft.py` now generates only `true.solidcraft` and `3dpr.solidcraft` in each enabled part's folder. `EXPORT_EXTRAS = False` and `EXPORT_STL = False` are visible in the recipe file. Add `--extras` for STEP and PNG previews; add `--verify` independently for generation verification; add `--stl` for STL independently. Python callers can use `solidcraft_context={"export_extras": True}`.

Ordinary generation checks command success and constrained sketches; reference measurements and saved-document reopening belong to optional verification. Diagnostic JSON and publication manifests remain for build tracking. Existing PNG/STEP/STL files are preserved but are not regenerated by the default command. The earlier sections below describe the migration history and optional full export route.

## Build scripts

Run these from the project folder:

| Command | Outputs |
| --- | --- |
| `python action_make_all.py` | SCAD/STL and SolidCraft, plus the existing SVG/project actions |
| `python action_make_solidcraft.py` | SolidCraft only: native CAD, STEP, PNG previews and STL |
| `python action_make_scad.py` | SCAD/STL only |
| `python action_make_scad_no_stl.py` | SCAD only |

The SolidCraft-only script populates/materializes parts first, waits for that
work to finish, then builds native CAD. It skips the separate SCAD output route,
SVG and project actions. The native pipeline uses independent exact geometry, STEP and reopen/edit verification, plus STL verification when explicitly enabled. Its optional `--reference-scad` audit requires the old libraries separately. Native scripts require the helper environment.
Existing `action_make_all_no_stl.py` retains its legacy behavior.

Both make-all and SolidCraft-only honor per-part output flags and accept
`solidcraft_context` through their Python `main()` functions, for example
`main(solidcraft_context={"part_filter": "plate", "modes": ["true"]})`.
With no context they process all enabled parts in both `true` and `3dpr` modes.
Make-all supports an explicit `main(run_solidcraft=False)` opt-out.

## Part definitions

`oobb_details` can carry the full project details dictionary, including custom dimensions, taxonomy fields and nested metadata. These values pass through to the native recipe's `**kwargs`; there is no supported-key allowlist or required `OOBB_DETAILS` declaration. This behavior lives in the shared helper's `components/construction/working.py`.

Declare the CAD type and desired outputs during population:

```python
option["oobb_type"] = "plate"
option["width"] = 3
option["height"] = 3
option["depth"] = 3
option["run_scad"] = True
option["run_solidcraft"] = True
```

`working_oomp_populate` writes these into the part definition:

```yaml
oobb_details:
  oobb_type: plate
  oobb_name: plate
  width: 3
  height: 3
  depth: 3
  run_scad: true
  run_solidcraft: true
```

`oobb_type: plate` calls `working_scad.get_plate(thing, **kwargs)` for SCAD and
`working_solidcraft.get_plate(thing, **kwargs)` for native CAD. These are separate,
editable functions using the same ordinary OOBB dictionaries and
`oobb.append_full(thing, **component)` calls. Keep session management, exports
and CAD verification outside those functions.

In `working_solidcraft.py`, start each component with `p3 = copy.deepcopy(kwargs)`,
then assign its fields individually (`p3["shape"] = "oobb_holes"`, and so on)
and call `oobb.append_full(thing, **p3)`. This is the user's preferred authoring
style. Start a fresh deep copy for each component to inherit part options;
subsequent assignments take precedence. Keep dimensions,
shape, position and hole depth visible in the recipe. The hole array's `depth`
is the plate depth. Add future `get_<type>` recipes in this same authoring file;
shared CAD mechanics continue to live in the helper's component folders.

For a new type, declare `oobb_type: bracket` and add `get_bracket` to each enabled
backend. There is no central dispatch list. An explicit missing type function
fails clearly; it never silently calls `get_base`. `oobb_name` can be a variant
or legacy name; it does not override the type. Old definitions without
`oobb_type` retain name-based dispatch.

The two output controls are independent and default to true when omitted. Use
a boolean for run_scad and True, False or "working_scad" for run_solidcraft. False skips that part's route and preserves previous files.
Project-wide run switches still apply. `action_make_all.py` enables both
backends; direct calls to `working.main()` still require `run_solidcraft=True`
in the tested helper environment. The native adapter automatically uses this project's
`working_solidcraft.py` when it contains recipe functions. Older launchers with
no recipes retain their shared `working_scad.py` builder.

SCAD-only selection is stdlib-only through `working_cad.py` and
`components/build_policy/working.py`. Native generation requires the configured
SolidCraft helper environment, as before. Native verification includes an
internal SCAD render of the native recipe's expanded definition even when the
separate SCAD output route is disabled.

For persistent changes, edit population options/defaults or use the existing
manual part metadata workflow. Direct edits to generated `working.yaml` can be
overwritten by population. Population leaves non-CAD options without an
`oobb_type` alone.

## Maintenance and tests

The policy component is an unchanged distribution of the canonical
`software_cad_mcp_helper/components/build_policy/working.py`. Synchronize that
file into this template and existing migrated projects when changing the shared
contract. Keep backend recipes independently editable.

```powershell
python -m unittest discover -s tests -v
```

The tests cover populated type/flags, real SCAD dispatch before rendering,
new-type dispatch, initial recipe parity and independent native edits. Full
native verification is performed by the helper pipeline when generating parts.

## Independent component and variable migration

`working_solidcraft.py` declares `CAD_API = "solidcraft"` and imports
`from oobb_solidcraft import api as oobb`. Keep the separate SCAD recipe unchanged.
The native plate recipe and print-preparation helper no longer import OOBB builders
or `scad_help`. Hardware dimensions load from packaged YAML; 6,939 source keys and
275 bearing lookup records are included. Component defaults live in their own folders.

The helper documentation now has distinct screw, countersunk, socket-cap,
self-tapping, nut, bearing and wire pages. Full 98-component migration is still in
progress; consult `notes_for_ai/10_implementation_status.md` in the helper before
using an unverified option. General hulls, native laser, advanced gears/threads,
Gridfinity and raw SCAD remain outside the completed native coverage.


## Optional hardware rendering detail

`RENDER_DETAIL = False` in `working_solidcraft.py` keeps ordinary generation unchanged. Set it to True to add detail to positive screws, nuts and bearings. See [the rendering switch guide](SOLIDCRAFT_RENDER_DETAIL.md) for per-part overrides and supported details.


## Direct native generation without STL

Run `python working_solidcraft.py` to build every populated, enabled part. `EXPORT_STL = False` is the default; add `--stl` to opt in. `--filter` and `--modes` select a smaller test. The script uses the helper Python from `solidcraft/config.json` and publishes verified outputs into each part folder. Interrupted writer locks recover automatically when their owner is confirmed dead.


## Files appear as each native build completes

Each verified part/mode is copied into `parts/<part-id>/` immediately, before the next build starts. The console prints `Published ...` with the destination, then reports success. Files no longer wait for the entire batch to finish. The live progress index is `build/solidcraft/runs/latest_run.json`; failed publication is reported as a failed result.

## Copied assemblies and overlapping screw holes

SolidCraft generation preserves component intent in copied print layouts. The
shared helper removes a grid bore only when it proves that another screw
cutter covers it throughout the material bounds; source requests remain in the
saved definition and the proof is listed in `plan.json` under
`boolean_optimizations`. This is recalculated on every build from
`working_scad.py`.

Arrays starting or ending inside material use fully constrained circle sketches
and finite, flat-bottom extrusion cuts, with at most 32 circles per cut for
large arrays. Their batches share radius and depth parameters. Concentric bores share a maximum-radius
expression only at their common centres. Countersunk screws with nut pockets
use a continuous head/shaft profile, with nut pockets and print bridges cut
first. Disconnected print regions finish their local cuts before they are combined
in the output file. These changes avoid repeated coincident Boolean cuts
without changing authored sizes or accepting displaced-tool warnings.

Make geometry changes in the recipe and regenerate, especially when changing
relationships between overlapping cutters. Native parameter edits do not
recalculate the compiler's geometric coverage proofs.

Normal STL export also checks that the mesh is closed and consistently wound.
If SolidCraft's STL has open triangles, the helper meshes its valid native STEP
boundary at 0.01 mm chord tolerance, checks the result, and records the method
and STEP hash in the build measurements. The original native STL stays in the
attempt folder as evidence. This converts the completed CAD boundary; geometry
and unsupported-model errors still fail before export.

For cylinder print layouts, a covering Z slice is expressed directly through
the cylinder depths when it is provably equivalent. This avoids a final large
Boolean cut through an already perforated model.

