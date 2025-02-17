#! /usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa: E122
import os, sys, glob, warnings
import numpy as np
from setuptools import setup, Extension


def get_geos_install_prefix():
    """Return GEOS installation prefix or None if not found."""
    env_candidate = os.environ.get("GEOS_DIR", None)
    if env_candidate is not None:
        # Normalize path separators for Windows
        return os.path.normpath(env_candidate)

    candidates = [
        os.path.expanduser("~/local"),
        os.path.expanduser("~"),
        "/usr/local",
        "/usr",
        "/opt/local",
        "/opt",
        "/sw",
    ]

    extensions = {"win32": "dll", "cygwin": "dll", "darwin": "dylib"}
    libext = extensions.get(sys.platform, "so*")
    libname = f"*geos_c*.{libext}"
    libdirs = ["bin", "lib", "lib/x86_64-linux-gnu", "lib64"]

    for prefix in candidates:
        # Normalize path for Windows
        prefix = os.path.normpath(prefix)
        for libdir in libdirs:
            # Use os.path.join for proper path construction
            lib_path = os.path.join(prefix, libdir, libname)
            # Use normalized glob pattern
            if glob.glob(lib_path):
                hfile = os.path.join(prefix, "include", "geos_c.h")
                if os.path.isfile(hfile):
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
        # Normalize all paths
        include_dir = os.path.normpath(os.path.join(geos_prefix, "include"))
        lib_dir = os.path.normpath(os.path.join(geos_prefix, "lib"))
        lib64_dir = os.path.normpath(os.path.join(geos_prefix, "lib64"))

        include_dirs.append(include_dir)
        library_dirs.extend([lib_dir, lib64_dir])
        runtime_library_dirs = library_dirs.copy()

        if os.name == "nt" or sys.platform == "cygwin":
            bin_dir = os.path.normpath(os.path.join(geos_prefix, "bin"))
            library_dirs.append(bin_dir)
            runtime_library_dirs = []
            # Normalize dll path pattern
            dll_pattern = os.path.join(geos_prefix, "*", "*geos_c*.dll")
            dlls = glob.glob(dll_pattern)
            if dlls:
                # Normalize dll paths
                dlls = [os.path.normpath(dll) for dll in dlls]
                data_files.append(("../..", sorted(dlls)))

    return {
        "name": "_geoslib",
        "sources": ["src/_geoslib.pyx"],
        "libraries": ["geos_c"],
        "include_dirs": include_dirs,
        "library_dirs": library_dirs,
        "runtime_library_dirs": runtime_library_dirs,
    }


setup(
    ext_modules=[Extension(**get_extension_kwargs())],
    data_files=get_extension_kwargs().get("data_files", []),
)
