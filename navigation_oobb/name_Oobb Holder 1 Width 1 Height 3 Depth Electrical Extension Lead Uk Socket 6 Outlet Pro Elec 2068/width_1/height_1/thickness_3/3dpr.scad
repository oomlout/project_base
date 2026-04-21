$fn = 50;

difference() {
	union() {
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						#translate(v = [0, 0, -3.0]) {
							cylinder(h = 3, r = 1.5);
						}
						#translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						#translate(v = [0, 0, -3.0]) {
							cylinder(h = 3, r = 1.8);
						}
						#translate(v = [0, 0, -3.0]) {
							cylinder(h = 3, r = 1.5);
						}
					}
					union();
				}
			}
		}
		cylinder(h = 3, r = 7.0);
	}
	union() {
		translate(v = [0.0, 0.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
	}
}
