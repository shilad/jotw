import pandas as pd


# This is loosely based on the RGAIProcessor.py file. It reads in and processes the validation dataset and uses it as a
# basis for comparison to evaluate the MTurk pilot task results.
#
# Nowhere does it differentiate between different reasons for disqualifying a video from the dataset, although it does
# count disqualification or lack thereof when considering whether the Turkers match the validation dataset. But it
# doesn't differentiate between, say, disqualifying a video for having bad lighting or disqualifying it for being just
# of someone's hands.

class ValidationProcessor():

    def __init__(self, validation_filepath, mturk_filepath):
        # read the validation dataset's CSV into a dataframe and format the dataframe appropriately
        self.validation_df = pd.read_csv(validation_filepath)
        self.validation_df.drop(self.validation_df.columns[12:], axis=1, inplace=True)
        self.validation_df.drop(['Initials', '1-3', '1-3.1', '1-3.2', '1-3.3', 'Comments'], axis=1, inplace=True)
        self.validation_df.rename(columns={'Randomly Selected URL':'URL', 'Conflict?':'Disqualified'}, inplace=True)

        self.check_validation_df()

        # read the MTurk task's into a dataframe and format it
        self.mturk_df = pd.read_csv(mturk_filepath)
        self.mturk_df = self.mturk_df.loc[:, ['Input.video_url', 'Answer.age', 'Answer.attractiveness', 'Answer.gender',
                                          'Answer.instrument', 'Answer.race', 'Answer.videoType']]
        self.mturk_df = self.mturk_df.set_index('Input.video_url')
        self.mturk_df.rename(columns={'Input.video_url':'URL', 'Answer.age':'Age',
                                      'Answer.attractiveness':'Attractiveness', 'Answer.gender':'Gender',
                                      'Answer.instrument':'Instrument', 'Answer.race':'Race',
                                      'Answer.videoType':'Disqualified'}, inplace=True)
        self.mturk_df = self.mturk_df.sort_index()

        # create dictionary of values as described in the HTML to values as described in the validation dataset
        self.metric_dict = {"Race":{"raceWhite":"White", "raceBlack":"Black", "raceHispanicLatino":"Hispanic",
                                    "raceAsian":"East Asian", "raceNativeAmerican":"Native American",
                                    "raceMiddleEastern":"Middle Eastern", "raceOther":"Other",
                                    "raceCantTell":"Not Sure", "Couldn't agree!":"X"},
                            "Gender":{"genderM":"Man", "genderF":"Woman", "genderN":"Non-binary", "genderX":"Not sure",
                                      "Couldn't agree!":"X"},
                            "Age":{"ageChild":"Child", "ageYoungAdult":"Young Adult", "ageMiddleAged":"Middle-Aged",
                                   "ageElder":"Elder", "Couldn't agree!":"X"},
                            "Instrument":{"saxophone":"SAX", "bass":"bass", "drums":"drums", "guitar":"guitar",
                                          "keyboard":"piano", "multiple":"other", "trumpet":"trumpet",
                                          "trombone":"trombone", "voice":"voice", "other":"other",
                                          "Couldn't agree!":"X"}}
        self.adjacent_ages = [['ageChild', 'ageYoungAdult'], ['ageMiddleAged', 'ageYoungAdult'],
                              ['ageElder', 'ageMiddleAged']]

    # makes sure the validation data matches where it should
    def check_validation_df(self):
        for i in range(1, 500, 2):
            row_one = self.validation_df.iloc[i]
            row_two = self.validation_df.iloc[i + 1]
            if row_one['Disqualified'] == 'NaN' and row_two['Disqualified'] == 'NaN':
                for metric in ['Race', 'Gender', 'Age', 'Instrument']:
                    # value = row_one[metric]
                    # if "/" in value:
                    #     self.validation_df = self.validation_df.set_value(i, metric, value.split("/"))
                    if row_one[metric] != row_two[metric]:
                        print "Something is wrong with your validation data! The url", row_one['URL'],\
                            "disagrees with", row_two['URL'], "on", metric, "!"
        self.validation_df = self.validation_df.iloc[1::2] # reduce the validation df to only odd-numbered rows
        # Note: The above line assumes that, if a video has been thrown out, that will be indicated in the 'Disqualified'
        # column in both of its rows. It only compares the actual values if the 'Disqualified' column, which records
        # invalid data, is empty, but it doesn't do anything with the column beyond that. This is not robust, but it
        # should work with this specific CSV.
        self.validation_df = self.validation_df.set_index('URL')

    # turker_position is an integer between 0 and 3 like first_turker and second_turker in the compare_two_turkers
    # method.
    def evaluate_one_turker(self, turker_position):
        total_agreements = 0
        total_disagreements = 0
        for i in range(0, 1500, 3):
            mturk_row = self.mturk_df.iloc[i + turker_position]
            url = mturk_row.name
            validation_row = self.validation_df.loc[url]
            current_match = True

            # only compare metrics if the video hasn't been thrown out
            if str(validation_row['Disqualified']) != 'nan':  # if the video is disqualified in the validation dataset
                if str(mturk_row['Disqualified']) != 'nan':  # if the video is also disqualified by the Turker
                    current_match = True
                else:  # if the validation dataset disqualifies the video, but the Turker doesn't
                    current_match = False
            else:
                if str(mturk_row['Disqualified']) == 'nan':  # if neither dataset disqualifies the video
                    for metric in ['Race', 'Gender', 'Age', 'Instrument']:
                        # if the Turker's input doesn't match anything in the list of acceptable answers for ANY of the
                        # metrics, it doesn't match. This cannot be reset if they agree on a later metric.
                        if self.metric_dict[metric][mturk_row[metric]] not in validation_row[metric].split("/"):
                            current_match = False
                else:  # if the Turker disqualifies the video, but the validation dataset doesn't
                    current_match = False

            if not current_match:
                total_disagreements += 1
            else:
                total_agreements += 1

        print "At position", turker_position, "there were", total_agreements, "agreements and", total_disagreements, \
            "disagreements with the validation dataset."
        return total_agreements, total_disagreements

    # first_turker and second_turker are integers 0-2 indicating which turkers should be compared with each other, since
    # there are 3 turkers per URL and the dataframe is organized by URL. For example, if first_turker is 0, then for
    # each URL, the first line will be compared (to some other line, determined by second_turker).
    def compare_two_turkers(self, first_turker, second_turker):
        total_agreements = 0
        total_disagreements = 0
        consensus_df = pd.DataFrame(columns=['URL', 'Race', 'Gender', 'Age', 'Instrument', 'Disqualified'])
        for i in range(0, 1500, 3):
            mturk_one = self.mturk_df.iloc[i + first_turker]
            mturk_two = self.mturk_df.iloc[i + second_turker]
            current_match = True
            current_consensus_line = {"URL":mturk_one.name}

            # only compare metrics if the video hasn't been thrown out
            if str(mturk_one['Disqualified']) != 'nan':  # if the video is disqualified by the first Turker
                if str(mturk_two['Disqualified']) != 'nan':  # if the video is also disqualified by the second Turker
                    current_match = True
                    current_consensus_line['Disqualified'] = mturk_one['Disqualified']
                else:  # if the first Turker disqualifies the video, but the second Turker doesn't
                    current_match = False
                    current_consensus_line['Disqualified'] = str(mturk_one['Disqualified']) + "/" +\
                                                             str(mturk_two['Disqualified'])
            else:
                if str(mturk_two['Disqualified']) == 'nan':  # if neither dataset disqualifies the video
                    for metric in ['Race', 'Gender', 'Age', 'Instrument']:
                        if mturk_one[metric] != mturk_two[metric]:
                            current_consensus_line[metric] = mturk_one[metric] + "/" + mturk_two[metric]
                            if metric == 'Age':
                                if sorted([mturk_one[metric], mturk_two[metric]]) in self.adjacent_ages:
                                    pass
                                else:
                                    current_match = False
                            else:
                                current_match = False
                        else:
                            current_consensus_line[metric] = mturk_one[metric]
                else:  # if the second Turker disqualifies the video, but the first Turker doesn't
                    current_match = False
                    current_consensus_line['Disqualified'] = str(mturk_one['Disqualified']) + "/" +\
                                                             str(mturk_two['Disqualified'])

            if not current_match:
                total_disagreements += 1
            else:
                total_agreements += 1
            consensus_df = consensus_df.append(current_consensus_line, ignore_index=True)

        print "Turkers at positions", first_turker, "and", second_turker, "had", total_agreements, "agreements and",\
            total_disagreements, "disagreements."
        return total_agreements, total_disagreements, consensus_df

    # This method is really similar to evaluate_one_turker and I probably could have planned this all out better.
    def evaluate_consensus(self, consensus_df):
        total_agreements = 0
        total_disagreements = 0
        for i in consensus_df.index.values.tolist():
            consensus_row = consensus_df.iloc[i]
            url = consensus_row['URL']
            validation_row = self.validation_df.loc[url]
            current_match = True

            # only compare metrics if the video hasn't been thrown out
            if str(validation_row['Disqualified']) != 'nan':  # if the video is disqualified in the validation dataset
                if str(consensus_row['Disqualified']) != 'nan':  # if the video is also disqualified by a Turker
                    current_match = True
                else:  # if the validation dataset disqualifies the video, but neither Turker does
                    current_match = False
            else:
                if str(consensus_row['Disqualified']) == 'nan':  # if neither dataset disqualifies the video
                    for metric in ['Race', 'Gender', 'Age', 'Instrument']:
                        match_exists = False
                        # if one of the Turkers' input matches anything in the list of acceptable answers
                        for item in consensus_row[metric].split("/"):
                            if self.metric_dict[metric][item] in validation_row[metric].split("/"):
                                match_exists = True
                        if not match_exists:
                            current_match = False
                else:  # if one or more Turker disqualifies the video, but the validation dataset doesn't
                    current_match = False

            if not current_match:
                total_disagreements += 1
            else:
                total_agreements += 1

        print "The consensus of these positions had", total_agreements, "agreements and", total_disagreements, \
            "disagreements with the validation dataset."
        return total_agreements, total_disagreements

    # This method doesn't find a rate of agreement among the 3 Turkers; it just creates a consensus dataframe for all of
    # them, to be evaluated against the validation dataset.
    def create_three_turker_consensus(self):
        consensus_df = pd.DataFrame(columns=['URL', 'Race', 'Gender', 'Age', 'Instrument', 'Disqualified'])
        for i in range(0, 1500, 3):
            mturk_one = self.mturk_df.iloc[i]
            mturk_two = self.mturk_df.iloc[i + 1]
            mturk_three = self.mturk_df.iloc[i + 2]
            current_consensus_line = {"URL": mturk_one.name}

            # had to do this one by one so reassignment would work properly. It's inefficient :/
            if str(mturk_one['Disqualified']) != "NaN":
                mturk_one = {"URL": mturk_one.name, "Race": mturk_one["Race"], "Gender": mturk_one["Gender"],
                             "Age": mturk_one["Age"], "Instrument": mturk_one["Instrument"],
                             "Disqualified":"Disqualified"}
            if str(mturk_two['Disqualified']) != "NaN":
                mturk_two = {"URL": mturk_two.name, "Race": mturk_two["Race"], "Age": mturk_two["Age"],
                             "Gender": mturk_two["Gender"], "Instrument": mturk_two["Instrument"],
                             "Disqualified":"Disqualified"}
            if str(mturk_three['Disqualified']) != "NaN":
                mturk_three = {"URL": mturk_three.name, "Race": mturk_three["Race"], "Gender": mturk_three["Gender"],
                               "Age": mturk_three["Age"], "Instrument": mturk_three["Instrument"],
                               "Disqualified":"Disqualified"}

            for metric in ['Race', 'Gender', 'Age', 'Instrument', 'Disqualified']:
                first_value = mturk_one[metric]
                second_value = mturk_two[metric]
                third_value = mturk_three[metric]
                if first_value == second_value == third_value:
                    current_consensus_line[metric] = first_value
                elif first_value == second_value or first_value == third_value or second_value == third_value:
                    if [first_value, second_value, third_value].count(first_value) > 1:  # if the first is the majority
                        current_consensus_line[metric] = first_value
                    elif [first_value, second_value, third_value].count(second_value) > 1:  # if the second is majority
                        current_consensus_line[metric] = second_value
                else:
                    current_consensus_line[metric] = "Couldn't agree!"
            consensus_df = consensus_df.append(current_consensus_line, ignore_index=True)
        return consensus_df


processor = ValidationProcessor('//Users/sen/Desktop/Validation Dataset.csv',
                                '//Users/sen/Desktop/MTurk Pilot Results.csv')
processor.evaluate_one_turker(0)
processor.evaluate_one_turker(1)
processor.evaluate_one_turker(2)

processor.evaluate_consensus(processor.compare_two_turkers(0, 1)[2])
processor.evaluate_consensus(processor.compare_two_turkers(1, 2)[2])
processor.evaluate_consensus(processor.compare_two_turkers(0, 2)[2])

print ""
print processor.create_three_turker_consensus()
processor.evaluate_consensus(processor.create_three_turker_consensus())