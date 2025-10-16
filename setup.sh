#!/bin/bash

# Setup script for NZ Property Flip Calculator

echo "🏠 Setting up NZ Property Flip Calculator..."

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL 12 or higher."
    exit 1
fi

echo "✓ Prerequisites met"

# Setup database
echo ""
echo "Setting up database..."
read -p "Enter PostgreSQL username (default: postgres): " db_user
db_user=${db_user:-postgres}

read -s -p "Enter PostgreSQL password: " db_password
echo ""

read -p "Enter database name (default: nz_property_flip): " db_name
db_name=${db_name:-nz_property_flip}

# Create database
PGPASSWORD=$db_password psql -U $db_user -c "CREATE DATABASE $db_name;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Database created"
else
    echo "ℹ Database may already exist (this is okay)"
fi

# Setup backend
echo ""
echo "Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
if [ ! -f .env ]; then
    cp .env.example .env
    # Update DATABASE_URL in .env
    sed -i.bak "s|postgresql://username:password@localhost:5432/nz_property_flip|postgresql://$db_user:$db_password@localhost:5432/$db_name|g" .env
    rm .env.bak
    echo "✓ Created .env file"
else
    echo "ℹ .env file already exists"
fi

deactivate
cd ..

# Setup frontend
echo ""
echo "Setting up frontend..."
cd frontend

npm install

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo ""
echo "1. Start the backend (in one terminal):"
echo "   cd backend"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   python app.py"
echo ""
echo "2. Start the frontend (in another terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open http://localhost:3000 in your browser"
echo ""

