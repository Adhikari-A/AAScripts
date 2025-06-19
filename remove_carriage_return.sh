#!/bin/bash
#
# It reads the input file *line-by-line*, removes every carriage-return (\r)
# and newline (\n) **inside each line**, then writes the cleaned text to
# the output file.

set -euo pipefail

infile=${1:?please give an input file}
outfile=${2:?please give an output file}

# Use a temporary file so we don’t clobber the output if something goes wrong.
tmp=$(mktemp)

while IFS= read -r line || [ -n "$line" ]; do
    # Remove both \r and \n from the current line, then re-add a single \n.
    printf '%s\n' "$(printf '%s' "$line" | tr -d '\r\n')" >> "$tmp"
done < "$infile"

mv -- "$tmp" "$outfile"
echo "Wrote cleaned copy to: $outfile"
