## fre run
This tool is still under development and not yet ready for use

## YAML configurations
- `model.yaml`
- `layouts.yaml`
- `input_datasets.yaml`
- `settings.yaml`
- `runtime_experiment.yaml`

```mermaid
---
config:
  flowchart:
    wrappingWidth: '500'
---
flowchart LR
    1[Model yaml]
    subgraph model_yaml_runtime_configs
        direction LR
        2["platforms.yaml (tbd)"]
        3[settings.yaml
            - experiment runtime and postprocessing settings]
        4[layouts.yaml]
        5[input_datasets.yaml]
        6[run_experiment.yaml]
    end
    1 -.- model_yaml_runtime_configs

2 --> platform_info
3 --> experiment_settings_info
4 --> layouts_info
5 --> input_datasets_info
6 --> experiment_info
```
