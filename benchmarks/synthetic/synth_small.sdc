# SDC for synth_small  period=10.0ns
create_clock -name clk -period 10.0 [get_ports clk]
set_clock_uncertainty -setup 0.15 [get_clocks clk]
set_input_delay  -clock clk -max 3.00 [get_ports {din[*]}]
set_output_delay -clock clk -max 2.00 [get_ports {dout[*]}]
set_driving_cell -lib_cell BUFX2 -pin Z [get_ports {din[*]}]
set_load 15.0 [get_ports {dout[*]}]
set_max_transition 0.6 [current_design]
