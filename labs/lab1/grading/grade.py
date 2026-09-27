import subprocess
import shutil
import os
import json
import threading
import math
import shlex
import argparse



def run_fuzzer(cwd: str, cmd_str: str, timeout: int, validate_cmd_str: str = None):
        command = shlex.split(cmd_str)
        ret_code = 0
        p = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)
        try:
                out, _ = p.communicate(timeout=timeout)
                ret_code = p.returncode

        except subprocess.TimeoutExpired:
                p.kill()
                out, _ = p.communicate()
        
        # handle other exceptions
        except Exception as e:
                p.kill()
                ret_code = p.returncode
                out, _ = p.communicate()
                # combine the exception with the output
                out += 'Exception:\n' + str(e) + '\n' + out
        
        # write return code and output to two files
        output_file = f"{cwd}/output"
        with open(output_file, "w") as f:
                f.write(out)
        ret_code_file = f"{cwd}/ret_code"
        with open(ret_code_file, "w") as f:
                f.write(str(ret_code))
        
        # run validation command if provided
        if validate_cmd_str is not None:
                command = shlex.split(validate_cmd_str)
                ret_code = 0
                p = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)
                out, _ = p.communicate()
                # write validation output to a file
                validate_output_file = f"{cwd}/validate_output"
                with open(validate_output_file, "w") as f:
                        f.write(out)
        

def setup_fuzzer_env(student_dir: str, template_dir: str, data_dir: str, requried_files: list[str]) -> str:
        student_dir_name = os.path.basename(student_dir)
        destination_dir = f"{data_dir}/{student_dir_name}"
        
        if os.path.exists(destination_dir):
                raise FileExistsError(f"The directory '{destination_dir}' already exists.")
        
        shutil.copytree(student_dir, destination_dir)

        # check if all required files are present
        for file in requried_files:
                if not os.path.exists(f"{template_dir}/{file}"):
                        raise FileNotFoundError(f"File '{file}' not found in '{student_dir}'.")
        
        # copy all required files to the destination directory
        for file in requried_files:
                if file.endswith('/'):
                        shutil.copytree(f"{template_dir}/{file}", f"{destination_dir}/{file}")
                else:
                        shutil.copy(f"{template_dir}/{file}", f"{destination_dir}/{file}")

        return destination_dir

class TestConfig:
        # fields: required_files, cmd_str, timeout
        def __init__(self, required_files: list[str], cmd_str: str, timeout: int, validate_cmd_str: str = None):
                self.required_files = required_files
                self.cmd_str = cmd_str
                self.timeout = timeout
                self.validate_cmd_str = validate_cmd_str
        # load from a json file
        @staticmethod
        def from_json(file: str) -> 'TestConfig':
                with open(file, "r") as f:
                        data = json.load(f)
                        return TestConfig(data['required_files'], data['cmd'], data['timeout'], data.get('validate_cmd', ''))
        def to_dict(self):
                return {
                        'required_files': self.required_files,
                        'cmd': self.cmd_str,
                        'timeout': self.timeout,
                        'validate_cmd': self.validate_cmd_str
                }
        def to_json(self):
                return json.dumps(self.to_dict(), indent=4)
        def __str__(self):
                return self.to_json()
        def __repr__(self) -> str:
                return str(self)
 
def run_one_fuzzer_test(student_dir: str, template_dir: str, data_dir: str, test_config: TestConfig):
        destination_dir = setup_fuzzer_env(student_dir, template_dir, data_dir, test_config.required_files)
        run_fuzzer(destination_dir, test_config.cmd_str, test_config.timeout, test_config.validate_cmd_str)
  
def run_fuzzer_test(all_students_dir: str, template_dir: str, data_dir: str):
        # load the test config from template_dir/config.json
        config = TestConfig.from_json(f"{template_dir}/config.json")
        # log the config
        print(f"Loaded config: {config}")

        results = {}

        batch_size = 16
        num_students = len(os.listdir(all_students_dir))
        num_batches = math.ceil(num_students / batch_size)

        for i in range(num_batches):
                start_index = i * batch_size
                end_index = min((i + 1) * batch_size, num_students)
                batch_students = os.listdir(all_students_dir)[start_index:end_index]

                threads = []
                # log the batch
                print(f"Running batch {i+1}/{num_batches} with students: {batch_students}")
                for student_dir in batch_students:
                        t = threading.Thread(target=lambda: results.update({student_dir: run_one_fuzzer_test(all_students_dir+'/'+student_dir, template_dir, data_dir, config)}))
                        threads.append(t)
                        t.start()
                for t in threads:
                        t.join()
        
        # recursively set files in data_dir to be readable and writable by all
        os.system(f"chmod -R 777 {data_dir}")


if __name__ == "__main__":
        # parse command line arguments: -s <student_dir> -t <template_dir> -d <data_dir>
        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--students", help="Directory containing all student directories", required=True)
        parser.add_argument("-t", "--template", help="Directory containing the template files", required=True)
        parser.add_argument("-d", "--data", help="Directory to store the data for each student", required=True)
        args = parser.parse_args()
        # create data dir if it does not exist
        if not os.path.exists(args.data):
                os.makedirs(args.data)
        run_fuzzer_test(args.students, args.template, args.data)