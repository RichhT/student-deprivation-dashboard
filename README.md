# Student Deprivation Dashboard

An interactive Streamlit dashboard for analyzing student demographic and deprivation data.

## Features

- **Overall Deprivation Metrics**: View total students and percentage disadvantaged
- **Interactive Filters**: Filter by year group to drill down into specific cohorts
- **Visual Analytics**:
  - Pie chart showing disadvantaged vs non-disadvantaged students
  - Bar chart of multiple deprivation factors (0-6 factors)
  - Year group comparison charts
  - Vulnerability factors breakdown (SEN, FSM, Pupil Premium, etc.)
  - Heatmap showing factors across year groups
- **Key Insights**: Highlighted statistics for multiple deprivation, child protection, and looked after children

## Quick Start

### Option 1: Using the provided script
```bash
./run_dashboard.sh
```

### Option 2: Manual start
```bash
# Activate the virtual environment
source venv/bin/activate

# Run the dashboard
streamlit run dashboard.py
```

The dashboard will automatically open in your default web browser at `http://localhost:8501`

## Dashboard Sections

1. **Top Metrics Bar**: Quick overview of total students, disadvantaged %, FSM %, SEN %, and Pupil Premium %

2. **Overall Deprivation Status**: Pie chart showing the proportion of disadvantaged students

3. **Multiple Deprivation Factors**: Distribution of students by number of disadvantage factors

4. **Year Group Analysis**: Compare deprivation rates across different year groups

5. **Vulnerability Factors**: Detailed breakdown of different types of disadvantage (SEN, FSM, Child Protection, etc.)

6. **Heatmap Analysis**: Visual representation of how different factors affect each year group

7. **Key Insights**: Highlighted statistics for students requiring urgent support

## Using Filters

Use the sidebar to filter data:
- **Select Year Groups**: Choose one or more year groups to analyze specific cohorts
- All charts and metrics update automatically based on your selection

## Data Source

The dashboard reads from `anonymised_data.csv` which contains anonymised student demographic data including:
- Year group information
- SEN status
- Free School Meals eligibility
- Pupil Premium status
- Young Carer status
- Looked After status
- Child Protection status
- L3 Graduated Response

## Requirements

All required packages are listed in `requirements.txt`:
- streamlit >= 1.28.0
- plotly >= 5.17.0

These are already installed in the virtual environment.
