import os

def get_aid_list(base_path):
    """
    Retrieves a list of directory names within the specified base path.

    Args:
        base_path (str): The path to the base directory where subdirectories will be listed.

    Returns:
        list: A list of directory names found in the base path. If the base path does not exist, 
            an empty list is returned.

    Raises:
        FileNotFoundError: If the specified base path does not exist, a message is printed, 
                        and an empty list is returned.
    """
    try:
        directorios = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        return directorios
    except FileNotFoundError:
        print(f"El directorio {base_path} no existe.")
        return []