from setuptools import setup, find_packages

setup(
    name="sta_choa",
    version="1.0.0",
    description="Chimp Optimization Algorithm over OpenSTA for VLSI Physical Design",
    author="R.Pavithra Guru",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={
        "console_scripts": [
            "sta-choa=main:cli",
        ]
    },
)
