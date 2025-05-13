import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import os
import utils

# Page configuration
st.set_page_config(
    page_title="Fertilizer Recommendation System",
    page_icon="🌱",
    layout="wide"
)

# Title and description
st.title("🌱 Fertilizer Recommendation System")
st.markdown("""
This application analyzes historical crop and soil data to predict optimal fertilizer requirements
for the next 6 months using time series forecasting.
""")

# Define API endpoint
API_URL = "https://smart-irrigation-vtxn.onrender.com"

# Function to load data
@st.cache_data
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        data['Date'] = pd.to_datetime(data['Date'])
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Function to get monthly statistics
def get_monthly_stats(data):
    monthly_data = data.copy()
    monthly_data['Month'] = monthly_data['Date'].dt.to_period('M')
    monthly_stats = monthly_data.groupby('Month').agg({
        'N': 'mean',
        'P': 'mean',
        'K': 'mean',
        'Temperature': 'mean',
        'Humidity': 'mean',
        'Crop_Yield': 'mean'
    }).reset_index()
    monthly_stats['Month'] = monthly_stats['Month'].astype(str)
    return monthly_stats

# Function to fetch forecast from API
def get_forecast():
    try:
        response = requests.get(f"{API_URL}/forecast")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching forecast: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return None

# Sidebar for data upload and model parameters
with st.sidebar:
    st.header("Data Settings")
    
    # Data source selection
    data_source = st.radio(
        "Choose data source:",
        ("Use provided dataset", "Upload your own CSV")
    )
    
    if data_source == "Upload your own CSV":
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        if uploaded_file is not None:
            data_path = uploaded_file
        else:
            data_path = "output.csv"  # Default to provided dataset
    else:
        data_path = "output.csv"
    
    st.header("Model Settings")
    st.markdown("Note: Model parameters are currently fixed in the API.")
    
    st.header("Fertilizer Information")
    st.markdown("""
    *N (Nitrogen):* Essential for leaf growth and chlorophyll production.
    
    *P (Phosphorus):* Supports root development and flowering.
    
    *K (Potassium):* Improves overall plant health and disease resistance.
    """)

# Load data
data = load_data(data_path)

# Main content
if data is not None:
    # Basic data analysis
    st.header("Historical Data Analysis")
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Data Timespan", f"{data['Date'].min().strftime('%b %Y')} - {data['Date'].max().strftime('%b %Y')}")
    with col2:
        st.metric("Average Nitrogen (N)", f"{data['N'].mean():.2f}")
    with col3:
        st.metric("Data Points", f"{len(data):,}")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["Monthly Trends", "Correlations", "Raw Data", "Forecast"])
    
    with tab1:
        st.subheader("Monthly Fertilizer Requirements")
        monthly_data = get_monthly_stats(data)
        
        # Nitrogen, Phosphorus, Potassium over time
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_data['Month'], y=monthly_data['N'], mode='lines+markers', name='Nitrogen (N)'))
        fig.add_trace(go.Scatter(x=monthly_data['Month'], y=monthly_data['P'], mode='lines+markers', name='Phosphorus (P)'))
        fig.add_trace(go.Scatter(x=monthly_data['Month'], y=monthly_data['K'], mode='lines+markers', name='Potassium (K)'))
        
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Value',
            legend_title='Nutrient',
            height=500,
            xaxis={'tickangle': -45}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Temperature and humidity
        st.subheader("Environmental Factors")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_data['Month'], y=monthly_data['Temperature'], mode='lines+markers', name='Temperature'))
        fig.add_trace(go.Scatter(x=monthly_data['Month'], y=monthly_data['Humidity'], mode='lines+markers', name='Humidity'))
        
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Value',
            legend_title='Factor',
            height=400,
            xaxis={'tickangle': -45}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Correlation Analysis")
        # Select columns for correlation
        corr_cols = ['N', 'P', 'K', 'Temperature', 'Humidity', 'Wind_Speed', 'Crop_Yield', 'Soil_Quality']
        corr_data = data[corr_cols].corr()
        
        # Plot correlation heatmap
        fig = px.imshow(
            corr_data,
            text_auto=True,
            color_continuous_scale='RdBu_r',
            title='Correlation Between Variables'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Scatter plot between selected variables
        st.subheader("Relationship Between Variables")
        col1, col2 = st.columns(2)
        with col1:
            x_var = st.selectbox("X-axis", corr_cols, index=0)
        with col2:
            y_var = st.selectbox("Y-axis", corr_cols, index=6)
        
        fig = px.scatter(data, x=x_var, y=y_var, color='Crop_Type', hover_data=['Date'])
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Raw Data")
        st.dataframe(data)
    
    with tab4:
        st.subheader("Forecasted Fertilizer Requirements")
        
        # Get forecast from API
        forecast_data = get_forecast()
        
        if forecast_data:
            forecast_results = forecast_data['forecast']
            
            # Create a dataframe from forecast results
            forecast_df = pd.DataFrame(forecast_results)
            
            # Use Month 1, Month 2, etc. instead of actual dates
            forecast_df['date'] = [f"Month {i+1}" for i in range(6)]
            
            # Display forecast results
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Plot forecast with confidence intervals
                fig = go.Figure()
                
                # Add historical data
                monthly_n = get_monthly_stats(data)
                fig.add_trace(go.Scatter(
                    x=monthly_n['Month'], 
                    y=monthly_n['N'], 
                    mode='lines+markers',
                    name='Historical N',
                    line=dict(color='blue')
                ))
                
                # Add forecast
                fig.add_trace(go.Scatter(
                    x=forecast_df['date'],
                    y=forecast_df['predicted_value'],
                    mode='lines+markers',
                    name='Forecast N',
                    line=dict(color='red')
                ))
                
                # Add confidence interval
                fig.add_trace(go.Scatter(
                    x=forecast_df['date'].tolist() + forecast_df['date'].tolist()[::-1],
                    y=forecast_df['upper_ci'].tolist() + forecast_df['lower_ci'].tolist()[::-1],
                    fill='toself',
                    fillcolor='rgba(255,0,0,0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    hoverinfo='skip',
                    showlegend=False
                ))
                
                fig.update_layout(
                    title='Nitrogen (N) Forecast for Next 6 Months',
                    xaxis_title='Month',
                    yaxis_title='Nitrogen Value',
                    hovermode='x unified',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Predicted Values")
                formatted_forecast = forecast_df[['date', 'predicted_value']].copy()
                formatted_forecast.columns = ['Month', 'N Value']
                formatted_forecast['N Value'] = formatted_forecast['N Value'].round(2)
                st.dataframe(formatted_forecast, hide_index=True)
                
                st.subheader("Confidence Intervals")
                ci_df = forecast_df[['date', 'lower_ci', 'upper_ci']].copy()
                ci_df.columns = ['Month', 'Lower CI', 'Upper CI']
                ci_df['Lower CI'] = ci_df['Lower CI'].round(2)
                ci_df['Upper CI'] = ci_df['Upper CI'].round(2)
                st.dataframe(ci_df, hide_index=True)
            
            # Fertilizer recommendation based on forecast
            st.subheader("Fertilizer Recommendations")
            st.markdown("""
            Based on the forecast, here are the recommended actions for the upcoming months:
            """)
            
            recommendations = utils.generate_recommendations(forecast_df)
            for month, rec in recommendations.items():
                with st.expander(f"Recommendation for {month}"):
                    st.write(rec)
        else:
            st.error("Unable to get forecast data. Make sure the API server is running.")
            
            # Provide instructions to start the API server
            st.info("""
            To start the API server, run the following command in a terminal:
            
            uvicorn main:app --host 0.0.0.0 --port 8000
            
            """)

else:
    st.error("No data available. Please check the file path or upload a valid CSV file.")
