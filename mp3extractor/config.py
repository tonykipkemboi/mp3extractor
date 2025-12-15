"""
Configuration management

Handles hierarchical configuration loading from files and CLI arguments.
Supports both YAML (preferred) and JSON formats.
"""

import json
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger('mp3extractor')

# Try to import PyYAML, but don't fail if not available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    logger.debug("PyYAML not available, will use JSON for config files")


@dataclass
class Config:
    """
    Configuration dataclass

    Holds all configuration settings for the extractor.
    """

    # Audio settings
    bitrate: str = '320k'
    sample_rate: Optional[int] = None

    # Output settings
    output_dir: Optional[str] = None

    # Processing settings
    workers: str = 'auto'  # 'auto' or number
    fail_fast: bool = False
    sequential: bool = False

    # Metadata settings
    preserve_metadata: bool = True
    metadata_tags: list = field(default_factory=lambda: ['title', 'artist', 'album', 'artwork'])

    # Progress settings
    show_progress: bool = True
    simple_progress: bool = False
    no_progress: bool = False

    # Logging settings
    log_level: str = 'INFO'
    log_file: Optional[str] = None
    verbose: bool = False
    quiet: bool = False

    # Config file settings
    config_file: Optional[str] = None

    @classmethod
    def defaults(cls) -> 'Config':
        """
        Create Config instance with default values

        Returns:
            Config with default settings
        """
        return cls()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert config to dictionary

        Returns:
            Dictionary representation of config
        """
        return asdict(self)

    def update(self, updates: Dict[str, Any]) -> 'Config':
        """
        Update config with new values

        Args:
            updates: Dictionary of values to update

        Returns:
            Self for chaining
        """
        for key, value in updates.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        return self

    def validate(self) -> bool:
        """
        Validate configuration values

        Returns:
            True if valid, raises ValueError if invalid
        """
        # Validate bitrate format
        if not self.bitrate.endswith('k') or not self.bitrate[:-1].isdigit():
            raise ValueError(f"Invalid bitrate format: {self.bitrate}. Must be like '320k', '256k'")

        bitrate_num = int(self.bitrate[:-1])
        if bitrate_num < 32 or bitrate_num > 320:
            raise ValueError(f"Bitrate {bitrate_num}k out of range (32-320)")

        # Validate sample rate
        if self.sample_rate is not None:
            valid_rates = [8000, 11025, 16000, 22050, 44100, 48000, 88200, 96000]
            if self.sample_rate not in valid_rates:
                raise ValueError(
                    f"Invalid sample rate: {self.sample_rate}. "
                    f"Must be one of {valid_rates}"
                )

        # Validate workers
        if self.workers != 'auto':
            try:
                workers_num = int(self.workers)
                if workers_num < 1 or workers_num > 32:
                    raise ValueError(f"Workers must be between 1-32 or 'auto'")
            except ValueError:
                raise ValueError(f"Workers must be a number or 'auto', got: {self.workers}")

        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_levels:
            raise ValueError(
                f"Invalid log level: {self.log_level}. "
                f"Must be one of {valid_levels}"
            )

        # Validate metadata tags
        valid_tags = ['title', 'artist', 'album', 'date', 'genre', 'artwork']
        for tag in self.metadata_tags:
            if tag not in valid_tags:
                raise ValueError(
                    f"Invalid metadata tag: {tag}. "
                    f"Must be one of {valid_tags}"
                )

        return True


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """
    Load YAML config file

    Args:
        file_path: Path to YAML file

    Returns:
        Dictionary of config values

    Raises:
        ValueError: If YAML parsing fails
    """
    if not HAS_YAML:
        raise ValueError("PyYAML not installed, cannot load YAML files")

    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        if data is None:
            return {}

        if not isinstance(data, dict):
            raise ValueError("Config file must contain a dictionary")

        logger.debug(f"Loaded YAML config from {file_path}")
        return data

    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {file_path}: {e}")
    except Exception as e:
        raise ValueError(f"Could not read {file_path}: {e}")


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Load JSON config file

    Args:
        file_path: Path to JSON file

    Returns:
        Dictionary of config values

    Raises:
        ValueError: If JSON parsing fails
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Config file must contain a JSON object")

        logger.debug(f"Loaded JSON config from {file_path}")
        return data

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")
    except Exception as e:
        raise ValueError(f"Could not read {file_path}: {e}")


def load_config_file(file_path: Path) -> Dict[str, Any]:
    """
    Load config file (auto-detect YAML or JSON)

    Args:
        file_path: Path to config file

    Returns:
        Dictionary of config values
    """
    if not file_path.exists():
        logger.warning(f"Config file not found: {file_path}")
        return {}

    # Try to determine format from extension
    suffix = file_path.suffix.lower()

    if suffix in ['.yaml', '.yml']:
        return load_yaml_file(file_path)
    elif suffix == '.json':
        return load_json_file(file_path)
    else:
        # Try YAML first, then JSON
        if HAS_YAML:
            try:
                return load_yaml_file(file_path)
            except ValueError:
                pass

        try:
            return load_json_file(file_path)
        except ValueError as e:
            raise ValueError(f"Could not parse {file_path} as YAML or JSON: {e}")


def get_user_config_path() -> Path:
    """
    Get path to user config file

    Returns:
        Path to ~/.config/mp3extractor/config.yaml (or .json)
    """
    if sys.platform == 'win32':
        config_dir = Path.home() / 'AppData' / 'Local' / 'mp3extractor'
    else:
        config_dir = Path.home() / '.config' / 'mp3extractor'

    # Try YAML first, then JSON
    yaml_path = config_dir / 'config.yaml'
    json_path = config_dir / 'config.json'

    if yaml_path.exists():
        return yaml_path
    elif json_path.exists():
        return json_path
    else:
        # Return YAML path as default (preferred)
        return yaml_path


def get_project_config_path() -> Path:
    """
    Get path to project-level config file

    Returns:
        Path to ./.mp3extractor.yaml (or .json) in current directory
    """
    cwd = Path.cwd()

    # Try different filenames
    for name in ['.mp3extractor.yaml', '.mp3extractor.yml', '.mp3extractor.json']:
        path = cwd / name
        if path.exists():
            return path

    # Return default (YAML preferred)
    return cwd / '.mp3extractor.yaml'


def load_config(cli_args: Optional[Any] = None) -> Config:
    """
    Load configuration from multiple sources with priority

    Priority (highest to lowest):
    1. CLI arguments
    2. Project config file (./.mp3extractor.yaml)
    3. User config file (~/.config/mp3extractor/config.yaml)
    4. Default values

    Args:
        cli_args: Parsed command-line arguments (argparse Namespace)

    Returns:
        Merged Config object

    Raises:
        ValueError: If config validation fails
    """
    # Start with defaults
    config = Config.defaults()

    # Load user config
    user_config_path = get_user_config_path()
    if user_config_path.exists():
        try:
            user_config = load_config_file(user_config_path)
            config.update(user_config)
            logger.debug(f"Loaded user config from {user_config_path}")
        except ValueError as e:
            logger.warning(f"Could not load user config: {e}")

    # Load project config
    project_config_path = get_project_config_path()
    if project_config_path.exists():
        try:
            project_config = load_config_file(project_config_path)
            config.update(project_config)
            logger.debug(f"Loaded project config from {project_config_path}")
        except ValueError as e:
            logger.warning(f"Could not load project config: {e}")

    # Load explicit config file if specified in CLI
    if cli_args and hasattr(cli_args, 'config') and cli_args.config:
        config_path = Path(cli_args.config).expanduser()
        try:
            explicit_config = load_config_file(config_path)
            config.update(explicit_config)
            logger.debug(f"Loaded explicit config from {config_path}")
        except ValueError as e:
            raise ValueError(f"Could not load specified config file: {e}")

    # Override with CLI arguments
    if cli_args:
        cli_dict = {k: v for k, v in vars(cli_args).items() if v is not None}
        config.update(cli_dict)

    # Validate final config
    try:
        config.validate()
    except ValueError as e:
        raise ValueError(f"Invalid configuration: {e}")

    return config


def save_default_config(file_path: Optional[Path] = None, format: str = 'yaml') -> Path:
    """
    Generate and save a default config file

    Args:
        file_path: Path to save config (optional, uses default location)
        format: File format ('yaml' or 'json')

    Returns:
        Path where config was saved

    Raises:
        ValueError: If format is invalid or saving fails
    """
    if file_path is None:
        file_path = get_user_config_path()

    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Get default config
    config = Config.defaults()
    config_dict = config.to_dict()

    # Add comments (only works with YAML)
    if format == 'yaml':
        if not HAS_YAML:
            raise ValueError("PyYAML not installed, cannot generate YAML config")

        # Create config with comments
        config_str = """# MP3 Extractor Configuration
# All settings are optional and can be overridden via command-line arguments

# Audio settings
bitrate: 320k           # Audio bitrate (e.g., 128k, 192k, 256k, 320k)
sample_rate: null       # Sample rate in Hz (null for auto, or 44100, 48000, etc.)

# Output settings
output_dir: null        # Default output directory (null for same as input)

# Processing settings
workers: auto           # Number of parallel workers ('auto' or 1-32)
fail_fast: false        # Stop on first error in batch processing
sequential: false       # Force sequential processing (same as workers: 1)

# Metadata settings
preserve_metadata: true # Copy metadata (title, artist, etc.) from source
metadata_tags:          # Which metadata tags to preserve
  - title
  - artist
  - album
  - artwork

# Progress settings
show_progress: true     # Show progress bars during conversion
simple_progress: false  # Use simple progress (for incompatible terminals)
no_progress: false      # Completely disable progress display

# Logging settings
log_level: INFO         # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
log_file: null          # Log file path (null for no file logging)
verbose: false          # Enable verbose output (sets log_level to DEBUG)
quiet: false            # Suppress console output except errors
"""

        try:
            with open(file_path, 'w') as f:
                f.write(config_str)
        except Exception as e:
            raise ValueError(f"Could not write config file: {e}")

    elif format == 'json':
        try:
            with open(file_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except Exception as e:
            raise ValueError(f"Could not write config file: {e}")

    else:
        raise ValueError(f"Invalid format: {format}. Must be 'yaml' or 'json'")

    logger.info(f"Generated default config file: {file_path}")
    return file_path
