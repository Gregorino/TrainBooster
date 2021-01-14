import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TrainingBooster",
    version="1.0.0",
    author="Gregor Podrekar",
    author_email="gregapo@gmail.com",
    description="Something to boost your DL training:)",
    long_description="",
    long_description_content_type="",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)