OUTPUT_PATH=brackets/scenario_v2_l3_a
rm -rf $OUTPUT_PATH
python generate_random_brackets.v2.py\
    --output-path $OUTPUT_PATH\
    --n-trials 250\
    --reverse-miss-pct-2FG 0.01\
    --reverse-make-pct-2FG 0.01\
    --reverse-miss-pct-3FG 0.02\
    --reverse-make-pct-3FG 0.02\
    --reverse-miss-pct-FT 0.01\
    --reverse-make-pct-FT 0.01
