import streamlit as st
from PIL import Image
import google.generativeai as genai
import creds
import json
import re
from typing import Dict, Optional
import plotly.graph_objects as go
import plotly.express as px

# Configure Gemini API
genai.configure(api_key=creds.api_key)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Streamlit page config
st.set_page_config(
    page_title="☀️ Solar Rooftop Analyzer", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🔆 Advanced Rooftop Solar Panel Feasibility Analyzer")
st.markdown("---")

# Constants and Assumptions
PANEL_EFFICIENCY = 0.20  # 20% efficiency for modern panels
SYSTEM_LOSSES = 0.86  # 14% total system losses (inverter, wiring, soiling, etc.)
CO2_FACTOR = 0.82  # kg CO2 per kWh (grid average)
PANEL_WATTAGE = 400  # Watts per panel
PANEL_AREA = 2.0  # m² per panel
COST_PER_KW = 45000  # INR per kW installed
ELECTRICITY_RATE = 7.5  # INR per kWh

# Input method selection
col1, col2 = st.columns([1, 3])
with col1:
    option = st.radio("Select input method:", ["📷 Upload Image", "📍 Coordinates"])

# Enhanced prompt with detailed instructions
base_prompt = """
You are an expert solar energy consultant analyzing rooftop solar panel feasibility.
Provide a comprehensive analysis following these guidelines:

CALCULATION METHODOLOGY:
1. Rooftop Area: 
   - For images: Estimate usable roof area considering obstacles, shadows, and edge setbacks (typically 70-80% of total)
   - For coordinates: Assume typical residential rooftop (100-200 m²) with 75% usability

2. Solar Irradiance:
   - Use location-specific data if identifiable
   - Default to regional averages (4-6 kWh/m²/day for most regions)
   - Account for seasonal variations

3. System Sizing:
   - Panel efficiency: 20%
   - System losses: 14% (inverter, wiring, temperature, soiling)
   - Recommended capacity = (Usable area × 0.15) kW
   - Panel count = Capacity / 0.4 kW per panel

4. Energy Generation:
   - Daily = Area × Irradiance × Efficiency × System performance
   - Monthly = Daily × 30
   - Annual = Daily × 365 × 0.95 (accounting for maintenance downtime)

5. Financial Analysis:
   - Installation cost: ₹45,000/kW
   - Electricity rate: ₹7.5/kWh
   - Annual savings = Annual generation × Electricity rate
   - Payback period = Total cost / Annual savings

6. Environmental Impact:
   - CO2 savings = Annual generation × 0.82 kg/kWh

RETURN STRICT JSON FORMAT:
{
  "location_analysis": {
    "latitude": <value or null>,
    "longitude": <value or null>,
    "climate_zone": "<tropical/temperate/arid/cold>",
    "roof_orientation": "<north/south/east/west/flat>",
    "roof_tilt_degrees": <0-45>,
    "shading_factor": <0.7-1.0>
  },
  "technical_specifications": {
    "total_roof_area_m2": <value>,
    "usable_roof_area_m2": <value>,
    "average_daily_irradiance_kWh_per_m2": <4-6>,
    "recommended_capacity_kW": <value>,
    "panel_count": <integer>,
    "panel_type": "monocrystalline",
    "inverter_capacity_kW": <value>,
    "system_efficiency_percent": <75-86>
  },
  "energy_production": {
    "estimated_daily_generation_kWh": <value>,
    "estimated_monthly_generation_kWh": <value>,
    "estimated_annual_generation_kWh": <value>,
    "capacity_utilization_factor_percent": <15-25>,
    "performance_ratio": <0.75-0.85>
  },
  "financial_analysis": {
    "total_installation_cost_INR": <value>,
    "annual_electricity_savings_INR": <value>,
    "payback_period_years": <value>,
    "25_year_savings_INR": <value>,
    "return_on_investment_percent": <value>
  },
  "environmental_impact": {
    "annual_CO2_reduction_kg": <value>,
    "25_year_CO2_reduction_tons": <value>,
    "equivalent_trees_planted": <value>
  },
  "regulatory_benefits": {
    "subsidy_percentage": <0-40>,
    "subsidy_amount_INR": <value>,
    "net_metering_available": true/false,
    "accelerated_depreciation_available": true/false
  },
  "recommendations": {
    "feasibility_score": <1-10>,
    "key_advantages": ["advantage1", "advantage2"],
    "potential_challenges": ["challenge1", "challenge2"],
    "implementation_timeline_months": <3-6>
  }
}

For invalid images return: {"error": "Invalid rooftop image", "valid_data": false}
Return ONLY the JSON, no explanations or markdown formatting.
"""

# Validation functions
def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate latitude and longitude values."""
    return -90 <= lat <= 90 and -180 <= lon <= 180

def validate_solar_data(data: Dict) -> bool:
    """Validate parsed solar analysis data."""
    try:
        # Check required fields
        required_sections = [
            'location_analysis', 'technical_specifications', 
            'energy_production', 'financial_analysis'
        ]
        for section in required_sections:
            if section not in data:
                return False
        
        # Validate ranges
        tech = data['technical_specifications']
        if not (0 < tech['usable_roof_area_m2'] <= tech['total_roof_area_m2']):
            return False
        if not (0 < tech['recommended_capacity_kW'] <= 1000):  # Max 1MW
            return False
        
        return True
    except:
        return False

def clean_json_response(text: str) -> str:
    """Clean and extract JSON from Gemini response."""
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Find JSON object
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    return text

# Enhanced visualizer with charts
def visualize_detailed_report(data: Dict):
    """Create comprehensive visualization of solar analysis."""
    
    # Header metrics
    st.subheader("🎯 Feasibility Overview")
    score = data['recommendations']['feasibility_score']
    score_color = "🟢" if score >= 7 else "🟡" if score >= 5 else "🔴"
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        f"{score_color} Feasibility Score", 
        f"{score}/10",
        help="Based on location, roof characteristics, and financial viability"
    )
    col2.metric(
        "💰 Payback Period", 
        f"{data['financial_analysis']['payback_period_years']:.1f} years"
    )
    col3.metric(
        "🌱 Annual CO₂ Reduction", 
        f"{data['environmental_impact']['annual_CO2_reduction_kg']:,.0f} kg"
    )
    col4.metric(
        "📊 ROI", 
        f"{data['financial_analysis']['return_on_investment_percent']:.1f}%"
    )
    
    # Technical specifications
    with st.expander("⚙️ Technical Specifications", expanded=True):
        tech = data['technical_specifications']
        loc = data['location_analysis']
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Usable Roof Area", f"{tech['usable_roof_area_m2']:.1f} m²")
        col2.metric("System Capacity", f"{tech['recommended_capacity_kW']:.1f} kW")
        col3.metric("Number of Panels", tech['panel_count'])
        
        col4, col5, col6 = st.columns(3)
        col4.metric("Daily Irradiance", f"{tech['average_daily_irradiance_kWh_per_m2']:.1f} kWh/m²")
        col5.metric("Roof Orientation", loc['roof_orientation'].title())
        col6.metric("System Efficiency", f"{tech['system_efficiency_percent']:.1f}%")
    
    # Energy production chart
    with st.expander("⚡ Energy Production Analysis", expanded=True):
        energy = data['energy_production']
        
        # Monthly generation chart
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_variation = [
            energy['estimated_monthly_generation_kWh'] * factor 
            for factor in [0.85, 0.90, 0.95, 1.0, 1.05, 1.1, 
                          1.1, 1.05, 1.0, 0.95, 0.90, 0.85]
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=months,
            y=monthly_variation,
            text=[f'{val:.0f}' for val in monthly_variation],
            textposition='auto',
            marker_color='gold'
        ))
        fig.update_layout(
            title="Estimated Monthly Energy Generation (kWh)",
            xaxis_title="Month",
            yaxis_title="Energy (kWh)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Daily Generation", f"{energy['estimated_daily_generation_kWh']:.1f} kWh")
        col2.metric("Monthly Average", f"{energy['estimated_monthly_generation_kWh']:,.0f} kWh")
        col3.metric("Annual Generation", f"{energy['estimated_annual_generation_kWh']:,.0f} kWh")
    
    # Financial analysis
    with st.expander("💰 Financial Analysis", expanded=True):
        fin = data['financial_analysis']
        reg = data['regulatory_benefits']
        
        # Cost breakdown pie chart
        labels = ['Base Cost', 'Subsidy Benefit']
        values = [
            fin['total_installation_cost_INR'] - reg['subsidy_amount_INR'],
            reg['subsidy_amount_INR']
        ]
        
        fig = px.pie(
            values=values, 
            names=labels,
            title="Installation Cost Breakdown",
            hole=0.4
        )
        fig.update_traces(
            text=[f'₹{v:,.0f}' for v in values],
                        textposition='inside',
            textinfo='percent+text'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Installation Cost", f"₹{fin['total_installation_cost_INR']:,.0f}")
            st.metric("Subsidy Amount", f"₹{reg['subsidy_amount_INR']:,.0f}")
            st.metric("Net Cost", f"₹{fin['total_installation_cost_INR'] - reg['subsidy_amount_INR']:,.0f}")
        
        with col2:
            st.metric("Annual Savings", f"₹{fin['annual_electricity_savings_INR']:,.0f}")
            st.metric("25-Year Savings", f"₹{fin['25_year_savings_INR']:,.0f}")
            st.metric("Net Metering", "✅ Available" if reg['net_metering_available'] else "❌ Not Available")
    
    # Environmental impact
    with st.expander("🌍 Environmental Impact", expanded=True):
        env = data['environmental_impact']
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Annual CO₂ Reduction", f"{env['annual_CO2_reduction_kg']:,.0f} kg")
        col2.metric("25-Year CO₂ Reduction", f"{env['25_year_CO2_reduction_tons']:.1f} tons")
        col3.metric("Equivalent Trees", f"{env['equivalent_trees_planted']:,.0f} trees")
        
        # CO2 savings over time
        years = list(range(1, 26))
        cumulative_co2 = [env['annual_CO2_reduction_kg'] * year / 1000 for year in years]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years,
            y=cumulative_co2,
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='green', width=3),
            marker=dict(size=6),
            name='CO₂ Reduction'
        ))
        fig.update_layout(
            title="Cumulative CO₂ Reduction Over 25 Years (Tons)",
            xaxis_title="Years",
            yaxis_title="CO₂ Reduction (Tons)",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    with st.expander("📋 Recommendations & Next Steps", expanded=True):
        rec = data['recommendations']
        
        st.markdown(f"**Implementation Timeline:** {rec['implementation_timeline_months']} months")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**✅ Key Advantages:**")
            for advantage in rec['key_advantages']:
                st.markdown(f"• {advantage}")
        
        with col2:
            st.markdown("**⚠️ Potential Challenges:**")
            for challenge in rec['potential_challenges']:
                st.markdown(f"• {challenge}")
    
    # Summary report
    st.markdown("---")
    st.caption("📌 **Note:** This is an AI-generated estimate based on satellite imagery, regional solar data, and standard industry assumptions. Actual results may vary. Please consult with a certified solar installer for precise calculations.")

# Error handling and retry mechanism
def analyze_with_retry(content, max_retries=3):
    """Analyze content with retry mechanism for better reliability."""
    for attempt in range(max_retries):
        try:
            response = model.generate_content(content)
            raw_text = response.text.strip()
            
            # Clean and parse JSON
            json_text = clean_json_response(raw_text)
            parsed = json.loads(json_text)
            
            # Check for error response
            if isinstance(parsed, dict) and parsed.get("valid_data") is False:
                st.error("⚠️ The uploaded image does not contain a valid rooftop. Please upload a clear aerial/top view of a building.")
                return None
            
            # Validate data structure
            if validate_solar_data(parsed):
                return parsed
            else:
                if attempt < max_retries - 1:
                    st.warning(f"Attempt {attempt + 1} failed. Retrying...")
                    continue
                else:
                    raise ValueError("Invalid data structure received")
                    
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                st.warning(f"JSON parsing error on attempt {attempt + 1}. Retrying...")
                continue
            else:
                st.error(f"Failed to parse response after {max_retries} attempts")
                with st.expander("🔍 Debug Information"):
                    st.text("Raw response:")
                    st.code(raw_text if 'raw_text' in locals() else "No response received")
                return None
                
        except Exception as e:
            if attempt < max_retries - 1:
                continue
            else:
                st.error(f"Analysis failed: {str(e)}")
                return None
    
    return None

# Main analysis function
def perform_analysis(content):
    """Main function to perform solar analysis."""
    with st.spinner("🔍 Analyzing solar potential... This may take a moment."):
        result = analyze_with_retry(content)
        if result:
            visualize_detailed_report(result)
            
            # Option to download report
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📥 Download Detailed Report", type="primary", use_container_width=True):
                    report_json = json.dumps(result, indent=2)
                    st.download_button(
                        label="Download JSON Report",
                        data=report_json,
                        file_name="solar_feasibility_report.json",
                        mime="application/json"
                    )

# Image upload interface
if option == "📷 Upload Image":
    with col2:
        st.info("📸 **Best results:** Upload a clear aerial/satellite view of the rooftop")
        
        uploaded_image = st.file_uploader(
            "Upload rooftop image", 
            type=["jpg", "jpeg", "png", "webp"],
            help="For best results, use Google Earth or drone imagery showing the complete rooftop"
        )
        
        if uploaded_image:
            # Display image with size limit
            image = Image.open(uploaded_image)
            
            # Resize if too large
            max_size = (1024, 1024)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(image, caption="Uploaded Rooftop Image", use_container_width=True)
            
            # Additional parameters
            with st.expander("🔧 Advanced Options"):
                col1, col2 = st.columns(2)
                with col1:
                    roof_type = st.selectbox(
                        "Roof Type",
                        ["Flat", "Sloped", "Mixed"],
                        help="Select the predominant roof type"
                    )
                with col2:
                    building_type = st.selectbox(
                        "Building Type",
                        ["Residential", "Commercial", "Industrial"],
                        help="This affects subsidy calculations"
                    )
            
            if st.button("🚀 Analyze Solar Potential", type="primary", use_container_width=True):
                enhanced_prompt = f"{base_prompt}\n\nAdditional context: Roof type is {roof_type}, Building type is {building_type}"
                perform_analysis([enhanced_prompt, image])

# Coordinate input interface
elif option == "📍 Coordinates":
    with col2:
        st.info("🌍 **Enter precise coordinates** of your building for location-based analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input(
                "Latitude", 
                format="%.6f", 
                value=28.6139,  # Default: New Delhi
                min_value=-90.0,
                max_value=90.0,
                help="Enter latitude in decimal degrees"
            )
        with col2:
            lon = st.number_input(
                "Longitude", 
                format="%.6f", 
                value=77.2090,  # Default: New Delhi
                min_value=-180.0,
                max_value=180.0,
                help="Enter longitude in decimal degrees"
            )
        
        # Additional parameters
        with st.expander("🏠 Building Details"):
            col1, col2 = st.columns(2)
            with col1:
                roof_area = st.number_input(
                    "Approximate Roof Area (m²)",
                    min_value=50,
                    max_value=10000,
                    value=150,
                    step=10,
                    help="Total roof area of your building"
                )
                building_type = st.selectbox(
                    "Building Type",
                    ["Residential", "Commercial", "Industrial"]
                )
            with col2:
                floors = st.number_input(
                    "Number of Floors",
                    min_value=1,
                    max_value=50,
                    value=2
                )
                roof_access = st.selectbox(
                    "Roof Accessibility",
                    ["Easy", "Moderate", "Difficult"]
                )
        
        if st.button("📡 Analyze Location", type="primary", use_container_width=True):
            if validate_coordinates(lat, lon):
                location_prompt = f"""
Analyze rooftop solar panel feasibility for:
- Latitude: {lat}
- Longitude: {lon}
- Approximate roof area: {roof_area} m²
- Building type: {building_type}
- Number of floors: {floors}
- Roof accessibility: {roof_access}

{base_prompt}
"""
                perform_analysis(location_prompt)
            else:
                st.error("❌ Invalid coordinates. Please check your input.")

# Sidebar with additional information
with st.sidebar:
    st.markdown("### 📚 Solar Energy Guide")
    
    with st.expander("☀️ How Solar Works"):
        st.markdown("""
        1. **Solar Panels** convert sunlight to DC electricity
        2. **Inverters** convert DC to AC for home use
        3. **Net Metering** exports excess power to grid
        4. **Battery Storage** (optional) stores excess energy
        """)
    
    with st.expander("💡 Tips for Best Results"):
        st.markdown("""
        **For Image Upload:**
        - Use aerial/satellite imagery
        - Ensure clear view of entire roof
        - Avoid shadows and obstructions
        
        **For Coordinates:**
        - Use precise decimal coordinates
        - Verify location on Google Maps
        - Provide accurate roof area estimate
        """)
    
    with st.expander("📊 Understanding Metrics"):
        st.markdown("""
        - **Feasibility Score**: 1-10 rating of solar viability
        - **Payback Period**: Years to recover investment
        - **ROI**: Return on investment over 25 years
        - **Capacity Factor**: Actual vs theoretical output
        - **Performance Ratio**: System efficiency metric
        """)
    
    st.markdown("---")
    st.markdown("### 🔗 Resources")
    st.markdown("[Solar Calculator](https://solarrooftop.gov.in/)")
    st.markdown("[Subsidy Information](https://solarrooftop.gov.in/)")
    st.markdown("[Net Metering Policies](https://solarrooftop.gov.in/)")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Powered by Google Gemini AI | For estimation purposes only | Consult professionals for implementation
    </div>
    """,
    unsafe_allow_html=True
)