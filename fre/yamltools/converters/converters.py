from pathlib import Path
import re
import yaml

try:
    from .xml import XML
except ImportError:
    from xml import XML


class CompileConverter(XML):
    """
    Converter class to parse compile experiment XML blocks and convert to YAML dictionaries.
    """
    
    def __init__(self, xmlfile: str|Path, experiment_name: str = None):

        super().__init__(xmlfile)
        self.experiments = self.get_experiments(experiment_name)
        self.yaml_dicts = {}


    def get_experiments(self, experiment_name: str = None):
        """
        Parse the XML and save each compile experiment block 
        """

        #prettify name
        prettify = lambda name: name.strip().replace("$(", "").replace(")", "")

        # if a particular experiment is not provided, get all compile experiments in xml    
        experiments = self.get_elements("experiment", self.soup, name=experiment_name)
        
        if experiments:
            experiment_dict = {}
            for experiment in experiments:
                name = prettify(self.get_attributes("name", experiment))
                experiment_dict[name] = experiment
            return experiment_dict

        raise RuntimeError("Cannot find experiments")


    def convert(self):        
        """
        Convert XML content to YAML dictionary
        """
        
        for experiment_name, experiment_content in self.experiments.items():                    
            compile_yaml = {"compile": {
                "experiment": self.get_attributes("name", experiment_content),
                "container_addlibs": "",
                "baremetal_linkerflags": "",
                "src": self.parse_components(experiment_content)}
            }
            self.yaml_dicts[experiment_name] = compile_yaml                    
            self.write_yaml(compile_yaml, "compile_"+experiment_name +".yaml")
                
            
    def parse_components(self, xml_content, component_name: str = None):
        """
        Parses component blocks to yaml dictionaries.  For example, converts 
       
        <component name="atmos_cubed_sphere" 
                   paths="GFDL_atmos_cubed_sphere/model, GFDL_atmos_cubed_sphere/driver/SHiELD/cloud_diagnosis.F90", 
                   requires="fms am5_phys">
          <source versionControl="git" root="https://github.com/NOAA-GFDL">
            <codeBase version="2024.01_am5">GFDL_atmos_cubed_sphere.git</codeBase>
          </source>
          <compile>
            <makeOverrides>USE_R4=$(USE_MIXED_MODE) ISA="-march=core-avx2 -qno-opt-dynamic-align"</makeOverrides>
            <cppDefs>$(F2003_FLAGS) -DSPMD -DCLIMATE_NUDGE</cppDefs>
          </compile>
        </component>
       
        to 
       
        {
        component: atmos_cubed_sphere
        repo: https://github.com/NOAA-GFDL/GFDL_atmos_cubed_sphere.git
        branch: 2024.01_am5
        paths: [GFDL_atmos_cubed_sphere/model, GFDL_atmos_cubed_sphere/driver/SHiELD/cloud_diagnosis.F90]
        requires: [fms, am5_phys]
        otherFlags: [$(F2003_FLAGS) -DSPMD -DCLIMATE_NUDGE]
        makeOverrides : [USE_R4=$(USE_MIXED_MODE), ISA="-march=core-avx2, -qno-opt-dynamic-align"]
        }
        """

        components = self.get_elements("component", xml_content, name=component_name)
        if components is None:
            return None
            
        parsed_components = []
        for component in components:

            codebase = self.get_elements("codeBase", component, find_all=False)
            source = self.get_elements("source", component, find_all=False)
            cppdefs = self.get_elements("cppDefs", component, find_all=False)
            compile_ = self.get_elements("compile", component, find_all=False)
            make_overrides = self.get_elements("makeOverrides", component, find_all=False)
            csh = self.get_elements("csh", component, find_all=False)

            #"repo": f"{self.get_attributes('root', source)}/{self.get_values(codebase)}",

            component_yaml = {
                "component": self.get_attributes("name", component),
                "repo": f"{self.get_attributes('root', source)}/{self.get_values(codebase)}",
                "branch": self.get_attributes("version", codebase),
                "paths": self.get_attributes("paths", component, tolist=True),
                "requires": self.get_attributes("requires", component, tolist=True),
                "otherFlags": self.get_attributes("includeDir", component, tolist=True),
                "cppdefs": self.get_values(cppdefs),
                "makeOverrides": self.get_values(make_overrides),
                "doF90Cpp": self.get_attributes("doF90Cpp", compile_),
                "additionalInstructions": self.get_values(csh, tolist=True, fieldsep="\n")
            }
            
            #remove None
            component_yaml = {key: value for key, value in component_yaml.items() if value is not None}
            parsed_components.append(component_yaml)
            
        return parsed_components


    def write_yaml(self, yamldict: dict, yamlfile: str|Path):           
        """
        Write YAML dictionary to file
        """

        with open(yamlfile, "w", encoding="utf-8") as openedfile:
            yaml.dump(yamldict, openedfile, sort_keys=False)


class PlatformConverter(XML):
    """
    Converter class to parse platform XML blocks and convert to YAML dictionaries.
    """

    def __init__(self, xmlfile: str | Path):

        super().__init__(xmlfile)
        self.platforms = self.get_platforms()
        self.yaml_dicts = {}


    def get_platforms(self):
        """
        Parse XML and save each platform block in declaration order.
        """

        platforms = self.get_elements("platform", self.soup)
        if platforms is None:
            raise RuntimeError("Cannot find platforms")

        platform_dict = {}
        for platform in platforms:
            platform_name = self.get_attributes("name", platform)
            if platform_name is None:
                raise RuntimeError("Found <platform> element with no name attribute")
            if platform_name in platform_dict:
                raise RuntimeError(f"Duplicate platform name found: {platform_name}")
            platform_dict[platform_name] = platform

        return platform_dict


    def convert(self):
        """
        Convert all XML platform content to one YAML dictionary.
        """

        parsed_platforms = []
        for platform_name in self.platforms:
            parsed_platforms.append(self.parse_platform(platform_name))

        self.yaml_dicts = {"platforms": parsed_platforms}
        self.write_yaml(self.yaml_dicts, "platforms.yaml")


    def parse_platform(self, platform_name: str, visited: set | None = None):
        """
        Parse one platform, resolving xi:include references as base content first,
        then applying local values as overrides.
        """

        if visited is None:
            visited = set()

        if platform_name in visited:
            raise RuntimeError(f"Circular xi:include reference detected for {platform_name}")

        if platform_name not in self.platforms:
            raise RuntimeError(f"Cannot resolve xi:include reference: {platform_name}")

        visited.add(platform_name)
        platform_element = self.platforms[platform_name]

        platform_yaml = {"name": platform_name}

        include_names = self.parse_xincludes(platform_element)
        unresolved_includes = []
        for include_name in include_names:
            if include_name in self.platforms:
                included_platform = self.parse_platform(include_name, visited=visited.copy())
                platform_yaml = self.merge_platform_dicts(platform_yaml, included_platform)
            else:
                unresolved_includes.append(include_name)

        current_platform = self.parse_platform_body(platform_element)
        platform_yaml = self.merge_platform_dicts(platform_yaml, current_platform)

        if include_names:
            platform_yaml["includes"] = include_names
        if unresolved_includes:
            platform_yaml["unresolvedIncludes"] = unresolved_includes

        return self.drop_empty_fields(platform_yaml)


    def parse_platform_body(self, platform_element):
        """
        Parse direct content under a platform block (without include inheritance).
        """

        #fre_version = self.get_values(self.get_elements("freVersion", platform_element, find_all=False))
        project = self.get_values(self.get_elements("project", platform_element, find_all=False))
        compiler = self.parse_compiler(platform_element)
        directory = self.parse_directory(platform_element)
        properties = self.parse_properties(platform_element)
        csh = self.parse_text_block(platform_element, "csh")

        platform_yaml = {
            "freVersion": fre_version,
            "project": project,
            "compiler": compiler.get("compiler"),
            "compilerVersion": compiler.get("compilerVersion"),
            "compilerType": compiler.get("compilerType"),
            "envSetup": self.derive_env_setup(compiler),
            "mkTemplate": self.derive_mk_template(platform_element, compiler),
            "modelRoot": self.derive_model_root(platform_element, project, directory),
            "directory": directory,
            "properties": properties,
            "csh": csh,
        }

        # Preserve known convenience fields used by platform YAML workflows.
        platform_yaml.update(self.derive_container_settings(platform_element))

        return self.drop_empty_fields(platform_yaml)


    def parse_compiler(self, platform_element):
        """
        Parse compiler attributes and normalize a friendly compiler name.
        """

        compiler_element = self.get_elements("compiler", platform_element, find_all=False)
        compiler_type = self.get_attributes("type", compiler_element)
        compiler_version = self.get_attributes("version", compiler_element)

        compiler_name = None
        if compiler_type:
            compiler_name = compiler_type.replace("_", "-").split("-")[0].strip()

        return self.drop_empty_fields({
            "compiler": compiler_name,
            "compilerType": compiler_type,
            "compilerVersion": compiler_version,
        })


    def parse_directory(self, platform_element):
        """
        Parse directory subfields under <directory>.
        """

        directory_element = self.get_elements("directory", platform_element, find_all=False)
        if directory_element is None:
            return None

        directory = {
            "stem": self.get_attributes("stem", directory_element),
            "include": self.get_values(self.get_elements("include", directory_element, find_all=False)),
            "archive": self.get_values(self.get_elements("archive", directory_element, find_all=False)),
            "analysis": self.get_values(self.get_elements("analysis", directory_element, find_all=False)),
        }

        return self.drop_empty_fields(directory)


    def parse_properties(self, platform_element):
        """
        Parse all <property name="..." value="..."/> blocks into a dictionary.
        """

        properties = self.get_elements("property", platform_element)
        if properties is None:
            return None

        parsed_properties = {}
        for property_element in properties:
            property_name = self.get_attributes("name", property_element)
            property_value = self.get_attributes("value", property_element)

            if property_name is not None:
                parsed_properties[property_name] = property_value if property_value is not None else ""

        return parsed_properties if parsed_properties else None


    def parse_text_block(self, platform_element, tag_name: str):
        """
        Parse free-form text blocks such as <csh>.
        """

        return self.get_values(self.get_elements(tag_name, platform_element, find_all=False))


    def parse_xincludes(self, platform_element):
        """
        Parse xi:include references and extract referenced platform names.
        """

        include_elements = self.get_elements("xi:include", platform_element)
        if include_elements is None:
            return []

        include_names = []
        for include_element in include_elements:
            xpointer = self.get_attributes("xpointer", include_element)
            if xpointer is None:
                continue

            include_name = self.extract_platform_name_from_xpointer(xpointer)
            if include_name is not None:
                include_names.append(include_name)

        return include_names


    def extract_platform_name_from_xpointer(self, xpointer: str):
        """
        Extract platform name from xpointer expression.
        """

        match = re.search(r"@name=['\"]([^'\"]+)['\"]", xpointer)
        if match:
            return match.group(1).strip()
        return None


    def derive_env_setup(self, compiler: dict):
        """
        Build a generic environment setup list from compiler fields.
        """

        if not compiler:
            return None

        env_setup = ["source $MODULESHOME/init/sh"]

        compiler_type = compiler.get("compilerType")
        compiler_version = compiler.get("compilerVersion")
        if compiler_type and compiler_version:
            env_setup.append(f"module load {compiler_type}/{compiler_version}")

        return env_setup


    def derive_mk_template(self, platform_element, compiler: dict):
        """
        Build a best-effort mkTemplate path using platform and compiler context.
        """

        platform_name = self.get_attributes("name", platform_element)
        if platform_name is None:
            return None

        compiler_type = compiler.get("compilerType") if compiler else None
        compiler_version = compiler.get("compilerVersion") if compiler else None

        if platform_name.startswith("ncrc") and compiler_type:
            site = platform_name.split(".")[0]
            compiler_stem = compiler_type.replace("_", "-")
            return f"/ncrc/home2/fms/local/opt/fre-commands/bronx-23/site/{site}/{compiler_stem}.mk"

        if platform_name.startswith("hpcme") and compiler and compiler.get("compiler"):
            major_version = ""
            if compiler_version:
                major_version = compiler_version.split(".")[0]
            compiler_token = compiler.get("compiler") + major_version
            return f"/apps/mkmf/templates/{platform_name.split('.')[0]}-{compiler_token}.mk"

        return None


    def derive_model_root(self, platform_element, project: str, directory: dict | None):
        """
        Build a generic modelRoot path for common site naming conventions.
        """

        platform_name = self.get_attributes("name", platform_element)
        if platform_name is None:
            return None

        stem = directory.get("stem") if directory else None

        if platform_name.startswith("ncrc5") and project and stem:
            return f"/gpfs/f5/{project}/scratch/${{USER}}/{stem}"

        if platform_name.startswith("ncrc6") and project and stem:
            return f"/gpfs/f6/{project}/scratch/${{USER}}/{stem}"

        if directory and directory.get("archive"):
            return directory["archive"]

        return None


    def derive_container_settings(self, platform_element):
        """
        Add generic container settings for platform names that imply container workflow.
        """

        platform_name = self.get_attributes("name", platform_element)
        if platform_name is None:
            return {}

        if platform_name.startswith("hpcme"):
            return {
                "RUNenv": "",
                "container": True,
                "containerBuild": "podman",
                "containerRun": "apptainer",
            }

        return {}


    def merge_platform_dicts(self, base: dict, override: dict):
        """
        Merge dictionaries recursively, with override values taking precedence.
        """

        if base is None:
            return override if override is not None else {}
        if override is None:
            return base

        merged = dict(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = self.merge_platform_dicts(merged[key], value)
            else:
                merged[key] = value
        return merged


    def drop_empty_fields(self, value):
        """
        Remove empty values recursively while keeping boolean False and numeric 0.
        """

        if isinstance(value, dict):
            cleaned = {}
            for key, item in value.items():
                normalized_item = self.drop_empty_fields(item)
                if normalized_item in (None, {}, []):
                    continue
                cleaned[key] = normalized_item
            return cleaned

        if isinstance(value, list):
            cleaned = [self.drop_empty_fields(item) for item in value]
            cleaned = [item for item in cleaned if item not in (None, {}, [])]
            return cleaned

        if isinstance(value, str):
            normalized = value.strip()
            return normalized if normalized else None

        return value


    def write_yaml(self, yamldict: dict, yamlfile: str | Path):
        """
        Write YAML dictionary to file.
        """

        with open(yamlfile, "w", encoding="utf-8") as openedfile:
            yaml.dump(yamldict, openedfile, sort_keys=False)


#xml = CompileConverter("./compile.xml")
#xml.convert()