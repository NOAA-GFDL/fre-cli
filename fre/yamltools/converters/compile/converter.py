import re

import xml.etree.ElementTree as ET
import argparse
import yaml

def parse_component(component: ET.Element) -> dict[str, str | list] | None:
    """Parse a single <component> XML element into a YAML-friendly dictionary."""

    def clean_text(string: str) -> list[str] | None:        
        clean_string = re.sub(r'\s+', ' ', string.replace('\t', '')).strip()
        if clean_string:
            return clean_string
        return None

    def get_compile_flag(flag: str) -> str | None:
        """
        Return text for cppDefs or makeOverrides in compile element block
        For example, 
        <compile>
            <cppDefs>-DDEBUG -Iinclude</cppDefs>
            <makeOverrides>-j8</makeOverrides>
        </compile> 
        returns 
        "-DDEBUG, -Iinclude" for get_compile_flag("cppDefs") 
        "-j8" for get_compile_flag("makeOverrides"), or 
        None if the flag is not defined.
        """
        compile_elem = component.find('compile')
        if compile_elem is not None:
            elem = compile_elem.find(flag)
            if elem is not None:
                elem_text = clean_text(elem.text)
                if elem_text:
                    return elem_text
        return None

    def get_paths() -> list[str] | None:
        """
        Return parsed component paths from the paths attribute.
        For example,
        <component name="am5_phys" paths="am5_phys/atmos_param am5_phys/atmos_shared"/>
        returns 
        ["am5_phys/atmos_param", "am5_phys/atmos_shared"] or 
        None if paths is not defined.
        """
        paths = component.attrib.get('paths')
        if paths and paths.strip():
            return [p.strip() for p in paths.split() if p.strip()]
        return None

    def get_requires() -> list[str] | None:
        """
        Return parsed component dependencies from the requires attribute.
        For example,
        <component name="am5_phys" requires="FMS rte-rrtmpgp rte-ecckd"/>
        returns 
        ["FMS", "rte-rrtmpgp", "rte-ecckd"] or 
        None if requires is not defined.
        """
        requires = component.attrib.get('requires')
        if requires and requires.strip():
            return [r.strip() for r in requires.split() if r.strip()]
        return None

    def get_doF90Cpp() -> bool | None:
        """
        Parse doF90Cpp from the compile block into a boolean when present.
        For example,
        <compile doF90Cpp="yes"/>
        returns True or 
        None if doF90Cpp is not defined.
        """
        compile_elem = component.find('compile')
        if compile_elem is not None:
            val = compile_elem.attrib.get('doF90Cpp')
            map_to_bool = {'yes': True, 'no': False}
            if val is not None:
                return map_to_bool.get(val.strip().lower())

        return None

    def get_additional_instructions() -> list[str] | None:
        """Extract source/csh instructions as non-empty lines."""
        source_elem = component.find('source')
        if source_elem is not None:
            csh_elem = source_elem.find('csh')
            if csh_elem is not None and csh_elem.text:
                cleaned_lines = []
                for line in csh_elem.text.splitlines():
                    # Remove tabs and normalize extra spaces
                    clean_line = clean_text(line)
                    if clean_line is not None:
                        cleaned_lines.append(clean_line)
                return cleaned_lines if cleaned_lines else None
        return None

    def get_repo_and_branch() -> tuple[str | None, str | None]:
        """
        Build repo URL and branch/version from source/codeBase tags.
        For example,
        <source versionControl="git" root="https://github.com/NOAA-GFDL">
          <codeBase version="2026.01"> FMS.git </codeBase>
        </source>
        returns 
        ("https://github.com/NOAA-GFDL/FMS.git", "2026.01") 
        """

        repo = None
        branch = None
        source_elem = component.find('source')
        if source_elem is not None:
            root = source_elem.attrib.get('root')
            codebase_elem = source_elem.find('codeBase')
            if root and codebase_elem is not None and codebase_elem.text:
                repo = f"{root.rstrip('/')}/{codebase_elem.text.strip().strip()}"
                branch = codebase_elem.attrib.get('version')
        return repo, branch

    repo, branch = get_repo_and_branch()
    component_name = component.attrib.get('name')
    if component_name is not None:
        component_name = component_name.strip() or None

    d = {
        'component': component_name,
        'repo': repo,
        'branch': branch,
        'paths': get_paths(),
        'requires': get_requires(),
        'cppdefs': get_compile_flag('cppDefs'),
        'makeOverrides': get_compile_flag('makeOverrides'),
        'doF90Cpp': get_doF90Cpp(),
        'additionalInstructions': get_additional_instructions(),
    }
    # Remove None values
    return {k: v for k, v in d.items() if v is not None}

def parse_experiment(experiment: ET.Element) -> [str, str | list]:
    """Parse one <experiment> element into the compile YAML object."""
    components = [parse_component(c) for c in experiment.findall('component')]
    return {
        'experiment': experiment.attrib.get('name'),
        'container_addlibs': '',
        'baremetal_linkerflags': '',
        'src': components if components else [],
    }

def xml_to_yaml(xml_path: str, yaml_path: str, experiment_name: str = None):
    """
    Convert compile XML to YAML.
    All experiments in the XML will be converted if experiment_name is None
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    experiments = root.findall('experiment')
    out = {}
    for exp in experiments:
        if experiment_name and exp.attrib.get('name') != experiment_name:
            continue
        yamldict = {'compile': parse_experiment(exp)}
        if experiment_name:
            break
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yamldict, f, sort_keys=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert compile XML to YAML")
    parser.add_argument("-x", "--xmlfile", required=True, help="Input XML file")
    parser.add_argument("-o", "--output", required=True, help="Output YAML file")
    parser.add_argument("-e", "--experiment", default=None, help="Experiment name (optional)")
    args = parser.parse_args()
    
    xml_to_yaml(args.xmlfile, args.output, args.experiment)
    print(f"\nConverted {args.xmlfile} to {args.output}.")
    print(f"Experiment: {args.experiment if args.experiment else 'All experiments'}")
    print("_______________")
    print("WARNING:  THIS CONVERTER OUTPUTS CLOSE-ENOUGH COMPILE YAML")
    print("PLEASE CHECK THE FOLLOWING:")
    print(" * PATHS")
    print(" * CPPDEFS AND OTHER FLAGS")
    print(" * ADDITIONALINSTRUCTIONS")
    print(" * PLEASE ADD IN THE APPROPRIATE ANCHORS")
