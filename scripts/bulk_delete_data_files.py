from openai import AzureOpenAI
import getpass

# ====== CONFIGURATION NOTES ======
# This script will prompt for:
# - Azure OpenAI API Key (masked input)
# - API Version
# - Azure Endpoint
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
    
    return {
        'api_key': api_key,
        'api_version': api_version,
        'azure_endpoint': azure_endpoint
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

def get_all_files(client):
    """
    Retrieve all files from the Azure OpenAI service.
    """
    try:
        response = client.files.list()
        return response.data
    except Exception as e:
        print(f"Error retrieving files: {e}")
        return []

def delete_all_files(client):
    """
    Delete all files from the Azure OpenAI service.
    Prints the name and ID of each file as it's being deleted.
    """
    print("Retrieving all files from Azure OpenAI service...")
    files = get_all_files(client)
    
    if not files:
        print("No files found to delete.")
        return {
            'success': True,
            'deleted_count': 0,
            'failed_count': 0,
            'total_files': 0
        }
    
    print(f"Found {len(files)} files to delete.\n")
    
    deleted_count = 0
    failed_count = 0
    
    for file in files:
        try:
            print(f"Deleting file: '{file.filename}' (ID: {file.id})")
            client.files.delete(file.id)
            print(f"✓ Successfully deleted: '{file.filename}' (ID: {file.id})")
            deleted_count += 1
        except Exception as e:
            print(f"✗ Failed to delete: '{file.filename}' (ID: {file.id}) - Error: {e}")
            failed_count += 1
        print("-" * 50)
    
    print(f"\nDeletion Summary:")
    print(f"Successfully deleted: {deleted_count} files")
    print(f"Failed to delete: {failed_count} files")
    print(f"Total files processed: {len(files)}")
    
    return {
        'success': failed_count == 0,
        'deleted_count': deleted_count,
        'failed_count': failed_count,
        'total_files': len(files)
    }

if __name__ == "__main__":
    print("\n")
    print("=" * 50)
    print("🗑️  Bulk Delete All Data Files from Azure OpenAI")
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
    
    # Show warning and confirm before proceeding
    print("\n⚠️  WARNING: This will delete ALL data files from your Azure OpenAI service!")
    print("This action cannot be undone!")
    confirmation = input("\nAre you sure you want to proceed? Type 'YES' to confirm: ")
    
    if confirmation == "YES":
        result = delete_all_files(client)
        print(f"\n✅ Deletion process completed!")
    else:
        print("Operation cancelled.")