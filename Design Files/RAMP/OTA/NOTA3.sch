v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 310 -420 310 -360 {lab=#net1}
N 470 -360 620 -360 {lab=#net1}
N 620 -420 620 -360 {lab=#net1}
N 520 -450 620 -450 {lab=gnd}
N 460 -670 580 -670 {lab=#net2}
N 310 -600 310 -480 {lab=#net2}
N 470 -360 470 -320 {lab=#net1}
N 310 -360 470 -360 {lab=#net1}
N 470 -260 470 -220 {lab=gnd}
N 460 -670 460 -600 {lab=#net2}
N 350 -670 460 -670 {lab=#net2}
N 310 -600 460 -600 {lab=#net2}
N 310 -640 310 -600 {lab=#net2}
N 620 -760 620 -670 {lab=VDD}
N 310 -760 620 -760 {lab=VDD}
N 310 -760 310 -670 {lab=VDD}
N 620 -560 620 -480 {lab=Vout}
N 200 -450 270 -450 {lab=plus}
N 660 -450 790 -450 {lab=minus}
N 240 -760 310 -760 {lab=VDD}
N 520 -450 520 -220 {lab=gnd}
N 310 -450 520 -450 {lab=gnd}
N 470 -220 520 -220 {lab=gnd}
N 200 -220 470 -220 {lab=gnd}
N 620 -560 850 -560 {lab=Vout}
N 620 -640 620 -560 {lab=Vout}
C {sg13g2_pr/sg13_hv_nmos.sym} 290 -450 0 0 {name=M1
l=1.5u
w=3.25u
ng=1
m=2
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 640 -450 0 1 {name=M2
l=1.5u
w=3.25u
ng=1
m=2
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 600 -670 0 0 {name=M3
l=2u
w=2u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 330 -670 0 1 {name=M4
l=2u
w=2u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {isource.sym} 470 -290 0 0 {name=I0 value=2u}
C {ipin.sym} 200 -450 0 0 {name=p2 lab=plus}
C {ipin.sym} 790 -450 0 1 {name=p3 lab=minus}
C {ipin.sym} 240 -760 0 0 {name=p1 lab=VDD}
C {ipin.sym} 200 -220 0 0 {name=p4 lab=gnd}
C {opin.sym} 850 -560 0 0 {name=p5 lab=Vout}
C {ngspice_probe.sym} 470 -360 0 0 {name=r1}
