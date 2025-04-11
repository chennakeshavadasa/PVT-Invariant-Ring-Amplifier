v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 670 -240 760 -240 {lab=GND}
N 510 -210 510 -160 {lab=#net1}
N 630 -160 760 -160 {lab=#net1}
N 760 -210 760 -160 {lab=#net1}
N 630 -160 630 -130 {lab=#net1}
N 510 -160 630 -160 {lab=#net1}
N 630 -70 630 -40 {lab=GND}
N 610 -470 720 -470 {lab=#net2}
N 510 -400 510 -270 {lab=#net2}
N 510 -400 610 -400 {lab=#net2}
N 510 -440 510 -400 {lab=#net2}
N 610 -470 610 -400 {lab=#net2}
N 550 -470 610 -470 {lab=#net2}
N 760 -560 760 -470 {lab=VDD}
N 510 -560 760 -560 {lab=VDD}
N 510 -560 510 -470 {lab=VDD}
N 760 -360 760 -270 {lab=Vout}
N 320 -560 510 -560 {lab=VDD}
N 630 -40 670 -40 {lab=GND}
N 670 -240 670 -40 {lab=GND}
N 510 -240 670 -240 {lab=GND}
N 320 -40 630 -40 {lab=GND}
N 380 -240 470 -240 {lab=PLUS}
N 800 -240 920 -240 {lab=MINUS}
N 760 -360 980 -360 {lab=Vout}
N 760 -440 760 -360 {lab=Vout}
C {sg13g2_pr/sg13_hv_nmos.sym} 490 -240 0 0 {name=M1
l=1.5u
w=3.5u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 780 -240 0 1 {name=M2
l=1.5u
w=3.5u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {isource.sym} 630 -100 0 0 {name=I0 value=2u}
C {sg13g2_pr/sg13_hv_pmos.sym} 740 -470 0 0 {name=M3
l=1u
w=0.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 530 -470 0 1 {name=M4
l=1u
w=0.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {ngspice_probe.sym} 630 -160 0 0 {name=r1}
C {ngspice_probe.sym} 610 -400 0 0 {name=r2}
C {ipin.sym} 320 -560 0 0 {name=p1 lab=VDD}
C {ipin.sym} 320 -40 0 0 {name=p2 lab=GND}
C {ipin.sym} 380 -240 0 0 {name=p3 lab=PLUS}
C {ipin.sym} 920 -240 0 1 {name=p4 lab=MINUS}
C {opin.sym} 980 -360 0 0 {name=p5 lab=Vout}
