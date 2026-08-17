#!/usr/bin/env python3

# rom_gen.py
#
# Copyright (C) 2026 James Petersen <m@jamespetersen.ca>
# Licensed under MIT. See LICENSE

from bsdiff4 import file_diff
from collections.abc import Sequence
import tomli_w

HEXNUMS = {chr(ord('A') + i) for i in range(6)} | {chr(ord('a') + i) for i in range(6)} | {chr(ord('0') + i) for i in range(10)}

def get_ap_struct_address(xmap: Sequence[str]) -> int:
    for l in xmap:
        if "gAP" not in l:
            continue
        if all(c in HEXNUMS for c in l[2:10]):
            return int(l[2:10], 16)
    raise ValueError("ap global not present in xmap")

def main():
    print("DIFF hg_us")
    file_diff("roms/hg_us_orig.nds", "roms/hg_us.nds", "patches/base_patch_hg_us.bsdiff4")
    print("DIFF ss_us")
    file_diff("roms/ss_us_orig.nds", "roms/ss_us.nds", "patches/base_patch_ss_us.bsdiff4")

    rom_info = {}
    ap_struct_addresses = rom_info["ap_struct_address"] = {}
    for version in ["hg_us", "ss_us"]:
        with open(f"roms/{version}.xMAP", "r") as f:
            ap_struct_addresses[version] = get_ap_struct_address(f.readlines())

    with open("data_gen/rom_info.toml", "wb") as f:
        tomli_w.dump(rom_info, f)

if __name__ == "__main__":
    main()
