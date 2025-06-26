import os
from openai import AzureOpenAI
import getpass

# ====== CONFIGURATION NOTES ======
# This script will prompt for:
# - Azure OpenAI API Key (masked input)
# - Azure Endpoint  
# - API Version
# - Vector Store ID
# - Directory Path (for verification)
# ===================================

def get_user_configuration():
    """
    Get Azure OpenAI configuration from user input.
    """
    print("🔧 Azure OpenAI Configuration Setup")
    print("-" * 40)
    
    # Get API Key (masked input)
    api_key = getpass.getpass("Enter your Azure OpenAI API Key: ")
    
    # Show masked API key for confirmation (show last 5 digits)
    if len(api_key) >= 5:
        masked_key = "*" * (len(api_key) - 5) + api_key[-5:]
    else:
        masked_key = "*" * len(api_key)
    
    print(f"API Key entered: {masked_key}")
    
    # Get Azure Endpoint
    azure_endpoint = input("Enter your Azure OpenAI Endpoint (e.g., https://your-service.openai.azure.com/): ").strip()
    while not azure_endpoint:
        print("Azure Endpoint is required.")
        azure_endpoint = input("Enter your Azure OpenAI Endpoint (e.g., https://your-service.openai.azure.com/): ").strip()
    
    # Get API Version
    api_version = input("Enter API Version (e.g., 2025-03-01-preview): ").strip()
    while not api_version:
        print("API Version is required.")
        api_version = input("Enter API Version (e.g., 2025-03-01-preview): ").strip()
    
    # Get Vector Store ID
    vector_store_id = input("Enter Vector Store ID (e.g., vs_8K3mX9nP2wQ7vR5tA6bC4dE1): ").strip()
    while not vector_store_id:
        print("Vector Store ID is required.")
        vector_store_id = input("Enter Vector Store ID (e.g., vs_8K3mX9nP2wQ7vR5tA6bC4dE1): ").strip()
    
    # Get Directory Path
    directory_path = input("Enter directory path to verify against (leave empty to skip verification): ").strip()
    
    return {
        'api_key': api_key,
        'api_version': api_version,
        'azure_endpoint': azure_endpoint,
        'vector_store_id': vector_store_id,
        'directory_path': directory_path
    }

def initialize_client(config):
    """
    Initialize the AzureOpenAI client with the provided configuration.
    """
    try:
        client = AzureOpenAI(
            api_key=config['api_key'],
            api_version=config['api_version'],
            azure_endpoint=config['azure_endpoint']
        )
        return client
    except Exception as e:
        print(f"Error initializing Azure OpenAI client: {e}")
        return None

def retrieve_all_files(client, vector_store_id):
    """
    Function to retrieve all files from the vector store.
    """
    print(f"Retrieving files from vector store: {vector_store_id}")
    all_files = []
    after = None

    try:
        while True:
            # Fetch the current page of files
            response = client.vector_stores.files.list(vector_store_id=vector_store_id, after=after)
            
            files = response.data
            
            for file in files:
                all_files.append(file.id)
            
            # Check if there are more files to fetch
            if response.has_more:
                after = response.data[-1].id
            else:
                break

        print(f"Found {len(all_files)} files in vector store.")
        return all_files
    except Exception as e:
        print(f"Error retrieving files from vector store: {e}")
        return []

def retrieve_name_of_all_files(client, files):
    """
    Retrieve the names of all files from their IDs.
    """
    print("Retrieving file names...")
    file_names = []
    failed_count = 0
    
    for file_id in files:
        try:
            file_info = client.files.retrieve(file_id=file_id)
            file_names.append(file_info.filename)
            print(f"  ✓ {file_info.filename}")
        except Exception as e:
            print(f"  ✗ Failed to retrieve info for file ID {file_id}: {e}")
            failed_count += 1
    
    print(f"\nFile retrieval summary:")
    print(f"Successfully retrieved: {len(file_names)} files")
    print(f"Failed to retrieve: {failed_count} files")
    
    return file_names

def verify_all_files_from_directory_is_present_in_list(directory, files):
    """
    Verify if all files from the directory are present in the vector store.
    """
    print(f"\nVerifying files from directory: {directory}")
    
    if not os.path.exists(directory):
        print(f"❌ Directory '{directory}' does not exist.")
        return
    
    try:
        directory_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        print(f"Found {len(directory_files)} files in directory.")
        
        present_count = 0
        missing_count = 0
        
        print("\nVerification Results:")
        for file in directory_files:
            if file in files:
                print(f"  ✓ {file} is present in the vector store.")
                present_count += 1
            else:
                print(f"  ✗ {file} is NOT present in the vector store.")
                missing_count += 1
        
        print(f"\nVerification Summary:")
        print(f"Files present in vector store: {present_count}")
        print(f"Files missing from vector store: {missing_count}")
        print(f"Total files checked: {len(directory_files)}")
        
    except Exception as e:
        print(f"Error reading directory: {e}")

def perform_upload_verification(client, config):
    """
    Perform the upload verification process.
    """
    print("🔍 Starting Upload Verification Process")
    print("-" * 40)
    
    # Retrieve the list of files from vector store
    files = retrieve_all_files(client, config['vector_store_id'])
    
    if not files:
        print("❌ No files found in vector store or error occurred.")
        return False
    
    # Retrieve the names of all files
    file_names = retrieve_name_of_all_files(client, files)
    
    if not file_names:
        print("❌ Could not retrieve file names.")
        return False
    
    # Verify if all files from the directory are present in the vector store (if directory provided)
    if config['directory_path']:
        verify_all_files_from_directory_is_present_in_list(config['directory_path'], file_names)
    else:
        print("\n📋 Vector Store File List:")
        for i, filename in enumerate(file_names, 1):
            print(f"  {i}. {filename}")
    
    return True

if __name__ == "__main__":
    print("\n")
    print("=" * 50)
    print("🔍 Upload Verification for Azure OpenAI Vector Store")
    print("=" * 50)
    
    # Get configuration from user
    config = get_user_configuration()
    
    # Initialize client
    print("\n🔄 Initializing Azure OpenAI client...")
    client = initialize_client(config)
    
    if not client:
        print("❌ Failed to initialize client. Please check your configuration.")
        exit(1)
    
    print("✅ Client initialized successfully!")
    
    # Show configuration summary
    print(f"\nConfiguration Summary:")
    print(f"Vector Store ID: {config['vector_store_id']}")
    if config['directory_path']:
        print(f"Directory to verify: {config['directory_path']}")
    else:
        print("Directory to verify: None (will list all files in vector store)")
    
    # Confirm before proceeding
    confirmation = input("\nProceed with verification? Type 'YES' to confirm: ")
    
    if confirmation == "YES":
        result = perform_upload_verification(client, config)
        if result:
            print(f"\n✅ Verification process completed successfully!")
        else:
            print(f"\n❌ Verification process failed.")
    else:
        print("Operation cancelled.")


