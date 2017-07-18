import pandas as pd


class RGAIProcessor():

    def __init__(self, filepath):
        # read the CSV into a dataframe and format the dataframe appropriately
        self.df = pd.read_csv(filepath)
        self.df = self.df.rename(columns={'1-3':'Race Certainty', '1-3.1': 'Gender Certainty', '1-3.2':'Age Certainty',
                                          '1-3.3':'Instrument Certainty'})
        self.df.drop(self.df.columns[11:], axis=1, inplace=True)
        self.df = self.df.sort_values(self.df.columns[0])
        self.df = self.df.reindex()  # on second thought, not sure this line is necessary

        # create a dictionary to store differences and a dict for invalid input (may delete these later)
        self.valid_mismatches = {}  # may delete this later
        self.invalid_pairs = {}  # may delete this later too

        # create lists to store numbers of mismatches later
        self.race_data = {'black': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                    'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'white': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                    'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'hispanic': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                       'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'east asian': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                         'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'south asian': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                          'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'native american': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                              'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'middle eastern': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                             'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'not sure': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                       'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'other': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                    'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'nan': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                    'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []}}
        self.gender_data = {'woman': {'woman': [], 'man': [], 'non-binary': [], 'not sure': [], 'nan': []},
                            'man': {'woman': [], 'man': [], 'non-binary': [], 'not sure': [], 'nan': []},
                            'non-binary': {'woman': [], 'man': [], 'non-binary': [], 'not sure': [], 'nan': []},
                            'not sure': {'woman': [], 'man': [], 'non-binary': [], 'not sure': [], 'nan': []},
                            'nan': {'woman': [], 'man': [], 'non-binary': [], 'not sure': [], 'nan': []}}
        self.age_data = {'child': {'child': [], 'young adult': [], 'middle-aged': [], 'elder': [], 'nan': []},
                         'young adult': {'child': [], 'young adult': [], 'middle-aged': [], 'elder': [], 'nan': []},
                         'middle-aged': {'child': [], 'young adult': [], 'middle-aged': [], 'elder': [], 'nan': []},
                         'elder': {'child': [], 'young adult': [], 'middle-aged': [], 'elder': [], 'nan': []},
                         'nan': {'child': [], 'young adult': [], 'middle-aged': [], 'elder': [], 'nan': []}}
        self.instrument_data = {'sax': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                        'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'trumpet': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                            'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'trombone': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                             'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'piano': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                          'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'voice': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                          'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'guitar': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                           'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'bass': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                         'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'drums': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                          'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'other': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                          'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'nan': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                        'bass': [], 'drums': [], 'other': [], 'nan': []}}

        # creates a list of age pairs that are close enough together for disagreement not to matter
        self.age_pairs = [['child', 'young adult'], ['middle-aged', 'young adult'], ['elder', 'middle-aged']]

        # creates a list of URLs deleted for having invalid input from both people, therefore probably not being videos
        self.deleted_urls = []
        self.invalid_input = []  # urls with at least one misspelling or something--deal with these later

    def compare_value(self, valueA, valueB, dictionary, value_options, url):
        if valueA in value_options and valueB in value_options:
            dictionary[valueA][valueB].append(url)
            # can add a line here later to keep track of which URLs these are
        else:
            self.invalid_input.append(url)
        if valueA == "nan" and valueB == "nan":
            self.deleted_urls.append(url)
        # if valueA != valueB:
        #     if valueA in value_options and valueB in value_options:
        #         if url not in self.valid_mismatches.keys():
        #             self.valid_mismatches[url] = {value: [valueA, valueB]}
        #         else:
        #             self.valid_mismatches[url][value] = [valueA, valueB]
        #     else:
        #         if url not in self.invalid_pairs.keys():
        #             self.invalid_pairs[url] = {value: [valueA, valueB]}
        #         else:
        #             self.invalid_pairs[url][value] = [valueA, valueB]

    def compare_rows(self):
        # iterate over even-numbered rows in the dataframe and compare each video to itself
        generator = self.df.iterrows()
        for i in range(0, 500):
            # choose the next two rows, starting at the beginning
            rowA = generator.next()
            rowB = generator.next()

            # pull URL, race, gender, age, and instrument values from their respective cells
            rowA_url = str(rowA[1][0]).lower()
            rowA_race = str(rowA[1][2]).lower()
            rowA_gender = str(rowA[1][4]).lower()
            rowA_age = str(rowA[1][6]).lower()
            rowA_instrument = str(rowA[1][8]).lower()

            rowB_url = str(rowB[1][0]).lower()
            rowB_race = str(rowB[1][2]).lower()
            rowB_gender = str(rowB[1][4]).lower()
            rowB_age = str(rowB[1][6]).lower()
            rowB_instrument = str(rowB[1][8]).lower()

            # actually compare values
            if rowA_url != rowB_url:
                print "Error! Tried to compare data for two different URLs!"
            else:
                self.compare_value(rowA_race, rowB_race, self.race_data, self.race_data.keys(), rowA_url)
                self.compare_value(rowA_gender, rowB_gender, self.gender_data, self.gender_data.keys(), rowA_url)
                self.compare_value(rowA_age, rowB_age, self.age_data, self.age_data.keys(), rowA_url)
                self.compare_value(rowA_instrument, rowB_instrument, self.instrument_data, self.instrument_data.keys(), rowA_url)
                    # if rowA_race in self.race_options and rowB_race in self.race_options:
                    #     if rowA_url not in self.valid_mismatches.keys():
                    #         self.valid_mismatches[rowA_url] = {'race': [rowA_race, rowB_race]}
                    #     else:
                    #         self.valid_mismatches[rowA_url]['race'] = [rowA_race, rowB_race]
                    # else:
                    #     if rowA_url not in self.invalid_pairs.keys():
                    #         self.invalid_pairs[rowA_url] = {'race': [rowA_race, rowB_race]}
                    #     else:
                    #         self.invalid_pairs[rowA_url]['race'] = [rowA_race, rowB_race]

                # self.compare_value(rowA_race, rowB_race, 'race', self.race_options, rowA_url)
                # self.compare_value(rowA_gender, rowB_gender, 'gender', self.gender_options, rowA_url)
                # self.compare_value(rowA_instrument, rowB_instrument, 'instrument', self.instrument_options, rowA_url)

                # ages = [rowA_age, rowB_age]
                # ages.sort()
                # if ages not in self.age_pairs:  # ignores mismatches where age results are very close
                #     self.compare_value(rowA_age, rowB_age, 'age', self.age_data.keys(), rowA_url)

        return self.valid_mismatches

    # def count_value_mismatches(self, value, input_dictionary):
    #     count = 0
    #     differences = {}  # number of times people have disagreed on this value in a specific way
    #     for key in input_dictionary.keys():
    #         if value in input_dictionary[key].keys():
    #             count += 1
    #             curr_difference = input_dictionary[key][value]
    #             curr_difference.sort()  # this ensures that ['young adult', 'elder'] and ['elder', 'young adult'] are
    #             # recognized as being the same kind of disagreement
    #             curr_difference = tuple(curr_difference)
    #             if curr_difference not in differences:
    #                 differences[curr_difference] = 1
    #             else:
    #                 differences[curr_difference] += 1
    #     return [count, differences]

    def fill_count_dict(self, input_dict, output_dict):
        for row_key in input_dict.keys():
            output_dict[row_key] = {}
            for column_key in input_dict[row_key].keys():
                output_dict[row_key][column_key] = len(input_dict[row_key][column_key])

    def print_aggregate_info(self):

        race_counts = {}
        gender_counts = {}
        age_counts = {}
        instrument_counts = {}
        self.fill_count_dict(processor.race_data, race_counts)
        self.fill_count_dict(processor.gender_data, gender_counts)
        self.fill_count_dict(processor.age_data, age_counts)
        self.fill_count_dict(processor.instrument_data, instrument_counts)

        race_df = pd.DataFrame(race_counts)
        gender_df = pd.DataFrame(gender_counts)
        age_df = pd.DataFrame(age_counts)
        instrument_df = pd.DataFrame(instrument_counts)
        for frame in [race_df, gender_df, age_df, instrument_df]:
            print frame
            print ""

        print len(self.deleted_urls), "URLs had one or more field in which both inputs were NaN."
        print "People entered non-options for", len(self.invalid_input), "URLs. They were:", self.invalid_input

        # print "There are", len(self.valid_mismatches.keys()), "valid, mismatched pairs and",\
        #       len(self.invalid_pairs.keys()), "pairs with at least one invalid input."
        # print ""
        #
        # valid_race_counts = self.count_value_mismatches('race', self.valid_mismatches)
        # valid_gender_counts = self.count_value_mismatches('gender', self.valid_mismatches)
        # valid_age_counts = self.count_value_mismatches('age', self.valid_mismatches)
        # valid_instrument_counts = self.count_value_mismatches('instrument', self.valid_mismatches)
        #
        # invalid_race_counts = self.count_value_mismatches('race', self.invalid_pairs)
        # invalid_gender_counts = self.count_value_mismatches('gender', self.invalid_pairs)
        # invalid_age_counts = self.count_value_mismatches('age', self.invalid_pairs)
        # invalid_instrument_counts = self.count_value_mismatches('instrument', self.invalid_pairs)
        #
        # print "Of the valid, mismatched pairs,", valid_race_counts[0], "disagreed on the performer's race,",\
        #       valid_gender_counts[0],"disagreed on gender,", valid_age_counts[0],"disagreed significantly on age, and",\
        #       valid_instrument_counts[0] ,"disagreed on instrument."
        # print "Race:", valid_race_counts[1]
        # print "Gender:", valid_gender_counts[1]
        # print "Age:", valid_age_counts[1]
        # print "Instrument:", valid_instrument_counts[1]
        # print ""
        # print "Of the pairs containing invalid inputs, there were", invalid_race_counts[0],"pairs for race,",\
        #       invalid_gender_counts[0],"pairs for gender,", invalid_age_counts[0],"pairs for age, and",\
        #       invalid_instrument_counts[0],"pairs for instrument."
        # print "Race:", invalid_race_counts[1]
        # print "Gender:", invalid_gender_counts[1]
        # print "Age:", invalid_age_counts[1]
        # print "Instrument:", invalid_instrument_counts[1]



processor = RGAIProcessor('//Users/sen/Desktop/RGAI.csv')
processor.compare_rows()

processor.print_aggregate_info()
