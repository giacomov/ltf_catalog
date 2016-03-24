# ltf_catalog
Catalog parser for the LAT Transient Factory

## Installation

Clone this repository with git:

```
git clone https://github.com/giacomov/ltf_catalog.git
```

Then go inside the repository and execute the setup:

```
cd ltf_catalog
python setup.py install
```

## Usage

You will need a data file. At the moment, the LAT Transient Factory catalog 
is private and you need to be part of the Fermi Large Area Telescope collaboration
to be able to access it. 

Let's say that your data file is called "LTF_March24_2016.csv". Then you can load
the catalog like this:

```python

import ltf_catalog as ltf

c = ltf.get_catalog("LTF_March24_2016.csv")
```

Now you can get the catalog of detections as:

```python

detections = c.get_detections()

```

By default the detections are selected requiring a final TS >= 25 and at least 3
events with a probability larger than 90% of belonging to the trigger. You can change
these criteria. For example, the following will consider detections all triggers with
a final TS >= 30 and at lest 10 events with a probability larger than 90% of belonging 
to the trigger:

```python

custom_detections = c.get_detections("Final_TS >= 30","GRB_events >= 10")

```

Once you have your catalog of detections, you can loop over them by doing:

```python

for trigger in detections.iteritems():
    
    [do your processing here]

```

So for example, this will print all the names and their maximum TS of the triggers:

```python

for trigger in detections.iteritems():
    
    print("Name: %s, maximum TS: %s" % (trigger.name, trigger.maximum_TS))

```

To see all methods and properties of the catalog and the triggers, see the API
documentation at http://ltf-catalog.readthedocs.org/
