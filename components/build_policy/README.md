# Build policy and type dispatch

This folder owns the standard-library-only policy distributed with the template.
`working_cad.py` is its public facade. The canonical source is
`software_cad_mcp_helper/components/build_policy/working.py`; keep copies in
sync rather than changing the template's dispatch policy independently.

See [CAD_BUILDING.md](../../CAD_BUILDING.md) for populate examples, independent
output flags and `oobb_type` → `get_<type>` dispatch. Backend geometry recipes
remain separately editable in the two `working_*.py` files.

Coverage: [test_cad_contract.py](../../tests/test_cad_contract.py).
