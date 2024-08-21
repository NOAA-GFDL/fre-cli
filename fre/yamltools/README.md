## FRE yamltools
### Tools:
- `combine-yaml.py`: creates a `combined-[experiment name].yaml` file in which the [model].yaml, compile.yaml, platforms.yaml, [experiment].yaml, and [analysisscript].yaml are merged

### **Tests**

To run `fre yamltools` test scripts, return to root directory of the fre-cli repo and call those tests with

    python -m pytest fre/yamltools/tests/[test script.py]

Or run all tests with

    python -m pytest fre/yamltools/tests
