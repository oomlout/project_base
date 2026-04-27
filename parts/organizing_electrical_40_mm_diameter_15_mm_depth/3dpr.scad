$fn = 50;

difference() {
	union() {
		translate(v = [0, 0, 3.0]) {
			cylinder(h = 12, r = 19.75);
		}
		cylinder(h = 3, r1 = 19.25, r2 = 19.75);
		translate(v = [0, 0, 13.0]) {
			cylinder(h = 2, r1 = 25.0, r2 = 22.5);
		}
	}
	union() {
		cylinder(h = 15, r = 19.25);
	}
}
