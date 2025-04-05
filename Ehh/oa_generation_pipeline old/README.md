# OA Generation Agent Pipeline

This project implements an automated Online Assessment (OA) generation system that creates personalized technical assessments based on candidate profiles and job descriptions.

## System Overview

The OA Generation Agent Pipeline is designed to automate the creation of technical assessments with the following features:

- Automated analysis of candidate resumes
- Skill mapping and proficiency estimation
- Question generation based on candidate skills and job requirements
- Reference answer generation for evaluation
- Response evaluation using AI reasoning

## System Architecture

The system consists of several core components:

1. **Data Integration Layer**: Standardizes and normalizes inputs from ATS and JD modules
2. **Candidate Profile Analyzer**: Creates comprehensive skill profiles from resume data
3. **Question Generation Engine**: Creates personalized assessment questions
4. **Answer Generation Service**: Generates reference answers for automated evaluation
5. **Evaluation System**: Scores candidate responses against reference answers
6. **Persistence Layer**: Stores questions, answers, and evaluations in flat files

## Project Structure

```
oa_generation_pipeline/
├── config/              # Configuration settings
├── data/                # Data directory
│   ├── sample/          # Sample data for development
│   └── output/          # Generated outputs
├── models/              # Data models
├── services/            # Core services
├── utils/               # Utility functions
├── main.py              # Main entry point
└── README.md            # Project documentation
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/oa-generation-pipeline.git
cd oa-generation-pipeline
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

### Generate Sample Data

To create sample data for development:

```bash
python main.py --create-sample
```

### Generate an Assessment

To generate an assessment for a candidate:

```bash
python main.py --resume path/to/resume.json --jd path/to/job_description.json --num-questions 5
```

### Evaluate Responses

To evaluate a candidate's responses:

```bash
python main.py --evaluate --assessment-id ASSESSMENT_ID --responses path/to/responses.json
```

## Configuration

Configuration settings are stored in `config/config.py`. You can modify these settings to change:

- Directory paths
- LLM provider and model
- Question categories and difficulty levels

## LLM Integration

The system supports integration with various LLM providers:

- OpenAI (GPT-4, etc.)
- Google (Gemini Pro, etc.)
- Anthropic (Claude)
- Mock LLM for testing

Set the LLM provider and API key in the configuration or environment variables.

## Development

### Adding New Question Templates

Add new question templates as JSON files in the `data/sample/templates` directory. Each template should follow this structure:

```json
{
  "template_id": "unique_id",
  "category": "core_cs",
  "subcategory": "dsa",
  "question_type": "coding",
  "difficulty": "medium",
  "template_text": "Write a function to find the {order} element in a linked list.",
  "variables": {
    "order": ["kth", "middle", "last", "third-to-last"]
  },
  "requires_skills": ["algorithms", "data_structures", "linked_lists"]
}
```

### Extending the System

To add new functionality:

1. Define new models in the `models/` directory
2. Implement new services in the `services/` directory
3. Add utilities as needed in the `utils/` directory
4. Update the main entry point to use the new components

## License

[MIT License](LICENSE)