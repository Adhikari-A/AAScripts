#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $(basename "$0") <file> <n_pieces>"
  echo "Splits <file> into <n_pieces> files by line count."
  echo "The (single) larger piece (remainder) is placed in the first output file."
}

if [[ $# -ne 2 ]]; then
  usage >&2
  exit 2
fi

infile=$1
n=$2

if [[ ! -f "$infile" ]]; then
  echo "Error: file not found: $infile" >&2
  exit 1
fi

if [[ ! "$n" =~ ^[0-9]+$ ]] || [[ "$n" -le 0 ]]; then
  echo "Error: n_pieces must be a positive integer, got: $n" >&2
  exit 1
fi

echo "Splitting files $infile in $n pieces."

# Total number of lines in the input file
total_lines=$(wc -l < "$infile")
total_lines=${total_lines##*( )}  # trim leading spaces (just in case)

# Compute sizes
base=$(( total_lines / n ))
rem=$(( total_lines % n ))

# Output naming
# e.g. input.txt.part01, input.txt.part02, ...
out_prefix="${infile}."
pad_width=${#n}

# Helper: make a zero-padded index like 01, 02, ...
fmt_idx() {
  local i=$1
  printf "%0${pad_width}d" "$i"
}

start_line=1

for ((i=0; i<n; i++)); do
  if (( i == 1 )); then
    piece_lines=$(( base + rem ))
  else
    piece_lines=$base
  fi

  out_file="${out_prefix}$(fmt_idx "$i")"

  # If there are more pieces than lines, some pieces will be empty.
  if (( piece_lines <= 0 )); then
    : > "$out_file"
    continue
  fi

  end_line=$(( start_line + piece_lines - 1 ))

  # Extract the line range [start_line, end_line]
  sed -n "${start_line},${end_line}p" "$infile" > "$out_file"

  start_line=$(( end_line + 1 ))
done
echo "Done."
