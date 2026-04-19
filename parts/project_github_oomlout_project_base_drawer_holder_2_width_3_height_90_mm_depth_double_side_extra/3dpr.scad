$fn = 50;
use <C:/gh/oomlout_oobb_version_5/_raw_scad_cache/gridfinity_base_tile_raw_480902361bf8bab1.scad>


difference() {
	union() {
		translate(v = [-42.0000000000, -63.0000000000, 0]) {
			cube(size = [87, 126, 1.5000000000]);
		}
		translate(v = [-42.0000000000, 61.0000000000, 0]) {
			cube(size = [87, 2, 90]);
		}
		translate(v = [43.0000000000, -63.0000000000, 0]) {
			cube(size = [2, 126, 90]);
		}
		translate(v = [-42.0000000000, -63.0000000000, 0]) {
			cube(size = [2, 126, 90]);
		}
		translate(v = [-21.0000000000, -42.0000000000, -4.6000000000]) {
			gridfinity_base_tile_raw(distancex = 0, distancey = 0, fitx = 0, fity = 0);
		}
		translate(v = [-21.0000000000, 0.0000000000, -4.6000000000]) {
			gridfinity_base_tile_raw(distancex = 0, distancey = 0, fitx = 0, fity = 0);
		}
		translate(v = [-21.0000000000, 42.0000000000, -4.6000000000]) {
			gridfinity_base_tile_raw(distancex = 0, distancey = 0, fitx = 0, fity = 0);
		}
		translate(v = [21.0000000000, -42.0000000000, -4.6000000000]) {
			gridfinity_base_tile_raw(distancex = 0, distancey = 0, fitx = 0, fity = 0);
		}
		translate(v = [21.0000000000, 0.0000000000, -4.6000000000]) {
			gridfinity_base_tile_raw(distancex = 0, distancey = 0, fitx = 0, fity = 0);
		}
		translate(v = [21.0000000000, 42.0000000000, -4.6000000000]) {
			gridfinity_base_tile_raw(distancex = 0, distancey = 0, fitx = 0, fity = 0);
		}
	}
	union();
}