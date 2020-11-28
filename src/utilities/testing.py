
import os
import shutil
import zipfile
import subprocess


class Testing:

    @staticmethod
    def run(filename, config):
        GIVEN_FILES = config.get("GIVEN_FILES")
        SUBMISSION_FILES = config.get("SUBMISSION_FILES")
        COMPILATION_FILES = config.get("COMPILATION_FILES")

        result = {}

        # *********************************************************************
        # Test 1: Is there exactly one zip-file?

        directory_content = os.listdir(f"./{filename}")
        if len(directory_content) > 1:
            result["result"] = "Failed"
            result["message"] = f"Too many zip-files in directory: " + \
                f"{directory_content}"
            return result  # Jump to next attendee

        # *********************************************************************
        # Test 2: Does the zip-file contain all the required files?

        # Extract files from zip-files
        student_path = f"./{filename}"
        zip_file_path = f"./{filename}/{directory_content[0]}"
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(student_path)

        # If the contents of the folder do not match the requirements, which are:
        # Each students directory now has the zip-file in it and
        actual_files = os.listdir(student_path)

        # directory_content is just the zip-file from before
        desired_files = directory_content + SUBMISSION_FILES

        wrong_files_submitted = not all([
            desired_file in actual_files for desired_file in desired_files
        ])

        if wrong_files_submitted:
            result["result"] = "Failed"
            result["message"] = f"Wrong files in zip-file:" + \
                f" Desired: {desired_files}, Actual: {actual_files}"
            return result  # Jump to next attendee

        # *********************************************************************
        # Test 3: Does Compilation work as expected?

        # Copy all given files into the students directory to compile them together
        for given_file in GIVEN_FILES:
            source = f"../given/{given_file}"
            destination = f"./{filename}/{given_file}"
            shutil.copyfile(source, destination)

        # Validate the state of the compilation directory
        directory_content = os.listdir(f"./{filename}")
        assert(all([
            file in directory_content for file in (SUBMISSION_FILES + GIVEN_FILES)
        ]))

        # Determining the compilation string
        compilation_string = Testing._get_compilation_string(
            f"./{filename}", COMPILATION_FILES
        )

        # Compiling the file
        process = subprocess.Popen(
            compilation_string,
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        output, message = process.communicate()

        if process.returncode != 0:
            result["result"] = "Failed"
            result["message"] = f"Did not compile: {message.decode()}"
            while result["message"].endswith('\n'):
                result["message"] = result["message"][:-1]
            result["input"] = {}

            for file in SUBMISSION_FILES:
                result["input"][file] = open(
                    f"./{filename}/{file}", 'r'
                ).read()

            return result  # Jump to next attendee

        # *********************************************************************
        # Test 4 (Manual): Execute the file and store the generated output

        def run_executable(slash="/"):
            # Executing the file
            process = subprocess.Popen(
                f".{slash}{filename}{slash}program.out", shell=True,
                stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )
            output, error_message = process.communicate()
            exit_code = process.returncode
            output = output.decode("utf-8", "replace")

            assert len(output) > 0

            result["result"] = "Success"
            result["exit_code"] = exit_code
            result["output"] = output
            while result["output"].endswith('\n'):
                result["output"] = result["output"][:-1]
            result["input"] = {}

        try:
            run_executable(slash="/")
        except:
            run_executable(slash="\\")

        for file in SUBMISSION_FILES:
            def read(enc):
                return open(
                    f"./{filename}/{file}", 'r',
                    encoding=enc
                ).read()

            try:
                result["input"][file] = read('utf-8')
            except:
                try:
                    result["input"][file] = read('utf-16')
                except:
                    try:
                        result["input"][file] = read('iso-8859-15')
                    except:
                        result["input"][file] = "Really weird file encoding ... Please look at the file directly!"

        return result

    @staticmethod
    def _get_compilation_string(relative_path, compilation_files):
        cs = "gcc -Wall -Werror -std=c99"
        for file in compilation_files:
            cs += f" {relative_path}/{file}"
        cs += f" -o {relative_path}/program.out"
        return cs
