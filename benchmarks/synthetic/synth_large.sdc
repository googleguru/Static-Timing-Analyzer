# SDC for synth_large  period=6.0ns
create_clock -name clk -period 6.0 [get_ports clk]
set_clock_uncertainty -setup 0.15 [get_clocks clk]
set_input_delay  -clock clk -max 1.80 [get_ports {din[*]}]
set_output_delay -clock clk -max 1.20 [get_ports {dout[*]}]
set_driving_cell -lib_cell BUFX2 -pin Z [get_ports {din[*]}]
set_load 15.0 [get_ports {dout[*]}]
set_max_transition 0.6 [current_design]
