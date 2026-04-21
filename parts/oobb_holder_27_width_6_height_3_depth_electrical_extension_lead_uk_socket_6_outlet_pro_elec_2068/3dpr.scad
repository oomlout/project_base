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
		hull() {
			translate(v = [-197.0, 39.5, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [197.0, 39.5, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [-197.0, -39.5, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [197.0, -39.5, 0]) {
				cylinder(h = 3, r = 5);
			}
		}
	}
	union() {
		translate(v = [-195.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-195.0, -22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-195.0, -7.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-195.0, 7.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-195.0, 22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-195.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-180.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-180.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-165.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-165.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-150.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-150.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-135.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-135.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-120.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-120.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-105.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-105.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-90.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-90.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-75.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-75.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-60.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-60.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-45.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-45.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-30.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-30.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-15.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-15.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [0.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [0.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [15.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [15.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [30.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [30.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [45.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [45.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [60.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [60.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [75.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [75.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [90.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [90.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [105.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [105.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [120.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [120.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [135.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [135.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [150.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [150.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [165.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [165.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [180.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [180.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [195.0, -37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [195.0, -22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [195.0, -7.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [195.0, 7.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [195.0, 22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [195.0, 37.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
	}
}
