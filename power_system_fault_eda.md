Power System Fault Dataset (EDA)

1. Dataset Overview & Key Statistics
- The dataset contains 506 records with 13 features. Fortunately, there are no missing values in any of the columns, indicating a complete dataset.
- Here are the key statistical highlights from the numerical data:
- Voltage: Ranges from 1800 V to 2300 V, with an average of 2049 V.
- Current: Ranges from 180 A to 250 A, with an average of 216 A.
- Power Load: Averages around 50 MW.
- Downtime & Fault Duration: Both average approximately 4.0 hours, with downtime maxing out at 7.0 hours for severe incidents.
- Weather Impact: Average temperatures during faults are 30.1°C, and average wind speeds are 19.7 km/h.
  
2. Visual Analysis
Below is a comprehensive visual breakdown of the dataset.


<img width="1600" height="1461" alt="Code_Generated_Image" src="https://github.com/user-attachments/assets/40044a0f-66ac-4a51-904f-6fa890331ecb" />

3. Key Insights from Visualizations

- Distribution of Fault Types (Top Left): The three main fault types—Transformer Failure, Overheating, and Line Breakage—are almost uniformly distributed across -the dataset, with Transformer Failures being marginally more frequent.
- Weather Conditions vs. Count (Top Right): Rainy and Clear weather conditions see the highest frequency of faults, followed closely by Thunderstorms. Interestingly, Snow and Windstorms account for the lowest volume of recorded faults in this dataset.
- Correlation Heatmap (Middle Left): There is a remarkably low correlation between the numerical features. For example, Voltage and Current have a correlation coefficient of just 0.09. This suggests that faults are not triggered by predictable linear relationships between these specific sensor readings (e.g., a simple voltage drop causing a spike in current), but rather by categorical factors or complex interactions not captured by simple correlation.
- Down Time Distribution (Middle Right): Downtime is broadly distributed across all fault types. While the median downtime is hovering around 4 hours for all categories, Transformer Failures display slightly more variability and can push recovery times toward the 7-hour maximum.
- Component Health at Time of Fault (Bottom Left): Components are fairly evenly split among Normal, Overheated, and Faulty states when a failure occurs. The fact that a significant number of components were classified as "Normal" right before failure might suggest sudden external triggers (like weather or immediate line breakage) rather than gradual degradation.
- Voltage vs. Current Scatter (Bottom Right): Plotting Voltage against Current separated by Fault Type reveals a completely scattered distribution. There are no clear clusters or thresholds (e.g., high current/low voltage zones) that isolate one fault type from another, reinforcing the lack of correlation found in the heatmap.
