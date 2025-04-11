v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 370 -210 370 -160 {lab=#net1}
N 500 -160 630 -160 {lab=#net1}
N 630 -210 630 -160 {lab=#net1}
N 560 -240 630 -240 {lab=GND}
N 500 -160 500 -100 {lab=#net1}
N 370 -160 500 -160 {lab=#net1}
N 500 -40 500 0 {lab=GND}
N 560 -240 560 0 {lab=GND}
N 370 -240 560 -240 {lab=GND}
N 500 0 560 0 {lab=GND}
N 370 -370 370 -270 {lab=#net2}
N 450 -440 590 -440 {lab=#net2}
N 370 -370 450 -370 {lab=#net2}
N 370 -410 370 -370 {lab=#net2}
N 450 -440 450 -370 {lab=#net2}
N 410 -440 450 -440 {lab=#net2}
N 370 -560 370 -440 {lab=VDD}
N 370 -560 630 -560 {lab=VDD}
N 630 -560 630 -440 {lab=VDD}
N 630 -340 630 -270 {lab=Vout}
N 670 -240 740 -240 {lab=MINUS}
N 250 -240 330 -240 {lab=PLUS}
N 150 -560 370 -560 {lab=VDD}
N 150 0 500 0 {lab=GND}
N 630 -340 840 -340 {lab=Vout}
N 630 -410 630 -340 {lab=Vout}
C {sg13g2_pr/sg13_hv_nmos.sym} 350 -240 0 0 {name=M1
l=1u
w=1.75u
ng=1
m=2
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 650 -240 0 1 {name=M2
l=1u
w=1.75u
ng=1
m=2
model=sg13_hv_nmos
spiceprefix=X
}
C {isource.sym} 500 -70 0 0 {name=I0 value=2u}
C {gnd.sym} 500 0 0 0 {name=l1 lab=GND}
C {sg13g2_pr/sg13_hv_pmos.sym} 610 -440 0 0 {name=M3
l=0.75u
w=0.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 390 -440 0 1 {name=M4
l=0.75u
w=0.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {ngspice_probe.sym} 370 -320 0 0 {name=r1}
C {ngspice_probe.sym} 500 -160 0 1 {name=r6}
C {ipin.sym} 150 -560 0 0 {name=p2 lab=VDD}
C {ipin.sym} 150 0 0 0 {name=p3 lab=GND}
C {ipin.sym} 250 -240 0 0 {name=p4 lab=PLUS}
C {ipin.sym} 740 -240 0 1 {name=p5 lab=MINUS}
C {opin.sym} 840 -340 0 0 {name=p1 lab=Vout}
