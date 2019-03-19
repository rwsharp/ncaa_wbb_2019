OUTPUT_PATH=brackets/scenario_a
rm -rf $OUTPUT_PATH
python generate_random_brackets.py\
    --data-path "~/Dropbox/Uncertain Principles/Articles/NCAAWomen2019/data"\
    --output-path $OUTPUT_PATH\
    --n-trials 250\
    --shots 2\
    --pm 1 1\
    --points 15 33 20
