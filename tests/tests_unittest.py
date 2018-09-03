import unittest
import os
import numpy as np
import pandas as pd
import exploface as ef


class TestFunctionsAnalysis(unittest.TestCase):
    def get_test_directory(self):
        return os.path.dirname(os.path.abspath(__file__))

    def test_compare_detection_tables(self):
        file_to_read_1 = os.path.join(self.get_test_directory(), "data", "multiple_active_au.csv")
        file_to_read_2 = os.path.join(self.get_test_directory(), "data", "multiple_active_au.csv")

        det_df_1 = ef.get_detections(file_to_read_1, 
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9
                    )

        det_df_2 = ef.get_detections(file_to_read_2, 
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9
                    )

        found, total, overlap_start = ef.analysis.find_overlap(det_df_1, det_df_2, "AU01", "AU01", room=1.0)

        self.assertEqual(found, 1)
        self.assertEqual(total, 1)

    def test_compare_detection_tables_shifts(self):
        file_to_read_1 = os.path.join(self.get_test_directory(), "data", "multiple_active_au_no_shift.csv")
        file_to_read_2 = os.path.join(self.get_test_directory(), "data", "multiple_active_au_shift1.csv")
        file_to_read_3 = os.path.join(self.get_test_directory(), "data", "multiple_active_au_shift2p5.csv")
        
        det_df = ef.get_detections(file_to_read_1, 
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9
                    )

        det_df_2 = ef.get_detections(file_to_read_2, 
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9
                    )

        det_df_3 = ef.get_detections(file_to_read_3, 
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9
                    )


        found, total, overlap_start = ef.analysis.find_overlap(det_df, det_df_2, "AU01", "AU01", room=0)
        self.assertEqual(found, 2)
        self.assertEqual(total, 2)

        found, total, overlap_start = ef.analysis.find_overlap(det_df, det_df_3, "AU01", "AU01", room=0.49)
        self.assertEqual(found, 0)
        self.assertEqual(total, 2)

        found, total, overlap_start = ef.analysis.find_overlap(det_df, det_df_3, "AU01", "AU01", room=0.5)
        self.assertEqual(found, 2)
        self.assertEqual(total, 2)


class TestFunctions(unittest.TestCase):
    def get_test_directory(self):
        return os.path.dirname(os.path.abspath(__file__))

    ##
    def test_info_function(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", "multiple_active_au.csv")
        
        info_dict = ef.get_info(file_to_read, max_len_col_names=50)

        self.assertEqual(info_dict["number_of_columns"], 40)
        self.assertEqual(info_dict["duration"], 19.9)
        self.assertEqual(info_dict["time_resolution"], 0.1)

    ##
    def test_statistics_function(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", "multiple_active_au_2.csv")
        
        stats_df = ef.get_statistics(file_to_read)

        for au in ['AU01', 'AU02', 'AU23']:
            self.assertEqual(round(stats_df.loc[au, "average_length_detection"], 4), 2.5)
            self.assertEqual(round(stats_df.loc[au, "nr_detections"],4), 2)
            self.assertEqual(round(stats_df.loc[au, "std_average_length_detection"], 4), round(0.7071067811865476,4))

    ##
    def test_write_elan_function(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", "multiple_active_au_2.csv")
        
        df = ef.write_elan_file(file_to_read)

        self.assertEqual(len(df["au"]), 6)
        self.assertEqual(len(set(df["au"])), 3)
        self.assertEqual(len(set(df["start"])),2)
        self.assertEqual(len(set(df["end"])),2)

    ##
    def test_column_selection(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", "multiple_active_au_2.csv")
        #df = ef.write_elan_file(file_to_read)
        stats_df = ef.get_statistics(file_to_read, column_selection=["AU23"])

        self.assertEqual('AU23' in stats_df.index, True )
        self.assertEqual('AU01' in stats_df.index, False )
        self.assertEqual('AU02' in stats_df.index, False )

        stats_df = ef.get_statistics(file_to_read, column_selection=["niks"])

        self.assertEqual(len(stats_df), 0 )

    ##
    def test_skip_seconds_at_end(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
            "multiple_active_au_2.csv")
        df = ef.write_elan_file(file_to_read, skip_seconds_at_end=15)

        self.assertEqual( len(df[df["au"]=="AU01"]), 1  )

    ##
    def test_uncertainty_threshold(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
            "multiple_active_au_3_low_confidence.csv")
        df = ef.write_elan_file(file_to_read, uncertainty_threshold=0.4)
        self.assertEqual( len(df[df["au"]=="AU01"]), 2  )

        df = ef.write_elan_file(file_to_read, uncertainty_threshold=1.0)
        self.assertEqual( len(df[df["au"]=="AU01"]), 1  )

    ##
    def test_intensity_threshold(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
            "multiple_active_au_4.csv")
        df = ef.write_elan_file(file_to_read, intensity_threshold=0.3)

        self.assertEqual( len(df[df["au"]=="AU01"]), 2  )
        self.assertEqual( len(df[df["au"]=="AU02"]), 2  )

        df = ef.write_elan_file(file_to_read, intensity_threshold=0.6)

        self.assertEqual( len(df[df["au"]=="AU01"]), 1  )
        self.assertEqual( len(df[df["au"]=="AU02"]), 1  )

    ##
    def test_time_threshold(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
            "multiple_active_au_2.csv")

        df = ef.write_elan_file(file_to_read, time_threshold=1)
        self.assertEqual( len(df[df["au"]=="AU01"]), 2  )
        self.assertEqual( len(df[df["au"]=="AU02"]), 2  )

        df = ef.write_elan_file(file_to_read, time_threshold=2.5)
        self.assertEqual( len(df[df["au"]=="AU01"]), 1  )
        self.assertEqual( len(df[df["au"]=="AU02"]), 1  )

    ##
    def test_smooth_time_threshold(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
            "multiple_active_au_2.csv")

        df = ef.write_elan_file(file_to_read, smooth_time_threshold=1)
        self.assertEqual( len(df[df["au"]=="AU01"]), 2  )
        self.assertEqual( len(df[df["au"]=="AU02"]), 2  )

        df = ef.write_elan_file(file_to_read, smooth_time_threshold=4)
        self.assertEqual( len(df[df["au"]=="AU01"]), 1  )
        self.assertEqual( len(df[df["au"]=="AU02"]), 1  )


if __name__ == '__main__':
    unittest.main()