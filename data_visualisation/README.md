# Main PA Workflow 
Each Python notebook is numbered in order, and has a breif description at the top of each notebook to explain the purpose of the code. Common funcitons are seprated and collated into defined classes in helpers.py (```TBM``` for TBM utility functions, ```SQL_TBM_query``` for Calling TBM SQL Server, ```bcolors``` for printing colours, ```Feature_Selection```, and ```Data_Functions```). object instances of these classes are created at the top of the notebooks. In general:

0. Call Data from SQL Server and save to local .pkl. Filter by TBM 1 and time span ('2022/02/01', '2022/04/01')
1. Join data for a complete dataset
2. Initial drop duplicates, Filter (by Equipment ID: TBM 1 and remove Trial Recipes), key generation, cycle time generation and EDA
3. Left Merge Alarm mapping and Alarm hisroy on Created Key.
4. Alarm Discovery: Alarm to GT allocation: Calculate PAAP start and finish times if needed. Do NOT Filter alarms by Type e.g.  FF, CF and MC, assin name in#dexes. Link these alarm name indexes that are occurring for the same green tire at those times identified as PA. Create GT to Alarm Index Mapping.
5. One Hot encode Alarm Indexes before we carry out feature selction to see relevant alarms.
6. Feature selection: Initial Filter using statistical univariate filter methods. 
7. Feature selection: Narrow down using ML Models. Identify which steps are posing the issue (i.e. is it sidewall, inner liner, is it transport time etc.)
8. View Selected Alarms and Discuss with Operations Team
9. With an Alarm, classifed the GT's which had this alarm (allocated on entire start/produced time instead). We then join the alarm mapping with alarm history and join this table to the GT's in production data and perform counts and validate apparent erroneous durations. Sort the alarms into 'Errors' and 'Valid'. i.e. Alarm Duration < PAAP & Cycle Time is a Valid Scenario. Errors are EITHER Alarm Duration > PAAP OR Alarm Duration > PAAP & Cycle Time
    Have decided to take the subset of Duration < Cycle Time as GT's that make feasible sense.
10. Carry out More detailed analysis to gauge size of the prize. Here we have taken the 95th percentile of cycle times to remove outlier GT's. We had already previously removed Trial Recipes. Then:

    •	Analyse if they have taken each alarm once or twice. Need to sort by Null i.e. (Mahesh is handling)

    •	Count of 'Valid' Alarms. Calculate percentage out of all GT's Produced 

    •	Recalculate time saving per cycle time for start_time and ProducedOn Time. i.e. Redo Allocation of GT's

    •	See Date dependence of PA alarms. (one day may be particularly bad due to converyor belt issue, or Recipe   inherent etc.) (Automation Conveyor may have an issue on one particylar day). See if Date Dependent

11. Continuation of 10, to carry out more detailed analysis to gauge size of the prize

    •	See correlation coeff with Duration and Cycle time/PAAP time

    •	General Analysis of PAAP Times

    •	Check next and previous tyres for the Errors.   

    •	Investigate for other TBM's

12.	Plot these comparisons and highlight your observations. Add any other analysis as we go along: 

    •	Total CT variation - m/c wise

    •	CT variation - application wise

    •	Total CT variation - Diameter wise

    •	Total CT variation - Recipe wise

    •	Number of changeovers - m/c wise 

    •	Number of changeovers - due to recipe, due to diameter

13. PREASSEMBLY LENGTH NOT CORRECT Alarm investigation. Alarm Duration Distribution, as this alarms Duration IS linked to Machine Stoppage Time. GT allocation, and Alarm duration vs PAAP time check. All seems okay, as vast majority are Scenario 1:

    • Scenario 1 : Alarm Duration < PAAP Times

    • Scenario 2 : Alarm Duration > PAAP Times 

    • Scenario 3 : Alarm Duration > PAAP Times & Cycle Time

14. Plot Probablity Density of 3 Scenarios, KDE Distribution of Cycle Times (not filtered by SKU), and cycle time percentiles. Compare GT's before and after Outlier removal at 85th percentile, and investigate effect on PAAP time. Conculsion was:

    Projected reduction in average Cycle Time If Alarm was non-existent: 0.683s

    Projected reduction in average PAAP Time If Alarm was non-existent: 0.499s
15. 14 workflow but for PAAP length out of tolerance
16. Take the GT's which were Scenario 1, and the Cycle times for all other steps (not just PAAP) and calculate z-scores for each column for each GT. This way, we can eliminate GT's which had outlier times in any other step than PAAP i.e. Remove GT's which had unusual steps other than PAAP. Plot Cycle Time of PREASSEMBLY LENGTH NOT CORRECT GT's after removal of non-PAAP step Outliers. Validate that longer cycle times were due to PAAP. 

