# LBORO-FYP
My Final Year Project for ITMB degree at Loughborough University

## Project Description
Personal Health Record (PHR) System - A mobile-first web application that allows patients to store, access, and share their medical information with healthcare providers.

### Features
- User authentication with secure password hashing
- Medical history document upload and viewing
- Lab results tracking with historical data visualization
- Vital signs monitoring
- Medication tracking
- Vaccination and allergy records
- Patient profile management
- Secure sharing of medical records with healthcare providers via QR code or short link

### Technologies Used
- **Backend**: FastAPI with PostgreSQL
- **Frontend**: Vue.js with PrimeVue and TailwindCSS

## Setup and Installation

### Prerequisites
Before starting, ensure you have the following installed:
- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js and npm** - [Download Node.js](https://nodejs.org/)
- **PostgreSQL** - [Download PostgreSQL](https://www.postgresql.org/download/)

### Manual Setup

#### Backend Setup
1. Navigate to the backend directory:

```bash
cd project_files/backend
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory with the following variables. Google Studio provides free API access, and you can get your key from [here](https://aistudio.google.com/apikey):

```
DATABASE_URL=postgresql://username@localhost/dbname
FILE_KEY=your_file_encryption_key
API_KEY=your_llm_api_key
```

4. Start the backend server:

```bash
uvicorn main --reload
```

#### Frontend Setup
1. Navigate to the frontend directory:

```bash
cd project_files/frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

## Running the Application

After setup, the application should be available at:
- Frontend: http://localhost:3000 (or the port specified in your Vue config)
- Backend API: http://localhost:8000

## Troubleshooting

### Application Issues
- **Database Connection Issues**: Ensure PostgreSQL is running and credentials in `.env` are correct
- **Port Conflicts**: If ports are already in use, modify the port settings in your configuration
- **NPM Errors**: Try deleting the `node_modules` folder and running `npm install` again
- **Backend Errors**: Check that all Python dependencies are installed properly

### Biber Issues (Thesis Document)
1. Delete all auxiliary files:
   * .aux
   * .bbl
   * .bcf
   * .blg
   * .run.xml
2. Run `biber --version`
3. If there's an error in step 2, delete all files in the error directory
4. Rerun the biber recipe in the Latex Workshop menu

## License
To be added