from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="se_models",
        version="0.1.0",
        packages=find_packages(exclude=["ros2_interface*"]),
        install_requires=[
            "pydantic>=2.0.0",
            "requests",
        ],
    )
