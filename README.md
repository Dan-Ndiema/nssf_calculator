# NSSF Contribution Calculator

A Python web application that calculates Kenyan NSSF (National Social Security Fund) 
contributions and projects retirement savings growth, built using the NSSF Act 2013 
tier structure (2026 rates).

## Features
- Calculates Tier I and Tier II NSSF contributions for any salary
- Projects retirement savings using compound growth modeling
- Member registration with Excel-based record storage
- Interactive savings growth visualization
- Downloadable PDF member statements

## Tech Stack
- Python
- Streamlit (web interface)
- Pandas (data handling)
- Plotly (data visualization)
- FPDF2 (PDF generation)
- openpyxl (Excel export)

## Background
Built during my industrial attachment at NSSF Kenya, combining hands-on experience 
with claims processing and member registration with my interest in Python development.

## Disclaimer
This is an educational/portfolio project and is not an official NSSF tool. 
Contribution calculations follow the publicly available NSSF Act 2013 tier 
structure but should not be used as a substitute for official NSSF statements.

## How to run locally
\`\`\`bash
pip install streamlit pandas plotly fpdf2 openpyxl
streamlit run app.py
\`\`\`

## Author
Daniel — Bachelor of Applied Statistics with Computing, University of Eldoret