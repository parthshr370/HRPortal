# ATS Resume Parser and Job Matcher

A comprehensive command-line tool for parsing resumes, matching them against job descriptions, and generating hiring recommendations using LangChain and OpenRouter.

## Features

- Resume parsing with structured output
- Job requirement matching with detailed analysis
- Hiring decision recommendations
- Support for multiple file formats (PDF, DOCX, TXT)
- Detailed scoring and analysis
- Output file generation

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ATS-Portal
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your OpenRouter API keys:
```
NON_REASONING_API_KEY=your_non_reasoning_api_key
REASONING_API_KEY=your_reasoning_api_key
```

## Usage

### Basic Resume Parsing
To parse a resume:
```bash
python main_cli.py path/to/resume.pdf
```

### Resume Parsing with Job Matching
To parse a resume and match it against a job description:
```bash
python main_cli.py path/to/resume.pdf --job path/to/job_description.txt
```

### Generate Output Files
To save all analysis results to files:
```bash
python main_cli.py path/to/resume.pdf --job path/to/job_description.txt --output results/candidate1
```

This will generate:
- results/candidate1_parsed_resume.json
- results/candidate1_match_analysis.json
- results/candidate1_decision.json

## Supported File Formats
- PDF (.pdf)
- Microsoft Word (.docx)
- Plain Text (.txt)

## Output
The tool provides:
1. Structured resume data in JSON format
2. Job match analysis with detailed scoring
3. Hiring recommendations including:
   - Decision status (Proceed/Hold/Reject)
   - Confidence score
   - Interview stage recommendation
   - Key strengths and concerns
   - Next steps and action items
   - Hiring manager notes

## Error Handling
- Comprehensive error handling for file operations
- Validation of API responses
- Clear error messages for troubleshooting

## Customization
You can modify the configuration in `config/config.py` to:
- Adjust matching weights
- Change model selections
- Update API configurations
- Modify supported file types

## Future Enhancements
- Web interface
- Batch processing
- HTML resume highlighting
- Analytics dashboard
- Database integration