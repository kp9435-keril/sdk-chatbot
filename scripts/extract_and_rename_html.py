import os
import shutil
from pathlib import Path
from typing import List, Tuple

# ====== CONFIGURATION NOTES ======
# This script will prompt for:
# - Source Directory Path
# - Destination Directory Path
# - Dry Run Option
# - Verbose Output Option
# ===================================


def find_html_files(source_dir: str) -> List[Tuple[str, str]]:
    """
    Recursively find all HTML files in the source directory.
    
    Args:
        source_dir (str): Path to the source directory
        
    Returns:
        List[Tuple[str, str]]: List of tuples containing (file_path, relative_path)
    """
    html_files = []
    source_path = Path(source_dir)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory '{source_dir}' does not exist")
    
    # Recursively find all HTML files
    for file_path in source_path.rglob("*.html"):
        if file_path.is_file():
            # Get relative path from source directory
            relative_path = file_path.relative_to(source_path)
            html_files.append((str(file_path), str(relative_path)))
    
    return html_files


def generate_new_filename(relative_path: str) -> str:
    """
    Generate new filename by replacing path separators with dots.
    
    Args:
        relative_path (str): Original relative path
        
    Returns:
        str: New filename with dot separators
    """
    # Convert path separators to dots
    new_name = relative_path.replace(os.sep, '.')
    
    # Handle case where path uses forward slashes (cross-platform compatibility)
    if '/' in new_name:
        new_name = new_name.replace('/', '.')
    
    return new_name


def copy_and_rename_files(html_files: List[Tuple[str, str]], dest_dir: str) -> dict:
    """
    Copy HTML files to destination directory with new names.
    
    Args:
        html_files (List[Tuple[str, str]]): List of (source_path, relative_path) tuples
        dest_dir (str): Destination directory path
        
    Returns:
        dict: Results summary with success status and counts
    """
    dest_path = Path(dest_dir)
    
    # Create destination directory if it doesn't exist
    dest_path.mkdir(parents=True, exist_ok=True)
    
    copied_count = 0
    skipped_count = 0
    
    for source_file, relative_path in html_files:
        # Generate new filename
        new_filename = generate_new_filename(relative_path)
        dest_file = dest_path / new_filename
        
        try:
            # Check if destination file already exists
            if dest_file.exists():
                print(f"  ⚠️  {new_filename} already exists, skipping...")
                skipped_count += 1
                continue
            
            # Copy the file
            shutil.copy2(source_file, dest_file)
            print(f"  ✓ Copied: {relative_path} -> {new_filename}")
            copied_count += 1
            
        except Exception as e:
            print(f"  ✗ Error copying {relative_path}: {e}")
            skipped_count += 1
    
    return {
        'success': True,
        'copied_count': copied_count,
        'skipped_count': skipped_count,
        'total_files': copied_count + skipped_count
    }


def get_user_configuration():
    """
    Get source and destination directory configuration from user input.
    """
    print("� HTML File Extractor Configuration Setup")
    print("-" * 40)
    
    # Get source directory
    source_dir = input("Enter source directory path (to search for HTML files): ").strip()
    while not source_dir:
        print("Source directory path is required.")
        source_dir = input("Enter source directory path (to search for HTML files): ").strip()
    
    # Get destination directory
    dest_dir = input("Enter destination directory path (where renamed files will be copied): ").strip()
    while not dest_dir:
        print("Destination directory path is required.")
        dest_dir = input("Enter destination directory path (where renamed files will be copied): ").strip()
    
    return {
        'source_dir': source_dir,
        'dest_dir': dest_dir
    }
def extract_and_rename_html_files(config):
    """
    Extract and rename HTML files from source to destination directory.
    """
    print("🔄 Starting HTML File Extraction and Renaming Process")
    print("-" * 40)
    
    try:
        # Validate source directory exists
        if not os.path.exists(config['source_dir']):
            print(f"❌ Source directory '{config['source_dir']}' does not exist.")
            return {
                'success': False,
                'copied_count': 0,
                'skipped_count': 0,
                'total_files': 0
            }
        
        # Find all HTML files
        print(f"Searching for HTML files in: {config['source_dir']}")
        html_files = find_html_files(config['source_dir'])
        
        if not html_files:
            print(f"No HTML files found in '{config['source_dir']}'")
            return {
                'success': True,
                'copied_count': 0,
                'skipped_count': 0,
                'total_files': 0
            }
        
        print(f"Found {len(html_files)} HTML file(s)")
        
        print("\nFiles to be processed:")
        for _, relative_path in html_files:
            new_name = generate_new_filename(relative_path)
            print(f"  {relative_path} -> {new_name}")
        
        # Copy and rename files
        print(f"\nCopying files to: {config['dest_dir']}")
        result = copy_and_rename_files(html_files, config['dest_dir'])
        
        print(f"\nExtraction Summary:")
        print(f"Successfully copied: {result['copied_count']} files")
        print(f"Files skipped: {result['skipped_count']} files")
        print(f"Total files processed: {result['total_files']}")
        
        return result
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'success': False,
            'copied_count': 0,
            'skipped_count': 0,
            'total_files': 0
        }


def main():
    """Main function to handle user input and execute the script."""
    print("\n")
    print("=" * 50)
    print("📁 HTML File Extractor and Renamer")
    print("=" * 50)
    
    # Get configuration from user
    config = get_user_configuration()
    
    # Show configuration summary
    print(f"\nConfiguration Summary:")
    print(f"Source directory: {config['source_dir']}")
    print(f"Destination directory: {config['dest_dir']}")
    
    # Confirm before proceeding
    confirmation = input("\nProceed with HTML file extraction and renaming? Type 'YES' to confirm: ")
    
    if confirmation == "YES":
        result = extract_and_rename_html_files(config)
        if result['success']:
            print(f"\n✅ HTML file extraction and renaming completed successfully!")
        else:
            print(f"\n❌ HTML file extraction failed.")
    else:
        print("Operation cancelled.")


if __name__ == "__main__":
    main()
