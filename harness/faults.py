"""R7, both directions: the clean co2-node-common.yaml must PASS the watchdog sim, and
each injected fault must FAIL it. Each fault is a single-span edit, and the span must
occur exactly once (R4).

  python faults.py <co2-node-common.yaml> <workdir>
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
src_path, work = sys.argv[1], sys.argv[2]
src = open(src_path, encoding="utf-8").read()

FAULTS = [
    (
        "F1 on_value NaN guard removed",
        "if (std::isnan(x)) return;   // the watchdog's own NaN must not reset the watchdog",
        "",
    ),
    ("F2 reboot cap 3 -> 4", "id(g_stale_reboots) < 3", "id(g_stale_reboots) < 4"),
    (
        "F3 stale threshold 240 s -> 24 s",
        "if (age < 240000) return;",
        "if (age < 24000) return;",
    ),
    (
        "F4 wrap-unsafe age arithmetic",
        "const uint32_t age = millis() - id(g_last_co2_ms);",
        "const uint64_t age = (uint64_t) millis() - id(g_last_co2_ms);",
    ),
    (
        "F5 recovery boot clears the fault",
        "publish_state(id(g_stale_reboots) > 0);",
        "publish_state(false);",
    ),
    (
        "F6 1.3 stale T left showing",
        "          if (!std::isnan(id(scd30_temperature).state)) id(scd30_temperature).publish_state(NAN);\n",
        "",
    ),
    (
        "F7 1.3 stale RH left showing",
        "          if (!std::isnan(id(scd30_humidity).state)) id(scd30_humidity).publish_state(NAN);\n",
        "",
    ),
    (
        "F8 1.3 T blanked ahead of the age test",
        "          if (age < 240000) return;\n",
        "          id(scd30_temperature).publish_state(NAN);\n          if (age < 240000) return;\n",
    ),
]


def sim(yaml_path, tag):
    cpp, exe = os.path.join(work, tag + ".cpp"), os.path.join(work, tag + ".exe")
    subprocess.run(
        [sys.executable, os.path.join(HERE, "gen.py"), yaml_path, cpp],
        check=True,
        capture_output=True,
    )
    c = subprocess.run(
        [
            sys.executable,
            "-m",
            "ziglang",
            "c++",
            "-std=c++17",
            "-Wall",
            "-Wextra",
            "-O1",
            cpp,
            "-o",
            exe,
        ],
        capture_output=True,
        text=True,
    )
    if c.returncode != 0:
        return "COMPILE-ERROR", c.stderr.strip().splitlines()[:6]
    r = subprocess.run([exe], capture_output=True, text=True)
    lines = r.stdout.strip().splitlines()
    return ("PASS" if r.returncode == 0 else "FAIL"), [
        line for line in lines if line.startswith(("  FAIL", "RESULT"))
    ][:6]


os.makedirs(work, exist_ok=True)
bad = 0
verdict, out = sim(src_path, "clean")
print("clean                                -> %s  (want PASS)" % verdict)
for line in out:
    print("    " + line)
bad += verdict != "PASS"
for name, old, new in FAULTS:
    n = src.count(old)
    if n != 1:
        print("%-36s -> SPAN COUNT %d (want 1)" % (name, n))
        bad += 1
        continue
    p = os.path.join(work, name.split()[0] + ".yaml")
    open(p, "w", encoding="utf-8", newline="\n").write(src.replace(old, new))
    verdict, out = sim(p, name.split()[0])
    print("%-36s -> %s  (want FAIL)" % (name, verdict))
    for line in out[:3]:
        print("    " + line)
    bad += verdict != "FAIL"
print(
    "FAULTS: %s (%d of %d directions wrong)"
    % ("PASS" if bad == 0 else "FAIL", bad, len(FAULTS) + 1)
)
sys.exit(1 if bad else 0)
