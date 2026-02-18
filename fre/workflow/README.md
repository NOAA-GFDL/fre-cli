# FRE workflow
`fre workflow` provides subtools that help to clone, install, and run a workflow from a repository.

## Quickstart
From the root of the fre-cli repository, run:
```
# Checkout/clone the post-processing workflow repository
fre workflow checkout -y fre/workflow/tests/AM5_example/am5.yaml -e c96L65_am5f7b12r1_amip_TESTING -a pp
```

## Subtools
- `fre workflow checkout [options]`
   - Purpose: Clone the workflow repository/branch, depending on the application passed.
   - Options:
        - `-y, --yamlfile [model yaml] (str; required)`
        - `-e, --experiment [experiment name] (str; required)`
        - `-a, --application [ run | pp ] (str; required)`
