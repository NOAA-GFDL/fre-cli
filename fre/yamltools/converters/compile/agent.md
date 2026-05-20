### Compile XML to YAML Converter 

QUESTION:
1.  Is it better to print out a generic platform.yaml than convert it?  
    It seems like the content of platform.yaml is very different from platform.xml
2.  How to handle csh blocks?
3.  How to handle CDATA?
4.  How to handle yaml anchors?

You are a xml-to-yaml converter that converts files in xml format to yaml format.

** Example **
Study this example:

For this xml:  
<experiment name="$(AM5_VERSION)_compile">
    <description>Experiment to build executable. See git log for source code provenance.</description>      
    <component name="mom6" requires="fms" paths="mom6/src/MOM6/config_src/{infra/FMS2,memory/dynamic_nonsymmetric,drivers/FMS_cap,external} mom6/src/MOM6/src/{*,*/*}" >
        <source versionControl="git" root="https://github.com/NOAA-GFDL">
            <codeBase version="2023.01"> ocean_BGC.git </codeBase>
            <csh><![CDATA[
                git clone -b dev/gfdl https://github.com/NOAA-GFDL/MOM6-examples.git mom6	      
                test -e mom6/.datasets
                if ($status != 0) then
                    echo ""; echo "" ; echo "   WARNING:  .datasets link in MOM6 examples directory is invalid"; echo ""; echo ""
                endif
            ]]></csh>
        </source>
        <compile doF90Cpp="yes">
            <cppDefs><![CDATA[ $(F2003_FLAGS) -DMAX_FIELDS_=100 -DNOT_SET_AFFINITY ]]></cppDefs>
            <makeOverrides>OPENMP=""</makeOverrides> 
        </compile>
    </component>

the converted yaml looks like:

compile:
  experiment:  !join [*AM5_VERSION, "_compile"]
  container_addlibs:
  baremetal_linkerflags:
  src:
    - component:  "mom6"
      repo: "https://github.com/NOAA-GFDL/ocean_GBC.git"
      branch: 2023.01
      paths: ["mom6/src/MOM6/config_src/infra/FMS2",
              "mom6/src/MOM6/config_src/memory/dynamic_nonsymmetric",
              "mom6/src/MOM6/config_src/drivers/FMS_cap",
              "mom6/src/MOM6/config_src/external",
              "mom6/src/MOM6/src/*",
              "mom6/src/MOM6/src/*/*"]
      cppdefs: "

** yaml format **
The xml must be converted to a yaml file that follows the json schema in 

https://github.com/NOAA-GFDL/gfdl_msd_schemas/blob/main/FRE/fre_make.json


** xml format **
Study this example xml:


There may be multiple <experiment> sections in the xml file.  
There may be multiple <component> sections under a <experiment>

** guide **
Here's how the xml elements and attributes map to yaml keys




