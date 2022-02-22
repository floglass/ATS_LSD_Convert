from unittest import TestCase

import pandas

from LSD_convert import *


class Test(TestCase):
    def test_check_ats(self):
        ats_test = '7-27-72-3 W4'
        ats_list = check_ats(ats_test)
        self.assertEqual(ats_list, [7, 27, 72, 3, 4])

    def test_ats_to_numeral(self):
        ats = '7-27-72-3 W4'
        numeral = ats_to_numeral(ats)
        self.assertEqual(numeral, '4030722707')

    def test_compare_to_database(self):
        numeral = 40100101100
        d = {'PID': [40100101090, 40100101100, 40100101150], 'Latitude': [49.00879773, 49.00875466, 49.01237059],
             'Longitude': [-110.00785000, -110.01339100, -110.01338800]}
        database = pandas.DataFrame(data=d)
        latlon = compare_to_database(numeral, database)
        self.assertEqual(latlon, [49.00875466, -110.01339100])

    def test_load_database(self):
        data_loaded = load_database()
        # self.assertEqual(data_loaded.loc[0, 'PID'], '40100101090')
        self.assertEqual(data_loaded.loc[0, 'PID'], '4010010109')

