def get_curing_history_between_dates(press_number, start, end):
    """This function returns a SQL query string which can be used to extract curing process parameter history between 
    the start and end date given as arguments for the given curing press. The dates must be in format YYYY-MM-DD HH:MM:SS and
    press number in format NNNNN
    """

    query = f"""
        SELECT    DateTime, TagName, vValue
        FROM      [Runtime].[dbo].[History]
        WHERE     TagName IN ('{press_number}_BARCODE_LH',
                            '{press_number}_BLADDER_COUNT_LH',
                            '{press_number}_INTERNAL_PRESSURE_LH',
                            '{press_number}_INTERNAL_TEMP_LH',
                            '{press_number}_PLATEN_TEMP_LH',
                            '{press_number}_SQUEEZE_FORCE_LH',
                            '{press_number}_BARCODE_RH',
                            '{press_number}_BLADDER_COUNT_RH',
                            '{press_number}_INTERNAL_PRESSURE_RH',
                            '{press_number}_INTERNAL_TEMP_RH',
                            '{press_number}_PLATEN_TEMP_RH',
                            '{press_number}_SQUEEZE_FORCE_RH',
                            '{press_number}_CURE_TIME',
                            '{press_number}_TOTAL_TIME')
        AND DateTime >= CONVERT(DATETIME, '{start}', 102)
        AND DateTime <= CONVERT(DATETIME, '{end}', 102)
        AND wwResolution = 1000
        AND wwRetrievalMode = N'Cyclic'
    """

    return query

def get_curing_production_info(press_number, start, end):
    """This function returns a SQL query string which can be used to extract information on
    the curing press such as tyre type and bladder count. The dates must be in format YYYY-MM-DD HH:MM:SS and the 
    press number in the format PRESS-NNNNN.
    """

    query = f"""
    SELECT * FROM [CURING].[dbo].[PROD_RPT]
    WHERE Press_No = '{press_number}'
    AND Date_Time >= CONVERT(DATETIME, '{start}', 102)
    AND Date_Time <= CONVERT(DATETIME, '{end}', 102)
    """

    return query


def get_curing_production_info_detailed(press_number, start, end):
    """This function returns a SQL query string which can be used to extract information on
    the curing press such as tyre type and bladder count. The dates must be in format YYYY-MM-DD HH:MM:SS and the 
    press number in the format PRESS-NNNNN.
    """
    # change where statement to where press number is in BLD_Press_No
    query = f"""
    SELECT * FROM [CURING].[dbo].[BLD_RESET_RPT] 
    WHERE BLD_Press_No = '{press_number}'
    AND BLD_Date_Time >= CONVERT(DATETIME, '{start}', 102)
    AND BLD_Date_Time <= CONVERT(DATETIME, '{end}', 102)
    """

    return query


def get_curing_history_between_dates_by_tag_name(start, end, tagname, includeDates):
    if includeDates:
        query = f'''
        SELECT DateTime, vValue
            FROM [Runtime].[dbo].[History]
            where TagName='{tagname}' and
            wwRetrievalMode='Cyclic' and wwResolution=1000
            and DateTime>'{start}' and DateTime<'{end}'
        '''
        return query
    else:
        query = f'''
        SELECT vValue
            FROM [Runtime].[dbo].[History]
            where TagName='{tagname}' and
            wwRetrievalMode='Cyclic' and wwResolution=1000
            and DateTime>'{start}' and DateTime<'{end}'
        '''
        return query

def createBladderCountQuery(press_num, start_date, end_date):
    if len(str(press_num)) == 1:
        press_num = f'0{press_num}'
    return f'''
    SELECT DateTime, vValue
            FROM [Runtime].[dbo].[History]
            where TagName='P91{press_num}_BLADDER_COUNT_LH' and
            wwRetrievalMode='Cyclic' and wwResolution=1000
            and DateTime>'{start_date}' and DateTime<'{end_date}'
    '''


def createPressureQuery(press_num, start_date, end_date):
    if len(str(press_num)) == 1:
        press_num = f'0{press_num}'
    return f'''
    SELECT DateTime, vValue
            FROM [Runtime].[dbo].[History]
            where TagName='P91{press_num}_INTERNAL_PRESSURE_LH' and
            wwRetrievalMode='Cyclic' and wwResolution=1000
            and DateTime>'{start_date}' and DateTime<'{end_date}'
    '''

def backUpPressureQuery(press_num, start_date, end_date):
    if len(str(press_num)) == 1:
        press_num = f'0{press_num}'
    return f'''
        SELECT DateTime, vValue
        FROM [Runtime].[dbo].[History]
        where TagName='P91{press_num}_INTERNAL_PRESSURE' and
        wwRetrievalMode='Cyclic' and wwResolution=1000
        and DateTime>'{start_date}' and DateTime<'{end_date}'
    '''