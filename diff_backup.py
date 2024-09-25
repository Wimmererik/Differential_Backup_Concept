import os
import shutil
import time

source_directory = "./source/"
full_backup_directory = "./full/"
differential_backup_directory = "./differential/"
    

def full_backup(src_dir: str, backup_dir: str):
    # Remove existing folder, copy source folder contents to backup_dir
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    shutil.copytree(src_dir, backup_dir)

    # Save timestamp of backup completion to .txt file
    with open(backup_dir+"timestamp.txt", "w") as f:
        f.write(str(time.time()))

    print(f"Full backup completed.")


def differential_backup(src_dir: str, diff_backup_dir: str, full_backup_dir: str):
    if not os.path.exists(diff_backup_dir):
        os.mkdir(diff_backup_dir)

    # Read full backup time
    if os.path.exists(full_backup_dir+"/timestamp.txt"):
        with open(full_backup_dir+"/timestamp.txt") as f:
            full_backup_time = f.read()

    for foldername, subfolders ,filenames in os.walk(src_dir):
        for filename in filenames:
            src_file = os.path.join(foldername, filename)
            file_copy = os.path.join(diff_backup_dir, os.path.relpath(src_file, src_dir))

            # Get editin timestamp of source file
            file_mod_time = str(os.path.getmtime(src_file))

            # Only copy if file was edited after last full backup
            if file_mod_time > full_backup_time:
                backup_subdir = os.path.dirname(file_copy)
                if not os.path.exists(backup_subdir):
                    os.makedirs(backup_subdir)
                shutil.copy2(src_file, file_copy)

    print(f"Differential backup completed.")


def restore_base(src_dir: str, full_backup_dir: str):
    if not os.path.exists(src_dir):
        os.mkdir(src_dir)
    
    if os.path.exists(full_backup_dir):
        for foldername, subfolders, filenames in os.walk(full_backup_dir):
            for filename in filenames:
                if not filename=="timestamp.txt":
                    src_file = os.path.join(foldername, filename)
                    file_copy = os.path.join(src_dir, os.path.relpath(src_file, full_backup_dir))
                    
                    backup_subdir = os.path.dirname(file_copy)
                    if not os.path.exists(backup_subdir):
                        os.makedirs(backup_subdir)
                    
                    shutil.copy2(src_file, file_copy)

    print("Initial full backup restored.")


def restore_full(src_dir: str, diff_backup_dir: str, full_backup_dir: str):
    if not os.path.exists(src_dir):
        os.mkdir(src_dir)
    
    # Restore full backup first
    if os.path.exists(full_backup_dir):
        for foldername, subfolders, filenames in os.walk(full_backup_dir):
            for filename in filenames:
                src_file = os.path.join(foldername, filename)
                file_copy = os.path.join(src_dir, os.path.relpath(src_file, full_backup_dir))
                
                backup_subdir = os.path.dirname(file_copy)
                if not os.path.exists(backup_subdir):
                    os.makedirs(backup_subdir)
                
                shutil.copy2(src_file, file_copy)

    # Then overwrite files with diff backups files
    if os.path.exists(diff_backup_dir):
        for foldername, subfolders, filenames in os.walk(diff_backup_dir):
            for filename in filenames:
                src_file = os.path.join(foldername, filename)
                file_copy = os.path.join(src_dir, os.path.relpath(src_file, diff_backup_dir))
                
                # Check if file exists in full backup and compare edit timestamps
                full_backup_file = os.path.join(full_backup_dir, os.path.relpath(src_file, diff_backup_dir))
                
                if os.path.exists(full_backup_file):
                    full_backup_mod_time = os.path.getmtime(full_backup_file)
                    diff_backup_mod_time = os.path.getmtime(src_file)

                    # Only copy newer files
                    if diff_backup_mod_time > full_backup_mod_time:
                        backup_subdir = os.path.dirname(file_copy)
                        if not os.path.exists(backup_subdir):
                            os.makedirs(backup_subdir)
                        shutil.copy2(src_file, file_copy)
                else:
                    # Copy files that are not in full backup
                    backup_subdir = os.path.dirname(file_copy)
                    if not os.path.exists(backup_subdir):
                        os.makedirs(backup_subdir)
                    shutil.copy2(src_file, file_copy)

    print("All backed up files restroed.")


def print_menu():
    print("Proof of Concept tool for differential backups:\n")
    print("  -> BaseBackup - Create a new full backup, will overwrite files in target directory")
    print("  -> DiffBackup - Create a new differential backup")
    print("  -> RestoreBase - Only restore the original full backup (Move to source folder)")
    print("  -> RestoreFull - Restore the files of all backups (Move to source folder)")
    print("  -> Exit - Exit the program\n")

    print("Since this is only a Proof of Concept, files are simply copied between different folders.\n")


def menu_input():
    while True:
        inp = input("> ").strip().lower()
        
        if inp == "exit":
            break
        elif inp == "basebackup":
            full_backup(source_directory, full_backup_directory)
        elif inp == "diffbackup":
            differential_backup(source_directory, differential_backup_directory, full_backup_directory)
        elif inp == "restorebase":
            restore_base(source_directory, full_backup_directory)
        elif inp == "restorefull":
            restore_full(source_directory, differential_backup_directory, full_backup_directory)
        else:
            print("Unknown command")


if __name__ == "__main__":

    print_menu()
    menu_input()
