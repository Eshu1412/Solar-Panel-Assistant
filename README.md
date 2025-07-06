# Solar Rooftop Analyzer - README

## 🔆 Advanced Rooftop Solar Panel Feasibility Analyzer

A sophisticated Streamlit application that leverages Google's Gemini AI to analyze rooftop solar panel feasibility through image analysis or geographic coordinates.

## 📋 Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Technical Details](#technical-details)
- [API Response Format](#api-response-format)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Functionality
- **Dual Input Methods**: Analyze via rooftop images or geographic coordinates
- **AI-Powered Analysis**: Utilizes Google Gemini 2.5 Flash for intelligent assessment
- **Comprehensive Reporting**: Detailed technical, financial, and environmental analysis
- **Interactive Visualizations**: Dynamic charts using Plotly for data representation
- **Retry Mechanism**: Robust error handling with automatic retries

### Analysis Components
1. **Technical Specifications**
   - Roof area assessment
   - System capacity recommendations
   - Panel count and configuration
   - Irradiance calculations

2. **Financial Analysis**
   - Installation cost breakdown
   - ROI calculations
   - Payback period estimation
   - 25-year savings projection
   - Subsidy calculations

3. **Environmental Impact**
   - CO₂ reduction metrics
   - Equivalent trees planted
   - Long-term environmental benefits

4. **Energy Production**
   - Daily, monthly, and annual generation estimates
   - Seasonal variation modeling
   - Performance ratio calculations

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/Eshu1412/Solar-Panel-Assistant.git
cd Solar-Panel-Assistant
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Configuration

1. **Set up Google Gemini API**
   - Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.streamlit/secrets.toml` file:
```toml
auth_key = "your-gemini-api-key-here"
```

2. **Customize Constants** (Optional)
```python
PANEL_EFFICIENCY = 0.20  # 20% efficiency
SYSTEM_LOSSES = 0.86     # 14% system losses
CO2_FACTOR = 0.82        # kg CO2 per kWh
PANEL_WATTAGE = 400      # Watts per panel
PANEL_AREA = 2.0         # m² per panel
COST_PER_KW = 45000      # INR per kW
ELECTRICITY_RATE = 7.5   # INR per kWh
```

## Usage

1. **Run the application**
```bash
streamlit run app.py
```

2. **Choose input method**
   - **Image Upload**: Upload aerial/satellite view of rooftop
   - **Coordinates**: Enter latitude and longitude

3. **Provide additional details** (optional)
   - Roof type and building specifications
   - Advanced configuration options

4. **Analyze and review results**
   - View comprehensive metrics
   - Explore interactive charts
   - Download detailed JSON report

## Technical Details

### System Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Input    │────▶│  Streamlit UI   │────▶│  Gemini API     │
│ (Image/Coords)  │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │ Visualization   │◀────│ JSON Response   │
                        │   (Plotly)      │     │   Processing    │
                        └─────────────────┘     └─────────────────┘
```

### Key Functions

#### `analyze_with_retry(content, max_retries=3)`
Implements robust retry mechanism for API calls with error handling.

#### `validate_solar_data(data: Dict) -> bool`
Validates the structure and ranges of parsed solar analysis data.

#### `visualize_detailed_report(data: Dict)`
Creates comprehensive visualization with metrics, charts, and recommendations.

#### `clean_json_response(text: str) -> str`
Extracts and cleans JSON from Gemini API responses.

## API Response Format

The application expects the following JSON structure from Gemini API:
```json
{
  "location_analysis": {
    "latitude": 28.6139,
    "longitude": 77.2090,
    "climate_zone": "tropical",
    "roof_orientation": "south",
    "roof_tilt_degrees": 15,
    "shading_factor": 0.9
  },
  "technical_specifications": {
    "total_roof_area_m2": 200,
    "usable_roof_area_m2": 150,
    "average_daily_irradiance_kWh_per_m2": 5.2,
    "recommended_capacity_kW": 22.5,
    "panel_count": 56,
    "panel_type": "monocrystalline",
    "inverter_capacity_kW": 25,
    "system_efficiency_percent": 82
  },
  "energy_production": {
    "estimated_daily_generation_kWh": 90,
    "estimated_monthly_generation_kWh": 2700,
    "estimated_annual_generation_kWh": 32850,
    "capacity_utilization_factor_percent": 18,
    "performance_ratio": 0.82
  },
  "financial_analysis": {
    "total_installation_cost_INR": 1012500,
    "annual_electricity_savings_INR": 246375,
    "payback_period_years": 4.1,
    "25_year_savings_INR": 6159375,
    "return_on_investment_percent": 508
  },
  "environmental_impact": {
    "annual_CO2_reduction_kg": 26937,
    "25_year_CO2_reduction_tons": 673.4,
    "equivalent_trees_planted": 1347
  },
  "regulatory_benefits": {
    "subsidy_percentage": 40,
    "subsidy_amount_INR": 405000,
    "net_metering_available": true,
    "accelerated_depreciation_available": false
  },
  "recommendations": {
    "feasibility_score": 9,
    "key_advantages": [
      "Excellent solar irradiance",
      "Optimal roof orientation"
    ],
    "potential_challenges": [
      "Initial capital requirement",
      "Grid connection approval"
    ],
    "implementation_timeline_months": 3
  }
}
```

## Dependencies

Create a `requirements.txt` file:
```txt
streamlit==1.28.1
pillow==10.1.0
google-generativeai==0.3.0
plotly==5.18.0
```

## Contributing

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)  
3. Commit changes (`git commit -m 'Add AmazingFeature'`)  
4. Push to branch (`git push origin feature/AmazingFeature`)  
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings to all functions
- Update tests for new features
- Ensure backward compatibility

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for powering the analysis  
- Streamlit for the web framework  
- Plotly for interactive visualizations  
- Solar industry standards from MNRE (Ministry of New and Renewable Energy, India)

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact: mauryatushar115@gmail.com
- Documentation: [Wiki](https://github.com/yourusername/solar-rooftop-analyzer/wiki)

---

**Note**: This application provides estimates based on AI analysis and standard industry assumptions. For actual implementation, consult with certified solar installers and conduct professional site assessments.
