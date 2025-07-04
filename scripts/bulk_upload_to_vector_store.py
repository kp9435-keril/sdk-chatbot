import os
from openai import AzureOpenAI
import getpass

# ====== CONFIGURATION NOTES ======
# This script will prompt for:
# - Azure OpenAI API Key (masked input)
# - Azure Endpoint  
# - API Version
# - Directory Path
# - Vector Store Option (Create new or use existing)
# - Vector Store Name (if creating new) OR Vector Store ID (if using existing)
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
    
    # Get Directory Path
    directory_path = input("Enter directory path containing files to upload: ").strip()
    while not directory_path:
        print("Directory path is required.")
        directory_path = input("Enter directory path containing files to upload: ").strip()
    
    # Ask if user wants to create new vector store or use existing one
    print("\n📂 Vector Store Options:")
    print("1. Create a new vector store")
    print("2. Upload to existing vector store")
    choice = input("Select option (1 or 2): ").strip()
    
    while choice not in ['1', '2']:
        print("Invalid choice. Please enter 1 or 2.")
        choice = input("Select option (1 or 2): ").strip()
    
    if choice == '1':
        # Get Vector Store Name for new store
        vector_store_name = input("Enter vector store name: ").strip()
        while not vector_store_name:
            print("Vector store name is required.")
            vector_store_name = input("Enter vector store name: ").strip()
        
        return {
            'api_key': api_key,
            'api_version': api_version,
            'azure_endpoint': azure_endpoint,
            'directory_path': directory_path,
            'vector_store_name': vector_store_name,
            'vector_store_id': None,
            'use_existing': False
        }
    else:
        # Get Vector Store ID for existing store
        vector_store_id = input("Enter existing vector store ID: ").strip()
        while not vector_store_id:
            print("Vector store ID is required.")
            vector_store_id = input("Enter existing vector store ID: ").strip()
        
        return {
            'api_key': api_key,
            'api_version': api_version,
            'azure_endpoint': azure_endpoint,
            'directory_path': directory_path,
            'vector_store_name': None,
            'vector_store_id': vector_store_id,
            'use_existing': True
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

def get_files_from_directory(directory_path):
    """
    Get all file paths from the specified directory.
    """
    try:
        if not os.path.exists(directory_path):
            print(f"Error: Directory '{directory_path}' does not exist.")
            return []
        
        file_paths = [
            os.path.join(directory_path, filename) 
            for filename in os.listdir(directory_path)
            if os.path.isfile(os.path.join(directory_path, filename))
        ]
        return file_paths
    except Exception as e:
        print(f"Error reading directory: {e}")
        return []

def upload_files_to_vector_store(client, directory_path, vector_store_name=None, vector_store_id=None):
    """
    Upload all files from a directory to a new or existing vector store in Azure OpenAI.
    Files are uploaded in batches of 250 to avoid API service limitations.
    """
    print(f"Starting bulk upload from directory: {directory_path}")
    
    # Get all file paths from the directory
    file_paths = get_files_from_directory(directory_path)
    
    if not file_paths:
        print("No files found to upload.")
        return {
            'success': False,
            'vector_store': None,
            'file_batches': [],
            'total_files': 0,
            'successful_uploads': 0,
            'failed_uploads': 0
        }
    
    print(f"Found {len(file_paths)} files to upload:")
    for file_path in file_paths:
        print(f"  - {os.path.basename(file_path)}")
    
    try:
        if vector_store_id:
            # Use existing vector store
            print(f"\nUsing existing vector store with ID: {vector_store_id}")
            try:
                vector_store = client.vector_stores.retrieve(vector_store_id)
                print(f"✓ Vector store retrieved: {vector_store.name} (ID: {vector_store.id})")
            except Exception as e:
                print(f"✗ Error retrieving vector store with ID {vector_store_id}: {e}")
                return {
                    'success': False,
                    'vector_store': None,
                    'file_batches': [],
                    'total_files': len(file_paths),
                    'successful_uploads': 0,
                    'failed_uploads': len(file_paths)
                }
        else:
            # Create new vector store
            print(f"\nCreating vector store: '{vector_store_name}'")
            vector_store = client.vector_stores.create(name=vector_store_name)
            print(f"✓ Vector store created with ID: {vector_store.id}")
        
        # ...existing upload logic... Split files into batches of 250
        batch_size = 250
        total_files = len(file_paths)
        total_batches = (total_files + batch_size - 1) // batch_size  # Ceiling division
        
        print(f"\nUploading {total_files} files in {total_batches} batch(es) of {batch_size} files each...")
        
        all_file_batches = []
        successful_uploads = 0
        failed_uploads = 0
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, total_files)
            batch_file_paths = file_paths[start_idx:end_idx]
            
            print(f"\n--- Processing Batch {batch_num + 1}/{total_batches} ({len(batch_file_paths)} files) ---")
            
            # Open the files in binary read mode for this batch
            file_streams = []
            for path in batch_file_paths:
                try:
                    file_streams.append(open(path, "rb"))
                except Exception as e:
                    print(f"  ✗ Error opening file {os.path.basename(path)}: {e}")
                    failed_uploads += 1
            
            if not file_streams:
                print(f"  ⚠️  No files could be opened for batch {batch_num + 1}, skipping...")
                continue
            
            try:
                print(f"  🔄 Uploading {len(file_streams)} files to vector store...")
                # Use the upload and poll SDK helper to upload the files, add them to the vector store,
                # and poll the status of the file batch for completion.
                file_batch = client.vector_stores.file_batches.upload_and_poll(
                    vector_store_id=vector_store.id, files=file_streams
                )
                
                # Print the status and the file counts of the batch
                print(f"  ✓ Batch {batch_num + 1} Status: {file_batch.status}")
                print(f"  ✓ Batch {batch_num + 1} File counts: {file_batch.file_counts}")
                
                all_file_batches.append(file_batch)
                successful_uploads += len(file_streams)
                
            except Exception as e:
                print(f"  ✗ Error during batch {batch_num + 1} upload: {e}")
                failed_uploads += len(file_streams)
            finally:
                # Close the file streams after uploading this batch
                for file_stream in file_streams:
                    try:
                        file_stream.close()
                    except:
                        pass
        
        print(f"\nFinal Upload Results:")
        print(f"Vector store ID: {vector_store.id}")
        print(f"Total batches processed: {len(all_file_batches)}")
        print(f"Successfully uploaded: {successful_uploads} files")
        print(f"Failed uploads: {failed_uploads} files")
        print(f"Total files processed: {total_files}")
        
        return {
            'success': failed_uploads == 0,
            'vector_store': vector_store,
            'file_batches': all_file_batches,
            'total_files': total_files,
            'successful_uploads': successful_uploads,
            'failed_uploads': failed_uploads
        }
        
    except Exception as e:
        print(f"Error during upload process: {e}")
        return {
            'success': False,
            'vector_store': None,
            'file_batches': [],
            'total_files': len(file_paths),
            'successful_uploads': 0,
            'failed_uploads': len(file_paths)
        }

if __name__ == "__main__":
    print("\n")
    print("=" * 50)
    print("📁 Bulk File Upload to Azure OpenAI Vector Store")
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
    
    # Show configuration and confirm before proceeding
    print(f"\nConfiguration Summary:")
    print(f"Directory: {config['directory_path']}")
    if config['use_existing']:
        print(f"Vector Store ID: {config['vector_store_id']}")
    else:
        print(f"Vector Store Name: {config['vector_store_name']}")
    confirmation = input("\nProceed with upload? Type 'YES' to confirm: ")
    
    if confirmation == "YES":
        if config['use_existing']:
            result = upload_files_to_vector_store(
                client, 
                config['directory_path'], 
                vector_store_id=config['vector_store_id']
            )
        else:
            result = upload_files_to_vector_store(
                client, 
                config['directory_path'], 
                vector_store_name=config['vector_store_name']
            )
        if result['success']:
            print(f"\n✅ Upload completed successfully!")
            print(f"Vector Store ID: {result['vector_store'].id}")
            print(f"Total files uploaded: {result['successful_uploads']}")
        else:
            print(f"\n❌ Upload failed.")
            if result['failed_uploads'] > 0:
                print(f"Failed uploads: {result['failed_uploads']} files")
            if result['successful_uploads'] > 0:
                print(f"Partial success: {result['successful_uploads']} files uploaded successfully")
    else:
        print("Operation cancelled.")
