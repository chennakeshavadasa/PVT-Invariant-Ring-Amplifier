v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 4 355 -705 525 -695 {}
B 4 525 -705 695 -695 {}
B 4 580 -705 750 -695 {}
B 4 580 -105 750 -95 {}
B 4 410 -105 580 -95 {}
B 4 350 -105 520 -95 {}
B 4 350 -705 520 -695 {}
T {RING AMPLIFIER STAGE 1 COMMON MODE} 130 -780 0 0 0.75 0.75 {}
N 500 -240 500 -100 {lab=GND}
N 500 -550 500 -440 {lab=#net1}
N 500 -410 540 -410 {lab=VDD}
N 540 -580 540 -410 {lab=VDD}
N 500 -580 540 -580 {lab=VDD}
N 500 -320 500 -270 {lab=V_CM1}
N 410 -240 460 -240 {lab=V_CM1}
N 410 -320 410 -240 {lab=V_CM1}
N 410 -410 460 -410 {lab=V_CM1}
N 410 -320 500 -320 {lab=V_CM1}
N 410 -410 410 -320 {lab=V_CM1}
N 500 -370 500 -320 {lab=V_CM1}
N 750 -370 750 -270 {lab=#net2}
N 650 -370 710 -370 {lab=V_CM1}
N 650 -540 710 -540 {lab=V_CM1}
N 650 -450 650 -370 {lab=V_CM1}
N 750 -240 750 -100 {lab=GND}
N 750 -450 750 -400 {lab=V_CM1}
N 650 -450 750 -450 {lab=V_CM1}
N 650 -540 650 -450 {lab=V_CM1}
N 500 -370 650 -370 {lab=V_CM1}
N 500 -380 500 -370 {lab=V_CM1}
N 500 -100 750 -100 {lab=GND}
N 605 -240 710 -240 {lab=VDD}
N 350 -580 350 -100 {lab=GND}
N 605 -700 750 -700 {lab=VDD}
N 750 -700 750 -540 {lab=VDD}
N 500 -700 500 -580 {lab=VDD}
N 350 -580 460 -580 {lab=GND}
N 605 -700 605 -240 {lab=VDD}
N 500 -700 605 -700 {lab=VDD}
N 350 -100 500 -100 {lab=GND}
N 350 -700 500 -700 {lab=VDD}
N 750 -455 910 -455 {lab=V_CM1}
N 750 -510 750 -455 {lab=V_CM1}
N 750 -455 750 -450 {lab=V_CM1}
C {sg13g2_pr/sg13_lv_nmos.sym} 480 -240 0 0 {name=M9
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 480 -410 0 0 {name=M10
l=0.13u
w=0.15u
ng=1
m=3
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 480 -580 0 0 {name=M11
l=0.13u
w=0.15u
ng=1
m=5
model=sg13_lv_pmos
spiceprefix=X
}
C {ngspice_probe.sym} 500 -320 0 0 {name=r10}
C {sg13g2_pr/sg13_lv_nmos.sym} 730 -370 0 0 {name=M12
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 730 -540 0 0 {name=M13
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 730 -240 0 0 {name=M14
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {ipin.sym} 350 -700 0 0 {name=p1 lab=VDD}
C {ipin.sym} 350 -100 0 0 {name=p2 lab=GND}
C {opin.sym} 910 -455 0 0 {name=p3 lab=V_CM1}
C {ngspice_probe.sym} 500 -480 0 0 {name=r1}
C {ngspice_probe.sym} 750 -300 0 0 {name=r2}
C {title.sym} 160 -30 0 0 {name=l1 author="Nithin Purushothama"}
