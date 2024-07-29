from pathlib import Path
import shutil
import json

class Config:
    """
    Class for managing configurations of the app
    """

    config_folder = Path(Path.home(), ".cjudge")
    config_file = Path(config_folder, "config.json")
    template_file = Path(config_folder, "template.cpp")
    package_config_folder = Path(Path(__file__).parent, "config")
    package_config_file = Path(package_config_folder, "config.json")
    package_template_file = Path(package_config_folder, "template.cpp")

    @staticmethod
    def create_config():
        """
        Create config folder and deletes any other previous config
        """
        # Check if config exists and creates it
        if(Config.config_folder.exists):
            shutil.rmtree(Config.config_folder)
        Config.config_folder.mkdir()

        # Move the corresponding files
        shutil.copyfile(Config.package_template_file, Config.template_file)
        shutil.copyfile(Config.package_config_file, Config.config_file)

    @staticmethod
    def repair_config():
        """
        Copies any missing file in the config folder
        """

        # Check if config exists and creates it
        if(not Config.config_folder.exists()):
            Config.config_folder.mkdir()

        package_config_folder = Path(Path(__file__).parent, "config")

        # Check template and config file
        if(not Config.template_file.exists()):
            shutil.copyfile(Config.package_template_file, Config.template_file)

        if(not Config.config_file.exists()):
            shutil.copyfile(Config.package_config_file, Config.config_file)
        

    @staticmethod
    def copy_template(path: Path):
        """
        Copy the code template to a destination path

        Args:
            path (Path): Destination path
        """

        Config.repair_config()
        shutil.copyfile(Config.template_file, path)

    @staticmethod
    def get_config_json():
        config_json = None
        try:
            file = open(Config.config_file, "r")
            config_json = json.load(file)
        except json.decoder.JSONDecodeError:
            shutil.copyfile(Config.package_config_file, Config.config_file)
            config_json = json.load(file)
        finally:
            file.close()
        
        return config_json

    @staticmethod
    def repair_config_parameter(config_json, parameter, new_value = None):
            if new_value == None:
                with open(Config.package_config_file, "r") as file:
                    package_config_json = json.load(file)

                parameter_value = package_config_json.get(parameter)
            else:
                parameter_value = new_value

            config_json[parameter] = parameter_value
            with open(Config.config_file, "w") as file:
                json.dump(config_json, file, indent="\t")

            return parameter_value

    @staticmethod
    def get_compiler():
        """
        Get the C++ compiler
        """

        Config.repair_config()
        config_json = Config.get_config_json()

        compiler = config_json.get("compiler")
        
        if(compiler != None):
            # If the value exist return
            return compiler
        else:
            compiler = Config.repair_config_parameter(config_json, "compiler")
            return compiler
    
    @staticmethod   
    def get_test_output():        
        """
        Get the default test output mode
        """

        Config.repair_config()
        config_json = Config.get_config_json()

        output = config_json.get("test-output")
        choices = ["minimal", "full", "error"]
        if(output in choices):
            return output
        else:
            output = Config.repair_config_parameter(config_json, "test-output")
            return output

    @staticmethod   
    def get_kattis_name():        
        """
        Get the default test output mode
        """

        Config.repair_config()
        config_json = Config.get_config_json()

        output = config_json.get("kattis-username")
        if(output != ""):
            return output
        else:
            output = Config.repair_config_parameter(config_json, "kattis-username", "")
            return None

    @staticmethod   
    def get_kattis_token():        
        """
        Get the default test output mode
        """

        Config.repair_config()
        config_json = Config.get_config_json()

        output = config_json.get("kattis-token")
        if(output != ""):
            return output
        else:
            output = Config.repair_config_parameter(config_json, "kattis-token", "")
            return None