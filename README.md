# Smart Seating Arrangement

A modern, AI-powered web application for generating optimized exam seating arrangements. This tool helps educational institutions efficiently manage exam seating while ensuring fair distribution and minimizing potential academic dishonesty.

## Author
- **Nihal N** - [@nihalshx](https://github.com/nihalshx)
  - Data Enthusiast who loves to learn and stay dedicated
  - Based in Kerala, India

## Features

- **AI-Powered Distribution**: Uses machine learning to predict student attendance and optimize seating arrangements
- **Smart Department Separation**: Implements intelligent algorithms to maintain minimum distance between students from the same department
- **Interactive Interface**: Real-time visualization with department color coding and instant updates
- **Multiple Export Options**: Support for CSV, PDF, and Excel formats
- **Advanced Search & Filter**: Quick student location and department-wise filtering
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark/Light Theme**: User-friendly interface with theme customization
- **Drag & Drop Upload**: Easy file upload with CSV preview
- **Real-time Statistics**: View total students, expected attendance, and capacity utilization

## Prerequisites

- Python 3.7+
- Flask
- Pandas
- NumPy
- scikit-learn
- ReportLab

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smart-seating-arrangement.git
cd smart-seating-arrangement
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Upload your CSV file with the following required columns:
   - Student_ID
   - Department
   - Year
   - Past_Attendance
   - Attended

4. Configure the number of rooms and seats per room

5. Generate the seating arrangement

## CSV File Format

Your CSV file should have the following structure:

```csv
Student_ID,Department,Year,Past_Attendance,Attended
STU001,CSE,1,0.85,1
STU002,ECE,2,0.92,1
STU003,ME,3,0.78,0
```

### Column Descriptions:
- `Student_ID`: Unique identifier for each student
- `Department`: Student's department code
- `Year`: Current year of study (1-4)
- `Past_Attendance`: Historical attendance rate (0-1)
- `Attended`: Previous attendance status (0 or 1)

## Features in Detail

### Seating Algorithm
- Uses machine learning to predict student attendance
- Implements department separation rules
- Optimizes room utilization
- Ensures fair distribution across rooms

### Export Options
- **CSV**: Comma-separated values for easy data manipulation
- **PDF**: Professional document format for printing
- **Excel**: Spreadsheet format with multiple sheets per room

### Interactive Features
- Real-time search functionality
- Department-wise filtering
- Seat information tooltips
- Drag and drop file upload
- CSV preview before processing

## Security Features

- Secure file handling
- Session management
- Input validation
- File type verification
- Size limits on uploads
- Automatic cleanup of old files

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask web framework
- Bootstrap for frontend styling
- Font Awesome for icons
- scikit-learn for machine learning capabilities
- ReportLab for PDF generation

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Roadmap

- [ ] Add support for custom department separation rules
- [ ] Implement room capacity optimization
- [ ] Add support for multiple exam sessions
- [ ] Include student special requirements
- [ ] Add export to Google Sheets
- [ ] Implement user authentication
- [ ] Add support for custom themes

## Version History

- 1.0.0
  - Initial Release
  - Basic seating arrangement functionality
  - Export to CSV, PDF, and Excel
  - Interactive interface with search and filter 

@app.route('/credits')
def credits():
    return render_template('credits.html') 