# **Fremake Canopy**

Through the fre-cli, `fre make` can be used to create and run a code checkout script and compile a model.

## **Usage (Users)**

* Refer to fre-cli README.md for foundational fre-cli usage guide and tips.
* Fremake package repository located at: https://gitlab.gfdl.noaa.gov/portable_climate/fremake_canopy/-/tree/main

### **Subtools Guide**

1)  **fre make**
    - configure
        - Postprocessing yaml configuration
        - Minimal Syntax: `fre pp configure -y [user-edit yaml file]`
        - Module(s) needed: n/a
        - Example: `fre pp configure -y /home/$user/pp/ue2/user-edits/edits.yaml`



Currently, running fre make create checkout creates 'test' directory and runs correctly if ran with the '-e' flag on initial call. However, if it's already been ran but with the '-e' flag, meaning that the testdir is already created, running it again with '-e' doesnt' seem to run the checkout script.
