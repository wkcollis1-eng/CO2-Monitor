"""Extract the CO2 watchdog lambdas VERBATIM from co2-node-common.yaml and wrap them
in a host C++ test (stubs for millis/App/global_preferences). The lambda text is
never retyped here (R10): the test runs exactly what the firmware will run.

  python gen.py <co2-node-common.yaml> <out.cpp>
"""

import os
import sys
import yaml


class TagIgnoringLoader(yaml.SafeLoader):
    pass


def _any_tag(loader, suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


TagIgnoringLoader.add_multi_constructor("!", _any_tag)

cfg = yaml.load(open(sys.argv[1], encoding="utf-8"), Loader=TagIgnoringLoader)
on_boot = [a["lambda"] for a in cfg["esphome"]["on_boot"]["then"] if "lambda" in a]
scd30 = [s for s in cfg["sensor"] if s.get("platform") == "scd30"]
on_value = [a["lambda"] for a in scd30[0]["co2"]["on_value"]["then"] if "lambda" in a]
tick = [a["lambda"] for a in cfg["interval"][0]["then"] if "lambda" in a]
filters = scd30[0]["co2"]["filters"]
assert len(on_boot) == 1 and len(on_value) == 1 and len(tick) == 1, (
    on_boot,
    on_value,
    tick,
)
# the stub below models exactly this filter
assert filters == [{"filter_out": 0.0}], filters

body = open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "sim.cpp.in"),
    encoding="utf-8",
).read()
body = (
    body.replace("/*ON_BOOT*/", on_boot[0])
    .replace("/*ON_VALUE*/", on_value[0])
    .replace("/*TICK*/", tick[0])
)
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(body)
print(
    "extracted: on_boot %d, on_value %d, tick %d lines"
    % tuple(len(x[0].splitlines()) for x in (on_boot, on_value, tick))
)
