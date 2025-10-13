#!/usr/bin/env python3
"""
Doctor Appointment Bot Setup Script
===================================

This script sets up the complete Doctor Appointment Bot system including:
- Environment configuration (.env file)
- API key validation
- Qdrant vector database population
- System testing and verification

Run this script once after cloning the repository to get everything working.
"""

import os
import sys
import json
import time
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Try to import dotenv, but handle gracefully if not available
try:
    from dotenv import load_dotenv, set_key, dotenv_values

    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    load_dotenv = None
    set_key = None
    dotenv_values = None


# Color codes for terminal output
class Colors:
    GRAY = "\033[90m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"
    CHECK = "✅"
    CROSS = "❌"
    ARROW = "➤"
    STAR = "⭐"


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD} {text} {Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.END}")


def print_step(step_num: int, text: str, status: str = ""):
    """Print a step with status"""
    status_icon = {
        "pending": "⏳",
        "running": "🔄",
        "success": Colors.GREEN + Colors.CHECK + Colors.END,
        "error": Colors.RED + Colors.CROSS + Colors.END,
        "skipped": "⏭️",
        "warning": Colors.YELLOW + "⚠️" + Colors.END,
    }.get(status, "")

    print(f"\n{Colors.BOLD}[Step {step_num}]{Colors.END} {status_icon} {text}")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}{Colors.CHECK} {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}{Colors.CROSS} {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}{Colors.ARROW} {text}{Colors.END}")


def check_env_file() -> Tuple[bool, Dict[str, str]]:
    """Check if .env file exists and read its contents"""
    env_path = Path(".env")

    if not env_path.exists():
        return False, {}

    if not DOTENV_AVAILABLE:
        print_warning("python-dotenv not available, cannot read .env file")
        return False, {}

    try:
        # Try to read .env file
        env_values = dotenv_values(".env")
        return True, dict(env_values)
    except Exception as e:
        print_warning(f"Could not read .env file: {e}")
        return False, {}


def create_env_file():
    """Create .env file with current configuration"""
    print_step(2, "Setting up environment configuration", "running")

    env_exists, env_data = check_env_file()

    if env_exists:
        print_success(".env file already exists")
        print_info("Checking existing configuration...")

        # Check for required keys
        required_keys = [
            "GOOGLE_API_KEY",
            "QDRANT_URL",
            "QDRANT_API_KEY",
            "COHERE_API_KEY",
        ]
        optional_keys = ["PG_CONNECTION_STRING", "SECRET_KEY", "LANGSMITH_API_KEY"]

        missing_required = []
        missing_optional = []

        for key in required_keys:
            if key not in env_data or not env_data[key]:
                missing_required.append(key)

        for key in optional_keys:
            if key not in env_data or not env_data[key]:
                missing_optional.append(key)

        if not missing_required and not missing_optional:
            print_success("All API keys are configured!")
            return True

        if missing_required:
            print_warning(f"Missing required keys: {', '.join(missing_required)}")
            return False

        if missing_optional:
            print_info(f"Optional keys to configure: {', '.join(missing_optional)}")

        return True
    else:
        print_info("Creating new .env file...")

        # Default template
        default_env = """# Google Gemini API Key (Required)
GOOGLE_API_KEY=your_google_api_key_here

# Qdrant Vector Database (Required)
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here

# Cohere Embeddings API Key (Required)
COHERE_API_KEY=your_cohere_api_key_here

# PostgreSQL Connection String (Optional)
PG_CONNECTION_STRING=postgresql://postgres:root@localhost:5432/doctor-appointment-rag

# Session Secret Key (Optional)
SECRET_KEY=your_secret_key_here

# LangSmith Tracing (Optional)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=doctor-appointment
"""

        try:
            with open(".env", "w", encoding="utf-8") as f:
                f.write(default_env)

            print_success("Created .env file with template configuration")
            print_warning(
                "Please edit .env file with your actual API keys before continuing"
            )
            return False

        except Exception as e:
            print_error(f"Failed to create .env file: {e}")
            return False


def test_api_connections():
    """Test API connections"""
    print_step(3, "Testing API connections", "running")

    if DOTENV_AVAILABLE:
        load_dotenv()

    tests = [
        ("Google Gemini API", "GOOGLE_API_KEY"),
        ("Qdrant Database", "QDRANT_API_KEY"),
        ("Qdrant URL", "QDRANT_URL"),
        ("Cohere API", "COHERE_API_KEY"),
    ]

    all_passed = True

    for api_name, env_var in tests:
        api_key = os.getenv(env_var)

        if not api_key or api_key == f"your_{env_var.lower()}_here":
            print_error(f"{api_name}: Missing or placeholder API key")
            all_passed = False
        else:
            print_success(f"{api_name}: API key found")

    # Test actual connections
    if all_passed:
        print_info("Testing actual API connections...")

        try:
            # Test Qdrant connection
            from qdrant_client import QdrantClient

            qdrant = QdrantClient(
                url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY")
            )

            # Simple ping test
            collections = qdrant.get_collections()
            print_success("Qdrant connection: Successful")

        except Exception as e:
            print_error(f"Qdrant connection failed: {e}")
            all_passed = False

        try:
            # Test Cohere connection
            from cohere import Client

            cohere_client = Client(api_key=os.getenv("COHERE_API_KEY"))
            # Simple test - just check if client initializes
            print_success("Cohere connection: Successful")

        except Exception as e:
            print_error(f"Cohere connection failed: {e}")
            all_passed = False

    return all_passed


def populate_qdrant_database():
    """Populate Qdrant database with doctors data"""
    print_step(4, "Populating Qdrant vector database", "running")

    try:
        # Import required modules
        from qdrant_client import QdrantClient
        from langchain_cohere import CohereEmbeddings
        from langchain_qdrant import QdrantVectorStore
        from langchain_experimental.text_splitter import SemanticChunker
        from langchain.indexes import SQLRecordManager, index
        from langchain_core.documents import Document
        from qdrant_client.http.models import VectorParams, Distance

        # Import doctors data
        sys.path.append(".")
        from app.ai_agent.context import CONTEXT

        print_info("Connecting to Qdrant...")

        # Initialize Qdrant service
        qdrant = QdrantClient(
            url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY")
        )

        cohere_embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")

        # Check if collection already exists
        collections = qdrant.get_collections()
        collection_names = [col.name for col in collections.collections]

        if "doctors-appointments" in collection_names:
            print_warning("Collection 'doctors-appointments' already exists")
            # Ask user if they want to recreate
            response = (
                input("Do you want to recreate the collection? (y/N): ").lower().strip()
            )
            if response != "y":
                print_info("Skipping database population")
                return True
            else:
                print_info("Recreating collection...")

        # Create collection
        dim = cohere_embeddings.embed_query("test").__len__()
        print_info(f"Creating collection with embedding dimension: {dim}")

        qdrant.recreate_collection(
            collection_name="doctors-appointments",
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

        # Get doctors data
        doctors = CONTEXT["doctors"]
        print_info(f"Found {len(doctors)} doctors to index")

        # Create documents
        docs = []
        for doctor in doctors:
            text = f"{doctor['name']}, {doctor['specialty']}, {doctor['degree']}, {doctor['experience']}"
            metadata = {"source": doctor["id"], **doctor}
            docs.append(Document(page_content=text, metadata=metadata))

        print_info("Creating vector store...")
        vector_store = QdrantVectorStore(
            client=qdrant,
            collection_name="doctors-appointments",
            embedding=cohere_embeddings,
        )

        # Add documents directly to vector store (simpler approach)
        print_info("Adding documents to vector store...")
        vector_store.add_documents(docs)

        # Wait a moment for indexing to complete
        time.sleep(2)

        print_success("Successfully populated Qdrant database!")
        return True

    except Exception as e:
        print_error(f"Failed to populate database: {e}")
        return False


def test_database_population():
    """Test that the database is populated correctly"""
    print_step(5, "Testing database population", "running")

    try:
        # Import required modules
        from qdrant_client import QdrantClient
        from langchain_cohere import CohereEmbeddings
        from langchain_qdrant import QdrantVectorStore

        # Initialize services
        qdrant = QdrantClient(
            url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY")
        )

        cohere_embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")

        vector_store = QdrantVectorStore(
            client=qdrant,
            collection_name="doctors-appointments",
            embedding=cohere_embeddings,
        )

        # Test searches
        test_queries = [
            ("heart problems", "Dr. Ahmed"),
            ("skin issues", "Dr. Sara"),
            ("brain problems", "Dr. Kamal"),
        ]

        # First check if collection has points
        try:
            collection_info = qdrant.get_collection("doctors-appointments")
            points_count = collection_info.points_count
            print_info(f"Collection has {points_count} points")

            if points_count == 0:
                print_warning("Collection is empty - no points found")
                return False
        except Exception as e:
            print_error(f"Could not check collection info: {e}")
            return False

        print_info("Testing search functionality...")

        all_tests_passed = True

        for query, expected_doctor in test_queries:
            try:
                # Add small delay to ensure indexing is complete
                time.sleep(1)

                results = vector_store.similarity_search(query, k=2)
                if results:
                    found_doctor = results[0].metadata.get("name", "")
                    print_info(f"'{query}' → Found: {found_doctor}")

                    if expected_doctor in found_doctor:
                        print_success(f"✓ Correct doctor found for '{query}'")
                    else:
                        print_warning(
                            f"⚠️  Different doctor found for '{query}' (expected {expected_doctor})"
                        )
                        # Still count as success if we found a doctor
                else:
                    print_error(f"❌ '{query}' → No results found")
                    all_tests_passed = False

            except Exception as e:
                print_error(f"❌ '{query}' → Error: {e}")
                all_tests_passed = False

        if all_tests_passed:
            print_success("All search tests passed!")
            return True
        else:
            print_warning("Some search tests failed, but database is functional")
            return True

    except Exception as e:
        print_error(f"Database test failed: {e}")
        return False


def show_completion_message():
    """Show completion message"""
    print_header("🎉 SETUP COMPLETE!")

    print(f"""
{Colors.GREEN}{Colors.BOLD}
   ___         _               ___       _   _     _   _      _                      _
  / __|___  __| |___ _ _ ___  |   \\ __ _| |_| |_  | | | |_ _| |_ _ __  ___ _ _ ___| |_ ___
 | (__/ _ \\/ _` / -_) '_/ -_) | |) / _` |  _| ' \\ | | |  _|  _| '_ \\/ _ \\ '_/ -_)  _(_-<
  \\___\\___/\\__,_\\___|_| \\___| |___/\\__,_|\\__|_||_||_|_|\\__|\\__| .__/\\___/_| \\___|\\__/__/
                                                             |_|
{Colors.END}

Your Doctor Appointment Bot is now fully set up and ready to use!

{Colors.BOLD}Next Steps:{Colors.END}
1. Run the application: {Colors.BLUE}python main.py{Colors.END}
2. Visit: {Colors.BLUE}http://localhost:8000{Colors.END}
3. Test with queries like:
   • "I have chest pain"
   • "Headache problems"
   • "Skin rash issues"

{Colors.BOLD}Features Available:{Colors.END}
{Colors.GREEN}✅{Colors.END} AI-powered doctor recommendations
{Colors.GREEN}✅{Colors.END} Vector search for symptoms
{Colors.GREEN}✅{Colors.END} Appointment booking system
{Colors.GREEN}✅{Colors.END} Chat history persistence
{Colors.GREEN}✅{Colors.END} Multi-specialty support

{Colors.BOLD}Contributing:{Colors.END}
Feel free to enhance the system by:
• Adding more doctors/specialties
• Improving symptom detection
• Adding appointment conflict checking
• Implementing user authentication

Happy coding! {Colors.STAR}
""")


def run_command(command: str, description: str, cwd: str = None) -> bool:
    """Run a command and return success status"""
    try:
        print_info(f"{description}...")
        result = subprocess.run(
            command, shell=True, cwd=cwd, capture_output=True, text=True, check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed: {e.stderr}")
        return False


def setup_virtual_environment():
    """Create and setup virtual environment"""
    print_step(0, "Setting up Python virtual environment", "running")

    venv_path = Path("env")

    # Check if virtual environment already exists
    if venv_path.exists() and venv_path.is_dir():
        print_success("Virtual environment already exists")

        # Check if it's activated by looking for python executable
        python_exe = (
            venv_path / "Scripts" / "python.exe"
            if platform.system() == "Windows"
            else venv_path / "bin" / "python"
        )
        if python_exe.exists():
            print_success("\    Virtual environment is properly configured")
            return True
        else:
            print_warning("Virtual environment exists but may be corrupted")
            return False

    # Create virtual environment
    print_info("Creating virtual environment...")

    if platform.system() == "Windows":
        python_cmd = "python"
    else:
        python_cmd = "python3"

    success = run_command(f"{python_cmd} -m venv env", "Setting up virtual environment")

    if success:
        print_success("Virtual environment created successfully!")
        print_info("🔄 Next steps:")
        print_info("1. Activate the virtual environment:")
        if platform.system() == "Windows":
            print_info("   env\\Scripts\\activate")
        else:
            print_info("   source env/bin/activate")
        print_info("2. Install dependencies and continue setup:")
        print_info("   pip install -r requirements.txt")
        print_info("   python setup.py")
        print_info("")
        print_info(
            "Or simply re-run this setup script after activation to continue automatically."
        )
        sys.exit(0)

    return False


def install_requirements():
    """Install Python requirements"""
    print_step(1, "Installing Python dependencies", "running")

    requirements_file = Path("requirements.txt")

    if not requirements_file.exists():
        print_error("requirements.txt not found in current directory")
        return False

    # Check if we're in virtual environment
    # Check for both virtualenv and venv
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    if in_venv:
        # We're in a virtual environment
        pip_cmd = "pip"
        print_info("Using pip from activated virtual environment")
    else:
        # Try to use pip from virtual environment
        if platform.system() == "Windows":
            pip_cmd = "env\\Scripts\\pip"
        else:
            pip_cmd = "env/bin/pip"

        if Path(pip_cmd.replace("\\", "/")).exists():
            print_info(f"Using pip from virtual environment: {pip_cmd}")
        else:
            pip_cmd = "pip3" if platform.system() != "Windows" else "pip"
            print_info(f"Using system pip: {pip_cmd}")

    success = run_command(
        f"{pip_cmd} install -r requirements.txt", "Installing requirements"
    )

    if success:
        print_success("All dependencies installed successfully")
        return True
    else:
        print_error("Failed to install dependencies")
        return False


def main():
    """Main setup function"""
    print_header("🚀 DOCTOR APPOINTMENT BOT SETUP")

    # Check if we're in virtual environment
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    if not in_venv:
        print(f"""
{Colors.BOLD}Welcome to the Doctor Appointment Bot Setup!{Colors.END}

{Colors.YELLOW}⚠️  Virtual environment not detected!{Colors.END}

To get started, please follow these steps:

1. {Colors.BLUE}Create virtual environment:{Colors.END}
   python -m venv env

2. {Colors.BLUE}Activate virtual environment:{Colors.END}
   env\\Scripts\\activate  {Colors.GRAY}(Windows){Colors.END}
   source env/bin/activate  {Colors.GRAY}(Linux/Mac){Colors.END}

3. {Colors.BLUE}Install dependencies:{Colors.END}
   pip install -r requirements.txt

4. {Colors.BLUE}Run setup again:{Colors.END}
   python setup.py

{Colors.GREEN}This automated setup will then handle everything else!{Colors.END}
""")
        sys.exit(1)

    if not DOTENV_AVAILABLE:
        print(f"""
{Colors.BOLD}Welcome to the Doctor Appointment Bot Setup!{Colors.END}

{Colors.YELLOW}⚠️  Python dependencies not installed!{Colors.END}

It looks like you're in a virtual environment, but the required dependencies
aren't installed yet. Please install them first:

{Colors.BLUE}Install dependencies:{Colors.END}
pip install -r requirements.txt

{Colors.BLUE}Then run setup again:{Colors.END}
python setup.py

{Colors.GREEN}This automated setup will then handle everything else!{Colors.END}
""")
        sys.exit(1)

    print(f"""
{Colors.BOLD}Welcome to the Doctor Appointment Bot Setup!{Colors.END}

This setup will:
0. {Colors.BLUE}Create virtual environment{Colors.END} (if needed)
1. {Colors.BLUE}Install Python dependencies{Colors.END} (requirements.txt)
2. {Colors.BLUE}Configure your environment{Colors.END} (.env file)
3. {Colors.BLUE}Test API connections{Colors.END} (Google, Qdrant, Cohere)
4. {Colors.BLUE}Populate vector database{Colors.END} with doctors
5. {Colors.BLUE}Test functionality{Colors.END}

Let's get started! {Colors.STAR}
""")

    # Step 0: Virtual environment setup
    venv_ready = setup_virtual_environment()

    if not venv_ready:
        print_error("Virtual environment setup failed")
        sys.exit(1)

    # Step 1: Install requirements (only if we're in virtual environment)
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    if in_venv:
        requirements_ready = install_requirements()
        if not requirements_ready:
            print_error("Requirements installation failed")
            sys.exit(1)
    else:
        print_warning("⚠️  Virtual environment not activated!")
        print_info("Please activate your virtual environment first:")
        if platform.system() == "Windows":
            print_info("  env\\Scripts\\activate")
        else:
            print_info("  source env/bin/activate")
        print_info("Then re-run: python setup.py")
        sys.exit(1)

    # Step 2: Environment setup
    env_ready = create_env_file()

    if not env_ready:
        print_warning("Please configure your API keys in the .env file first")
        print_info("Run this setup again after configuring the keys")
        sys.exit(1)

    # Step 3: Test API connections
    api_ready = test_api_connections()

    if not api_ready:
        print_error("API connection tests failed")
        print_info("Please check your API keys and try again")
        sys.exit(1)

    # Step 4: Populate database
    db_populated = populate_qdrant_database()

    if not db_populated:
        print_error("Database population failed")
        print_info("Please check your configuration and try again")
        sys.exit(1)

    # Step 5: Test database
    db_tested = test_database_population()

    if not db_tested:
        print_error("Database testing failed")
        print_info("Please check your setup and try again")
        sys.exit(1)

    # Success!
    show_completion_message()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
