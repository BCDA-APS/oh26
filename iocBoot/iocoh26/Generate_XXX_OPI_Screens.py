#!/usr/bin/python3

import os
import re
import concurrent.futures
import filecmp

def parse_envpaths(envpaths_file):
    """Parse envPaths file for module directories."""
    paths = {}
    with open(envpaths_file, 'r') as file:
        for line in file:
            match = re.match(r'epicsEnvSet\("(\w+)",\s*"(.*?)"\)', line)
            if match:
                key, path = match.groups()
                # Skip broad umbrellas unless explicitly needed
                if key not in ["AREA_DETECTOR", "SUPPORT", "TOP", "XXX"]:
                    paths[key] = path
    return paths

def find_opi_files(base_dir, dest_dir):
    """Find all .opi files under base_dir, excluding the staging dir."""
    opi_files = []
    for root, _, files in os.walk(base_dir):
        if os.path.abspath(root).startswith(os.path.abspath(dest_dir)):
            continue  # don’t recurse into staging dir
        for file in files:
            if file.endswith(".opi"):
                opi_files.append(os.path.join(root, file))
    return opi_files

def create_symlink(opi_file, dest_dir, env_key=None):
    """Create or update a symlink for a .opi file in dest_dir."""
    basename   = os.path.basename(opi_file)
    dest_file  = os.path.join(dest_dir, basename)
    new_target = os.path.realpath(opi_file)  # always resolve to real file

    # If a real file (not symlink) already exists in dest_dir, leave it alone
    if os.path.isfile(dest_file) and not os.path.islink(dest_file):
        return

    try:
        os.symlink(new_target, dest_file)
    except FileExistsError:
        existing_target = os.path.realpath(dest_file) if os.path.islink(dest_file) else dest_file

        # If both point to the same real file, nothing to do
        if existing_target == new_target:
            return

        # Curated beats autoconvert
        if "autoconvert" in existing_target and "autoconvert" not in new_target:
            os.remove(dest_file)
            os.symlink(new_target, dest_file)
            return
        if "autoconvert" in new_target and "autoconvert" not in existing_target:
            return  # keep curated one, ignore autoconvert

        # Real conflict: both curated, different contents
        try:
            if not filecmp.cmp(existing_target, new_target, shallow=False):
                print(f"WARNING [{env_key}]: duplicate curated screens with different contents:\n"
                      f"  existing: {existing_target}\n"
                      f"  new:      {new_target}")
        except OSError as e:
            print(f"WARNING [{env_key}]: could not compare {existing_target} and {new_target}: {e}")

def process_path(env_key, path, dest_dir):
    """Walk one envPath entry and create symlinks for its .opi files."""
    opi_files = find_opi_files(path, dest_dir)
    for opi_file in opi_files:
        create_symlink(opi_file, dest_dir, env_key)
    return opi_files

def main(envpaths_file, dest_dir):
    """Main driver: parse envPaths and process all entries in parallel."""
    paths = parse_envpaths(envpaths_file)
    all_bob_files = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for key, path in paths.items():
#            print(f"Scanning [{key}] → {path}")
            futures.append(executor.submit(process_path, key, path, dest_dir))
        for future in concurrent.futures.as_completed(futures):
            all_bob_files.extend(future.result())

    print(f"Total .opi files linked/checked: {len(all_bob_files)}")

if __name__ == "__main__":
    # resolve the envPaths file from current working directory
    envpaths_file = os.path.abspath("./envPaths")

    # use the directory that actually contains envPaths
    envpaths_dir = os.path.dirname(envpaths_file)

    # build dest_dir relative to that directory
    dest_dir = os.path.abspath(os.path.join(envpaths_dir, "..", "..", "xxxApp","op", "opi","autoconvert" ))

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    main(envpaths_file, dest_dir)

