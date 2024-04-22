import pandas as pd
import matplotlib.pyplot as plt

file_path = "/Users/coz/Downloads/ExINPNSA_20211019_20240101_L1_MERGEDv3.xlsx"

try:
    # Making Pandas Read Excel file 
    df = pd.read_excel(file_path)

    # Select specific columns
    selected_columns = ["T_min", "time_reference", "INP_Conc", "Flag"]
    df_selected = df.loc[:, selected_columns]
    
    # Filter out the flagged data
    #df_filtered = df_selected[df_selected["Flag"].isnull()]
    
    #All data including flag and not flag
    #df_filtered = df_selected
    
    # Only flagged data
    df_filtered = df_selected[df_selected["Flag"].notnull()]

    # Plotting
    plt.figure(figsize=(10, 6))

    # Plot Time reference on the x-axis and INP_Conc on the y-axis
    plt.scatter(df_filtered["time_reference"], df_filtered["INP_Conc"], c=df_filtered["T_min"], cmap='coolwarm', marker='o', label='INP_Conc', vmin=-35, vmax=-10, s=3)
    plt.yscale('log')  # Setting y-axis to logarithmic scale
    plt.xlabel('Time reference')
    plt.ylabel('INP_Conc')
    plt.title('INP Concentration over Time')
    plt.colorbar(label='Temperature (°C)')
    plt.grid(True)
    plt.legend()

    # Set x-axis limits
    start_date = pd.to_datetime("2021-10-19")
    end_date = pd.to_datetime("2024-01-01")
    plt.xlim(start_date, end_date)

    plt.show()
    
except FileNotFoundError:
    print(f"File '{file_path}' not found.")
