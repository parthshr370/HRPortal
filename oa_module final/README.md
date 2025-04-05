# HR Portal Online Assessment Module

## Overview
This module generates personalized online assessments based on job descriptions and candidate resumes. It uses AI to create tailored questions that evaluate both technical skills and passion for the role.

## Features
- Dynamic question generation based on JD-resume matches
- Multiple question types (coding, system design, behavioral)
- Automated evaluation with detailed feedback
- Passion detection in responses
- Simple Streamlit web interface

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd oa_module
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file with your API keys:
```
NON_REASONING_API_KEY=your_openrouter_api_key
REASONING_API_KEY=your_openai_api_key
```

## Usage

### Running the Streamlit App
```bash
streamlit run streamlit_app.py
```

### Using the Module Programmatically
```python
import asyncio
from main import OAModule

# Initialize module
oa_module = OAModule()

# Process markdown input
with open('input.md', 'r') as f:
    markdown_content = f.read()
    
# Generate assessment
assessment = await oa_module.process_input(markdown_content)

# Evaluate responses
responses = {
    "question_id": "candidate_response",
    # ... more responses
}
result = await oa_module.evaluate_responses(assessment, responses)

# Generate report
report = oa_module.generate_report(result)
print(report)
```

## Input Format
The module expects a markdown file containing:
- Job Description section
- Resume section
- Previous analysis (optional)

Example format:
```markdown
# Job Description
[Job description content]

# Resume
[Resume content]

# Analysis
[Previous analysis content]
```

## Testing
Run the test suite:
```bash
pytest tests/
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
MIT License

## Authors
[Your Name]