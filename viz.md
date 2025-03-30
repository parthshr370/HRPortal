```mermaid
graph TD
    subgraph "Input Sources"
        ATS[ATS Module Output] --> DI
        JD[JD Module Output] --> DI
    end

    subgraph "Data Processing"
        DI[Data Integration Layer] --> CPA
        CPA[Candidate Profile Analyzer] --> SM[Skill Map Generation]
        SM --> QGE
    end

    subgraph "Question Generation"
        QGE[Question Generation Engine]
        JT[JSON Templates] --> QGE
        QGE --> Q[Generated Questions]
    end

    subgraph "Answer & Evaluation"
        Q --> AGS[Answer Generation Service]
        AGS --> RA[Reference Answers]
        AGS --> SR[Scoring Rubrics]
        CR[Candidate Responses] --> ES[Evaluation System]
        RA --> ES
        SR --> ES
        ES --> ER[Evaluation Results]
    end

    subgraph "Persistence Layer"
        Q --> PL[Persistence Layer]
        RA --> PL
        ER --> PL
    end

    subgraph "LLM Integration"
        LLMS[LLM Service - Gemini API]
        CPA -.-> LLMS
        QGE -.-> LLMS
        AGS -.-> LLMS
        ES -.-> LLMS
    end

    classDef primary fill:#f9f,stroke:#333,stroke-width:2px;
    classDef secondary fill:#bbf,stroke:#333,stroke-width:1px;
    classDef storage fill:#bfb,stroke:#333,stroke-width:1px;
    
    class DI,CPA,QGE,AGS,ES primary;
    class SM,Q,RA,SR,CR,ER secondary;
    class JT,PL storage;```