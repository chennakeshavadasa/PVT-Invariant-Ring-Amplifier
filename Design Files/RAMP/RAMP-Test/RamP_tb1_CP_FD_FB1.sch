v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 380 -150 380 -130 {lab=GND}
N 380 -250 380 -210 {lab=VICM}
N 950 -350 950 -325 {lab=GND}
N 950 -430 950 -410 {lab=VDD}
N 560 -420 560 -390 {lab=VDD}
N 560 -170 560 -150 {lab=GND}
N 740 -150 740 -130 {lab=GND}
N 380 -310 460 -310 {lab=Vout}
N 380 -250 460 -250 {lab=VICM}
N 380 -480 740 -480 {lab=Vout}
N 380 -480 380 -310 {lab=Vout}
N 740 -240 740 -210 {lab=#net1}
N 680 -240 740 -240 {lab=#net1}
N 830 -230 830 -210 {lab=GND}
N 830 -320 830 -290 {lab=Vout}
N 740 -320 830 -320 {lab=Vout}
N 740 -480 740 -320 {lab=Vout}
N 680 -320 740 -320 {lab=Vout}
C {vsource.sym} 380 -180 0 0 {name=V1 value=0.825 savecurrent=false}
C {vsource.sym} 950 -380 0 0 {name=V2 value=1.65 savecurrent=false}
C {vdd.sym} 950 -430 0 0 {name=l1 lab=VDD}
C {gnd.sym} 950 -325 0 0 {name=l2 lab=GND}
C {gnd.sym} 380 -130 0 0 {name=l3 lab=GND}
C {vdd.sym} 560 -420 0 0 {name=l4 lab=VDD}
C {gnd.sym} 560 -150 0 0 {name=l5 lab=GND}
C {capa.sym} 740 -180 0 0 {name=C1
m=1
value=50p
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 740 -130 0 0 {name=l6 lab=GND}
C {devices/launcher.sym} 490 -90 0 0 {name=h1
descr="load op & annotate" 
tclcommand="xschem raw_read $netlist_dir/RamP_tb1_CP_FB1.raw; set show_hidden_texts 1; xschem annotate_op"}
C {ngspice_probe.sym} 380 -310 0 1 {name=r1}
C {code_shown.sym} 0 -190 0 0 {
name=TT_MODELS
only_toplevel=true
value="
** IHP models
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
"
spice_ignore=false
      }
C {lab_pin.sym} 380 -250 0 0 {name=p2 sig_type=std_logic lab=VICM}
C {devices/code_shown.sym} 0 -510 0 0 {name="NGSPICE" only_toplevel=true 
value="
.option wnflag=1
.option savecurrents
.temp 27
.control
save all
write RamP_tb1_CP_FD_FB1.raw
set appendwrite 
op
write RamP_tb1_CP_FD_FB1.raw
**dc temp -50 150 1
tran 1m 10m 1m
**ac dec 20 1 1e8
**plot vdb(vout2) vdb(vout1)
.endc
"}
C {lab_pin.sym} 830 -320 0 1 {name=p1 sig_type=std_logic lab=Vout}
C {/foss/designs/RAMP/Fully-Diff-RAMP/RAMP-FD.sym} 200 -280 2 1 {name=x2}
C {capa.sym} 830 -260 0 0 {name=C2
m=1
value=50p
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 830 -210 0 0 {name=l8 lab=GND}
