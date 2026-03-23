#!/usr/bin/env python3
"""
Penumbra Collection Configuration Cleaner
_________________________________________
A utility to remove all disabled mod settings in a Penumbra collection configuration file.
This helps resolving conflicts when a mod is enabled in one collection and disabled in another.
"""

import json
import os
import sys
import shutil
from collections import OrderedDict
import argparse

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "filename",
        help = """
            Path to your Penumbra collection configuration file.
            They are located at `$HOME/.xlcore/pluginConfigs/Penumbra/collections`.
        """
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1) # missing argument

    args = parser.parse_args()
    execute(args.filename)

def execute(input_filename):
    if not os.path.isfile(input_filename):
        print(f"Error: File '{input_filename}' not found.")
        return

    backup_filename = f"{input_filename}.backup"

    try:
        # Load the data using 'utf-8-sig' as 'utf-8' might not be correctly decoded
        print(f"Reading {input_filename}...")
        with open(input_filename, 'r', encoding='utf-8-sig') as f:
            # use OrderedDict to keep original order
            data = json.load(f, object_pairs_hook=OrderedDict)

        if "Settings" not in data or not isinstance(data["Settings"], OrderedDict):
            print("Error: JSON root does not contain a 'Settings' object.")
            return

        original_settings = data["Settings"]
        fixed_settings = OrderedDict()
        removed_count = 0

        for name, content in original_settings.items():
            if isinstance(content, dict) and content.get("Enabled") is False:
                print(f"removing {name}...")
                removed_count += 1
            else:
                fixed_settings[name] = content

        data["Settings"] = fixed_settings

        # make a backup
        print(f"Creating backup: {backup_filename}")
        shutil.move(input_filename, backup_filename)

        print(f"Writing cleaned data to: {input_filename}")
        with open(input_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print("-" * 30)
        print("Success!")
        print(f"Removed {removed_count} disabled objects.")
        print(f"Original file backed up as: {backup_filename}")

    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e.msg}")
        print(f"Location: Line {e.lineno}, Column {e.colno}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
