# PII Test Data Generator

A React application that generates realistic datasets with sensitive and non-sensitive data for testing PII detection tools.

## Features

- **50 columns** of mixed sensitive and non-sensitive data
- **100,000 rows** of realistic test data
- **Real ICD-10-CM codes** and NDC numbers from official sources
- **Variable completeness** (15-100% field completion)
- **Realistic data errors** (~5% error rate with O/0 and I/1 confusion)
- **CSV export** functionality
- **Interactive preview** before generating full dataset

## Getting Started

### Prerequisites
- Node.js (download from nodejs.org)
- npm (comes with Node.js)

### Installation

1. Open Terminal and navigate to this project folder:
   ```bash
   cd /path/to/pii-data-generator
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open your browser to `http://localhost:3000`

## Usage

1. **Preview Sample Data**: Click the green button to see a sample of the data structure
2. **Download Data Dictionary**: Click the purple button to get column definitions
3. **Generate Full Dataset**: Click the blue button to create and download 100,000 rows

## Data Types Included

### Sensitive Data (25 columns)
- Personal identifiers (names, SSN, addresses)
- Contact information (email, phone numbers)
- Financial data (bank accounts, credit cards)
- Medical codes (ICD-10-CM diagnosis codes, NDC numbers)
- Government IDs (driver's license, passport, military ID)

### Non-Sensitive Data (25 columns)
- Work information (department, job title, hire date)
- Preferences (favorite color, hobbies, shirt size)
- Demographics (age, education, marital status)
- System data (timestamps, employee IDs)

## File Structure

```
pii-data-generator/
├── src/
│   ├── PiiDataGenerator.jsx    # Main component
│   ├── App.js                  # App wrapper
│   ├── App.css                 # Styling
│   └── index.js               # Entry point
├── public/
│   └── index.html             # HTML template
├── package.json               # Dependencies
└── README.md                  # This file
```

## Technologies Used

- React 18
- Lucide React (for icons)
- Tailwind CSS (for styling)
- JavaScript ES6+

## License

MIT License - Feel free to use and modify for your projects.