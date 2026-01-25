fn main() {
    let vals_laptop: &[u64] = &[
        0x1fc0,      // col
        0x4080,      // channel
        0x4b300,     // group
        0x88000,     // group
        0x110000,    // dimm/rank
        0x220000,    // bank
        0x440000,    // bank
        0xffff80000, // row
    ];
    let vals_laptop_1_dimm: &[u64] = &[
        0x000001fc0, // col
        0x000002040, // group
        0x000044000, // group
        0x000088000, // rank
        0x000110000, // bank
        0x000220000, // bank
        0x7fffc0000, // row
    ];
    let vals_intel_a_21: &[u64] = &[
        0x0000001FC0, // col
        0x0000082600, // channel
        0x0000005400, // group
        0x0248088000, // group
        0x0000110000, // dimm/rank
        0x0493220000, // bank
        0x0924C40000, // bank
        0x0FFFF80000, // row
    ];
    let vals_intel_a_22: &[u64] = &[
        0x0000001FC0, // col
        0x0000082600, // channel
        0x0000005400, // group
        0x1248108000, // group
        0x0000210000, // dimm & rank
        0x0492420000, // bank
        0x0000840000, // dimm & rank
        0x0925080000, // bank
        0x1FFFF00000, // row
    ];

    // ddr5, so sub-channel
    let vals_intel_b_22: &[u64] = &[
        0x0000001BC0, // col
        0x0000102100, // rank
        0x0000104200, // channel / sub channel
        0x0000186400, // channel / sub channel
        0x0444208000, // group
        0x0888410000, // group
        0x0000820000, // rank
        0x0111040000, // bank
        0x0222080000, // bank
        0x0FFFF00000, // row
    ];

    for vals in [
        vals_laptop,
        vals_laptop_1_dimm,
        vals_intel_a_21,
        vals_intel_a_22,
        vals_intel_b_22,
    ] {
        let mut address_bits = vals.iter().map(|x: &u64| x.ilog2() + 1).max().unwrap() as usize;
        eprintln!("bits: {address_bits}");
        let cacheline_size_bytes = 512 / 8 as u64;
        for v in vals {
            assert!(v % cacheline_size_bytes == 0);
        }
        address_bits -= cacheline_size_bytes.ilog2() as usize;
        for v in vals {
            eprintln!("{:0address_bits$b}", v / cacheline_size_bytes);
        }
        eprintln!();
    }
}
