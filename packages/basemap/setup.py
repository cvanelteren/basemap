#! /usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa: E122
import os, sys, glob, warnings
import numpy as np
from setuptools import setup, Extension
from pathlib import Path


def get_geos_install_prefix():
    """Return GEOS installation prefix or None if not found."""
    env_candidate = os.environ.get("GEOS_DIR", None)
    print("GEOS_DIR:", env_candidate)  # Debug print
    if env_candidate is not None:
        return Path(env_candidate)

    candidates = [
        Path.home() / "local",
        Path.home(),
        Path("/usr/local"),
        Path("/usr"),
        Path("/opt/local"),
        Path("/opt"),
        Path("/sw"),
    ]

    extensions = {"win32": "dll", "cygwin": "dll", "darwin": "dylib"}
    libext = extensions.get(sys.platform, "so*")
    libname = f"*geos_c*.{libext}"
    libdirs = ["bin", "lib", "lib/x86_64-linux-gnu", "lib64"]

    for prefix in candidates:
        for libdir in libdirs:
            if list(prefix.glob(f"{libdir}/{libname}")):
                hfile = prefix / "include" / "geos_c.h"
                if hfile.is_file():
                    return prefix
    return None


def get_extension_kwargs():
    include_dirs = [np.get_include()]
    library_dirs = []
    runtime_library_dirs = []
    data_files = []

    # Get GEOS paths
    geos_prefix = get_geos_install_prefix()
    if geos_prefix:
        # Convert to Path object if it isn't already
        geos_prefix = Path(geos_prefix)

        include_dir = geos_prefix / "include"
        lib_dir = geos_prefix / "lib"
        lib64_dir = geos_prefix / "lib64"

        include_dirs.append(include_dir)
        library_dirs.extend([lib_dir, lib64_dir])
        runtime_library_dirs = library_dirs.copy()

        if os.name == "nt" or sys.platform == "cygwin":
            bin_dir = geos_prefix / "bin"
            library_dirs.append(bin_dir)
            runtime_library_dirs = []

            # Use Path.glob for finding DLLs
            dlls = list(geos_prefix.glob("**/*geos_c*.dll"))
            if dlls:
                # Convert Path objects to strings
                dll_paths = [str(dll) for dll in dlls]
                data_files.append(("../..", sorted(dll_paths)))

    include_dirs = [str(i) for i in include_dirs]
    library_dirs = [str(i) for i in library_dirs]
    runtime_library_dirs = [str(i) for i in runtime_library_dirs]
    print("include_dirs", include_dirs)
    print("library_dirs", library_dirs)
    print("runtime_library_dirs", runtime_library_dirs)
    return (
        dict(
            name="_geoslib",
            sources=["src/_geoslib.pyx"],
            libraries=["geos_c"],
            include_dirs=include_dirs,
            library_dirs=library_dirs,
            runtime_library_dirs=runtime_library_dirs,
        ),
        data_files,
    )


kwargs, data_files = get_extension_kwargs()
setup(
    ext_modules=[Extension(**kwargs, data_files=data_files)],
)
