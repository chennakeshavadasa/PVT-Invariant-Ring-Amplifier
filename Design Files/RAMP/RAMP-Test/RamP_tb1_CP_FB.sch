v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Targeted BW=20MHz} 0 -640 0 0 0.4 0.4 {}
N 380 -310 460 -310 {lab=#net1}
N 660 -280 740 -280 {lab=#net2}
N 380 -250 460 -250 {lab=VICM}
N 380 -150 380 -130 {lab=GND}
N 380 -250 380 -210 {lab=VICM}
N 880 -350 880 -325 {lab=GND}
N 880 -430 880 -410 {lab=VDD}
N 540 -380 540 -350 {lab=VDD}
N 540 -210 540 -190 {lab=GND}
N 740 -170 740 -150 {lab=GND}
N 740 -280 740 -230 {lab=#net2}
N 540 -510 580 -510 {
lab=probe}
N 540 -670 540 -640 {
lab=GND}
N 540 -580 540 -510 {
lab=probe}
N 500 -510 540 -510 {
lab=probe}
N 740 -510 740 -280 {lab=#net2}
N 640 -510 740 -510 {lab=#net2}
N 380 -510 440 -510 {lab=#net1}
N 380 -510 380 -310 {lab=#net1}
C {/foss/designs/RAMP/Fully-Diff-RAMP/RAMP.sym} 280 -280 2 1 {name=x1 }
C {vsource.sym} 380 -180 0 0 {name=V1 value=0.825 savecurrent=false}
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
C {devices/code_shown.sym} -540 -870 0 0 {name="NGSPICE" only_toplevel=true 
value="
.options savecurrents
.control
 let runs=2
 let run=0

 alter @Vprobe1[acmag]=1
 alter @iprobe1[acmag]=0

 dowhile run < runs

 set run =$&run
 ac dec 20 0.01 10G
 write RamP_tb1_CP_FB_\{$run\}.raw

 all
 alter @Vprobe1[acmag]=0
 alter @iprobe1[acmag]=1
 let run = run + 1
 end

 let ip22 = ac2.i(Vprobe2)
 let vprb1 = ac1.probe
 let mb = 1/(vprb1+ip22)-1
 let phase_mb = 180/PI*vp(mb)
 plot vdb(mb)
 plot vdb(x1.Vo_STG1) vdb(x1.mp_dz) vdb(x1.mn_dz)

 plot phase_mb
 plot vdb(mb) phase_mb

 meas ac peak MAX vmag(mb) FROM=2 TO=1.5G
 let f3db = peak/sqrt(2)
 meas ac f1 WHEN vmag(mb)=f3db RISE=1
 meas ac BW WHEN vmag(mb)=f3db FALL=1
 let GBW = peak*BW
 meas ac pm_deg find phase_mb when vdb(mb)=0
 meas ac dominant_pole_f when vdb(mb)=0
 meas ac loop_gain find vdb(mb) at=0.01
 let Phase_margin=180-abs(pm_deg)
 print GBW
 print Phase_margin

 op
 show m : gm : gmbs : gds : vds : vdsat : vgs : vth : id
.endc
"}
C {devices/launcher.sym} 500 -90 0 0 {name=h1
descr="load op & annotate" 
tclcommand="xschem raw_read $netlist_dir/Deadzone_try_1.raw; set show_hidden_texts 1; xschem annotate_op"}
C {ngspice_probe.sym} 380 -310 0 1 {name=r1}
C {code_shown.sym} 0 -500 0 0 {
name=TT_MODELS
only_toplevel=true
value="
** IHP models
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
"
spice_ignore=false
      }
C {vsource.sym} 470 -510 1 1 {name=Vprobe2 value=0 savecurrent=false}
C {vsource.sym} 610 -510 3 0 {name=Vprobe1 value="dc 0 ac 1" savecurrent=false}
C {isource.sym} 540 -610 0 0 {name=iprobe1 value="dc 0 ac 1"}
C {lab_pin.sym} 540 -510 3 0 {name=p1 sig_type=std_logic lab=probe}
C {gnd.sym} 540 -670 2 0 {name=l8 lab=GND}
C {lab_pin.sym} 380 -250 0 0 {name=p2 sig_type=std_logic lab=VICM}
C {ngspice_probe.sym} 740 -280 0 0 {name=r2}
