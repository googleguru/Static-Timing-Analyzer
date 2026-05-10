# Synthetic SDC constraints for sta-choa simple_design benchmark.
# Copyright (c) 2024 sta-choa project (MIT License)

# Primary clock: 10 ns period (100 MHz)
create_clock -name clk -period 10.0 [get_ports clk]

# Clock uncertainty: 0.1 ns setup, 0.05 ns hold
set_clock_uncertainty -setup 0.1 [get_clocks clk]
set_clock_uncertainty -hold  0.05 [get_clocks clk]

# Clock transition
set_clock_transition 0.05 [get_clocks clk]

# Input delays (30% of clock period)
set_input_delay -clock clk -max 3.0 [get_ports {data_in[*]}]
set_input_delay -clock clk -min 0.5 [get_ports {data_in[*]}]
set_input_delay -clock clk -max 2.0 [get_ports rst_n]
set_input_delay -clock clk -min 0.2 [get_ports rst_n]

# Output delays (20% of clock period)
set_output_delay -clock clk -max 2.0 [get_ports {data_out[*]}]
set_output_delay -clock clk -min 0.3 [get_ports {data_out[*]}]
set_output_delay -clock clk -max 2.0 [get_ports overflow]
set_output_delay -clock clk -min 0.3 [get_ports overflow]

# Drive strength on inputs
set_driving_cell -lib_cell BUFX2 -pin Z [get_ports {data_in[*] rst_n}]

# Load on outputs
set_load 10.0 [get_ports {data_out[*] overflow}]

# Max transition
set_max_transition 0.5 [current_design]

# Max fanout
set_max_fanout 20 [current_design]
