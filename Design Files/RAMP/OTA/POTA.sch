v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 490 -520 490 -490 {lab=#net1}
N 620 -520 760 -520 {lab=#net1}
N 760 -520 760 -490 {lab=#net1}
N 490 -520 620 -520 {lab=#net1}
N 570 -460 760 -460 {lab=VDD}
N 800 -460 890 -460 {lab=MINUS}
N 490 -360 490 -290 {lab=#net2}
N 760 -360 760 -290 {lab=Vout}
N 620 -260 720 -260 {lab=#net2}
N 490 -360 620 -360 {lab=#net2}
N 490 -430 490 -360 {lab=#net2}
N 620 -360 620 -260 {lab=#net2}
N 530 -260 620 -260 {lab=#net2}
N 490 -140 760 -140 {lab=GND}
N 490 -260 490 -140 {lab=GND}
N 760 -260 760 -140 {lab=GND}
N 570 -680 620 -680 {lab=VDD}
N 340 -460 450 -460 {lab=PLUS}
N 620 -580 620 -520 {lab=#net1}
N 620 -680 620 -640 {lab=VDD}
N 570 -680 570 -460 {lab=VDD}
N 490 -460 570 -460 {lab=VDD}
N 330 -680 570 -680 {lab=VDD}
N 350 -140 490 -140 {lab=GND}
N 760 -360 900 -360 {lab=Vout}
N 760 -430 760 -360 {lab=Vout}
C {sg13g2_pr/sg13_lv_pmos.sym} 470 -460 0 0 {name=M2
l=0.5u
w=1.2u
ng=1
m=2
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 740 -260 0 0 {name=M4
l=2u
w=0.5u
ng=1
m=2
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 510 -260 0 1 {name=M5
l=2u
w=0.5u
ng=1
m=2
model=sg13_hv_nmos
spiceprefix=X
}
C {isource.sym} 620 -610 0 0 {name=I1 value=2u}
C {ngspice_probe.sym} 495 -360 0 0 {name=r1}
C {ngspice_probe.sym} 620 -520 0 0 {name=r2}
C {ngspice_probe.sym} 760 -360 0 0 {name=r6}
C {ipin.sym} 330 -680 0 0 {name=p2 lab=VDD}
C {ipin.sym} 350 -140 0 0 {name=p3 lab=GND}
C {ipin.sym} 340 -460 0 0 {name=p1 lab=PLUS}
C {ipin.sym} 890 -460 0 1 {name=p4 lab=MINUS}
C {opin.sym} 900 -360 0 0 {name=p5 lab=Vout}
C {sg13g2_pr/sg13_lv_pmos.sym} 780 -460 0 1 {name=M1
l=0.5u
w=1.2u
ng=1
m=2
model=sg13_lv_pmos
spiceprefix=X
}
