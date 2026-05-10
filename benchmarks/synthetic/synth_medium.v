// Auto-generated synthetic benchmark: synth_medium
// Stages=5  Bits=8  Seed=1
// Copyright (c) 2024 sta-choa project (MIT License)

module synth_medium (
    input  wire        clk,
    input  wire [7:0]  din,
    output wire [7:0]  dout
);

    wire w_s0b0;
    wire w_s0b1;
    wire w_s0b2;
    wire w_s0b3;
    wire w_s0b4;
    wire w_s0b5;
    wire w_s0b6;
    wire w_s0b7;
    wire w_s1b0;
    wire w_s1b1;
    wire w_s1b2;
    wire w_s1b3;
    wire w_s1b4;
    wire w_s1b5;
    wire w_s1b6;
    wire w_s1b7;
    wire w_s2b0;
    wire w_s2b1;
    wire w_s2b2;
    wire w_s2b3;
    wire w_s2b4;
    wire w_s2b5;
    wire w_s2b6;
    wire w_s2b7;
    wire w_s3b0;
    wire w_s3b1;
    wire w_s3b2;
    wire w_s3b3;
    wire w_s3b4;
    wire w_s3b5;
    wire w_s3b6;
    wire w_s3b7;
    wire w_s4b0;
    wire w_s4b1;
    wire w_s4b2;
    wire w_s4b3;
    wire w_s4b4;
    wire w_s4b5;
    wire w_s4b6;
    wire w_s4b7;
    wire q0;
    wire q1;
    wire q2;
    wire q3;
    wire q4;
    wire q5;
    wire q6;
    wire q7;

    OR2X1 u0 (.A(din[1]), .B(din[4]), Z(w_s0b0));
    AND2X1 u1 (.A(din[7]), .B(din[7]), ZN(w_s0b1));
    NOR2X1 u2 (.A(din[6]), .B(din[3]), ZN(w_s0b2));
    AND2X1 u3 (.A(din[7]), .B(din[0]), ZN(w_s0b3));
    BUFX2 u4 (.A(din[6]), .Z(w_s0b4));
    NOR2X1 u5 (.A(din[0]), .B(din[7]), ZN(w_s0b5));
    NAND2X1 u6 (.A(din[3]), .B(din[1]), ZN(w_s0b6));
    NAND2X1 u7 (.A(din[0]), .B(din[0]), ZN(w_s0b7));
    AND2X1 u8 (.A(w_s0b0), .B(w_s0b6), ZN(w_s1b0));
    INVX1 u9 (.A(w_s0b3), .ZN(w_s1b1));
    NOR2X1 u10 (.A(w_s0b0), .B(w_s0b3), ZN(w_s1b2));
    BUFX2 u11 (.A(w_s0b7), .Z(w_s1b3));
    NOR2X1 u12 (.A(w_s0b3), .B(w_s0b5), ZN(w_s1b4));
    OR2X1 u13 (.A(w_s0b3), .B(w_s0b7), Z(w_s1b5));
    NAND2X1 u14 (.A(w_s0b0), .B(w_s0b6), ZN(w_s1b6));
    BUFX2 u15 (.A(w_s0b1), .Z(w_s1b7));
    OR2X1 u16 (.A(w_s1b4), .B(w_s1b1), Z(w_s2b0));
    INVX1 u17 (.A(w_s1b5), .ZN(w_s2b1));
    INVX1 u18 (.A(w_s1b6), .ZN(w_s2b2));
    XOR2X1 u19 (.A(w_s1b3), .B(w_s1b4), Z(w_s2b3));
    NAND2X1 u20 (.A(w_s1b7), .B(w_s1b6), ZN(w_s2b4));
    XOR2X1 u21 (.A(w_s1b0), .B(w_s1b7), Z(w_s2b5));
    OR2X1 u22 (.A(w_s1b6), .B(w_s1b6), Z(w_s2b6));
    INVX1 u23 (.A(w_s1b2), .ZN(w_s2b7));
    NAND2X1 u24 (.A(w_s2b5), .B(w_s2b1), ZN(w_s3b0));
    NOR2X1 u25 (.A(w_s2b1), .B(w_s2b2), ZN(w_s3b1));
    XOR2X1 u26 (.A(w_s2b6), .B(w_s2b5), Z(w_s3b2));
    NOR2X1 u27 (.A(w_s2b0), .B(w_s2b7), ZN(w_s3b3));
    AND2X1 u28 (.A(w_s2b4), .B(w_s2b6), ZN(w_s3b4));
    INVX1 u29 (.A(w_s2b2), .ZN(w_s3b5));
    OR2X1 u30 (.A(w_s2b3), .B(w_s2b0), Z(w_s3b6));
    BUFX2 u31 (.A(w_s2b3), .Z(w_s3b7));
    XOR2X1 u32 (.A(w_s3b3), .B(w_s3b6), Z(w_s4b0));
    XOR2X1 u33 (.A(w_s3b5), .B(w_s3b5), Z(w_s4b1));
    NOR2X1 u34 (.A(w_s3b4), .B(w_s3b0), ZN(w_s4b2));
    NOR2X1 u35 (.A(w_s3b2), .B(w_s3b3), ZN(w_s4b3));
    NOR2X1 u36 (.A(w_s3b0), .B(w_s3b7), ZN(w_s4b4));
    BUFX2 u37 (.A(w_s3b5), .Z(w_s4b5));
    XOR2X1 u38 (.A(w_s3b3), .B(w_s3b6), Z(w_s4b6));
    NOR2X1 u39 (.A(w_s3b5), .B(w_s3b6), ZN(w_s4b7));

    DFFX1 uff0 (.D(w_s4b0), .CK(clk), .Q(q0), .QN());
    DFFX1 uff1 (.D(w_s4b1), .CK(clk), .Q(q1), .QN());
    DFFX1 uff2 (.D(w_s4b2), .CK(clk), .Q(q2), .QN());
    DFFX1 uff3 (.D(w_s4b3), .CK(clk), .Q(q3), .QN());
    DFFX1 uff4 (.D(w_s4b4), .CK(clk), .Q(q4), .QN());
    DFFX1 uff5 (.D(w_s4b5), .CK(clk), .Q(q5), .QN());
    DFFX1 uff6 (.D(w_s4b6), .CK(clk), .Q(q6), .QN());
    DFFX1 uff7 (.D(w_s4b7), .CK(clk), .Q(q7), .QN());

    BUFX2 uout0 (.A(q0), .Z(dout[0]));
    BUFX2 uout1 (.A(q1), .Z(dout[1]));
    BUFX2 uout2 (.A(q2), .Z(dout[2]));
    BUFX2 uout3 (.A(q3), .Z(dout[3]));
    BUFX2 uout4 (.A(q4), .Z(dout[4]));
    BUFX2 uout5 (.A(q5), .Z(dout[5]));
    BUFX2 uout6 (.A(q6), .Z(dout[6]));
    BUFX2 uout7 (.A(q7), .Z(dout[7]));

endmodule
