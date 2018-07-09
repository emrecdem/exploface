import unittest
import os
import numpy as np
import pandas as pd
import exploface as ef


class TestFunctions(unittest.TestCase):
    def get_test_directory(self):
        return os.path.dirname(os.path.abspath(__file__))

    def test_info_function(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", "multiple_active_au.csv")
        
        info_dict = ef.get_info(file_to_read)

        self.assertEqual(info_dict["number_of_columns"], 40)
        self.assertEqual(info_dict["duration"], 19.9)
        self.assertEqual(info_dict["time_resolution"], 0.1)

    def test_statistics_function(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", "multiple_active_au_2.csv")
        
        stats_dict = ef.get_statistics(file_to_read)

        for au in ['AU01', 'AU02', 'AU23']:
            self.assertEqual(stats_dict[au]["average_length_detection"], 2.5)
            self.assertEqual(stats_dict[au]["nr_detections"], 2)
            self.assertEqual(round(stats_dict[au]["std_average_length_detection"],4), round(0.7071067811865476,4))

    def test_write_elan_function(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", "multiple_active_au_2.csv")
        
        df = ef.write_elan_file(file_to_read)

        self.assertEqual(len(df["au"]), 6)
        self.assertEqual(len(set(df["au"])), 3)
        self.assertEqual(len(set(df["start"])),2)
        self.assertEqual(len(set(df["end"])),2)


if __name__ == '__main__':
    unittest.main()