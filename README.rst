ltf\_catalog
============

Catalog parser for the LAT Transient Factory

Installation
------------

Clone this repository with git:

::

    git clone https://github.com/giacomov/ltf_catalog.git

Then go inside the repository and execute the setup:

::

    cd ltf_catalog
    python setup.py install

Usage
-----

You will need a data file. At the moment, the LAT Transient Factory
catalog is private and you need to be part of the Fermi Large Area
Telescope collaboration to be able to access it.

Let's say that your data file is called "LTF\_March24\_2016.csv". Then
you can load the catalog like this:

::


    import ltf_catalog as ltf

    c = ltf.get_catalog("LTF_March24_2016.csv")

Now you can get the catalog of detections as:

::


    detections = c.get_catalog_of_detections()

By default the detections are selected requiring a final TS >= 25 and at
least 3 events with a probability larger than 90% of belonging to the
trigger. You can change these criteria. For example, the following will
consider detections all triggers with a final TS >= 30 and at lest 10
events with a probability larger than 90% of belonging to the trigger:

::


    custom_detections = c.get_catalog_of_detections("Final_TS >= 30","GRB_events >= 10")

Once you have your catalog of detections, you can loop over them by
doing:

::


    for trigger in detections.iteritems():
        
        [do your processing here]

So for example, this will print all the available information:

::


    for trigger in detections.iteritems():
        
        for det in detections.iteritems():
    print("%s %s %s %s %s %s %s %s" %(det.name, det.trigger_time, det.date, det.gcn_type,
                                      det.get_longest_time_scale_with_detection(), det.time_scale_with_largest_TS,
                                      det.maximum_TS, det.get_position_with_smallest_error()))

To see all methods and properties of the catalog and the triggers, see
the API documentation at http://ltf-catalog.readthedocs.org/
