v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 660 -280 740 -280 {lab=Vout}
N 740 -450 740 -280 {lab=Vout}
N 380 -150 380 -130 {lab=GND}
N 380 -250 380 -210 {lab=VICM}
N 880 -350 880 -325 {lab=GND}
N 880 -430 880 -410 {lab=VDD}
N 540 -380 540 -350 {lab=VDD}
N 540 -210 540 -190 {lab=GND}
N 740 -170 740 -150 {lab=GND}
N 740 -280 740 -230 {lab=Vout}
N 380 -310 460 -310 {lab=Vout}
N 380 -250 460 -250 {lab=VICM}
N 380 -450 380 -310 {lab=Vout}
N 380 -450 740 -450 {lab=Vout}
C {/foss/designs/RAMP/Fully-Diff-RAMP/RAMP.sym} 280 -280 2 1 {name=x1}
C {vsource.sym} 380 -180 0 0 {name=V1 value="dc .825 PULSE(0 0.825 1p 10n 10n 1u 2u 1)" savecurrent=false}
C {vsource.sym} 880 -380 0 0 {name=V2 value=1.65 savecurrent=false}
C {vdd.sym} 880 -430 0 0 {name=l1 lab=VDD}
C {gnd.sym} 880 -325 0 0 {name=l2 lab=GND}
C {gnd.sym} 380 -130 0 0 {name=l3 lab=GND}
C {vdd.sym} 540 -380 0 0 {name=l4 lab=VDD}
C {gnd.sym} 540 -190 0 0 {name=l5 lab=GND}
C {capa.sym} 740 -200 0 0 {name=C1
m=1
value=50p
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 740 -150 0 0 {name=l6 lab=GND}
C {title.sym} 160 -30 0 0 {name=l7 author="Nithin Purushothama"}
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
C {ngspice_probe.sym} 740 -280 0 0 {name=r2}
C {devices/code_shown.sym} 0 -510 0 0 {name="NGSPICE" only_toplevel=true 
value="
.option wnflag=1
.option savecurrents
.temp 27
.control
save all
write RamP_tb1_CP_FB1.raw
set appendwrite 
op
write RamP_tb1_CP_FB1.raw
**dc temp -50 150 1
tran 100n 2u 100n
**ac dec 20 1 1e8
**plot vdb(vout2) vdb(vout1)
.endc
"}
C {lab_pin.sym} 740 -280 0 1 {name=p1 sig_type=std_logic lab=Vout}
