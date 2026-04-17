from setuptools import setup, find_packages

setup(
    name="rate_limiter",
    version="1.0.0",
    description="A production-grade rate limiting library for Python using Redis.",
    author="Ricky",
    packages=find_packages(),
    install_requires=[
        "redis>=5.0.0",
        "hiredis>=2.2.0"
    ],
    python_requires=">=3.7",
)
