import os
import shutil


class ErrorsMessages:
    no_eu4_mods = "No EUIV mods found."
    no_eu4_documents = "No EUIV documents folder found in the default location."


class AnswerHandler:
    @staticmethod
    def is_a_yes_answer(answer):
        return answer.lower() == "y" or answer.lower() == "yes" or answer.lower() == "true"

    @staticmethod
    def is_copy_or_move_answer(answer):
        if answer.lower() == "c" or answer.lower() == "copy" or answer.lower() == "co" or answer.lower() == "cp":
            return "c"
        elif answer.lower() == "m" or answer.lower() == "move" or answer.lower() == "mo" or answer.lower() == "mv":
            return "m"


class ModHandler:
    def __init__(self, current_mod_dir, target_mod_dir, copy_mods=False):
        self.current_mod_dir = current_mod_dir
        self.target_mod_dir = target_mod_dir
        self.copy_mods = copy_mods
        self.existing_ids = []

    def move_mod(self, mod_id):
        if os.path.exists(os.path.join(self.target_mod_dir, mod_id)):
            print(f"Mod {mod_id} already exists in the target folder. Skipping.")
            self.existing_ids.append(mod_id)
            return

        if self.copy_mods:
            shutil.copytree(os.path.join(self.current_mod_dir, mod_id).__str__(),
                            os.path.join(self.target_mod_dir, mod_id).__str__())
            print(f"Mod {mod_id} copied to the target folder.")
        else:
            os.rename(os.path.join(self.current_mod_dir, mod_id), os.path.join(self.target_mod_dir, mod_id))
            print(f"Mod {mod_id} moved to the target folder.")

        descriptor_mod_file = os.path.join(self.target_mod_dir, mod_id, "descriptor.mod")
        if os.path.exists(descriptor_mod_file):
            os.rename(descriptor_mod_file, os.path.join(self.target_mod_dir, f"{mod_id}.mod"))
            print(f"descriptor.mod file moved to target folder and renamed to {mod_id}.mod.")

            with open(os.path.join(self.target_mod_dir, f"{mod_id}.mod"), "r") as file:
                lines = file.readlines()

            with open(os.path.join(self.target_mod_dir, f"{mod_id}.mod"), "w") as file:
                path_initially_existed = False
                for line in lines:
                    if "path" in line:
                        path_initially_existed = True
                        line = f"path=\"mod/{mod_id}/\"\n"
                    file.write(line)

                if not path_initially_existed:
                    file.write(f"\npath=\"mod/{mod_id}/\"\n")
            print(f"{mod_id}.mod file updated with correct mod path.")
        else:
            print(f"descriptor.mod file not found for mod {mod_id}. Creating a basic one.")
            with open(os.path.join(self.target_mod_dir, f"{mod_id}.mod"), "w") as file:
                file.write(f"name=\"{mod_id}\"\n")
                file.write(f"path=\"mod/{mod_id}/\"\n")
                file.write("supported_version=\"*\"\n")

    def confirm_move_existing_mods(self):
        if self.existing_ids:
            print("The following mods already existed in the target folder:")
            for mod_id in self.existing_ids:
                print(mod_id)

            print("Do you want to overwrite them anyway? (y/n)")
            if AnswerHandler.is_a_yes_answer(input()):
                for mod_id in self.existing_ids:
                    shutil.rmtree(os.path.join(self.target_mod_dir, mod_id))
                    print(f"Mod {mod_id} folder removed from the target folder.")

                    os.remove(os.path.join(self.target_mod_dir, f"{mod_id}.mod"))
                    print(f"{mod_id}.mod file removed from the target folder.")

                    self.move_mod(mod_id)
            else:
                print("Existing mods not moved.")
        else:
            print("No confirmations needed.")


class Program:
    document_folder = os.path.join(os.path.expanduser("~"), "Documents")
    eu4_documents_folder = os.path.join(document_folder, "Paradox Interactive", "Europa Universalis IV")
    target_mods_folder = os.path.join(eu4_documents_folder, "mod")
    current_directory = os.path.dirname(os.path.abspath(__file__))
    initial_mods_folder = ""

    @staticmethod
    def initialize():
        if os.path.exists(os.path.join(Program.current_directory, "steamcmd.exe")):
            print("SteamCMD found.")
            Program.initial_mods_folder = os.path.join(Program.current_directory, "steamapps", "workshop", "content",
                                                       "236850")
        else:
            print("SteamCMD not found in current directory, checking for EUIV content folder.")
            Program.initial_mods_folder = os.path.join(Program.current_directory, "236850")

        if not os.path.exists(Program.initial_mods_folder):
            print(
                "Neither steamcmd nor the EUIV content folder found. Would you like to use the current directory "
                "instead? (y/n)")
            if AnswerHandler.is_a_yes_answer(input()):
                Program.initial_mods_folder = Program.current_directory
                print("Using current directory as mods folder.")
            else:
                raise Exception(ErrorsMessages.no_eu4_mods)

        print("EUIV mods folder set.")

        if not os.path.exists(Program.eu4_documents_folder):
            raise Exception(ErrorsMessages.no_eu4_documents)

        print("EUIV documents folder set.")

        if not os.path.exists(Program.target_mods_folder):
            os.makedirs(Program.target_mods_folder)
            print("EUIV Documents mods folder created.")
        else:
            print("EUIV Documents mods folder found.")

    @staticmethod
    def move_mods():
        print("Do you want to copy or fully move the mods? (c/m)")
        copy_or_move = AnswerHandler.is_copy_or_move_answer(input())
        mod_handler = ModHandler(Program.initial_mods_folder, Program.target_mods_folder, copy_or_move == "c")
        for mod in os.listdir(Program.initial_mods_folder):
            mod_handler.move_mod(mod)
        mod_handler.confirm_move_existing_mods()


def main():
    Program.initialize()
    Program.move_mods()


if __name__ == "__main__":
    main()
