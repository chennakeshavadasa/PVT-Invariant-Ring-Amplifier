v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 4 160 -480 1060 -475 {}
B 4 160 -485 1060 -480 {}
B 4 160 -125 1060 -120 {}
B 4 160 -120 1060 -115 {}
T {SINGLE ENDED RING AMPLIFIER } 310 -550 0 0 0.75 0.75 {}
N 480 -300 620 -300 {lab=#net1}
N 380 -480 380 -360 {lab=VDD}
N 380 -480 710 -480 {lab=VDD}
N 710 -480 710 -380 {lab=VDD}
N 800 -320 960 -320 {lab=#net2}
N 960 -410 960 -320 {lab=#net2}
N 960 -410 1020 -410 {lab=#net2}
N 1060 -480 1060 -410 {lab=VDD}
N 710 -480 1060 -480 {lab=VDD}
N 800 -280 960 -280 {lab=#net3}
N 960 -280 960 -200 {lab=#net3}
N 960 -200 1020 -200 {lab=#net3}
N 1060 -300 1060 -230 {lab=Vout}
N 1060 -200 1060 -120 {lab=GND}
N 230 -320 320 -320 {lab=minus}
N 230 -400 230 -320 {lab=minus}
N 180 -400 230 -400 {lab=minus}
N 230 -280 320 -280 {lab=plus}
N 230 -280 230 -200 {lab=plus}
N 180 -200 230 -200 {lab=plus}
N 380 -240 380 -120 {lab=GND}
N 710 -120 1060 -120 {lab=GND}
N 710 -220 710 -120 {lab=GND}
N 380 -120 710 -120 {lab=GND}
N 160 -480 380 -480 {lab=VDD}
N 160 -120 380 -120 {lab=GND}
N 1060 -300 1200 -300 {lab=Vout}
N 1060 -380 1060 -300 {lab=Vout}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG1.sym} 120 -300 0 0 {name=x1}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG2.sym} 420 -300 0 0 {name=x2}
C {sg13g2_pr/sg13_hv_nmos.sym} 1040 -200 0 0 {name=M1
l=1u
w=2.3u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 1040 -410 0 0 {name=M2
l=0.5u
w=4.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {iopin.sym} 160 -120 0 1 {name=p1 lab=GND}
C {iopin.sym} 160 -480 0 1 {name=p2 lab=VDD}
C {iopin.sym} 180 -200 0 1 {name=p3 lab=plus}
C {iopin.sym} 180 -400 0 1 {name=p4 lab=minus}
C {iopin.sym} 1200 -300 0 0 {name=p5 lab=Vout}
C {title.sym} 160 -30 0 0 {name=l1 author="Nithin Purushothama"}
