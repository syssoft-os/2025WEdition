 ## ORWC Benchmark

 Build and run the benchmark:

 ```bash
 make
 ./build/orwc
 ```

 Notes:
 - Artifacts (objects and executable) are placed in `build/`.
 - Results are printed to stdout and saved to `orwc_benchmark.csv` in the project root.

 ## Plot
 uv is recomended to create an manage the python environemnt
 ```
 cd plot
 uv venv
 uv pip install -r requirements.txt
 uv run plot.py ../orwc_benchmark.csv
 ```