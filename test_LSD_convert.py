from unittest import TestCase

import pandas
import time

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

    def test_compare_to_sqlitedb(self):
        # numeral = 4010010110
        # numeral = 4050700406
        numeral = 4030701013  # duplicates (ie: 2x query)
        latlon= compare_to_sqlitedb(numeral)
        self.assertAlmostEqual(latlon[0], 55.0513795962817)
        self.assertAlmostEqual(latlon[1], -110.38353028603642)

    def test_compare_both_methods_to_get_latlon(self):
        numeral = 4030701013
        start_sqlite = time.perf_counter()
        latlon_sqlite = compare_to_sqlitedb(numeral)
        stop_sqlite = time.perf_counter()
        start_db = time.perf_counter()
        d = load_database()
        latlon_csv = compare_to_database(str(numeral), d, test=1)
        stop_db = time.perf_counter()
        print("SQLITE3 execution: {}, DB execution: {}".format(stop_sqlite-start_sqlite, stop_db-start_db))
        self.assertEqual(latlon_sqlite[0], latlon_csv[0])
        self.assertEqual(latlon_sqlite[1], latlon_csv[1])

