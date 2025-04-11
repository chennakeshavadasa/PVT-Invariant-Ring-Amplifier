v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 4 980 -485 1880 -480 {}
B 4 980 -490 1880 -485 {}
B 4 980 -130 1880 -125 {}
B 4 980 -125 1880 -120 {}
B 4 380 -485 1280 -480 {}
B 4 380 -490 1280 -485 {}
B 4 380 -125 1280 -120 {}
B 4 380 -130 1280 -125 {}
B 4 140 -485 1040 -480 {}
B 4 140 -490 1040 -485 {}
B 4 210 -125 1110 -120 {}
B 4 210 -130 1110 -125 {}
B 4 1385 -485 2285 -480 {}
B 4 1385 -490 2285 -485 {}
B 4 1385 -125 2285 -120 {}
B 4 1385 -130 2285 -125 {}
B 4 140 -125 1040 -120 {}
B 4 140 -130 1040 -125 {}
T {FULLY DIFFERENTIAL RING AMPLIFIER } 900 -570 0 0 0.75 0.75 {}
N 1010 -335 1100 -335 {lab=minus}
N 960 -405 1010 -405 {lab=minus}
N 1010 -275 1100 -275 {lab=plus}
N 960 -205 1010 -205 {lab=plus}
N 1010 -405 1010 -335 {lab=minus}
N 250 -420 310 -420 {lab=#net1}
N 210 -485 210 -420 {lab=VDD}
N 625 -485 880 -485 {lab=VDD}
N 250 -210 310 -210 {lab=#net2}
N 210 -310 210 -240 {lab=VoutP}
N 70 -310 210 -310 {lab=VoutP}
N 210 -390 210 -310 {lab=VoutP}
N 1210 -485 1540 -485 {lab=VDD}
N 1210 -125 1540 -125 {lab=GND}
N 140 -485 210 -485 {lab=VDD}
N 210 -125 625 -125 {lab=GND}
N 625 -125 880 -125 {lab=GND}
N 1210 -205 1210 -125 {lab=GND}
N 1210 -485 1210 -405 {lab=VDD}
N 880 -485 1210 -485 {lab=VDD}
N 880 -485 880 -365 {lab=VDD}
N 880 -125 1210 -125 {lab=GND}
N 880 -245 880 -125 {lab=GND}
N 1540 -205 1540 -125 {lab=GND}
N 1540 -485 1540 -420 {lab=VDD}
N 1320 -345 1675 -345 {lab=#net3}
N 1675 -345 1675 -330 {lab=#net3}
N 1675 -330 1760 -330 {lab=#net3}
N 1880 -485 1880 -440 {lab=VDD}
N 1540 -485 1880 -485 {lab=VDD}
N 1540 -125 1880 -125 {lab=GND}
N 1880 -185 1880 -125 {lab=GND}
N 745 -250 1760 -250 {lab=#net4}
N 1010 -275 1010 -205 {lab=plus}
N 785 -330 785 -160 {lab=#net5}
N 745 -330 785 -330 {lab=#net5}
N 625 -485 625 -440 {lab=VDD}
N 625 -185 625 -125 {lab=GND}
N 2115 -415 2175 -415 {lab=#net6}
N 2215 -485 2215 -415 {lab=VDD}
N 2115 -205 2175 -205 {lab=#net7}
N 2215 -305 2215 -235 {lab=VoutN}
N 2215 -305 2355 -305 {lab=VoutN}
N 2215 -385 2215 -305 {lab=VoutN}
N 310 -355 505 -355 {lab=#net1}
N 310 -420 310 -355 {lab=#net1}
N 310 -295 505 -295 {lab=#net2}
N 310 -295 310 -210 {lab=#net2}
N 210 -485 625 -485 {lab=VDD}
N 140 -125 210 -125 {lab=GND}
N 1880 -485 2215 -485 {lab=VDD}
N 2000 -355 2115 -355 {lab=#net6}
N 2115 -415 2115 -355 {lab=#net6}
N 2000 -295 2115 -295 {lab=#net7}
N 2115 -295 2115 -205 {lab=#net7}
N 1880 -125 2215 -125 {lab=GND}
N 2215 -205 2215 -125 {lab=GND}
N 210 -210 210 -125 {lab=GND}
N 1040 -325 1340 -325 {lab=#net8}
N 1340 -325 1340 -305 {lab=#net8}
N 1340 -305 1440 -305 {lab=#net8}
N 1040 -305 1100 -305 {lab=#net8}
N 1320 -270 1320 -160 {lab=#net5}
N 785 -160 1320 -160 {lab=#net5}
N 745 -375 1640 -375 {lab=#net9}
N 1640 -400 1640 -375 {lab=#net9}
N 1640 -400 1660 -400 {lab=#net9}
N 1660 -400 1660 -375 {lab=#net9}
N 1660 -375 1760 -375 {lab=#net9}
N 1040 -325 1040 -305 {lab=#net8}
N 960 -305 1040 -305 {lab=#net8}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG2.sym} 1540 -315 0 0 {name=x2}
C {iopin.sym} 140 -125 0 1 {name=p1 lab=GND}
C {iopin.sym} 140 -485 0 1 {name=p2 lab=VDD}
C {iopin.sym} 960 -205 0 1 {name=p3 lab=plus}
C {iopin.sym} 960 -405 0 1 {name=p4 lab=minus}
C {sg13g2_pr/sg13_hv_nmos.sym} 230 -210 0 1 {name=M1
l=1u
w=2.3u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 230 -420 0 1 {name=M4
l=0.5u
w=4.5u
ng=1
m=4
model=sg13_hv_pmos
spiceprefix=X
}
C {iopin.sym} 70 -310 0 1 {name=p6 lab=VoutP}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG1-FD.sym} 900 -305 0 0 {name=x1}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG1-CM.sym} 600 -305 0 0 {name=x4}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG2_Replica.sym} 940 -310 0 0 {name=x5}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG2.sym} 965 -315 0 1 {name=x6}
C {sg13g2_pr/sg13_hv_nmos.sym} 2195 -205 0 0 {name=M5
l=1u
w=2.3u
ng=1
m=4
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 2195 -415 0 0 {name=M6
l=0.5u
w=4.5u
ng=1
m=4
model=sg13_hv_pmos
spiceprefix=X
}
C {iopin.sym} 2355 -305 0 0 {name=p9 lab=VoutN}
