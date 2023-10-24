from django.shortcuts import render
from .models import FileUpload
import pandas as pd
from django.http import JsonResponse

# Create your views here.
#format number into thousands, lakhs, crores, etc.
def formatNumber(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T', 'P'][magnitude])
    

def comparsion_percentage(start_date, end_date):
    color = ["#e2929f","#66ceb4"]
    if start_date == 0:
        return "0%" , color[1] , "fa fa-angle-up"
    pct = ((end_date - start_date) / start_date) * 100
    if pct < 0:
        return formatNumber(round(pct, 2)) + '%' , color[0] , "fa fa-angle-down"
    else:
        return formatNumber(round(pct, 2)) + '%' , color[1] , "fa fa-angle-up"



from datetime import timedelta
import pandas as pd

def analysis(data, start_date=None, end_date=None):
    if start_date is None:
        # Set a default start date (e.g., one week ago)
        start_date = pd.to_datetime(data['Timestamp'].max()) - pd.DateOffset(weeks=1)
    else:
        # Convert the provided start date to a datetime object
        start_date = pd.to_datetime(start_date)
    
    if end_date is None:
        # Set a default end date (e.g., the most recent date in the data)
        end_date = pd.to_datetime(data['Timestamp'].max())
    else:
        # Convert the provided end date to a datetime object
        end_date = pd.to_datetime(end_date)

    # Calculate the number of days to compare
    num_days_to_compare = (end_date - start_date).days + 1

    print("Number of days to compare: ", num_days_to_compare)

    # Determine whether to use the default or custom previous date range
    if start_date is not None and end_date is not None:
        previous_start_date = start_date - pd.DateOffset(days=num_days_to_compare)
        previous_end_date = start_date - pd.DateOffset(seconds=1)  # Adjust for 23:59:59 on the previous day
    else:
        # Use the default previous date range behavior
        previous_start_date = start_date - pd.DateOffset(weeks=1)
        previous_end_date = end_date - pd.DateOffset(1)

    print("Previous Start Date: ", previous_start_date)
    print("Previous End Date: ", previous_end_date)

    # Filter the data for the selected date range
    selected_data = data[(data['Timestamp'] >= start_date) & (data['Timestamp'] <= end_date)]
    print("Selected Data: ", selected_data)

    # Filter the data for the previous date range
    previous_data = data[(data['Timestamp'] >= previous_start_date) & (data['Timestamp'] <= previous_end_date)]
    print("Previous Data: ", previous_data)

    # Define the fields to analyze with their corresponding units
    fields_to_analyze = {
        'Wind_Speed (m/s)': 'm/s',
        'Wind_Generation (kW)': 'kW',
        'Wave_Height (m)': 'm',
        'Wave_Generation (kW)': 'kW',
        'Tidal_Current (m/s)': 'm/s',
        'Tidal_Generation (kW)': 'kW',
        'Water_Temperature (°C)': '°C',
        'Total_Renewable_Generation (kW)': 'kW',
    }

    fieldname = {
        'Wind_Speed (m/s)': 'Wind Speed',
        'Wind_Generation (kW)': 'Wind Generation',
        'Wave_Height (m)': 'Wave Height',
        'Wave_Generation (kW)': 'Wave Generation',
        'Tidal_Current (m/s)': 'Tidal Current',
        'Tidal_Generation (kW)': 'Tidal Generation',
        'Water_Temperature (°C)': 'Water Temperature',
        'Total_Renewable_Generation (kW)': 'Total Generation',
    }

    out_data = []

    for field, unit in fields_to_analyze.items():
        # Calculate statistics for the selected and previous date ranges
        avg_selected = selected_data[field].mean()
        min_selected = selected_data[field].min()
        max_selected = selected_data[field].max()

        avg_previous = previous_data[field].mean()
        min_previous = previous_data[field].min()
        max_previous = previous_data[field].max()

        # Calculate the percentage change for each statistic
        avg_change = ((avg_selected - avg_previous) / avg_previous) * 100  if avg_previous != 0 else 0 # Percentage change
        min_change = ((min_selected - min_previous) / min_previous) * 100  if min_previous != 0 else 0
        max_change = ((max_selected - max_previous) / max_previous) * 100  # Percentage change

        avg_change, color, _ = comparsion_percentage(avg_previous, avg_selected)

        # Add the statistics to the output list
        out_data.append({
            'Field': fieldname[field],
            'Units': unit,
            "Average": formatNumber(round(avg_selected, 2)) + ' ' + unit,
            "Minimum": formatNumber(round(min_selected, 2)) + ' ' + unit,
            "Maximum": formatNumber(round(max_selected, 2)) + ' ' + unit,
            "Percentage_Change_Average": avg_change,
            "Percentage_Change_Average_Color": color,
            "Percentage Change (Minimum)": formatNumber(round(min_change, 2)) + '%',
            "Percentage Change (Maximum)": formatNumber(round(max_change, 2)) + '%',
            "Average_Previous_Period": formatNumber(round(avg_previous, 2)) + ' ' + unit,
            "Minimum_Previous_Period": formatNumber(round(min_previous, 2)) + ' ' + unit,
            "Maximum_Previous_Period": formatNumber(round(max_previous, 2)) + ' ' + unit,
        })


    return out_data

















def hourly_line_graph(data, start_date=None, end_date=None):
    if start_date is None:
    # Set a default start date (e.g., one week ago)
        start_date = pd.to_datetime(data['Timestamp'].max()) - pd.DateOffset(weeks=1)
    else:
        # Convert the provided start date to a datetime object
        start_date = pd.to_datetime(start_date)
    
    if end_date is None:
        # Set a default end date (e.g., the most recent date in the data)
        end_date = pd.to_datetime(data['Timestamp'].max())
    else:
        # Convert the provided end date to a datetime object
        end_date = pd.to_datetime(end_date)

    # Calculate the number of days to compare
    num_days_to_compare = (end_date - start_date).days

    # Filter the data for the selected date range
    selected_data = data[(data['Timestamp'] >= start_date) & (data['Timestamp'] <= end_date)]

    # Calculate the previous date range for comparison
    previous_start_date = start_date - pd.DateOffset(days=num_days_to_compare)
    previous_end_date = start_date - pd.DateOffset(days=1)

    # Filter the data for the previous date range
    data = data[(data['Timestamp'] >= start_date) & (data['Timestamp'] <= end_date)]


    # print(data)
    # Prepare the data for 'Wind_Speed (m/s)' column
    hourly_data = data[['Hour', 'Wind_Speed (m/s)']]
    hourly_data = hourly_data.groupby('Hour').mean()
    hourly_data = hourly_data.reset_index()
    hourly_data['Hour'] = hourly_data['Hour'].astype(str)

    # Prepare the data for 'Wave_Height (m)' column
    hourly_data2 = data[['Hour', 'Wave_Height (m)']]
    hourly_data2 = hourly_data2.groupby('Hour').mean()
    hourly_data2 = hourly_data2.reset_index()
    hourly_data2['Hour'] = hourly_data2['Hour'].astype(str)

    # Prepare the data for 'Tidal_Current (m/s)' column
    hourly_data3 = data[['Hour', 'Tidal_Current (m/s)']]
    hourly_data3 = hourly_data3.groupby('Hour').mean()
    hourly_data3 = hourly_data3.reset_index()
    hourly_data3['Hour'] = hourly_data3['Hour'].astype(str)

    # Prepare the data for 'Water_Temperature (°C)' column
    hourly_data4 = data[['Hour', 'Water_Temperature (°C)']]
    hourly_data4 = hourly_data4.groupby('Hour').mean()
    hourly_data4 = hourly_data4.reset_index()
    hourly_data4['Hour'] = hourly_data4['Hour'].astype(str)

    # Prepare the data for 'Wind_Generation (kW)' column
    hourly_data5 = data[['Hour', 'Wind_Generation (kW)']]
    hourly_data5 = hourly_data5.groupby('Hour').sum()
    hourly_data5 = hourly_data5.reset_index()
    hourly_data5['Hour'] = hourly_data5['Hour'].astype(str)

    # Prepare the data for 'Wave_Generation (kW)' column
    hourly_data6 = data[['Hour', 'Wave_Generation (kW)']]
    hourly_data6 = hourly_data6.groupby('Hour').sum()
    hourly_data6 = hourly_data6.reset_index()
    hourly_data6['Hour'] = hourly_data6['Hour'].astype(str)

    # Prepare the data for 'Tidal_Generation (kW)' column
    hourly_data7 = data[['Hour', 'Tidal_Generation (kW)']]
    hourly_data7 = hourly_data7.groupby('Hour').sum()
    hourly_data7 = hourly_data7.reset_index()
    hourly_data7['Hour'] = hourly_data7['Hour'].astype(str)

    # Prepare the data for 'Total_Renewable_Generation (kW)' column
    hourly_data8 = data[['Hour', 'Total_Renewable_Generation (kW)']]
    hourly_data8 = hourly_data8.groupby('Hour').sum()
    hourly_data8 = hourly_data8.reset_index()
    hourly_data8['Hour'] = hourly_data8['Hour'].astype(str)

    #chart labels and values for 'Wind_Speed (m/s)' column
    chart_labels = hourly_data['Hour'].tolist()
    chart_values = hourly_data['Wind_Speed (m/s)'].tolist()

    #chart labels and values for 'Wave_Height (m)' column
    chart_labels2 = hourly_data2['Hour'].tolist()
    chart_values2 = hourly_data2['Wave_Height (m)'].tolist()

    #chart labels and values for 'Tidal_Current (m/s)' column
    chart_labels3 = hourly_data3['Hour'].tolist()
    chart_values3 = hourly_data3['Tidal_Current (m/s)'].tolist()

    #chart labels and values for 'Water_Temperature (°C)' column
    chart_labels4 = hourly_data4['Hour'].tolist()
    chart_values4 = hourly_data4['Water_Temperature (°C)'].tolist()

    #chart labels and values for 'Wind_Generation (kW)' column
    chart_labels5 = hourly_data5['Hour'].tolist()
    chart_values5 = hourly_data5['Wind_Generation (kW)'].tolist()

    #chart labels and values for 'Wave_Generation (kW)' column
    chart_labels6 = hourly_data6['Hour'].tolist()
    chart_values6 = hourly_data6['Wave_Generation (kW)'].tolist()

    #chart labels and values for 'Tidal_Generation (kW)' column
    chart_labels7 = hourly_data7['Hour'].tolist()
    chart_values7 = hourly_data7['Tidal_Generation (kW)'].tolist()

    #chart labels and values for 'Total_Renewable_Generation (kW)' column
    chart_labels8 = hourly_data8['Hour'].tolist()
    chart_values8 = hourly_data8['Total_Renewable_Generation (kW)'].tolist()

    chart_data = {
        'labels': chart_labels,
        'values': chart_values,
    }

    chart_data2 = {
        'labels': chart_labels2,
        'values': chart_values2,
    }

    chart_data3 = {
        'labels': chart_labels3,
        'values': chart_values3,
    }

    chart_data4 = {
        'labels': chart_labels4,
        'values': chart_values4,
    }

    chart_data5 = {
        'labels': chart_labels5,
        'values': chart_values5,
    }

    chart_data6 = {
        'labels': chart_labels6,
        'values': chart_values6,
    }

    chart_data7 = {
        'labels': chart_labels7,
        'values': chart_values7,
    }

    chart_data8 = {
        'labels': chart_labels8,
        'values': [round(value, 0) for value in chart_values8],
    }

    return chart_data, chart_data2, chart_data3, chart_data4, chart_data5, chart_data6, chart_data7, chart_data8





import pandas as pd
import numpy as np



def convert_units(value, unit):
    # Define your unit conversion logic here
    if pd.notna(value):
        if unit == 'kW':
            formatted_value = f"{round(value)} kW"
        elif unit == '%':
            formatted_value = f"{round(value)}%"
        else:
            formatted_value = f"{value} {unit}"
        return formatted_value
    else:
        # Handle the case when 'value' is NaN
        return "N/A"  # You can replace "N/A" with any default value you prefer



def heatmap_data(data, start_date, end_date):
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    data['Hour'] = data['Timestamp'].dt.hour
    data['Date'] = data['Timestamp'].dt.date
    filtered_df = data[(data['Timestamp'] >= start_date) & (data['Timestamp'] <= end_date)]
    
    def legends_data(heatmap_color):
        legends = {
            'c1': "<10%",
            'c2': "10-20%",
            'c3': "20-30%",
        }

        legends_array = []

        for key, value in legends.items():
            legends_array.append({
                'color': heatmap_color[key],
                'label': value
            })

        return legends_array

    border_dict = {
        "hour": {
            "high": ["red", "solid"],
            "low": ["red", "dotted"]
        },
        "day": {
            "high": ["purple", "solid"],
            "low": ["purple", "dotted"]
        }
    }

    pivot_df = filtered_df.pivot_table(index='Date', columns='Hour', values='Total_Renewable_Generation (kW)', aggfunc='sum')
    pivot_data1 = filtered_df.pivot_table(index='Date', columns='Hour', values='Wind_Generation (kW)', aggfunc='sum')
    pivot_data2 = filtered_df.pivot_table(index='Date', columns='Hour', values='Wave_Generation (kW)', aggfunc='sum')
    pivot_data3 = filtered_df.pivot_table(index='Date', columns='Hour', values='Tidal_Generation (kW)', aggfunc='sum')

    pivot_df = pivot_df.fillna(0)
    # Calculate the mean and standard deviation for each row
    row_means = pivot_df.mean(axis=1)
    row_stds = pivot_df.std(axis=1)

    # Calculate the upper and lower anomaly thresholds (2 * std from the mean)
    upper_threshold = row_means + row_stds * 2
    lower_threshold = row_means - row_stds * 2

    # Identify rows with values above or below the thresholds as anomalies
    pivot_array = pivot_df.to_numpy()
    upper_threshold_array = upper_threshold.to_numpy()[:, np.newaxis]
    lower_threshold_array = lower_threshold.to_numpy()[:, np.newaxis]

    high_anomaly = (pivot_array > upper_threshold_array)
    low_anomaly = (pivot_array < lower_threshold_array)

    # Calculate the total range
    total_max = pivot_df.sum(axis=1).max()  # Find the maximum total value across all days
    total_min = pivot_df.sum(axis=1).min()

    print("Total Max: ", total_max)
    print("Total Min: ", total_min)

    result = []

    for date in pivot_df.index:
        date_data = {
            'Date': date,
            'Data': [],
            'Anomaly': False  # Initialize 'Anomaly' as False
        }

        # Calculate the Total for the X axis
        total_x_axis = pivot_df.loc[date].sum()
        date_data['Total'] = convert_units(total_x_axis, 'kW')

        high_anomaly_flag = False
        low_anomaly_flag = False

        for hour in pivot_df.columns:
            hour_data = {
                'Hour': hour,
                'Value': convert_units(pivot_df.loc[date, hour], 'kW'),
                'high_Anomaly': np.any(high_anomaly[pivot_df.index == date, pivot_df.columns == hour][0]),
                'low_Anomaly': np.all(low_anomaly[pivot_df.index == date, pivot_df.columns == hour][0]),
                'WindData': convert_units(pivot_data1.loc[date, hour], 'kW'),  # Add wind data
                'TidalData': convert_units(pivot_data2.loc[date, hour], 'kW'),  # Add tidal data
                'WaveData': convert_units(pivot_data3.loc[date, hour], 'kW')  # Add wave data
            }

            if hour_data['high_Anomaly']:
                high_anomaly_flag = True
            if hour_data['low_Anomaly']:
                low_anomaly_flag = True

            date_data['Data'].append(hour_data)

        # Determine border color and style based on the anomaly status of the row
        if high_anomaly_flag and low_anomaly_flag:
            date_data['BorderColor'] = border_dict['hour']['high'][0]
            date_data['BorderStyle'] = border_dict['hour']['high'][1]
        elif high_anomaly_flag:
            date_data['BorderColor'] = border_dict['hour']['high'][0]
            date_data['BorderStyle'] = border_dict['hour']['high'][1]
        elif low_anomaly_flag:
            date_data['BorderColor'] = border_dict['hour']['low'][0]
            date_data['BorderStyle'] = border_dict['hour']['low'][1]
        else:
            date_data['BorderColor'] = ''  # No anomaly, so no border color
            date_data['BorderStyle'] = ''

        # Define a small tolerance for comparison
        tolerance = 1e-6

        # Check if total_x_axis is within the tolerance range of total_max or total_min
        if abs(total_x_axis - total_max) < tolerance:
            date_data['TotalBorderColor'] = border_dict['day']['high'][0]
            date_data['TotalBorderStyle'] = border_dict['day']['high'][1]
        elif abs(total_x_axis - total_min) < tolerance:
            date_data['TotalBorderColor'] = border_dict['day']['low'][0]
            date_data['TotalBorderStyle'] = border_dict['day']['low'][1]
        else:
            date_data['TotalBorderColor'] = ''
            date_data['TotalBorderStyle'] = ''

        result.append(date_data)

    return result




from datetime import datetime, timedelta

def heatmap_analysis(request):
    file = FileUpload.objects.all()
    data = pd.read_csv(file[0].file)
    current_date = datetime.now()
    start_date = current_date - timedelta(days=7)
    end_date = current_date - timedelta(days=0)
    print(start_date)
    print(end_date)
    heatmap_df = heatmap_data(data, '2023-10-16 00:00:00', '2023-10-22 23:59:59')
    return heatmap_df
def get_data():
    file = FileUpload.objects.filter().first()
    data = pd.read_csv(file.file)
    return data

# def filter_data(request):
#     start_date = request.POST.get('start_date')
#     end_date = request.POST.get('end_date')
#     print(start_date)
#     print(end_date)

#     if start_date and end_date is not None:
#         # Perform filtering based on start_date and end_date
#         file = FileUpload.objects.all()
#         data = pd.read_csv(file[0].file)
#         data['Timestamp'] = pd.to_datetime(data['Timestamp'])
#         data['Hour'] = data['Timestamp'].dt.hour
#         data['Date'] = data['Timestamp'].dt.date

#         filtered_df = (data['Timestamp'].dt.date >= pd.to_datetime(start_date).date()) & (data['Timestamp'].dt.date <= pd.to_datetime(end_date).date())
#         filtered_data = data[filtered_df]
#         print(data)
        
#         # filtered_data = data[filtered_df]
        
        
#     else:
#         # If no dates are selected, show all data
#         file = FileUpload.objects.all()
#         data = pd.read_csv(file[0].file)
#         filtered_data = data
      
#         # print(filtered_df)
#     return filtered_data

import pandas as pd





def filter_data(request):
    import datetime

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    if start_date and end_date is not None:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    else:
        # Get the current date and time
        now = datetime.datetime.now()

        # Set the start_date and end_date variables to the current date with a time of 00:00:00 and cuurent time 
        start_date = now.date()
        end_date = now

    # Format the dates to include the time
    start_date_formatted = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date_formatted = end_date.strftime('%Y-%m-%d %H:%M:%S')

    return start_date_formatted, end_date_formatted














    
    
    

def home(request):
    # data = filter_data(request)

    # print(data)
    # file = FileUpload.objects.all()
    # data = pd.read_csv(file[0].file)
    data = pd.read_csv("Analysis\static\data.csv")
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    data['Hour'] = data['Timestamp'].dt.hour
    data['Date'] = data['Timestamp'].dt.date
    filter_date = filter_data(request)
    statistics = analysis(data, filter_date[0], filter_date[1])
    print(statistics)
    chart_data = hourly_line_graph(data, filter_date[0], filter_date[1])
    wind_speed = chart_data[0]
    wave_height = chart_data[1]
    tidal_current = chart_data[2]
    water_temperature = chart_data[3]
    wind_generation = chart_data[4]
    wave_generation = chart_data[5]
    tidal_generation = chart_data[6]
    total_generation = chart_data[7]
    heatmap_insights = heatmap_analysis(request)

    

    # heatmap_analysis = heatmap_data(data,'2023-10-10 00:00:00', '2023-10-17 23:59:59')
  
    return render(request, "home.html", {"statistics": statistics, "chart_data": wind_speed, "chart_data2": wave_height, "chart_data3": tidal_current, "chart_data4": water_temperature, "chart_data5": wind_generation, "chart_data6": wave_generation, "chart_data7": tidal_generation, "chart_data8": total_generation , "heatmap_data": heatmap_insights, "start_date": filter_date[0], "end_date": filter_date[1]})