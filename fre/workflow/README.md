# FRE workflow

The`fre workflow` toolset allows user to clone, install, and run a cylc workflow.

## Quickstart
From the top-level dircetory of the fre-cli repository:
```
# Checkout/clone the post-processing workflow repository
fre workflow checkout -y fre/workflow/tests/AM5_example/am5.yaml -e c96L65_am5f7b12r1_amip_TESTING --application pp
```

## Subtools
- `fre workflow checkout [options]`
   - Purpose: Clone the specified workflow repository from the settings.yaml, associated with the application passed.
   - Options:
        - `-y, --yamlfile [model yaml] (str; required)`
        - `-e, --experiment [experiment name] (str; required)`
        - `-a, --application [ run | pp ] (str; required)`
        - `--target-dir [target location where workflow will be cloned] (str; optional; default is ~/.fre-workflows`
        - `--force-checkout (bool; optional)`
