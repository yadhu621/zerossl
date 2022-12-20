from setuptools import setup,find_packages
long_description = 'Package that provides a CLI to interact with ZeroSSL API'
setup(
    name='zerossl',
    version='0.1.3',
    author='Yadhu',
    author_email='yadhu621@gmail.com',
    url='https://github.com/yadhu621/zerossl',
    description='Interact with ZeroSSL API',
    long_description= long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points ={
    'console_scripts': ['zerossl = zerossl.main:main']
    },
    keywords=['zerossl'],
    zip_safe=False,
    install_requires=[
        'requests==2.26.0',
        'pyOpenSSL==22.0.0',
        'boto3==1.23.0'
    ]
)
