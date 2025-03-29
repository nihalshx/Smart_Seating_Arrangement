# Smart Seating Arrangement

A modern, rule-based web application for generating optimized exam seating arrangements. This tool helps educational institutions efficiently manage exam seating while ensuring fair distribution and minimizing potential academic dishonesty.

## Author
- **Nihal N** - [@nihalshx](https://github.com/nihalshx)
  - Data Enthusiast who loves to learn and stay dedicated
  - Based in Kerala, India

## Features

- **Rule-based Attendance Prediction**: Uses historical attendance patterns to predict which students will attend exams
- **Smart Department Separation**: Implements intelligent algorithms to maintain minimum distance between students from the same department
- **Interactive Interface**: Real-time visualization with department color coding and instant updates
- **Multiple Export Options**: Support for CSV, PDF, and Excel formats
- **Advanced Search & Filter**: Quick student location and department-wise filtering
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark/Light Theme**: User-friendly interface with theme customization
- **Drag & Drop Upload**: Easy file upload with CSV preview
- **Real-time Statistics**: View total students, expected attendance, and capacity utilization
- **Vercel Deployment**: Easy deployment to Vercel's serverless platform
- **Environment Variables**: Configurable application settings

## Prerequisites

- Python 3.7+
- Flask
- Pandas
- NumPy
- ReportLab
- python-dotenv

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

4. Set up environment variables:
```bash
cp .env.example .env
```
Then edit the `.env` file with your specific configuration.

## Environment Variables

The application uses the following environment variables which can be configured in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Flask secret key for securing sessions | your-secure-key-here |
| DEBUG | Flask debug mode | False |
| FLASK_ENV | Flask environment | production |
| MAX_UPLOAD_SIZE_MB | Maximum upload file size in MB | 16 |
| SESSION_LIFETIME_HOURS | Session timeout in hours | 1 |
| UPLOAD_FOLDER | Path to upload directory | uploads |

## Usage

### Local Development

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

4. Configure the number of rooms and seats per room

5. Generate the seating arrangement

### Vercel Deployment

This application is configured for easy deployment to Vercel's serverless platform:

1. Fork or clone this repository to your GitHub account
2. Connect your GitHub account to Vercel
3. Create a new project in Vercel and import your repository
4. Add environment variables in the Vercel dashboard
5. Deploy the application

For detailed instructions, see [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md).

## CSV File Format

Your CSV file should have the following structure:

```csv
Student_ID,Department,Year,Past_Attendance
STU001,CSE,1,0.85
STU002,ECE,2,0.92
STU003,ME,3,0.78
```

### Column Descriptions:
- `Student_ID`: Unique identifier for each student
- `Department`: Student's department code
- `Year`: Current year of study (1-4)
- `Past_Attendance`: Historical attendance rate (0-1)

## Features in Detail

### Attendance Prediction Algorithm
- Based on historical attendance patterns
- Considers year of study (seniors are more likely to attend)
- Adjusts probability based on past attendance trends
- No machine learning required

### Seating Algorithm
- Implements department separation rules
- Optimizes room utilization
- Ensures fair distribution across rooms

### Export Options
- **CSV**: Comma-separated values for easy data manipulation
- **PDF**: Professional document format for printing

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

- 2.1.0
  - Added environment variable support
  - Added configuration via .env file
  - Improved documentation
- 2.0.0
  - Removed machine learning dependency
  - Added rule-based prediction algorithm
  - Improved performance and reduced dependencies
- 1.0.0
  - Initial Release
  - Basic seating arrangement functionality
  - Export to CSV, PDF, and Excel
  - Interactive interface with search and filter

@app.route('/credits')
def credits():
    return render_template('credits.html') 