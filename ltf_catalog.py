import numpy

class TriggerResults(object):

    def __init__(self, name, windows):

        self._name = name

        self._windows = windows
    
    @property
    def name(self):
        """
        Return the trigger name
        
        :return: trigger name
        """
        return self._name
    
    @property
    def windows(self):
        """
        Return the time windows for this trigger where the search has been successfully
        executed
        
        :return: a list of time windows
        """
        return self._windows
    
    @property
    def longest_time_scale(self):
        """
        Return the longest time scale among the time windows loaded.
        
        :return: the longest time windows
        """
        
        return self.windows['Time_scale'].max()
    
    @property
    def time_scale_with_largest_TS(self):
        """
        Return the time scale which resulted in the largest TS
        
        :return: the time window with the maximum TS
        """
        
        id = self.windows['Final_TS'].argmax()

        return self.windows['Time_scale'][id]
    
    @property
    def maximum_TS(self):
        """
        Return the largest TS found among all the time scales where the search has been
        successfully executed
        
        :return: the maximum of TS
        """
        
        id = self.windows['Final_TS'].argmax()
        
        return self.windows['Final_TS'][id]
    
    @property
    def position_with_smallest_error(self):
        """
        Return the position with the smallest error among all the time scales where
        the search has been successfully executed.
        
        :return: a tuple (R.A., Dec, error), where the error is the 90% containment (statistical only)
        """
        
        #Find position with the smallest error

        id = self.windows['Localization_error'].argmin()

        ra,dec = (self.windows['Output_RA'][id], self.windows['Output_Dec'][id])

        return (ra,dec, self.windows['Localization_error'][id])

def get_catalog(catalog_file):
    """
    Load the catalog from the provided file
    
    :param catalog_file: a comma-separated catalog file
    :return: an instance of the Catalog class
    
    """
    
    data = numpy.recfromtxt(catalog_file, delimiter=',', names=True,
                            dtype=[('Trigger_name', 'S12'),
                                   ('Time_scale', '<i8'),
                                   ('Final_TS', '<f8'),
                                   ('Output_RA', '<f8'),
                                   ('Output_Dec', '<f8'),
                                   ('Localization_error', '<f8'),
                                   ('Closest_point_source', 'S43'),
                                   ('Angular_distance', '<f8'),
                                   ('Photon_index', '<f8'),
                                   ('Photon_index_error', '<f8'),
                                   ('GRB_events', '<i8')])
    
    # Filter out windows with NULL as Final_TS
    
    idx = numpy.isnan(data['Final_TS'])
    
    data = data[~idx]
    
    return Catalog(data)

class Catalog(object):
    
    def __init__(self, data):

        self._data = data

        self._triggers = numpy.unique( self.data['Trigger_name'] )

        print("Catalog has %s entries, with %s distinct triggers" %(self.data.shape[0],self.triggers.shape[0]))
    
    @property
    def data(self):
        """
        Returns a numpy.ndarray containing the currently loaded data
        """
        
        return self._data
    
    @property
    def triggers(self):
        """
        Return the list of all the triggers
        """
        
        return self._triggers
        
    def get_catalog_of_detections(self, *criteria):
        """
        Return a new catalog containing only the detections, according to the default
        criteria or the custom one specified during the call.
        
        Examples:
        
        Get the detections with the standard criteria (Final_TS >= 25 and GRB_Events >= 3):
        
            > detections = c.get_catalog_of_detections()
        
        Get the detections requiring a TS larger than 30 and more than 10 events:
            
            > detections = c.get_catalog_of_detections("Final_TS >= 30","GRB_events >= 10")
        
        """
        
        if len(criteria)==0:
            
            criteria = ["Final_TS >= 25", "GRB_events >= 3"]
        
        # Make all columns in data as part of locals, so that the criteria can be
        # evaluated directly
        
        for name in self._data.dtype.names:
            
            locals()[name] = self._data[name]
        
        selection_string = "(" + ") & (".join(criteria) + ")"
        
        try:
            
            idx = eval(selection_string)
        
        except:
            
            raise RuntimeError("The provided criteria %s are not valid" % (selection_string))
        
        return Catalog(self.data[idx]) 
    
    def get_trigger(self, triggername):
        """
        Returns the results relative to the provided trigger
        """
        
        assert triggername in self.data['Trigger_name'], "Trigger name %s is not in the database" % triggername
        
        this_windows = self.data[(self.data['Trigger_name']==triggername)]

        assert len(this_windows) > 0, "Database file is corrupt, trigger %s has no time windows" % triggername

        return TriggerResults(triggername, this_windows)
    
    def iteritems(self):
        """
        Iterate through the loaded data, one trigger at the time.
        """        

        for trigger in self.triggers:
            
            yield self.get_trigger(trigger)
