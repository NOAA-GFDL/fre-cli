User plug-in scripts run custom code at defined points in the postprocessing workflow. Three
types are supported: refineDiag and preAnalysis scripts run on raw history files before
postprocessing; legacy cshell analysis scripts run after postprocessing on processed output.

refineDiag scripts
------------------
refineDiag scripts are user-provided cshell scripts that run on raw history files before
postprocessing and produce new "spoofed" history files. These new files are then postprocessed
alongside native model output, allowing users to define custom derived diagnostics as if they were
native model output.

Configure refineDiag scripts under ``postprocess.refinediag``:

.. code-block:: console

 directories:
   refined_history_dir: /path/to/refined/history/output

 postprocess:
   refinediag:
     my_script_label:
       script: /absolute/path/to/script.csh
       inputs:
         - atmos_month
       outputs:
         - atmos_month_refined
       do_refinediag: true

Output file names must differ from any existing history file names. Multiple refineDiag scripts
can be defined, each under its own label.

preAnalysis scripts
-------------------
preAnalysis scripts are user-provided cshell scripts that run on raw history files before
postprocessing, similar to refineDiag scripts, but do not produce new history files. They are
suited for user-specific tasks such as populating custom databases or producing output outside the
FRE managed directory structure.

Configure preAnalysis scripts under ``postprocess.preanalysis``:

.. code-block:: console

 postprocess:
   preanalysis:
     my_preanalysis_label:
       script: /absolute/path/to/script.csh
       inputs:
         - atmos_month
       do_preanalysis: true

Legacy cshell analysis scripts
-------------------------------
Legacy cshell analysis scripts are user-provided scripts that run after postprocessing using
postprocessed output to produce figures or other user-specified output. Unlike refineDiag and
preAnalysis scripts, analysis scripts have no downstream dependencies in the FRE postprocessing
workflow.

Analysis scripts are configured under the top-level ``analysis:`` key, separate from
``postprocess:``:

.. code-block:: console

 directories:
   analysis_dir: /path/to/analysis/scripts

 analysis:
   my_analysis_label:
     legacy:
       script: /path/to/analysis_script.csh
     required:
       data_frequency: mon
       date_range: ['1979', '2020']

Each analysis script is associated with one data frequency. For scripts that span multiple
components, associate the script with the component that has the longest run interval.

A new Python-native analysis framework is being developed for the FRE 2026.02 release.
