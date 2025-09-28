import React, { useState, useCallback } from 'react';
import { Download, Eye, Database, FileText } from 'lucide-react';

const PiiDataGenerator = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState([]);

  // Data dictionary defining all 50 columns
  const dataDictionary = [
    { column: 'record_id', type: 'INTEGER', description: 'Unique record identifier', sensitive: false, completeness: 100 },
    { column: 'first_name', type: 'VARCHAR(50)', description: 'Employee first name', sensitive: true, completeness: 98 },
    { column: 'middle_name', type: 'VARCHAR(50)', description: 'Employee middle name', sensitive: true, completeness: 45 },
    { column: 'last_name', type: 'VARCHAR(50)', description: 'Employee last name', sensitive: true, completeness: 98 },
    { column: 'maiden_name', type: 'VARCHAR(50)', description: 'Previous/maiden name', sensitive: true, completeness: 25 },
    { column: 'ssn', type: 'VARCHAR(11)', description: 'Social Security Number', sensitive: true, completeness: 85 },
    { column: 'email', type: 'VARCHAR(100)', description: 'Primary email address', sensitive: true, completeness: 92 },
    { column: 'phone_primary', type: 'VARCHAR(15)', description: 'Primary phone number', sensitive: true, completeness: 88 },
    { column: 'phone_mobile', type: 'VARCHAR(15)', description: 'Mobile phone number', sensitive: true, completeness: 75 },
    { column: 'address_street', type: 'VARCHAR(200)', description: 'Street address', sensitive: true, completeness: 90 },
    { column: 'address_city', type: 'VARCHAR(100)', description: 'City name', sensitive: true, completeness: 90 },
    { column: 'address_state', type: 'VARCHAR(50)', description: 'State/Province', sensitive: true, completeness: 90 },
    { column: 'address_zip', type: 'VARCHAR(10)', description: 'ZIP/Postal code', sensitive: true, completeness: 88 },
    { column: 'latitude', type: 'DECIMAL(10,8)', description: 'Geographic latitude', sensitive: true, completeness: 35 },
    { column: 'longitude', type: 'DECIMAL(11,8)', description: 'Geographic longitude', sensitive: true, completeness: 35 },
    { column: 'drivers_license', type: 'VARCHAR(20)', description: 'Driver license number', sensitive: true, completeness: 70 },
    { column: 'passport_number', type: 'VARCHAR(15)', description: 'Passport number', sensitive: true, completeness: 40 },
    { column: 'military_id', type: 'VARCHAR(15)', description: 'Military identification', sensitive: true, completeness: 15 },
    { column: 'bank_account', type: 'VARCHAR(20)', description: 'Bank account number', sensitive: true, completeness: 65 },
    { column: 'routing_number', type: 'VARCHAR(9)', description: 'Bank routing number', sensitive: true, completeness: 65 },
    { column: 'credit_card', type: 'VARCHAR(19)', description: 'Credit card number', sensitive: true, completeness: 55 },
    { column: 'medical_code_primary', type: 'VARCHAR(10)', description: 'Primary ICD-10-CM diagnosis code', sensitive: true, completeness: 30 },
    { column: 'medical_code_secondary', type: 'VARCHAR(10)', description: 'Secondary ICD-10-CM diagnosis code', sensitive: true, completeness: 15 },
    { column: 'prescription_drug', type: 'VARCHAR(100)', description: 'FDA-approved medication name', sensitive: true, completeness: 25 },
    { column: 'drug_ndc', type: 'VARCHAR(15)', description: 'National Drug Code (FDA format)', sensitive: true, completeness: 20 },
    { column: 'dosage', type: 'VARCHAR(50)', description: 'Medication dosage', sensitive: true, completeness: 22 },
    { column: 'age', type: 'INTEGER', description: 'Employee age', sensitive: false, completeness: 95 },
    { column: 'department', type: 'VARCHAR(100)', description: 'Work department', sensitive: false, completeness: 98 },
    { column: 'job_title', type: 'VARCHAR(100)', description: 'Job position title', sensitive: false, completeness: 97 },
    { column: 'hire_date', type: 'DATE', description: 'Employment start date', sensitive: false, completeness: 99 },
    { column: 'salary_band', type: 'VARCHAR(20)', description: 'Salary range category', sensitive: false, completeness: 85 },
    { column: 'employee_status', type: 'VARCHAR(20)', description: 'Employment status', sensitive: false, completeness: 100 },
    { column: 'manager_id', type: 'INTEGER', description: 'Manager employee ID', sensitive: false, completeness: 90 },
    { column: 'office_location', type: 'VARCHAR(100)', description: 'Primary office location', sensitive: false, completeness: 95 },
    { column: 'favorite_color', type: 'VARCHAR(30)', description: 'Preferred color', sensitive: false, completeness: 60 },
    { column: 'hobby', type: 'VARCHAR(100)', description: 'Primary hobby/interest', sensitive: false, completeness: 70 },
    { column: 'pet_type', type: 'VARCHAR(50)', description: 'Type of pet owned', sensitive: false, completeness: 55 },
    { column: 'education_level', type: 'VARCHAR(50)', description: 'Highest education completed', sensitive: false, completeness: 85 },
    { column: 'marital_status', type: 'VARCHAR(20)', description: 'Marital status', sensitive: false, completeness: 75 },
    { column: 'emergency_contact_name', type: 'VARCHAR(100)', description: 'Emergency contact person', sensitive: true, completeness: 80 },
    { column: 'emergency_contact_phone', type: 'VARCHAR(15)', description: 'Emergency contact phone', sensitive: true, completeness: 78 },
    { column: 'shirt_size', type: 'VARCHAR(10)', description: 'T-shirt size preference', sensitive: false, completeness: 65 },
    { column: 'cafeteria_plan', type: 'VARCHAR(50)', description: 'Meal plan selection', sensitive: false, completeness: 70 },
    { column: 'parking_spot', type: 'VARCHAR(20)', description: 'Assigned parking space', sensitive: false, completeness: 40 },
    { column: 'team_name', type: 'VARCHAR(100)', description: 'Project team assignment', sensitive: false, completeness: 85 },
    { column: 'skills', type: 'TEXT', description: 'Professional skills list', sensitive: false, completeness: 80 },
    { column: 'certifications', type: 'TEXT', description: 'Professional certifications', sensitive: false, completeness: 45 },
    { column: 'language_spoken', type: 'VARCHAR(100)', description: 'Primary language', sensitive: false, completeness: 90 },
    { column: 'work_schedule', type: 'VARCHAR(50)', description: 'Work schedule type', sensitive: false, completeness: 95 },
    { column: 'created_timestamp', type: 'TIMESTAMP', description: 'Record creation time', sensitive: false, completeness: 100 }
  ];

  // Helper functions for generating realistic data
  const randomChoice = (arr) => arr[Math.floor(Math.random() * arr.length)];
  
  const addDataErrors = (value, errorRate = 0.05) => {
    if (Math.random() < errorRate && value) {
      return value.toString()
        .replace(/0/g, Math.random() < 0.5 ? 'O' : '0')
        .replace(/1/g, Math.random() < 0.5 ? 'I' : '1')
        .replace(/O/g, Math.random() < 0.5 ? '0' : 'O')
        .replace(/I/g, Math.random() < 0.5 ? '1' : 'I');
    }
    return value;
  };

  const shouldIncludeField = (completeness) => Math.random() * 100 < completeness;

  const generateSSN = () => {
    const area = String(Math.floor(Math.random() * 899) + 100).padStart(3, '0');
    const group = String(Math.floor(Math.random() * 99) + 1).padStart(2, '0');
    const serial = String(Math.floor(Math.random() * 9999) + 1).padStart(4, '0');
    return addDataErrors(`${area}-${group}-${serial}`);
  };

  const generatePhone = () => {
    const area = String(Math.floor(Math.random() * 800) + 200);
    const exchange = String(Math.floor(Math.random() * 800) + 200);
    const number = String(Math.floor(Math.random() * 10000)).padStart(4, '0');
    return addDataErrors(`(${area}) ${exchange}-${number}`);
  };

  const generateEmail = (firstName, lastName) => {
    const domains = ['company.com', 'email.com', 'test.org', 'sample.net'];
    const domain = randomChoice(domains);
    return `${firstName?.toLowerCase()}.${lastName?.toLowerCase()}@${domain}`;
  };

  const generateAddress = () => {
    const streetNumbers = [Math.floor(Math.random() * 9999) + 1];
    const streetNames = ['Main St', 'Oak Ave', 'First St', 'Park Rd', 'Elm Dr', 'Cedar Ln'];
    const cities = ['Springfield', 'Franklin', 'Georgetown', 'Clinton', 'Madison', 'Washington'];
    const states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI'];
    
    const street = `${randomChoice(streetNumbers)} ${randomChoice(streetNames)}`;
    const city = randomChoice(cities);
    const state = randomChoice(states);
    const zip = String(Math.floor(Math.random() * 90000) + 10000);
    
    return { street, city, state, zip };
  };

  const generateCoordinates = () => {
    const lat = (Math.random() * 180 - 90).toFixed(8);
    const lng = (Math.random() * 360 - 180).toFixed(8);
    return { lat, lng };
  };

  const generateDriversLicense = () => {
    const states = ['CA', 'NY', 'TX', 'FL'];
    const state = randomChoice(states);
    const number = String(Math.floor(Math.random() * 100000000)).padStart(8, '0');
    return addDataErrors(`${state}${number}`);
  };

  const generateBankAccount = () => {
    return addDataErrors(String(Math.floor(Math.random() * 1000000000000)).padStart(12, '0'));
  };

  const generateRoutingNumber = () => {
    const routing = String(Math.floor(Math.random() * 900000000) + 100000000);
    return addDataErrors(routing);
  };

  const generateCreditCard = () => {
    const prefixes = ['4532', '5555', '3782', '6011'];
    const prefix = randomChoice(prefixes);
    const remaining = String(Math.floor(Math.random() * 1000000000000)).padStart(12, '0');
    return addDataErrors(`${prefix}${remaining}`);
  };

  const generateMedicalCode = () => {
    // Real ICD-10-CM codes from official sources
    const codes = [
      // Diabetes mellitus codes
      'E11.9', 'E11.65', 'E11.21', 'E11.42', 'E11.69', 'E10.9', 'E08.9', 'E09.9',
      // Cardiovascular codes
      'I10', 'I25.10', 'I50.9', 'I48.91', 'I35.0', 'I20.9', 'I70.90', 'I73.9',
      // Respiratory codes
      'J44.0', 'J44.1', 'J45.9', 'J06.9', 'J18.9', 'J20.9', 'J42', 'J43.9',
      // Mental health codes
      'F32.9', 'F31.9', 'F20.9', 'F41.9', 'F43.10', 'F90.9', 'F17.210', 'F33.9',
      // Musculoskeletal codes
      'M79.3', 'M25.50', 'M54.5', 'M06.9', 'M19.90', 'M75.30', 'M16.10', 'M62.9',
      // Digestive codes
      'K21.9', 'K59.00', 'K30', 'K92.2', 'K35.9', 'K57.90', 'K76.9', 'K25.9',
      // Neurological codes
      'G43.909', 'G40.909', 'G20', 'G56.00', 'G47.00', 'G89.29', 'G93.1', 'G35',
      // Endocrine codes
      'E78.5', 'E78.2', 'E78.00', 'E03.9', 'E05.90', 'E66.9', 'E83.10', 'E87.70',
      // Infectious disease codes
      'A09', 'B34.9', 'A49.9', 'B37.9', 'A08.4', 'B96.20', 'B99.9', 'A41.9',
      // Symptoms and signs
      'R50.9', 'R53.83', 'R06.02', 'R11.10', 'R51', 'R42', 'R10.9', 'R60.9',
      // Injury codes
      'S72.001A', 'S06.9X0A', 'T14.8XXA', 'S82.90XA', 'S42.90XA', 'S72.90XA',
      // Genitourinary codes
      'N39.0', 'N18.6', 'N20.0', 'N40.1', 'N92.6', 'N95.1', 'N30.90', 'N81.10',
      // Skin codes
      'L30.9', 'L20.9', 'L70.9', 'L40.9', 'L50.9', 'L85.9', 'L98.9', 'L29.9',
      // Eye and ear codes
      'H52.13', 'H35.9', 'H61.20', 'H65.90', 'H25.9', 'H40.9', 'H93.90', 'H57.9',
      // Pregnancy-related codes
      'O80', 'O21.9', 'O26.90', 'O99.89', 'O48.1', 'O70.9', 'O85', 'O90.89'
    ];
    return randomChoice(codes);
  };

  const generateRow = (id) => {
    const firstNames = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Lisa', 'Robert', 'Emily', 'James', 'Maria'];
    const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'];
    const departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations', 'IT', 'Legal', 'Customer Service'];
    const jobTitles = ['Senior Developer', 'Marketing Manager', 'Sales Rep', 'HR Specialist', 'Accountant', 'Project Manager'];
    
    const firstName = shouldIncludeField(98) ? randomChoice(firstNames) : null;
    const lastName = shouldIncludeField(98) ? randomChoice(lastNames) : null;
    const address = generateAddress();
    const coords = generateCoordinates();

    return {
      record_id: id,
      first_name: firstName,
      middle_name: shouldIncludeField(45) ? randomChoice(firstNames) : null,
      last_name: lastName,
      maiden_name: shouldIncludeField(25) ? randomChoice(lastNames) : null,
      ssn: shouldIncludeField(85) ? generateSSN() : null,
      email: shouldIncludeField(92) && firstName && lastName ? generateEmail(firstName, lastName) : null,
      phone_primary: shouldIncludeField(88) ? generatePhone() : null,
      phone_mobile: shouldIncludeField(75) ? generatePhone() : null,
      address_street: shouldIncludeField(90) ? address.street : null,
      address_city: shouldIncludeField(90) ? address.city : null,
      address_state: shouldIncludeField(90) ? address.state : null,
      address_zip: shouldIncludeField(88) ? address.zip : null,
      latitude: shouldIncludeField(35) ? coords.lat : null,
      longitude: shouldIncludeField(35) ? coords.lng : null,
      drivers_license: shouldIncludeField(70) ? generateDriversLicense() : null,
      passport_number: shouldIncludeField(40) ? addDataErrors(`P${Math.floor(Math.random() * 100000000)}`) : null,
      military_id: shouldIncludeField(15) ? addDataErrors(`MIL${Math.floor(Math.random() * 1000000)}`) : null,
      bank_account: shouldIncludeField(65) ? generateBankAccount() : null,
      routing_number: shouldIncludeField(65) ? generateRoutingNumber() : null,
      credit_card: shouldIncludeField(55) ? generateCreditCard() : null,
      medical_code_primary: shouldIncludeField(30) ? generateMedicalCode() : null,
      medical_code_secondary: shouldIncludeField(15) ? generateMedicalCode() : null,
      prescription_drug: shouldIncludeField(25) ? randomChoice([
        'Lisinopril', 'Metformin', 'Albuterol', 'Omeprazole', 'Simvastatin', 'Amlodipine',
        'Metoprolol', 'Hydrochlorothiazide', 'Atorvastatin', 'Prednisone', 'Azithromycin',
        'Amoxicillin', 'Ibuprofen', 'Gabapentin', 'Sertraline', 'Furosemide', 'Tramadol',
        'Trazodone', 'Losartan', 'Pantoprazole', 'Levothyroxine', 'Warfarin', 'Insulin'
      ]) : null,
      drug_ndc: shouldIncludeField(20) ? randomChoice([
        '0074-3956-02', '0093-0128-01', '49884-0587-22', '0781-1506-01', '0006-0740-31',
        '0069-1530-68', '0378-0207-01', '0172-4339-70', '0093-7663-56', '0054-4764-25',
        '0555-0808-02', '0781-2077-01', '0904-6876-61', '50458-0321-60', '0172-5506-70',
        '43063-0311-30', '0378-6135-93', '59762-3130-01', '0093-0135-01', '0591-3226-01'
      ]) : null,
      dosage: shouldIncludeField(22) ? randomChoice(['10mg daily', '500mg twice daily', '90mcg as needed']) : null,
      age: shouldIncludeField(95) ? Math.floor(Math.random() * 45) + 22 : null,
      department: shouldIncludeField(98) ? randomChoice(departments) : null,
      job_title: shouldIncludeField(97) ? randomChoice(jobTitles) : null,
      hire_date: shouldIncludeField(99) ? new Date(2015 + Math.random() * 9, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1).toISOString().split('T')[0] : null,
      salary_band: shouldIncludeField(85) ? randomChoice(['Band 1', 'Band 2', 'Band 3', 'Band 4']) : null,
      employee_status: randomChoice(['Active', 'Inactive', 'On Leave']),
      manager_id: shouldIncludeField(90) ? Math.floor(Math.random() * 1000) + 1000 : null,
      office_location: shouldIncludeField(95) ? randomChoice(['New York', 'San Francisco', 'Chicago', 'Austin']) : null,
      favorite_color: shouldIncludeField(60) ? randomChoice(['Blue', 'Red', 'Green', 'Purple', 'Orange']) : null,
      hobby: shouldIncludeField(70) ? randomChoice(['Reading', 'Gaming', 'Cooking', 'Sports', 'Music']) : null,
      pet_type: shouldIncludeField(55) ? randomChoice(['Dog', 'Cat', 'Fish', 'Bird', 'None']) : null,
      education_level: shouldIncludeField(85) ? randomChoice(['High School', 'Bachelor', 'Master', 'PhD']) : null,
      marital_status: shouldIncludeField(75) ? randomChoice(['Single', 'Married', 'Divorced', 'Widowed']) : null,
      emergency_contact_name: shouldIncludeField(80) ? `${randomChoice(firstNames)} ${randomChoice(lastNames)}` : null,
      emergency_contact_phone: shouldIncludeField(78) ? generatePhone() : null,
      shirt_size: shouldIncludeField(65) ? randomChoice(['XS', 'S', 'M', 'L', 'XL', 'XXL']) : null,
      cafeteria_plan: shouldIncludeField(70) ? randomChoice(['Basic', 'Premium', 'Family', 'None']) : null,
      parking_spot: shouldIncludeField(40) ? `A${Math.floor(Math.random() * 100) + 1}` : null,
      team_name: shouldIncludeField(85) ? randomChoice(['Alpha Team', 'Beta Squad', 'Gamma Group', 'Delta Force']) : null,
      skills: shouldIncludeField(80) ? randomChoice(['JavaScript, Python', 'Excel, PowerPoint', 'SQL, Tableau']) : null,
      certifications: shouldIncludeField(45) ? randomChoice(['PMP', 'AWS Certified', 'Six Sigma', 'CPA']) : null,
      language_spoken: shouldIncludeField(90) ? randomChoice(['English', 'Spanish', 'French', 'German', 'Chinese']) : null,
      work_schedule: shouldIncludeField(95) ? randomChoice(['Full-time', 'Part-time', 'Contract', 'Remote']) : null,
      created_timestamp: new Date().toISOString()
    };
  };

  const generatePreview = () => {
    const preview = [];
    for (let i = 1; i <= 10; i++) {
      preview.push(generateRow(i));
    }
    setPreviewData(preview);
    setShowPreview(true);
  };

  const generateAndDownloadData = useCallback(async () => {
    setIsGenerating(true);
    
    try {
      // Generate header
      const headers = dataDictionary.map(col => col.column).join(',');
      let csvContent = headers + '\n';
      
      // Generate data in chunks to avoid memory issues
      const chunkSize = 1000;
      const totalRows = 100000;
      
      for (let chunk = 0; chunk < totalRows / chunkSize; chunk++) {
        let chunkData = '';
        
        for (let i = 1; i <= chunkSize; i++) {
          const rowId = chunk * chunkSize + i;
          const row = generateRow(rowId);
          
          const rowValues = dataDictionary.map(col => {
            const value = row[col.column];
            if (value === null || value === undefined) return '';
            return `"${value.toString().replace(/"/g, '""')}"`;
          });
          
          chunkData += rowValues.join(',') + '\n';
        }
        
        csvContent += chunkData;
        
        // Allow UI to update
        await new Promise(resolve => setTimeout(resolve, 1));
      }
      
      // Create and download file
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', 'pii_test_data_100k.csv');
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
    } catch (error) {
      console.error('Error generating data:', error);
      alert('Error generating data. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  }, []);

  const downloadDataDictionary = () => {
    const headers = ['Column Name', 'Data Type', 'Description', 'Sensitive', 'Expected Completeness %'].join(',');
    const rows = dataDictionary.map(col => 
      [col.column, col.type, `"${col.description}"`, col.sensitive ? 'Yes' : 'No', col.completeness].join(',')
    );
    
    const csvContent = [headers, ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'data_dictionary.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4 flex items-center">
          <Database className="mr-3" />
          PII Test Data Generator
        </h1>
        <p className="text-gray-600 mb-6">
          Generate a realistic dataset with 50 columns and 100,000 rows containing mixed sensitive and non-sensitive data.
          Includes varying completeness rates, realistic data entry errors, and authentic ICD-10-CM codes and NDC numbers 
          from official public sources (WHO/CDC/FDA).
        </p>
        
        <div className="grid md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-900">Dataset Size</h3>
            <p className="text-blue-700">50 columns × 100,000 rows</p>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <h3 className="font-semibold text-red-900">Sensitive Fields</h3>
            <p className="text-red-700">25 columns containing PII + real ICD-10/NDC codes</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-semibold text-green-900">Data Accuracy</h3>
            <p className="text-green-700">~5% error rate in sensitive data</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-4 mb-6">
          <button
            onClick={generateAndDownloadData}
            disabled={isGenerating}
            className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
          >
            <Download className="mr-2" size={20} />
            {isGenerating ? 'Generating...' : 'Generate & Download Full Dataset'}
          </button>
          
          <button
            onClick={generatePreview}
            className="flex items-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold"
          >
            <Eye className="mr-2" size={20} />
            Preview Sample Data
          </button>
          
          <button
            onClick={downloadDataDictionary}
            className="flex items-center px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-semibold"
          >
            <FileText className="mr-2" size={20} />
            Download Data Dictionary
          </button>
        </div>

        <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
          <h4 className="font-semibold text-blue-900 mb-2">What You'll Get:</h4>
          <ul className="text-blue-800 text-sm space-y-1">
            <li>• <strong>Full Dataset:</strong> 100,000 rows × 50 columns CSV file (~50MB)</li>
            <li>• <strong>Data Dictionary:</strong> Complete column definitions with sensitivity flags</li>
            <li>• <strong>Real Medical Codes:</strong> 75+ authentic ICD-10-CM codes, 20+ NDC numbers</li>
            <li>• <strong>Realistic Errors:</strong> 5% data entry mistakes (O/0, I/1 confusion)</li>
            <li>• <strong>Variable Completeness:</strong> 15-100% field completion rates</li>
          </ul>
        </div>
      </div>

      {/* Sample Data Preview */}
      {showPreview && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Sample Data Preview (First 10 Rows)</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full table-auto text-xs">
              <thead>
                <tr className="bg-gray-50">
                  {dataDictionary.slice(0, 10).map((col, idx) => (
                    <th key={idx} className="px-2 py-1 text-left font-semibold">
                      {col.column}
                    </th>
                  ))}
                  <th className="px-2 py-1 text-left font-semibold">...</th>
                </tr>
              </thead>
              <tbody>
                {previewData.map((row, idx) => (
                  <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                    {dataDictionary.slice(0, 10).map((col, colIdx) => (
                      <td key={colIdx} className="px-2 py-1 max-w-32 truncate">
                        {row[col.column] || ''}
                      </td>
                    ))}
                    <td className="px-2 py-1">...</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-gray-600 text-sm mt-2">
            * Preview shows only first 10 columns. Full dataset contains all 50 columns.
          </p>
        </div>
      )}

      {isGenerating && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                Generating 100,000 rows of data... This may take a few moments.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Data Dictionary Table */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Complete Data Dictionary (50 Columns)</h2>
        <div className="overflow-x-auto max-h-96 overflow-y-auto">
          <table className="min-w-full table-auto">
            <thead className="sticky top-0 bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left font-semibold">Column</th>
                <th className="px-4 py-2 text-left font-semibold">Type</th>
                <th className="px-4 py-2 text-left font-semibold">Description</th>
                <th className="px-4 py-2 text-left font-semibold">Sensitive</th>
                <th className="px-4 py-2 text-left font-semibold">Completeness</th>
              </tr>
            </thead>
            <tbody>
              {dataDictionary.map((col, idx) => (
                <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                  <td className="px-4 py-2 font-mono text-sm">{col.column}</td>
                  <td className="px-4 py-2 text-sm">{col.type}</td>
                  <td className="px-4 py-2 text-sm">{col.description}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      col.sensitive 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {col.sensitive ? 'Yes' : 'No'}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-sm">{col.completeness}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PiiDataGenerator;