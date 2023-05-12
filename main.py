import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import plotly.express as px
import world_bank_data as wb
from datetime import date

from functools import reduce

today = date.today()

st.title('World Bank Data Explorer')

st.write("""Discover a world of economic and development insights with the World Bank Data Explorer app. 
         Access vast data collections, explore interactive visualizations, and uncover compelling trends effortlessly. 
         Whether you're an economist or a curious mind, this user-friendly app lets you compare, share, 
         and stay informed with ease.""")

######### SIDE BAR #########

#Side Bar
st.sidebar.header('Query Parameters')

col1, col2 = st.sidebar.columns(2)
from_date = col1.selectbox('From', list(range(1950,2023)))
to_date = col2.selectbox('To', list(reversed(range(1950,2024))))
date_range = str(from_date) + ":" + str(to_date)


countries = st.sidebar.multiselect('Countries', list(wb.get_countries()["name"]))
countries_ids = wb.get_countries().loc[wb.get_countries()["name"].isin(countries)].index.astype(str).tolist()


    
topic  = st.sidebar.selectbox('Topic', list(wb.get_topics()["value"]))
topics_id = wb.get_topics().loc[wb.get_topics()["value"] == topic].index.astype(int)[0]

source = st.sidebar.selectbox('Source', list(wb.get_sources()["name"]))
sources_id = wb.get_sources().loc[wb.get_sources()["name"] == source].index.astype(int)[0]


######### MAIN #########


try:
    
    st.header('Indicators')
    st.write("Select the indicators you want to visualize")
    
    df = wb.get_indicators(topic=topics_id, source=sources_id).drop("unit", axis=1)
    df.insert(0, "Select",  False)
    edited_df =  st.experimental_data_editor(df)




    # Define a list of series IDs
    series_ids = edited_df.loc[edited_df["Select"] == True].index.tolist()
    
    
    try:


        # Retrieve the Series data from the World Bank API for each series ID
        data_frames = []
        for series_id in series_ids:
            series = wb.get_series(indicator=series_id, country=countries_ids, date=date_range)
            
            # Convert series to DataFrame and reset index
            df_series = series.reset_index()
            df_series.columns = ['country', 'name', 'year', 'value']
            
            
            # Pivot the DataFrame to have indicators as columns
            df_pivot = df_series.pivot_table(values='value', index=['country', 'year'], columns='name')
            
            # Append the DataFrame to the list
            data_frames.append(df_pivot)


        # Use join to merge all dataframes
        df_final = data_frames[0].join(data_frames[1:], how='outer')


        # Reset index
        df_final.reset_index(inplace=True)



        ######################################################################


        st.header('Data')
        st.write("Here are the resuls from your query")

        st.dataframe(df_final)

        @st.cache_data
        def convert_df(df_final):
            return df_final.to_csv(index=False).encode('utf-8')


        csv = convert_df(df_final)

        st.download_button(
        "Download CSV",
        csv,
        "data.csv",
        "text/csv",
        key='download-csv'
        )




        ################################################################


        st.header('Data Visualization')
        st.write("Visualization of the data")

        topics = df_final.columns[2:].tolist()

        radio = st.radio('Select a chart type', ('country', 'topic'), horizontal=True)

        if radio == 'topic':
            
            for topic in topics:
                st.write(f'## {topic}')
                topic_data = df_final.pivot(index='year', columns='country', values=topic)
                
                cols = st.columns(len(countries))
                
                for i, country in enumerate(countries):
                    last_value = topic_data[country].iloc[-1] 
                    first_value = topic_data[country].iloc[0] 
                    value = format(round(last_value, 2),',')
                    delta = "{:.2%}".format(((last_value-first_value)/first_value))
                    cols[i].metric(label=country, value=value, delta=delta)

                st.line_chart(topic_data, use_container_width=True)
                
                # Create a DataFrame for this country with each indicator as a column
                topic_data = df_final[topic]
                

            
        else:
            # List of unique countries
            countries = df_final['country'].unique()
            
            df_final = df_final.set_index(['country', 'year'])
            


            for country in countries:
                st.write(f'### {country}')
                
                # Create a DataFrame for this country with each indicator as a column
                country_data = df_final.loc[country]
                
                cols = st.columns(len(topics))
                
                for i, topic in enumerate(topics):
                    last_value = df_final.loc[country].iloc[-1][topic] 
                    first_value = df_final.loc[country].iloc[1][topic] 
                    value = format(round(last_value, 2),',')
                    delta = '{:.2%}'.format(((last_value-first_value)/first_value))       
                    cols[i].metric(label=topic, value=value, delta=delta)

                
                # Plot the data
                st.line_chart(country_data, use_container_width=True)

    except:
        st.warning("No data found. Select at least 1 parameter and try selecting other parameters.")
except:
    st.warning("No indicators found")
 

 

        













