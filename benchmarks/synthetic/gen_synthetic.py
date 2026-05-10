#!/usr/bin/env python3
"""
Generates additional synthetic Verilog + SDC benchmarks for framework testing.
Benchmarks are NOT based on real IP; they use only the simple_lib cells.
"""
import argparse
import random
from pathlib import Path

CELLS  = ["AND2X1", "OR2X1", "NAND2X1", "NOR2X1", "XOR2X1", "INVX1", "BUFX2"]
BINARY = ["AND2X1", "OR2X1", "NAND2X1", "NOR2X1", "XOR2X1"]
UNARY  = ["INVX1", "BUFX2"]


def gen_netlist(name: str, n_stages: int, n_bits: int, seed: int) -> str:
    rng = random.Random(seed)
    lines = [
        f"// Auto-generated synthetic benchmark: {name}",
        f"// Stages={n_stages}  Bits={n_bits}  Seed={seed}",
        f"// Copyright (c) 2024 sta-choa project (MIT License)",
        "",
        f"module {name} (",
        f"    input  wire        clk,",
        f"    input  wire [{n_bits-1}:0]  din,",
        f"    output wire [{n_bits-1}:0]  dout",
        ");",
        "",
    ]
    # Wire declarations
    prev_stage = [f"din[{i}]" for i in range(n_bits)]
    wire_decls = []
    inst_lines = []
    inst_idx = 0

    for s in range(n_stages):
        cur_stage = []
        for b in range(n_bits):
            wire_name = f"w_s{s}b{b}"
            wire_decls.append(f"    wire {wire_name};")
            cell = rng.choice(CELLS)
            if cell in BINARY:
                a = rng.choice(prev_stage)
                b2 = rng.choice(prev_stage)
                inst_lines.append(f"    {cell} u{inst_idx} (.A({a}), .B({b2}), {'ZN' if 'N' in cell else 'Z'}({wire_name}));")
            else:
                a = rng.choice(prev_stage)
                pin_out = "ZN" if cell == "INVX1" else "Z"
                inst_lines.append(f"    {cell} u{inst_idx} (.A({a}), .{pin_out}({wire_name}));")
            cur_stage.append(wire_name)
            inst_idx += 1
        prev_stage = cur_stage

    # Registers at end
    ff_lines = []
    out_lines = []
    for b in range(n_bits):
        q_wire = f"q{b}"
        wire_decls.append(f"    wire {q_wire};")
        ff_lines.append(f"    DFFX1 uff{b} (.D({prev_stage[b]}), .CK(clk), .Q({q_wire}), .QN());")
        out_lines.append(f"    BUFX2 uout{b} (.A({q_wire}), .Z(dout[{b}]));")

    lines.extend(wire_decls)
    lines.append("")
    lines.extend(inst_lines)
    lines.append("")
    lines.extend(ff_lines)
    lines.append("")
    lines.extend(out_lines)
    lines.append("")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


def gen_sdc(name: str, period_ns: float, n_bits: int) -> str:
    return f"""\
# SDC for {name}  period={period_ns}ns
create_clock -name clk -period {period_ns} [get_ports clk]
set_clock_uncertainty -setup 0.15 [get_clocks clk]
set_input_delay  -clock clk -max {period_ns*0.3:.2f} [get_ports {{din[*]}}]
set_output_delay -clock clk -max {period_ns*0.2:.2f} [get_ports {{dout[*]}}]
set_driving_cell -lib_cell BUFX2 -pin Z [get_ports {{din[*]}}]
set_load 15.0 [get_ports {{dout[*]}}]
set_max_transition 0.6 [current_design]
"""


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic STA benchmarks")
    parser.add_argument("--out-dir", default="benchmarks/synthetic", help="Output directory")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    configs = [
        ("synth_small",   3,  4, 10.0, args.seed),
        ("synth_medium",  5,  8,  8.0, args.seed + 1),
        ("synth_large",   8, 16,  6.0, args.seed + 2),
        ("synth_tight",   6,  8,  5.0, args.seed + 3),
    ]

    for name, stages, bits, period, seed in configs:
        v_path  = out / f"{name}.v"
        sdc_path = out / f"{name}.sdc"
        v_path.write_text(gen_netlist(name, stages, bits, seed))
        sdc_path.write_text(gen_sdc(name, period, bits))
        print(f"Generated: {v_path}  {sdc_path}")

    print("Done.")


if __name__ == "__main__":
    main()
