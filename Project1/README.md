# ![](https://ga-dash.s3.amazonaws.com/production/assets/logo-9f88ae6c9c3871690e33280fcf557f33.png) Project 1: Standardized Test Analysis

### Overview
The Department has commissioned a project to analyze 2019 SAT test performance for the various districts in the state to identify any trends so they can allocate resources more appropriately for 2020.

The SAT and ACT are standardized tests that many colleges and universities in the United States require for their admissions process. This score is used along with other materials such as grade point average (GPA) and essay responses to determine whether or not a potential student will be accepted to the university.

### Problem Statement
The state of California has one of the largest student population in the US, spread over 2,170 school districts. This project aims to identify districts with lowest overall student performance on the 2019 SAT tests so the California Department of Education (CDE) can recommend programs and better allocate resources to such districts in need.

### Information
California is the largest state in the US, with an estimated population of 39.3 million across 58 counties. However, it also has the highest poverty rate of the 50 states, with the high cost of living being one of the key reasons.

An Oxfam Internation report has shown that quality public education is a powerful way of reducing income inequality and creating fairer societies for all. This is in line with the vision and goal of the California Department of Education.

In 2013, California enacted the Local Control Funding Formula (LCFF) to provide more resources to meet the educational needs of lower income students. Local districts are also provided more autonomy and flexibility over how they choose to spend the state funding. However, this alone may not be enough in advancing equity.

### Datasets
* [`sat_2017.csv`](./data/sat_2017.csv): 2017 SAT Scores by State
* [`sat_2018.csv`](./data/sat_2018.csv): 2018 SAT Scores by State
* [`sat_2019.csv`](./data/sat_2019.csv): 2019 SAT Scores by State
* [`sat_2019_ca.csv`](./data/sat_2019_ca.csv): 2019 SAT Scores in California by School
* [`frpm1819.xlsx`](./data/frpm1819.xlsx): 2019 FRPM Student Poverty Data


#### Data Dictionary
|Feature|Type|Dataset|Description|
|---|---|---|---|
|**state**|*object*|sat_combined|One of the 50 states in the United States and the District of Columbia.|
|**participation_\<year\>**|*float*|sat_combined|The overall SAT participation rate for a state in a particular year.<br>(between 0 and 1 where 1 represents 100%)|
|**total_\<year\>**|*int*|sat_combined|The combined score from the two sections of the SAT in a particular year.<br>(between 400 to 1600 where 1600 represents a perfect score)|
|**code**|*int*|ca_sch_info|This 14 digit code is an official, unique identification of a school within California.<br>The first two digits identify the county, the next five digits identify the school district, and the last seven digits identify the school.|
|**school**|*object*|ca_sch_info|School name.|
|**district**|*object*|ca_sch_info|District or Administrative Authority name.|
|**enrolment**|*int*|ca_sch_info|Number of Grade 12 students enrolled as of the start of 2019 school year.|
|**test_taker**|*int*|ca_sch_info|Number of Grade 12 students that participated in the 2019 SAT|
|**pct_benchmark**|*float*|ca_sch_info|Percentage of Grade 12 students that participated in the 2019 SAT and met SAT benchmark.<br>(between 0 and 1 where 1 represents 100%)|
|**pct_test**|*int*|ca_sch_info|Percentage of Grade 12 students that participated in the 2019 SAT divided by enrolment.<br>(between 0 and 1 where 1 represents 100%)|
|**frpm_eligible**|*int*|ca_sch_info|Percentage of students eligible for free or reduced-price meals (FRPM) based on household income or categorical eligibility criteria.<br>(between 0 and 1 where 1 represents 100%)|

### Methodology
Based on data provided by CDE, as well as publicly available information, we analysed the SAT 2019 performance among Grade 12 students across the various school districts, based on number of students that met the SAT benchmark. Schools with 0 enrolment or had SAT participation levels that were too low for benchmarking were omitted from the analysis.<br><br>
The top and bottom performing districts were isolated to identify if there may have been any other factors attributing to their performance.<br><br>
Cross-referencing available data on student poverty, based on unduplicated count of students who are eligible for Free or Reduced-Price Meals (FRPM), we assessed whether there is any correlation between student poverty and performance.

### Key Findings
California was ranked 33rd among all the US states based on SAT mean test score, although the state’s SAT participation rate of 63% was higher than the median of 54%.

Among the 335 school districts analysed, there is a very wide range (0 – 92%) for the percentage of students meeting the SAT benchmark. Most districts achieved between 30% to 62% of their students meeting the SAT benchmark.

The top 5 performing districts achieved close to 90% of test takers meeting the SAT benchmark. At the same time, they have a low FRPM eligibility of less than 10%.
The bottom 5 performing districts have less than 10% of test takers meeting the SAT benchmark. Yet, these districts generally have around 90% FRPM eligibility.

Based on this information, we dived deeper and identified a strong negative correlation (r ~ -0.85) between percentage of students that achieve the SAT benchmark and FRPM eligibility.

Lower income districts may be where aid is required the most.

### Recommendations
- **Review of the School Facility Program (SFP)**<br>
The SFP has been assessed to be relatively regressive, as school facility funding has been shown to be higher in districts with higher median household income and lower in districts with higher concentrations of disadvantaged students. The condition and availablilty of facilities for students would directly impact their ability to study and prepare for tests, especially for lower income students that may not have access to a conducive facility in their homes.<br><br>

- **Increase in teaching staff and resources**<br>
The LCFF has been fully implemented this year, with districts now receiving additional funding based on their share of higher-need students (e.g. low income, English learner and/or foster youth). This better distribution of funds from the state could enable schools to increase their teacher to student ratios, so as to better provide extra support to students preparing for SAT.<br><br>
The department could also consider to implement programs that enable districts to cross share their tecahing resources. This could help to supplement districts or schools with more severe shortage of staff.<br><br>

- **Encourage more students to prepare and participate in the SAT.**<br>
Studies have shown that earning a college degree is one of the best ways to improve one's economic performance. Especially within the lower income districts, students should be encouraged to take full advantage of available fiscal support that helps to offset their exam fees and maximise their attempts at the SAT. Schools should also allocate more resources in helping students better prepare from an earlier grade.
