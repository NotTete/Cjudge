from pathlib import Path
import shutil

class Config:
    """
    Class for managing configurations of the app
    """

    config_folder = Path(Path.home(), ".cjudge")
    config_file = Path(config_folder, "config.json")
    template_file = Path(config_folder, "template.cpp")

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
        package_config_folder = Path(Path(__file__).parent, "config")

        package_template_file = Path(package_config_folder, "template.cpp")
        shutil.copyfile(package_template_file, Config.template_file)

        package_config_file = Path(package_config_folder, "config.json")
        shutil.copyfile(package_config_file, Config.config_file)

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
            package_template_file = Path(package_config_folder, "template.cpp")
            shutil.copyfile(package_template_file, Config.template_file)

        if(not Config.config_file.exists()):
            package_config_file = Path(package_config_folder, "config.json")
            shutil.copyfile(package_config_file, Config.config_file)
        

    @staticmethod
    def copy_template(path: Path):
        """
        Copy the code template to a destination path

        Args:
            path (Path): Destination path
        """

        Config.repair_config()
        shutil.copyfile(Config.template_file, path)
