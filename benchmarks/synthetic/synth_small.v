// Auto-generated synthetic benchmark: synth_small
// Stages=3  Bits=4  Seed=0
// Copyright (c) 2024 sta-choa project (MIT License)

module synth_small (
    input  wire        clk,
    input  wire [3:0]  din,
    output wire [3:0]  dout
);

    wire w_s0b0;
    wire w_s0b1;
    wire w_s0b2;
    wire w_s0b3;
    wire w_s1b0;
    wire w_s1b1;
    wire w_s1b2;
    wire w_s1b3;
    wire w_s2b0;
    wire w_s2b1;
    wire w_s2b2;
    wire w_s2b3;
    wire q0;
    wire q1;
    wire q2;
    wire q3;

    BUFX2 u0 (.A(din[3]), .Z(w_s0b0));
    BUFX2 u1 (.A(din[3]), .Z(w_s0b1));
    AND2X1 u2 (.A(din[2]), .B(din[3]), ZN(w_s0b2));
    NOR2X1 u3 (.A(din[2]), .B(din[3]), ZN(w_s0b3));
    NAND2X1 u4 (.A(w_s0b1), .B(w_s0b1), ZN(w_s1b0));
    NAND2X1 u5 (.A(w_s0b1), .B(w_s0b0), ZN(w_s1b1));
    XOR2X1 u6 (.A(w_s0b2), .B(w_s0b1), Z(w_s1b2));
    NAND2X1 u7 (.A(w_s0b0), .B(w_s0b0), ZN(w_s1b3));
    BUFX2 u8 (.A(w_s1b2), .Z(w_s2b0));
    NOR2X1 u9 (.A(w_s1b0), .B(w_s1b2), ZN(w_s2b1));
    NOR2X1 u10 (.A(w_s1b2), .B(w_s1b1), ZN(w_s2b2));
    XOR2X1 u11 (.A(w_s1b3), .B(w_s1b3), Z(w_s2b3));

    DFFX1 uff0 (.D(w_s2b0), .CK(clk), .Q(q0), .QN());
    DFFX1 uff1 (.D(w_s2b1), .CK(clk), .Q(q1), .QN());
    DFFX1 uff2 (.D(w_s2b2), .CK(clk), .Q(q2), .QN());
    DFFX1 uff3 (.D(w_s2b3), .CK(clk), .Q(q3), .QN());

    BUFX2 uout0 (.A(q0), .Z(dout[0]));
    BUFX2 uout1 (.A(q1), .Z(dout[1]));
    BUFX2 uout2 (.A(q2), .Z(dout[2]));
    BUFX2 uout3 (.A(q3), .Z(dout[3]));

endmodule
