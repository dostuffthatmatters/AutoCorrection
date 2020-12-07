
config = {
    "HW_NUMBER": 2,

    # The file that the students were provided with
    "GIVEN_FILES": ["main_bot_correction.c", "stdin.txt"],

    # The files that are required to be in the submitted zip-file
    "SUBMISSION_FILES": ["lonely_bot.c"],

    # These are alle the files that should be compiled and linked together.
    # May not be equal to GIVEN_FILES + SUBMISSION_FILES. However all files
    # from GIVEN_FILES + SUBMISSION_FILES will be present in the directory
    # where the compilation takes place
    "COMPILATION_FILES": ["main_bot_correction.c"]
}
