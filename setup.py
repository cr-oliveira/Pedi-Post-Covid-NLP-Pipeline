from setuptools import setup, find_namespace_packages

# read the contents of the README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="misc_nlp",
    version="1.0.1.5",
    description="An NLP pipeline for COVID-19 surveillance used in the Department of Veterans Affairs Biosurveillance.",
    author="julie.silvestri,alec.chapman",
    author_email="julie@insideoutbox.org,alec.chapman@hsc.utah.edu",
    packages=find_namespace_packages(include=["misc_nlp","misc_nlp.cov_bsv", "misc_nlp.cov_bsv.knowledge_base", "misc_nlp.mis", "misc_nlp.mis.knowledge_base"]),
    install_requires=[
        "medspacy==0.2.0.0",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Apache,MIT'
)
