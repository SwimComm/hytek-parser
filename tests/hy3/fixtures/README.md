# hy3 integration test fixtures

Small Hy-Tek `.hy3` files used by `tests/hy3/test_integration.py` to verify
parser behaviour across MM generations.

## Provenance

Each fixture is a trimmed-down, PII-redacted slice of a real MM output file
from publicly distributed meet results:

| File | MM version | Source meet | Covers |
|---|---|---|---|
| `mm2_2_0fg_relay_multi_team.hy3` | MM2 2.0Fg | 2007 Pacific Committee R-W SC Meet | Bug 1 (blank E2/F2 date column) + Bug 2-A (multi-team relay attribution) |
| `mm3_3_0ea_individuals_blank_date.hy3` | MM3 3.0Ea | 2011 CA CSSC Fall Mile | Bug 1 on a different MM generation |
| `mm5_8_0fd_relay_alternates.hy3` | MM5 8.0Fd | 2025 WMPSSDL Championships | Bug 2-B (F3 swimmer dict preserves leg numbers for alternates) |
| `mm4_ymca_col92_division_citizenship.hy3` | MM4 4.0Ec | 2013 YMCA Nationals Short Course (Virginia Swimming) | E1 col-92 `meet_division` (`SW`); D1 `citizenship` (`USA`); C1 `region` (NE/MD/NI); E2 pad+button timing; F2 relay pad+button timing |
| `mm_col77_division.hy3` | MM5 6.0Cc | 2015 State/Non-State Open 25 yd (Wisconsin Swimming) | E1 col-77 `meet_division` (`JV`); E2 `alt_time_code` (`A`, `K`); pad-vs-button divergence (pad=107.39 vs btn1=102.49); C1 `region` (`WI`) |
| `mm_pad_button_divergence.hy3` | MM5 8.0Fd | 2025 MT HOT Tropical Meet (Montana Swimming) | clear pad-vs-button divergence (pad=36.26 vs result=75.29, half-pool touchpad); E2 `alt_time_code` (`A`); two LSC regions (MT, WY) |

## Redaction

The following D1, C1, and C2/C3 fields were replaced with placeholders of the
same column width so the files remain parseable:

- `D1` last_name → `Swimmer<meet_id>`
- `D1` first_name → `Test`
- `D1` nick_name, middle_initial, usa_swimming_id → blank
- `D1` date_of_birth → `01011970`
- `C1` contact_name_1 (cols 56-85) → `Test Contact` padded to 30 chars, or blank if original was blank
- `C1` contact_name_2 (cols 86-115) → `Test Contact` padded to 30 chars, or blank if original was blank
- `C2` address_1, city, zip_code → blank (state and country retained)
- `C3` daytime_phone, evening_phone, fax, email → blank

Team codes, team names, meet name, facility, and event metadata are
intact — these are public information from the original meet results.

## Coverage gaps (known)

`backup_4_time` (E2 col 75-82) is always zero in the three source meets;
no real file with a non-zero value was found among the designated sources. The field
is exercised by the line-parser-level tests in `test_e_event_parsers.py` but is not
covered by any integration fixture.

## Bug references

The bugs these fixtures exercise are described in the PR that introduced
this test suite (release 2.0.0). The matching line-parser-level tests
live in `tests/hy3/line_parsers/test_e_event_parsers.py` and
`tests/hy3/line_parsers/test_f_relay_parsers.py`.
