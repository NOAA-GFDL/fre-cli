# **Frepp Canopy**
_Brief description of tool group's purpose._

* [Tool Group] Supports:
   - _List_
   - _of_
   - _supported_
   - _features_

* **_Any notes/warnings for user_**

The [tool group] fre-cli tools are described below ([Subcommands](#subcommands)) as well as a Guide on the order in which to use them (Guide).

## **Usage (Users)**
* Refer to fre-cli [README.md](https://github.com/NOAA-GFDL/fre-cli/blob/main/README.md) for foundational fre-cli usage guide and tips.
* [tool group] package repository located at: _insert permalink_


## Subcommands
- `fre [tool group] [subcommand] [options]`
   - Purpose: _Insert subcommand purpose_
   - Options:
        - `-[short command], --[long command] [name of argument] (required/not required)`
## Guide
### **[Certain type of build/run]:**
```bash
# Short description of subcommand 1
fre [tool group] [subcommand] -[short/long command 1] [argument(s) 1] -[short/long command 2] [argument(s) 2] etc.

# Short description of subcommand 2
fre [tool group] [subcommand] -[short/long command 1] [argument(s) 1] -[short/long command 2] [argument(s) 2] etc.

# Short description of subcommand 3
fre [tool group] [subcommand] -[short/long command 1] [argument(s) 1] -[short/long command 2] [argument(s) 2] etc.

etc.
```
### **PP Wrapper Decision Tree**
![pp_wrapper_decsiontree](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/d3eaa237-1e29-4922-9d83-8d9d11925c54)

### **Tests**

To `fre pp` tests, return to root directory of the fre-cli repo and call just those tests with

    python -m pytest fre/pp/tests/[test script.py]

Or run all tests with

    python -m pytests fre/pp/tests
