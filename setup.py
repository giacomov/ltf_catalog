from distutils.core import setup

setup(
    
    name="ltf_catalog",
    
    packages = ["ltf_catalog"],
        
    version = 'v0.1',
    
    description = "Read the results of the LAT Transient Factory triggered algorithm",
    
    author = 'Giacomo Vianello (Stanford University)',
    
    author_email = 'giacomo.vianello@gmail.com',

    install_requires=['numpy']

)
