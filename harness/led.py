"""R7, both directions, for the fault LED (interval[1] of co2-node-common.yaml).
The LED lambda is extracted VERBATIM and run on the host, tick by tick (one tick =
one 100 ms interval call). The clean file must PASS; each injected fault must FAIL.
Each fault is a single-span edit, and the span must occur exactly once (R4).

  python led.py <co2-node-common.yaml> <workdir>

What it checks: dark while healthy; a 5 Hz strobe (alternating ticks) while the
fault is on, while a test runs, and while both are; dark from the first tick after
both end. It does not run the 15 s script delay (ESPHome core) or the hardware.
"""

import os
import subprocess
import sys

import yaml


class TagIgnoringLoader(
    yaml.SafeLoader
):  # as gen.py: !secret etc. load as plain values
    pass


def _any_tag(loader, suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


TagIgnoringLoader.add_multi_constructor("!", _any_tag)

CPP = r"""
#include <cstdio>
struct BinarySensor { bool state = false; };
struct Output { bool on = false; void turn_on() { on = true; } void turn_off() { on = false; } };
static BinarySensor co2_fault;
static Output status_led_out;
static bool g_led_test = false;
#define id(x) (x)

static void tick() {
/*LED*/
}

static int bad = 0;
// n ticks in one condition; strobe = must alternate starting lit, else must stay dark
static void phase(const char *name, bool fault, bool test, bool strobe) {
  co2_fault.state = fault; g_led_test = test;
  int lit = 0, wrong = 0; bool prev = status_led_out.on;
  for (int i = 0; i < 20; i++) {
    tick();
    bool on = status_led_out.on;
    lit += on;
    if (strobe ? (on == prev) : on) wrong++;
    prev = on;
  }
  bool ok = wrong == 0 && lit == (strobe ? 10 : 0);
  printf("  %s %-28s lit %2d/20, wrong ticks %d\n", ok ? "ok  " : "FAIL", name, lit, wrong);
  bad += !ok;
}

int main() {
  phase("healthy", false, false, false);
  phase("fault on", true, false, true);
  phase("fault cleared", false, false, false);
  phase("test running", false, true, true);
  phase("test ended", false, false, false);
  phase("fault + test", true, true, true);
  phase("both cleared", false, false, false);
  phase("fault again (after a test)", true, false, true);
  printf("RESULT: %s\n", bad ? "FAIL" : "PASS");
  return bad ? 1 : 0;
}
"""

FAULTS = [
    (
        "L1 test ignored",
        "(id(co2_fault).state || id(g_led_test))",
        "(id(co2_fault).state)",
    ),
    ("L2 fault ignored", "(id(co2_fault).state || id(g_led_test))", "(id(g_led_test))"),
    ("L3 steady, no strobe", "&& !lit;", ";"),
    (
        "L4 inverted output",
        "if (lit) id(status_led_out)",
        "if (!lit) id(status_led_out)",
    ),
]

src_path, work = sys.argv[1], sys.argv[2]
src = open(src_path, encoding="utf-8").read()


def led_lambda(text):
    cfg = yaml.load(text, Loader=TagIgnoringLoader)
    entry = cfg["interval"][1]
    lams = [a["lambda"] for a in entry["then"] if "lambda" in a]
    assert entry["interval"] == "100ms" and len(lams) == 1, entry
    assert "status_led_out" in lams[0], lams[0]
    return lams[0]


def sim(text, tag):
    cpp, exe = os.path.join(work, tag + ".cpp"), os.path.join(work, tag + ".exe")
    open(cpp, "w", encoding="utf-8", newline="\n").write(
        CPP.replace("/*LED*/", led_lambda(text))
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
    return ("PASS" if r.returncode == 0 else "FAIL"), r.stdout.strip().splitlines()


os.makedirs(work, exist_ok=True)
bad = 0
verdict, out = sim(src, "led_clean")
print("clean                    -> %s  (want PASS)" % verdict)
for line in out:
    print("    " + line)
bad += verdict != "PASS"
for name, old, new in FAULTS:
    n = src.count(old)
    if n != 1:
        print("%-24s -> SPAN COUNT %d (want 1)" % (name, n))
        bad += 1
        continue
    verdict, out = sim(src.replace(old, new), "led_" + name.split()[0])
    print("%-24s -> %s  (want FAIL)" % (name, verdict))
    for line in [x for x in out if x.lstrip().startswith("FAIL")][:2]:
        print("    " + line)
    bad += verdict != "FAIL"
print(
    "LED: %s (%d of %d directions wrong)"
    % ("PASS" if bad == 0 else "FAIL", bad, len(FAULTS) + 1)
)
sys.exit(1 if bad else 0)
