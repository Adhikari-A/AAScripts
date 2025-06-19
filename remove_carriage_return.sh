#!/bin/bash
#
# It reads the input file *line-by-line*, removes every carriage-return (\r)
# and newline (\n) **inside each line**, then writes the cleaned text to
# the output file.

infile="$1"
outfile="$2"

if [[ -z $infile || -z $outfile ]]
then
  echo "Usage:"
  echo "./remove_carriage_return.sh IN_FILE OUT_FILE"
  echo "IN_FILE: contains annoying carriage return characters"
  echo "OUT_FILE: where the nice clean content wil be saved"
  exit 0
fi

if [ ! -f "$infile" ]
then
  echo "This is not a file:"
  echo "$infile"
  echo "Exiting."
  exit 1
fi

# Use a temporary file so we don’t clobber the output if something goes wrong.
tmp=$(mktemp)

while IFS= read -r line || [ -n "$line" ]; do
    # Remove both \r and \n from the current line, then re-add a single \n.
    printf '%s\n' "$(printf '%s' "$line" | tr -d '\r\n')" >> "$tmp"
done < "$infile"

mv -- "$tmp" "$outfile"
echo "Wrote cleaned copy to: $outfile"
