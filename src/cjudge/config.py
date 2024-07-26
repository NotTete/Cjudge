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
    def get_compiler():
        """
        Get the C++ compiler
        """

        Config.repair_config()
        
        # Try to get the compiler from the config json
        config_json = None
        try:
            file = open(Config.config_file, "r")
            config_json = json.load(file)
        except json.decoder.JSONDecodeError:
            shutil.copyfile(Config.package_config_file, Config.config_file)
            config_json = json.load(file)
        finally:
            file.close()

        compiler = config_json.get("compiler")
        
        if(compiler != None):
            # If the value exist return
            return compiler
        else:
            # Else get it from package
            with open(Config.package_config_file, "r") as file:
                package_config_json = json.load(file)

            compiler = package_config_json.get("compiler")

            # Save it on the config file
            config_json["compiler"] = compiler
            with open(Config.config_file, "w") as file:
                json.dump(config_json, file, indent="\t")

            return compiler
    
        