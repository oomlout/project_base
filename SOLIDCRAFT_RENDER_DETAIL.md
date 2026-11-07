# Optional rendering detail

Near the top of working_solidcraft.py:

```python
RENDER_DETAIL = False
```

Set it to True for detailed positive screws, nuts and bearings. Override per part with `oobb_details.render_detail: true` (YAML), or per request with `p3["render_detail"] = True` / `False` before `oobb.append_full(thing, **p3)`.

The same make-all and SolidCraft-only commands pick up this switch. Bare plates and negative hardware pockets keep their existing geometry. The SCAD recipe is unchanged. Screw depth must be explicit. Cosmetic screw grooves are rings, not true helical threads; bearings use a shielded appearance with recessed race detail. Cutter-specific access/clearance options are not part of the positive display model.

Implementation, editable YAML proportions, examples and boundaries live in the helper's `components/render_hardware` folder. Migration decisions are in `notes_for_ai/11_render_detail.md`.
