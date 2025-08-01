# FRE SFollow Module

The FRE SFollow module provides functionality to monitor SLURM job output in real-time. It queries job information using `scontrol` and follows the standard output file using `less +F`.

## Features

- Query SLURM job information using job ID
- Extract standard output file path from job information
- Follow output files in real-time using `less +F`
- Validation mode to check job status without following
- Comprehensive error handling and user feedback

## Usage

### Command Line Interface

The sfollow module integrates with the FRE CLI framework and can be used as follows:

```bash
# Follow a job's output in real-time
fre sfollow 12345

# Validate a job exists and has output without following
fre sfollow 12345 --validate

# Short form of validate flag
fre sfollow 12345 -v
```

### Examples

```bash
# Monitor a running job
fre sfollow 135549171

# Check if a job has output available
fre sfollow 135549171 --validate
```

## Module Structure

```
fre/sfollow/
├── __init__.py              # Module initialization
├── sfollow.py               # Core functionality
├── fresfollow.py           # Click CLI interface
├── README.md               # This file
└── tests/                  # Unit tests
    ├── __init__.py
    ├── test_sfollow.py     # Tests for core functionality
    └── test_fresfollow.py  # Tests for CLI interface
```

## Core Functions

### `get_job_info(job_id: str) -> str`
Retrieves job information from SLURM using the `scontrol show jobid` command.

### `parse_stdout_path(scontrol_output: str) -> Optional[str]`
Parses the standard output file path from scontrol output by looking for lines containing 'StdOut='.

### `follow_output_file(file_path: str) -> None`
Follows the output file using `less +F` command for real-time monitoring.

### `follow_job_output(job_id: str) -> Tuple[bool, str]`
Main function that combines all functionality to follow a SLURM job's output.

## Dependencies

- `subprocess` - For running system commands
- `os` - For file system operations
- `click` - For command line interface
- `typing` - For type hints

## Requirements

- SLURM workload manager with `scontrol` command available
- `less` command available for file following
- Python 3.6+ with typing support

## Error Handling

The module includes comprehensive error handling for:

- SLURM command failures (job not found, permission issues)
- Missing commands (`scontrol`, `less`)
- File system errors (output file not found, permission issues)
- User interrupts (Ctrl+C)

## Testing

Run the unit tests using:

```bash
# Run all tests in the sfollow module
python -m pytest fre/sfollow/tests/

# Run specific test files
python -m pytest fre/sfollow/tests/test_sfollow.py
python -m pytest fre/sfollow/tests/test_fresfollow.py

# Run with coverage
python -m pytest fre/sfollow/tests/ --cov=fre.sfollow
```

## Development

When adding new functionality:

1. Update the core functions in `sfollow.py`
2. Update the CLI interface in `fresfollow.py` if needed
3. Add comprehensive unit tests
4. Update this README with new features
5. Ensure all tests pass

## Integration with FRE-CLI

The sfollow module is integrated into the main FRE-CLI framework through:

1. Entry in `fre/fre.py` lazy_subcommands dictionary
2. CLI command defined in `fresfollow.py`
3. Module structure following FRE-CLI conventions

## Author

Tom Robinson  
NOAA | GFDL  
2025
