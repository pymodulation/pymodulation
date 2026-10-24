#
# test_documentation.py
#
# Copyright The PyModulation Contributors.
#
# This file is part of PyModulation library.
#
# PyModulation library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyModulation library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PyModulation library. If not, see <http://www.gnu.org/licenses/>.
#
#

from pathlib import Path
import re
import textwrap

import pytest

USAGE = Path(__file__).resolve().parents[1] / "docs" / "usage.rst"

def usage_examples():
    """Extract indented Python blocks, preserving their source line numbers."""
    source = USAGE.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^\.\. code-block:: python[ \t]*\n"
        r"(?P<code>(?:[ \t]+[^\n]*\n|[ \t]*\n)+)",
        re.MULTILINE,
    )
    examples = []
    for match in pattern.finditer(source):
        line = source.count("\n", 0, match.start("code")) + 1
        code = textwrap.dedent(match.group("code"))
        examples.append(pytest.param(line, code, id=f"usage.rst:{line}"))
    if not examples:
        raise ValueError(f"No Python usage examples found in {USAGE}")
    return examples

@pytest.mark.parametrize("line, code", usage_examples())
def test_usage_example(line, code):
    # Separate namespaces keep examples independent. Padding makes tracebacks
    # point to the original documentation lines, including assertion failures.
    namespace = {"__name__": "__main__"}
    exec(compile("\n" * (line - 1) + code, str(USAGE), "exec"), namespace)
