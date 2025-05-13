import pandas as pd

def generate_recommendations(forecast_df):
    """
    Generate fertilizer recommendations based on forecast data
    
    Args:
        forecast_df: DataFrame containing forecast data with date and predicted_value columns
        
    Returns:
        Dictionary with months as keys and recommendation text as values
    """
    recommendations = {}
    
    for index, row in forecast_df.iterrows():
        month = row['date']
        n_value = row['predicted_value']
        
        # Basic recommendation logic based on N value
        if n_value > 70:
            recommendation = f"""
            *High Nitrogen Required: {n_value:.2f}*
            
            - Apply high-nitrogen fertilizers like Ammonium Nitrate or Urea
            - Recommended application rate: 2.5-3.0 kg per acre
            - Apply in split doses to prevent nitrogen runoff
            - Monitor plants for signs of excess nitrogen (excessive vegetative growth)
            - Consider soil testing before application
            """
        elif n_value > 55:
            recommendation = f"""
            *Moderate-High Nitrogen Required: {n_value:.2f}*
            
            - Apply balanced NPK fertilizer with higher N content (e.g., 20-10-10)
            - Recommended application rate: 2.0-2.5 kg per acre
            - Focus on slow-release nitrogen sources
            - For leafy crops, consider foliar nitrogen application
            - Monitor soil moisture to maximize nitrogen uptake
            """
        elif n_value > 40:
            recommendation = f"""
            *Moderate Nitrogen Required: {n_value:.2f}*
            
            - Apply balanced NPK fertilizer (e.g., 15-15-15)
            - Recommended application rate: 1.5-2.0 kg per acre
            - Incorporate organic matter to improve nitrogen retention
            - Consider crop rotation with legumes in future planning
            - Monitor for signs of nitrogen deficiency (yellowing of older leaves)
            """
        else:
            recommendation = f"""
            *Low-Moderate Nitrogen Required: {n_value:.2f}*
            
            - Apply light nitrogen fertilization (e.g., 10-10-10)
            - Recommended application rate: 1.0-1.5 kg per acre
            - Consider organic alternatives like compost or manure
            - Implement cover crops to build soil nitrogen naturally
            - Avoid over-application which may lead to nutrient runoff
            """
        
        # Add soil health notes
        recommendation += """
        
        *Additional Soil Health Recommendations:*
        - Maintain proper soil pH (6.0-7.0) for optimal nutrient availability
        - Ensure adequate soil moisture for nutrient uptake
        - Consider micronutrient supplements if deficiency symptoms are present
        - Practice sustainable soil management to improve long-term fertility
        """
        
        recommendations[month] = recommendation
    
    return recommendations
