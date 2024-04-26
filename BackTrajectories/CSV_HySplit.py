import csv
import os

directory = "D:/HySplit/HOUM1/GDAS1/raw"
filebases = [file for file in os.listdir(directory) if file.endswith('.csv')]
files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.csv')]

for file,filebase in zip(files,filebases):
    print(file)
    try:
        with open(str(file), 'r') as infile:
            lines = infile.readlines()

        for i, line in enumerate(lines):
            if len(line.split()) > 8:
                lines = lines[i:]
                break

        output_data = []
        header = ["Number", "run", "year", "month", "day", "hour", "minute", "second", "point", "lat", "long", "altitude", "pressure", "rainfall", "sum_rain", "7mm_removed"]
        output_data.append(header)

        for line in lines:
            components = [component for component in line.split() if component]
            output_data.append(components)

        # Sort the data
        def custom_sort(row):
            try:
                number = int(row[0])
            except ValueError:
                number = int(float(row[0]))
            try:
                point = -int(row[8])
            except ValueError:
                point = -int(float(row[8]))
            return (number, point)

        output_data = sorted(output_data[1:], key=custom_sort)

        accumulated_rainfall = 0
        for row in output_data:
            row.append(0)
            row.append(0)
            try:
                current_rainfall = float(row[header.index('rainfall')])
            except ValueError:
                current_rainfall = 0.0
            accumulated_rainfall += current_rainfall
            row[14] = str(accumulated_rainfall)
            if accumulated_rainfall > 7:
                row[15] = 'NaN'
            else:
                row[15] = str(accumulated_rainfall)

        output_data.insert(0, header) 
        with open('D:/HySplit/HOUM1/GDAS1/'+str(filebase), 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(output_data)
            print("CSV conversion complete!")
    except:
        pass

