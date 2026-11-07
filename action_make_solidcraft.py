"""Populate the parts and generate verified SolidCraft outputs only."""


def main(**kwargs):
    kwargs["run_oomp_populate"] = True
    kwargs["run_oomp"] = True
    kwargs["run_action"] = False
    kwargs["run_scad"] = False
    # True, False, or "working_scad"; use the same switch as make-all.
    kwargs.setdefault("run_solidcraft", "working_scad")
    kwargs["run_svg"] = False
    # SCAD stays off; native STL is enabled by export_stl below.
    kwargs["generate_stl"] = False

    # Rebuild native CAD and all selected exports from the recipe every run.
    kwargs["export_extras"] = kwargs.get("export_extras", True)  # STEP and PNG previews.
    kwargs["export_stl"] = kwargs.get("export_stl", True)
    kwargs["verify_solidcraft"] = kwargs.get("verify_solidcraft", False)

    import working
    working.run(**kwargs)


if __name__ == "__main__":
    main()
