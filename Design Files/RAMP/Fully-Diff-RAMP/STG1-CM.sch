v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 4 -335 -605 -165 -595 {}
B 4 -165 -605 5 -595 {}
B 4 -110 -605 60 -595 {}
B 4 -110 -5 60 5 {}
B 4 -280 -5 -110 5 {}
B 4 -340 -5 -170 5 {}
B 4 -340 -605 -170 -595 {}
N -190 -140 -190 0 {lab=GND}
N -190 -450 -190 -340 {lab=#net1}
N -190 -310 -150 -310 {lab=VDD}
N -150 -480 -150 -310 {lab=VDD}
N -190 -480 -150 -480 {lab=VDD}
N -190 -220 -190 -170 {lab=V_CM1}
N -280 -140 -230 -140 {lab=V_CM1}
N -280 -220 -280 -140 {lab=V_CM1}
N -280 -310 -230 -310 {lab=V_CM1}
N -280 -220 -190 -220 {lab=V_CM1}
N -280 -310 -280 -220 {lab=V_CM1}
N -190 -270 -190 -220 {lab=V_CM1}
N 60 -270 60 -170 {lab=#net2}
N -40 -270 20 -270 {lab=V_CM1}
N -40 -440 20 -440 {lab=V_CM1}
N -40 -350 -40 -270 {lab=V_CM1}
N 60 -140 60 0 {lab=GND}
N 60 -350 60 -300 {lab=V_CM1}
N -40 -350 60 -350 {lab=V_CM1}
N -40 -440 -40 -350 {lab=V_CM1}
N -190 -270 -40 -270 {lab=V_CM1}
N -190 -280 -190 -270 {lab=V_CM1}
N -190 0 60 0 {lab=GND}
N -85 -140 20 -140 {lab=VDD}
N -340 -480 -340 0 {lab=GND}
N -85 -600 60 -600 {lab=VDD}
N 60 -600 60 -440 {lab=VDD}
N -190 -600 -190 -480 {lab=VDD}
N -340 -480 -230 -480 {lab=GND}
N -85 -600 -85 -140 {lab=VDD}
N -190 -600 -85 -600 {lab=VDD}
N -340 0 -190 0 {lab=GND}
N -340 -600 -190 -600 {lab=VDD}
N 60 -355 220 -355 {lab=V_CM1}
N 60 -410 60 -355 {lab=V_CM1}
N 60 -355 60 -350 {lab=V_CM1}
C {sg13g2_pr/sg13_lv_nmos.sym} -210 -140 0 0 {name=M9
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} -210 -310 0 0 {name=M10
l=0.13u
w=0.15u
ng=1
m=3
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} -210 -480 0 0 {name=M11
l=0.13u
w=0.15u
ng=1
m=5
model=sg13_lv_pmos
spiceprefix=X
}
C {ngspice_probe.sym} -190 -220 0 0 {name=r10}
C {sg13g2_pr/sg13_lv_nmos.sym} 40 -270 0 0 {name=M12
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 40 -440 0 0 {name=M13
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 40 -140 0 0 {name=M14
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {ipin.sym} -340 -600 0 0 {name=p1 lab=VDD}
C {ipin.sym} -340 0 0 0 {name=p2 lab=GND}
C {opin.sym} 220 -355 0 0 {name=p3 lab=V_CM1}
