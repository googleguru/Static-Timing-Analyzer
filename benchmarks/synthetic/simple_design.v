// Synthetic Verilog netlist for sta-choa framework testing.
// Gate-level netlist using simple_lib cells.
// NOT derived from any third-party IP.
// Copyright (c) 2024 sta-choa project (MIT License)

module simple_design (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [7:0]  data_in,
    output wire [7:0]  data_out,
    output wire        overflow
);

    // Internal wires — combinational stage 1
    wire [7:0] stage1_out;
    wire [7:0] stage2_out;
    wire [7:0] stage3_out;
    wire       carry_chain;
    wire       inv_rst;

    // Buffered inputs
    wire [7:0] data_buf;
    wire       rst_buf;

    BUFX2  u_buf_rst  (.A(rst_n),     .Z(rst_buf));
    INVX1  u_inv_rst  (.A(rst_buf),   .ZN(inv_rst));

    BUFX2  u_buf0 (.A(data_in[0]), .Z(data_buf[0]));
    BUFX2  u_buf1 (.A(data_in[1]), .Z(data_buf[1]));
    BUFX2  u_buf2 (.A(data_in[2]), .Z(data_buf[2]));
    BUFX2  u_buf3 (.A(data_in[3]), .Z(data_buf[3]));
    BUFX2  u_buf4 (.A(data_in[4]), .Z(data_buf[4]));
    BUFX2  u_buf5 (.A(data_in[5]), .Z(data_buf[5]));
    BUFX2  u_buf6 (.A(data_in[6]), .Z(data_buf[6]));
    BUFX2  u_buf7 (.A(data_in[7]), .Z(data_buf[7]));

    // Stage 1: XOR reduction tree (simulates adder-like logic)
    wire xor01, xor23, xor45, xor67;
    XOR2X1 u_xor01 (.A(data_buf[0]), .B(data_buf[1]), .Z(xor01));
    XOR2X1 u_xor23 (.A(data_buf[2]), .B(data_buf[3]), .Z(xor23));
    XOR2X1 u_xor45 (.A(data_buf[4]), .B(data_buf[5]), .Z(xor45));
    XOR2X1 u_xor67 (.A(data_buf[6]), .B(data_buf[7]), .Z(xor67));

    AND2X1 u_and01_23 (.A(xor01), .B(xor23), .Z(stage1_out[0]));
    AND2X1 u_and45_67 (.A(xor45), .B(xor67), .Z(stage1_out[1]));
    OR2X1  u_or01_23  (.A(xor01), .B(xor23), .Z(stage1_out[2]));
    OR2X1  u_or45_67  (.A(xor45), .B(xor67), .Z(stage1_out[3]));
    NAND2X1 u_nand01  (.A(data_buf[0]), .B(data_buf[2]), .ZN(stage1_out[4]));
    NAND2X1 u_nand02  (.A(data_buf[4]), .B(data_buf[6]), .ZN(stage1_out[5]));
    NOR2X1  u_nor01   (.A(data_buf[1]), .B(data_buf[3]), .ZN(stage1_out[6]));
    NOR2X1  u_nor02   (.A(data_buf[5]), .B(data_buf[7]), .ZN(stage1_out[7]));

    // Stage 2: logic mixing with rst
    wire [7:0] s1_rst;
    AND2X1 u_s1r0 (.A(stage1_out[0]), .B(rst_buf), .Z(s1_rst[0]));
    AND2X1 u_s1r1 (.A(stage1_out[1]), .B(rst_buf), .Z(s1_rst[1]));
    AND2X1 u_s1r2 (.A(stage1_out[2]), .B(rst_buf), .Z(s1_rst[2]));
    AND2X1 u_s1r3 (.A(stage1_out[3]), .B(rst_buf), .Z(s1_rst[3]));
    OR2X1  u_s1r4 (.A(stage1_out[4]), .B(inv_rst), .Z(s1_rst[4]));
    OR2X1  u_s1r5 (.A(stage1_out[5]), .B(inv_rst), .Z(s1_rst[5]));
    INVX1  u_s1r6 (.A(stage1_out[6]),              .ZN(s1_rst[6]));
    INVX1  u_s1r7 (.A(stage1_out[7]),              .ZN(s1_rst[7]));

    // Stage 2 output buffered
    BUFX2 u_s2b0 (.A(s1_rst[0]), .Z(stage2_out[0]));
    BUFX2 u_s2b1 (.A(s1_rst[1]), .Z(stage2_out[1]));
    BUFX2 u_s2b2 (.A(s1_rst[2]), .Z(stage2_out[2]));
    BUFX2 u_s2b3 (.A(s1_rst[3]), .Z(stage2_out[3]));
    BUFX2 u_s2b4 (.A(s1_rst[4]), .Z(stage2_out[4]));
    BUFX2 u_s2b5 (.A(s1_rst[5]), .Z(stage2_out[5]));
    BUFX2 u_s2b6 (.A(s1_rst[6]), .Z(stage2_out[6]));
    BUFX2 u_s2b7 (.A(s1_rst[7]), .Z(stage2_out[7]));

    // Stage 3: further logic
    XOR2X1 u_s3x0 (.A(stage2_out[0]), .B(stage2_out[4]), .Z(stage3_out[0]));
    XOR2X1 u_s3x1 (.A(stage2_out[1]), .B(stage2_out[5]), .Z(stage3_out[1]));
    XOR2X1 u_s3x2 (.A(stage2_out[2]), .B(stage2_out[6]), .Z(stage3_out[2]));
    XOR2X1 u_s3x3 (.A(stage2_out[3]), .B(stage2_out[7]), .Z(stage3_out[3]));
    AND2X1 u_s3a0 (.A(stage2_out[0]), .B(stage2_out[1]), .Z(stage3_out[4]));
    AND2X1 u_s3a1 (.A(stage2_out[2]), .B(stage2_out[3]), .Z(stage3_out[5]));
    OR2X1  u_s3o0 (.A(stage2_out[4]), .B(stage2_out[5]), .Z(stage3_out[6]));
    OR2X1  u_s3o1 (.A(stage2_out[6]), .B(stage2_out[7]), .Z(stage3_out[7]));

    // Carry / overflow logic
    wire carry0, carry1;
    AND2X1 u_carry0 (.A(stage3_out[0]), .B(stage3_out[1]), .Z(carry0));
    AND2X1 u_carry1 (.A(stage3_out[2]), .B(stage3_out[3]), .Z(carry1));
    OR2X1  u_carry_or(.A(carry0),       .B(carry1),        .Z(carry_chain));

    // Registers — data pipeline
    wire [7:0] q_ff;

    DFFX1 u_ff0 (.D(stage3_out[0]), .CK(clk), .Q(q_ff[0]), .QN());
    DFFX1 u_ff1 (.D(stage3_out[1]), .CK(clk), .Q(q_ff[1]), .QN());
    DFFX1 u_ff2 (.D(stage3_out[2]), .CK(clk), .Q(q_ff[2]), .QN());
    DFFX1 u_ff3 (.D(stage3_out[3]), .CK(clk), .Q(q_ff[3]), .QN());
    DFFX1 u_ff4 (.D(stage3_out[4]), .CK(clk), .Q(q_ff[4]), .QN());
    DFFX1 u_ff5 (.D(stage3_out[5]), .CK(clk), .Q(q_ff[5]), .QN());
    DFFX1 u_ff6 (.D(stage3_out[6]), .CK(clk), .Q(q_ff[6]), .QN());
    DFFX1 u_ff7 (.D(stage3_out[7]), .CK(clk), .Q(q_ff[7]), .QN());

    // Overflow register
    DFFX1 u_ff_ov (.D(carry_chain), .CK(clk), .Q(overflow), .QN());

    // Output stage
    BUFX2 u_out0 (.A(q_ff[0]), .Z(data_out[0]));
    BUFX2 u_out1 (.A(q_ff[1]), .Z(data_out[1]));
    BUFX2 u_out2 (.A(q_ff[2]), .Z(data_out[2]));
    BUFX2 u_out3 (.A(q_ff[3]), .Z(data_out[3]));
    BUFX2 u_out4 (.A(q_ff[4]), .Z(data_out[4]));
    BUFX2 u_out5 (.A(q_ff[5]), .Z(data_out[5]));
    BUFX2 u_out6 (.A(q_ff[6]), .Z(data_out[6]));
    BUFX2 u_out7 (.A(q_ff[7]), .Z(data_out[7]));

endmodule
