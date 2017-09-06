from setuptools import setup, find_packages

scripts = {
  'console_scripts' : [
    'fdtool = amitools.tools.fdtool:main',
    'geotool = amitools.tools.geotool:main',
    'hunktool = amitools.tools.hunktool:main',
    'rdbtool = amitools.tools.rdbtool:main',
    'romtool = amitools.tools.romtool:main',
    'typetool = amitools.tools.typetool:main',
    'vamos = amitools.tools.vamos:main',
    'vamospath = amitools.tools.vamospath:main',
    'xdfscan = amitools.tools.xdfscan:main',
    'xdftool = amitools.tools.xdftool:main',
    'amipath = amitools.tools.amipath:main'
  ]
}

setup(
    name = "amitools",
    description='A package to support development with classic Amiga m68k systems',
    long_description=open("README.md").read(),
    version = "0.2.0",
    maintainer = "Christian Vogelgsang",
    maintainer_email = "chris@vogelgsang.org",
    url = "http://github.com/cnvogelg/amitools",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: System :: Emulators",
    ],
    license = "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    packages = find_packages(),
    zip_safe = False,
    entry_points = scripts,
    setup_requires = ['pytest-runner'],
    tests_require= ['pytest'],
    install_requires = ['lhafile==0.2.1','bare68k'],
    dependency_links = [
      "http://github.com/FrodeSolheim/python-lhafile/zipball/master#egg=lhafile-0.2.1"
    ],
    include_package_data=True
)

