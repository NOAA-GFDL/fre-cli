import pytest
import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
import importlib.util

# Import functions from compile-converter (hyphenated module name)
spec = importlib.util.spec_from_file_location("compile_converter", "compile-converter.py")
compile_converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compile_converter)

parse_component = compile_converter.parse_component
parse_experiment = compile_converter.parse_experiment
xml_to_yaml = compile_converter.xml_to_yaml


class TestGetCompileFlag:
    """Test get_compile_flag nested function via parse_component."""
    
    def test_cpp_defs_present(self):
        """Test parsing cppDefs flag from compile block."""
        xml_str = '''
        <component name="test_comp">
            <compile>
                <cppDefs>  -DDEBUG   -Iinclude  </cppDefs>
            </compile>
        </component>
        '''
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert result['cppdefs'] == '-DDEBUG -Iinclude'
    
    def test_make_overrides_present(self):
        """Test parsing makeOverrides flag from compile block."""
        xml_str = '''
        <component name="test_comp">
            <compile>
                <makeOverrides>-j8</makeOverrides>
            </compile>
        </component>
        '''
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert result['makeOverrides'] == '-j8'
    
    def test_flag_not_defined(self):
        """Test when compile flag is not defined."""
        xml_str = '<component name="test_comp"><compile></compile></component>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert 'cppdefs' not in result  # Should be filtered out
        assert 'makeOverrides' not in result
    

class TestGetPaths:
    """Test get_paths nested function via parse_component."""
    
    def test_single_path(self):
        """Test parsing single path."""
        xml_str = '<component name="test" paths="am5_phys/atmos_param"/>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert result['paths'] == ['am5_phys/atmos_param']
    
    def test_multiple_paths(self):
        """Test parsing multiple space-separated paths."""
        xml_str = '<component name="test" paths="am5_phys/atmos_param   am5_phys/atmos_shared am5_phys/madeup"/>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert result['paths'] == ['am5_phys/atmos_param', 'am5_phys/atmos_shared', "am5_phys/madeup"]
        
    def test_paths_not_defined(self):
        """Test when paths attribute is missing."""
        xml_str = '<component name="test"/>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert 'paths' not in result
    
    def test_empty_paths_string(self):
        """Test when paths is empty string."""
        xml_str = '<component name="test" paths=""/>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert 'paths' not in result


class TestGetRequires:
    """Test get_requires nested function via parse_component."""
    
    def test_single_requirement(self):
        """Test parsing single requirement."""
        xml_str = '<component name="test" requires="FMS"/>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert result['requires'] == ['FMS']
    
    def test_multiple_requirements(self):
        """Test parsing multiple space-separated requirements."""
        xml_str = '<component name="test" requires="FMS      rte-rrtmpgp rte-ecckd"/>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert result['requires'] == ['FMS', 'rte-rrtmpgp', 'rte-ecckd']
        
    def test_requires_not_defined(self):
        """Test when requires attribute is missing."""
        xml_str = '<component name="test"/>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert 'requires' not in result
    
    def test_empty_requires_string(self):
        """Test when requires is empty string."""
        xml_str = '<component name="test" requires=""/>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert 'requires' not in result


class TestGetDoF90Cpp:
    """Test get_doF90Cpp nested function via parse_component."""
    
    def test_doF90Cpp_yes(self):
        """Test parsing doF90Cpp as 'yes'."""
        xml_str = '''
        <component name="test">
            <compile doF90Cpp="yes"/>
        </component>
        '''
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert result['doF90Cpp'] is True
    
    def test_doF90Cpp_no(self):
        """Test parsing doF90Cpp as 'no'."""
        xml_str = '''
        <component name="test">
            <compile doF90Cpp="no"/>
        </component>
        '''
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert result['doF90Cpp'] is False
        
    def test_doF90Cpp_not_defined(self):
        """Test when doF90Cpp is not defined."""
        xml_str = '<component name="test"><compile></compile></component>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert 'doF90Cpp' not in result


class TestGetAdditionalInstructions:
    """Test get_additional_instructions nested function via parse_component."""
    
    def test_single_instruction(self):
        """Test parsing single instruction."""
        xml_str = '''
        <component name="test">
            <source>
                <csh>echo "Building"</csh>
            </source>
        </component>
        '''
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert result['additionalInstructions'] == ['echo "Building"']
    
    def test_multiple_instructions(self):
        """Test parsing multiple instructions across lines."""
        xml_str = '''
        <component name="test">
            <source>
                <csh>
                        echo "Line 1"
                    echo       "Line 2"
                </csh>
            </source>
        </component>
        '''
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert result['additionalInstructions'] == ['echo "Line 1"', 'echo "Line 2"']
            
    def test_no_instructions(self):
        """Test when no instructions are defined."""
        xml_str = '<component name="test"><source></source></component>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert 'additionalInstructions' not in result


class TestGetRepoAndBranch:
    """Test get_repo_and_branch nested function via parse_component."""
    
    def test_valid_repo_and_branch(self):
        """Test parsing valid repo URL and branch."""
        xml_str = '''
        <component name="test">
            <source root="https://github.com/NOAA-GFDL">
                <codeBase version="2026.01">  FMS.git  </codeBase>
            </source>
        </component>
        '''
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert result['repo'] == 'https://github.com/NOAA-GFDL/FMS.git'
        assert result['branch'] == '2026.01'
    
    def test_repo_with_trailing_slash(self):
        """Test repo root with trailing slash."""
        xml_str = '''
        <component name="test">
            <source root="https://github.com/NOAA-GFDL/">
                <codeBase version="1.0">repo.git</codeBase>
            </source>
        </component>
        '''
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert result['repo'] == 'https://github.com/NOAA-GFDL/repo.git'
        
    def test_no_source_element(self):
        """Test when source element is missing."""
        xml_str = '<component name="test"/>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert 'repo' not in result
        assert 'branch' not in result
    
    def test_no_codebase_element(self):
        """Test when codeBase element is missing."""
        xml_str = '''
        <component name="test">
            <source root="https://github.com/NOAA-GFDL"/>
        </component>
        '''
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert 'repo' not in result
        assert 'branch' not in result
    
    def test_no_root_attribute(self):
        """Test when root attribute is missing."""
        xml_str = '''
        <component name="test">
            <source>
                <codeBase version="1.0">FMS.git</codeBase>
            </source>
        </component>
        '''
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        assert 'repo' not in result
        assert 'branch' not in result


class TestParseComponent:
    """Test parse_component main function."""
    
    def test_complete_component(self):
        """Test parsing a complete component with all attributes."""
        xml_str = '''
        <component name="  am5_phys  " paths="path1 path2" requires="FMS">
            <compile doF90Cpp="yes">
                <cppDefs>-DDEBUG</cppDefs>
                <makeOverrides>-j8</makeOverrides>
            </compile>
            <source root="https://github.com/NOAA-GFDL">
                <codeBase version="2026.01">FMS.git</codeBase>
                <csh>echo "building"</csh>
            </source>
        </component>
        '''
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        
        assert result['component'] == 'am5_phys'
        assert result['paths'] == ['path1', 'path2']
        assert result['requires'] == ['FMS']
        assert result['cppdefs'] == '-DDEBUG'
        assert result['makeOverrides'] == '-j8'
        assert result['doF90Cpp'] is True
        assert result['repo'] == 'https://github.com/NOAA-GFDL/FMS.git'
        assert result['branch'] == '2026.01'
        assert result['additionalInstructions'] == ['echo "building"']
    
    def test_minimal_component(self):
        """Test parsing minimal component with only name."""
        xml_str = '<component name="minimal"/>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        
        assert result['component'] == 'minimal'
        assert len(result) == 1  # Only component field
    
    def test_component_without_name(self):
        """Test parsing component without name attribute."""
        xml_str = '<component/>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        
        assert result == {}  # All None values filtered out
    
    def test_none_values_filtered(self):
        """Test that None values are filtered from output."""
        xml_str = '<component name="test"/>'
        component = ET.fromstring(xml_str)
        result = parse_component(component)
        
        # Verify no None values exist in result
        for v in result.values():
            assert v is not None


class TestParseExperiment:
    """Test parse_experiment function."""
    
    def test_experiment_with_components(self):
        """Test parsing experiment with multiple components."""
        xml_str = '''
        <experiment name="test_exp">
            <component name="comp1" paths="path1"/>
            <component name="comp2" paths="path2"/>
        </experiment>
        '''
        experiment = ET.fromstring(xml_str)
        result = parse_experiment(experiment)
        
        assert result['experiment'] == 'test_exp'
        assert result['container_addlibs'] == ''
        assert result['baremetal_linkerflags'] == ''
        assert len(result['src']) == 2
        assert result['src'][0]['component'] == 'comp1'
        assert result['src'][1]['component'] == 'comp2'
    
    def test_experiment_without_components(self):
        """Test parsing experiment without components."""
        xml_str = '<experiment name="empty_exp"/>'
        experiment = ET.fromstring(xml_str)
        result = parse_experiment(experiment)
        
        assert result['experiment'] == 'empty_exp'
        assert result['src'] == []
    
    def test_experiment_without_name(self):
        """Test parsing experiment without name attribute."""
        xml_str = '''
        <experiment>
            <component name="comp1"/>
        </experiment>
        '''
        experiment = ET.fromstring(xml_str)
        result = parse_experiment(experiment)
        
        assert result['experiment'] is None
        assert len(result['src']) == 1


class TestXmlToYaml:
    """Test xml_to_yaml main conversion function."""
    
    def test_basic_xml_to_yaml_conversion(self, tmp_path):
        """Test basic XML to YAML conversion."""
        xml_content = '''
        <compile>
            <experiment name="exp1">
                <component name="comp1" paths="path1"/>
            </experiment>
        </compile>
        '''
        xml_file = tmp_path / 'test.xml'
        yaml_file = tmp_path / 'test.yaml'

        xml_file.write_text(xml_content)

        xml_to_yaml(xml_file, yaml_file)

        assert yaml_file.exists()
        data = yaml.safe_load(yaml_file.read_text())

        assert 'compile' in data
        assert data['compile']['experiment'] == 'exp1'
        assert len(data['compile']['src']) == 1
    
    def test_xml_to_yaml_with_specific_experiment(self, tmp_path):
        """Test XML to YAML conversion with specific experiment filter."""
        xml_content = '''
        <compile>
            <experiment name="exp1">
                <component name="comp1"/>
            </experiment>
            <experiment name="exp2">
                <component name="comp2"/>
            </experiment>
        </compile>
        '''
        xml_file = tmp_path / 'test.xml'
        yaml_file = tmp_path / 'test.yaml'

        xml_file.write_text(xml_content)

        xml_to_yaml(xml_file, yaml_file, experiment_name='exp2')

        data = yaml.safe_load(yaml_file.read_text())

        assert data['compile']['experiment'] == 'exp2'
        assert len(data['compile']['src']) == 1
        assert data['compile']['src'][0]['component'] == 'comp2'
    
    def test_xml_to_yaml_multiple_components(self, tmp_path):
        """Test XML to YAML with multiple components."""
        xml_content = '''
        <compile>
            <experiment name="multi_comp">
                <component name="comp1" paths="path1" requires="FMS"/>
                <component name="comp2" paths="path2" requires="FMS comp1"/>
                <component name="comp3" paths="path3"/>
            </experiment>
        </compile>
        '''
        xml_file = tmp_path / 'test.xml'
        yaml_file = tmp_path / 'test.yaml'

        xml_file.write_text(xml_content)

        xml_to_yaml(xml_file, yaml_file)

        data = yaml.safe_load(yaml_file.read_text())

        assert len(data['compile']['src']) == 3
        assert data['compile']['src'][0]['component'] == 'comp1'
        assert data['compile']['src'][1]['component'] == 'comp2'
        assert data['compile']['src'][2]['component'] == 'comp3'
    
    def test_xml_to_yaml_nonexistent_file(self):
        """Test error handling for non-existent XML file."""
        with pytest.raises(FileNotFoundError):
            xml_to_yaml('/nonexistent/path/test.xml', '/tmp/output.yaml')
    
    def test_xml_to_yaml_invalid_xml(self, tmp_path):
        """Test error handling for invalid XML."""
        xml_file = tmp_path / 'invalid.xml'
        yaml_file = tmp_path / 'output.yaml'

        xml_file.write_text('<invalid>This is not well-formed XML</')

        with pytest.raises(Exception):  # XML parsing error
            xml_to_yaml(xml_file, yaml_file)
    
    def test_xml_to_yaml_output_file_created(self, tmp_path):
        """Test that output file is created with correct permissions."""
        xml_content = '''
        <compile>
            <experiment name="exp1">
                <component name="comp1"/>
            </experiment>
        </compile>
        '''
        xml_file = tmp_path / 'test.xml'
        yaml_file = tmp_path / 'test.yaml'

        xml_file.write_text(xml_content)

        xml_to_yaml(xml_file, yaml_file)

        assert Path(yaml_file).exists()
        assert yaml_file.stat().st_size > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
