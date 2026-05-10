# Benchmark Collateral

## Synthetic Benchmarks (included — always runnable)

Located in `benchmarks/synthetic/`. Generated from `gen_synthetic.py` using only
hand-crafted Liberty cells. No external IP required.

| Name | Gates (approx) | Clock Period | Family |
|---|---|---|---|
| simple_design | ~60 | 10 ns | synthetic |
| synth_small | ~20 | 10 ns | synthetic |
| synth_medium | ~50 | 8 ns | synthetic |
| synth_large | ~150 | 6 ns | synthetic |
| synth_tight | ~70 | 5 ns | synthetic |

## ISCAS-85 Benchmarks (NOT included — must be prepared)

1. Download gate-level Verilog from a public academic repository (e.g., the
   [verilog-iscas](https://github.com/squillero/iscas85) project or similar).
2. Map to a compatible Liberty library (the synthetic `simple.lib` can be used
   for quick testing if cell names match).
3. Write an SDC with `create_clock` and I/O delays.
4. Place files under `benchmarks/iscas85/<circuit>/`.
5. The manifest `manifests/iscas85.yaml` will automatically pick them up.

## ISCAS-89 Benchmarks (NOT included — must be prepared)

Same flow as ISCAS-85. Place files under `benchmarks/iscas89/<circuit>/`.
The manifest `manifests/iscas89.yaml` references the expected paths.

## IPSD / TAU Contest Benchmarks (NOT included — must be sourced)

TAU 2018/2019 contest circuits require registration with contest organizers:
- https://www.ispd.cc/contests/
- https://sites.google.com/view/taucontest

Place files under `benchmarks/ipsd/<year>/`.
The manifest `manifests/ipsd.yaml` references the expected paths.

## Adding a Custom Benchmark

Create a YAML manifest entry:
```yaml
benchmarks:
  - name: my_design
    family: custom
    liberty: path/to/tech.lib
    verilog: path/to/my_design.v
    sdc:     path/to/my_design.sdc
    spef:    path/to/my_design.spef   # optional
    sdf:     ~                         # optional
    top_module: my_design
    clock_period_ns: 10.0
    enabled: true
```

Then add the manifest path to `configs/default.yaml` under `manifests:`.
