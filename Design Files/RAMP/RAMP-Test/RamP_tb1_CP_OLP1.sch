v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 810 -310 890 -310 {lab=vout}
N 530 -280 610 -280 {lab=VICM}
N 530 -180 530 -160 {lab=GND}
N 530 -280 530 -240 {lab=VICM}
N 310 -270 310 -245 {lab=GND}
N 310 -350 310 -330 {lab=VDD}
N 690 -410 690 -380 {lab=VDD}
N 690 -240 690 -220 {lab=GND}
N 890 -200 890 -180 {lab=GND}
N 890 -310 890 -260 {lab=vout}
N 400 -240 400 -220 {lab=GND}
N 400 -340 400 -300 {lab=#net1}
N 400 -340 610 -340 {lab=#net1}
C {/foss/designs/RAMP/Fully-Diff-RAMP/RAMP.sym} 430 -310 2 1 {name=x1}
C {vsource.sym} 530 -210 0 0 {name=V1 value="dc 0.825 ac 1" savecurrent=false}
C {vsource.sym} 310 -300 0 0 {name=V2 value=1.65 savecurrent=false}
C {vdd.sym} 310 -350 0 0 {name=l1 lab=VDD}
C {gnd.sym} 310 -245 0 0 {name=l2 lab=GND}
C {gnd.sym} 530 -160 0 0 {name=l3 lab=GND}
C {vdd.sym} 690 -410 0 0 {name=l4 lab=VDD}
C {gnd.sym} 690 -220 0 0 {name=l5 lab=GND}
C {capa.sym} 890 -230 0 0 {name=C1
m=1
value=50p
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 890 -180 0 0 {name=l6 lab=GND}
C {title.sym} 160 -30 0 0 {name=l7 author="Nithin Purushothama"}
C {devices/launcher.sym} 700 -120 0 0 {name=h1
descr="load op & annotate" 
tclcommand="xschem raw_read $netlist_dir/write RamP_tb1_CP_OLP1.raw
; set show_hidden_texts 1; xschem annotate_op"}
C {ngspice_probe.sym} 530 -340 0 1 {name=r1}
C {code_shown.sym} 0 -460 0 0 {
name=TT_MODELS
only_toplevel=true
value="
** IHP models
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
"
spice_ignore=false
      }
C {lab_pin.sym} 530 -280 0 0 {name=p2 sig_type=std_logic lab=VICM}
C {ngspice_probe.sym} 890 -310 0 0 {name=r2}
C {vsource.sym} 400 -270 0 0 {name=V3 value="dc 0.825 ac 1 180" savecurrent=false}
C {gnd.sym} 400 -220 0 0 {name=l8 lab=GND}
C {devices/code_shown.sym} 0 -360 0 0 {name="NGSPICE" only_toplevel=true 
value="
.option wnflag=1
.option savecurrents
.temp 27
.control
save all
write RamP_tb1_CP_OLP1.raw
set appendwrite 
op
write RamP_tb1_CP_OLP1.raw
**dc temp -50 150 1
**tran 1m 10m 1m
ac dec 20 1 1e8
plot vdb(vout) vdb(x1.vo_stg1) vdb(x1.mp_dz) vdb(x1.mn_dz)
.endc
"}
C {lab_pin.sym} 890 -310 0 1 {name=p1 sig_type=std_logic lab=vout}
