import numpy
import collections


def _get_columns_dictionary():

    catalog_columns = "Trigger_name,Trigger_time,Trigger_date,Time_scale,Input_RA,Input_Dec,GCN_instrument," \
                      "GCN_type,Radius_of_the_search,IRF_used,TS_map_maximum," \
                      "Final_TS,Output_RA,Output_Dec,Localization_error,Angular_distance,Closest_point_source," \
                      "Photon_index,Photon_index_error,GRB_events,Status_of_the_job,Job_start_time,Job_end_time," \
                      "Job_duration".split(",")

    # Define the types as (converter, null_value)

    string_type = (str, "")
    float_type_nan = (float, numpy.nan)
    float_type_pos = (float, -1)
    int_type = (int, -1)

    catalog_formats = (string_type,
                       float_type_pos,
                       string_type,
                       float_type_pos,
                       float_type_nan,
                       float_type_nan,
                       string_type,
                       string_type,
                       float_type_pos,
                       string_type,
                       float_type_pos,
                       float_type_pos,
                       float_type_nan,
                       float_type_nan,
                       float_type_pos,
                       float_type_pos,
                       string_type,
                       float_type_nan,
                       float_type_nan,
                       int_type,
                       string_type,
                       string_type,
                       string_type,
                       float_type_pos
                       )

    assert len(catalog_formats) == len(catalog_columns)

    col_dict = collections.OrderedDict()

    for col,format in zip(catalog_columns, catalog_formats):

        col_dict[col] = format

    return col_dict

columns_formats = _get_columns_dictionary()


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
        Returns the time windows for this trigger where the search has been successfully
        executed
        
        :return: a list of time windows
        """
        return self._windows

    @property
    def trigger_time(self):
        """
        Returns the trigger time

        :return: the trigger time
        """

        return self._windows['Trigger_time'][0]

    @property
    def date(self):
        """
        Returns the date in UTC format

        :return: a string containing the date in UTC format
        """

        return self._windows['Trigger_date'][0]

    @property
    def gcn_type(self):
        """
        Returns the GCN_type, which can be used to figure out if this GRB belongs to the seed from the
        GBM, INTEGRAL, SWIFT and so on

        :return: a string
        """

        return self._windows['GCN_type'][0]

    def get_longest_time_scale_with_detection(self, TS = 25):
        """
        Returns the longest time scale among the time windows having a TS larger than TS

        :param TS: threshold for claiming a detection (default : 25)
        :return: the longest time windows
        """

        idx = self.windows['Final_TS'] >= TS

        return self.windows['Time_scale'][idx].max()

    @property
    def time_scale_with_largest_TS(self):
        """
        Returns the time scale which resulted in the largest TS
        
        :return: the time window with the maximum TS
        """

        id = self.windows['Final_TS'].argmax()

        return self.windows['Time_scale'][id]

    @property
    def maximum_TS(self):
        """
        Returns the largest TS
        
        :return: the maximum of TS
        """

        id = self.windows['Final_TS'].argmax()

        return self.windows['Final_TS'][id]

    def get_position_with_smallest_error(self, TS = 25):
        """
        Returns the position with the smallest error among all the time scales where
        the candidate has a TS larger than the provided threshold

        :param TS: threshold for TS (default: 25)
        :return: a tuple (R.A., Dec, error), where the error is the 90% containment (statistical only)
        """

        # Exclude zero errors (which means that gtfindsrc failed) and select only detections

        idx = (self.windows['Localization_error'] > 0) & (self.windows['Final_TS'] >= TS)

        if numpy.sum(idx) == 0:

            raise RuntimeError("No window above the threshold of %s for %s" % (TS, self.name))

        # Find position with the smallest error

        id = self.windows['Localization_error'][idx].argmin()

        ra, dec = (self.windows['Output_RA'][idx][id], self.windows['Output_Dec'][idx][id])

        return (ra, dec, self.windows['Localization_error'][idx][id])


def get_catalog(catalog_file):
    """
    Load the catalog from the provided file
    
    :param catalog_file: a comma-separated catalog file
    :return: an instance of the Catalog class
    
    """

    # Read them all as strings at first

    dtypes = map(lambda name:(name, 'S100'), columns_formats.keys())

    data_ = numpy.recfromcsv(catalog_file, names=True, case_sensitive=True, dtype=dtypes)

    # Convert to the proper python format

    data_dict = collections.OrderedDict()

    for col in columns_formats:

        converter = columns_formats[col][0]
        null_value = columns_formats[col][1]

        this_data = data_[col]

        idx = (this_data == "NULL")

        this_data[idx] = null_value

        data_dict[col] = numpy.array(this_data, converter)

    # Convert to numpy.ndarray

    formats = tuple(map(lambda x:x.dtype.str, data_dict.values()))

    data = numpy.zeros(data_dict.values()[0].shape[0], dtype={'names': data_dict.keys(),
                                                                'formats': formats})

    for col in data_dict:

        data[col][:] = data_dict[col]

    # data = numpy.recfromtxt(catalog_file, delimiter=',', names=True,
    #                         dtype=[('Trigger_name', 'S12'),
    #                                ('Trigger_date', 'S23'),
    #                                ('Trigger_time','<f8'),
    #                                ('GCN_type','S35'),
    #                                ('Time_scale', '<f8'),
    #                                ('Final_TS', '<f8'),
    #                                ('Output_RA', '<f8'),
    #                                ('Output_Dec', '<f8'),
    #                                ('Localization_error', '<f8'),
    #                                ('Closest_point_source', 'S43'),
    #                                ('Angular_distance', '<f8'),
    #                                ('Photon_index', '<f8'),
    #                                ('Photon_index_error', '<f8'),
    #                                ('GRB_events', '<i8')])

    return Catalog(data)


class Catalog(object):
    def __init__(self, data):

        self._data = data

        self._triggers = numpy.unique(self.data['Trigger_name'])

        print("Catalog has %s entries, with %s distinct triggers" % (len(self.data['Trigger_name']),
                                                                     self.triggers.shape[0]))

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

        if len(criteria) == 0:

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

        # Get the names of the selected triggers

        names = numpy.unique(self._data['Trigger_name'][idx])

        # Get all the entries which refers to one of the detection
        idx = numpy.in1d(self.data['Trigger_name'], names)

        return Catalog(self.data[idx])

    def get_trigger(self, triggername):
        """
        Returns the results relative to the provided trigger
        """

        assert triggername in self.data['Trigger_name'], "Trigger name %s is not in the database" % triggername

        this_windows = self.data[(self.data['Trigger_name'] == triggername)]

        assert len(this_windows) > 0, "Database file is corrupt, trigger %s has no time windows" % triggername

        return TriggerResults(triggername, this_windows)

    def iteritems(self):
        """
        Iterate through the loaded data, one trigger at the time.
        """

        for trigger in self.triggers:
            yield self.get_trigger(trigger)
