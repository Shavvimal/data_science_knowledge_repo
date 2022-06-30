from pickletools import float8
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import scipy.stats as sp
from collections import Counter
from sklearn.preprocessing import MultiLabelBinarizer


# Hide the false positive warning 
pd.options.mode.chained_assignment = None  # default='warn'

class bcolors:
    '''Print colours. Use example: f'{bcolors.OKGREEN}coloured text' '''
    def __init__(self):
        self.HEADER = '\033[95m'
        self.BLUE = '\033[94m'
        self.CYAN = '\033[96m'
        self.GREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'

    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def printh(self, str: str):
        print(f'{self.HEADER}{str}')
    
    def printb(self, str: str):
        print(f'{self.BLUE}{str}')
    
    def printc(self, str: str):
        print(f'{self.CYAN}{str}')
    
    def printg(self, str: str):
        print(f'{self.GREEN}{str}')
    
    def printw(self, str: str):
        print(f'{self.WARNING}{str}')
    
    def printf(self, str: str):
        print(f'{self.FAIL}{str}')
    
    def printn(self, str: str):
        print(f'{self.ENDC}{str}')
    
    def printbb(self, str: str):
        print(f'{self.BOLD}{str}')

    def printu(self, str: str):
        print(f'{self.UNDERLINE}{str}')
    
    def gv(self, str: str, val):
        self.printg(f'{str} {self.ENDC}{val}')

class SQL_TBM_query:
    '''Class for Calling TBM SQL Server'''
    def __init__(self, date_start, date_end):
        self.date_start = date_start
        self.date_end = date_end

    def get_TBM_data_to_pkl(self, filter: bool = False, TBM_querey_addon: str = ''):
        con = pyodbc.connect("Driver={SQL Server};server=172.25.200.107;database=MHSHistory;uid=MHSANLISYS;pwd=analisyspassword")
        TBM_querey_addon = f'\'{TBM_querey_addon}\''
        sql = f"select * from TBM_PRODUCTION_DATA where ProducedOn > '{self.date_start} 06:00:00.000 ' and ProducedOn < '{self.date_end} 06:00:00.000' {f'and EquipmentID = {TBM_querey_addon}' if filter else ''}"	
        print(f'{bcolors.CYAN}SQL Querey: \n{bcolors.ENDC}{sql}')
        df100 = pd.read_sql (sql,con)
        df100.sort_values(by='ProducedOn', ascending=True, inplace=True)
        df100.to_pickle("./pkl/tbm_data.pkl")
        print(f'{bcolors.GREEN}Successfully Created: tbm_data.pkl')

    def get_TBM_alarm_to_pkl(self):
        con = pyodbc.connect("Driver={SQL Server};server=172.25.200.107;database=MHSHistory;uid=MHSANLISYS;pwd=analisyspassword")
        sql = f"SELECT HistoryMessageID, MessageID, TimeStamp, Duration, EquipmentID FROM [TBMHistory].[dbo].[MESSAGE_HISTORY] where TimeStamp>'{self.date_start}' and TimeStamp<'{self.date_end}' and Duration is not NULL"	
        print(f'{bcolors.CYAN}SQL Querey: \n{bcolors.ENDC}{sql}')
        df100 = pd.read_sql (sql,con)
        df100.to_pickle("./pkl/tbm_alarm.pkl")
        print(f'{bcolors.GREEN}Successfully Created: tbm_alarm.pkl')

    def get_alarm_Map_to_pkl(self):
        con = pyodbc.connect("Driver={SQL Server};server=172.25.200.107;database=MHSHistory;uid=MHSANLISYS;pwd=analisyspassword")
        sql = f"SELECT DISTINCT MessageID, PlcNr, Type, Name, Solution, EquipmentID FROM [TBMHistory].[dbo].[MESSAGE]"	
        print(f'{bcolors.CYAN}SQL Querey: \n{bcolors.ENDC}{sql}')
        df100 = pd.read_sql (sql,con)
        df100.to_pickle("./pkl/alarm_map.pkl")
        print(f'{bcolors.GREEN}Successfully Created: alarm_map.pkl')

class TBM:
    '''TBM utility functions'''

    def rename_df(self, df):
        df_renamed = df.rename(columns={'UserName' : 'Name_of_Active_Operator', 
        # 'RecipeName' : 'Name_of_Active_Recipe', 
        'VST_VHMC_MES_PRODUCTION_ORDER' : 'Name_of_Active_Production_Order', 
        'VDT_VHMC_MES_DATE_TIME_STAMP' : 'date/time', 
        'VST_VHMC_MES_GT_BARCODE' : 'Barcode_on_build_tire', 
        'VST_VHMC_MES_GT_CODE' : 'GT_Code_of_the_built_tire', 
        'VRL_VHMC_MES_GT_ACTUAL_WEIGHT' : 'Actual_Weight_of_GT_(written_by_MES)', 
        'VRL_VHMC_MES_GT_MIN_WEIGHT' : 'Minimum_allowed_Weight_of_GT', 
        'VRL_VHMC_MES_GT_MAX_WEIGHT' : 'Maximum_allowed_Weight_of_GT', 
        'VST_VHMC_MES_1BLO_IDENTIFIER' : 'Material_Code_of_Breaker_1_Material', 
        'VST_VHMC_MES_1BLO_CART_IDENTIFIER' : 'Cartridge_RFID_of_Breaker_1_Material_(_C:ette_RFID_Code)', 
        'VIN_VHMC_MES_1BLO_MATERIAL_STATUS' : 'Material_Status_of_Breaker_1_Material_(0_NOT_OK_1_OK)', 
        'VRL_VHMC_MES_1BCU_TEMP_ME:URED' : 'Breaker_1_Cutter_Temperature', 
        'VRL_VHMC_MES_1BCU_TEMP_SETPOINT' : 'Breaker_1_Measured_Width_by_VVS_(_by_camera)', 
        'VRL_VHMC_MES_BR1_WIDTH_ME:URED' : 'Breaker_1_Measured_Width_by_VVS(_by_camera)', 
        'VRL_VHMC_MES_BR1_WIDTH_SETPOINT' : 'Breaker_1_Width_Setpoint', 
        'VRL_VHMC_MES_BR1_LENGTH_ME:URED' : 'Breaker_1_Me:ured_Length_by_VVS(_by_camera)', 
        'VRL_VHMC_MES_BR1_LENGTH_SETPOINT' : 'Breaker_1_Length_Setpoint', 
        'VRL_VHMC_MES_BR1_LE_ANGLE_ME:URED' : 'Breaker_1_Me:ured_LE_Angle_by_VVS(_by_camera)', 
        'VRL_VHMC_MES_BR1_TE_ANGLE_ME:URED' : 'Breaker_1_Me:ured_TE_Angle_by_VVS(_by_camera)', 
        'VRL_VHMC_MES_BR1_ANGLE_SETPOINT' : 'Breaker_1_Angle_Setpoint', 
        'VRL_VHMC_MES_BR1_POS_WIDTH_OK' : 'Breaker_1_Pos_Width_OK_by_VVS(_by_camera)', 
        'VRL_VHMC_MES_BR1_ME:_LENGTH_AXIS' : 'Breaker_1_Me:ured_Length_by_Axis', 
        'VRL_VHMC_MES_BR1_USE_VVS_LENGTH' : 'Breaker_1_Use_VVS_Length_length_for_stretching', 
        'VRL_VHMC_MES_BR1_SPOT_POSITION' : 'Breaker_1_Spot_Position', 
        'VRL_VHMC_MES_1BPR_CYCLE_HOMING' : 'Breaker_1_Cycle_time_Homing', 
        'VRL_VHMC_MES_1BPR_CYCLE_LM' : 'Breaker_1_Cycle_time_Length_Me:ure', 
        'VRL_VHMC_MES_1BPR_CYCLE_CUTTING' : 'Breaker_1_Cycle_time_Cutting', 
        'VRL_VHMC_MES_1BPR_CYCLE_TRANSPORT' : 'Breaker_1_Cycle_time_Transport', 
        'VRL_VHMC_MES_1BPR_CYCLE_CART_EMPTY' : 'Breaker_1_Cycle_time_Cart_Empty_(c:ette_empty)', 
        'VRL_VHMC_MES_1BPR_CYCLE_MOVE_TO_GAP' : 'Breaker_1_Cycle_time_Move_to_Gap', 
        'VRL_VHMC_MES_1BPR_CYCLE_REMOVE' : 'Breaker_1_Cycle_time_Remove', 
        'VRL_VHMC_MES_1BPR_CYCLE_MAT_AT_FRONT' : 'Breaker_1_Cycle_time_Mat_At_Front', 
        'VRL_VHMC_MES_1BPR_CYCLE_TOTAL' : 'Breaker_1_Cycle_time_Total', 
        'VRL_VHMC_MES_1BAP_BODY_MIN_OFF_CENTER' : 'Breaker_1_BTMO_Me:ured_minimum_Body_Offcenter', 
        'VRL_VHMC_MES_1BAP_BODY_MAX_OFF_CENTER' : 'Breaker_1_BTMO_Me:ured_maximum_Body_Offcenter', 
        'VRL_VHMC_MES_1BAP_BODY_AVG_OFF_CENTER' : 'Breaker_1_BTMO_Me:ured_average_Body_Offcenter', 
        'VRL_VHMC_MES_1BAP_BODY_MIN_WIDTH' : 'Breaker_1_BTMO_Me:ured_minimum_Body_Width', 
        'VRL_VHMC_MES_1BAP_BODY_MAX_WIDTH' : 'Breaker_1_BTMO_Me:ured_maximum_Body_Width', 
        'VRL_VHMC_MES_1BAP_BODY_AVERAGE_WIDTH' : 'Breaker_1_BTMO_Me:ured_average_Body_Width', 
        'VRL_VHMC_MES_1BAP_SPLICE_MIN_OFF_CENTER' : 'Breaker_1_BTMO_Me:ured_minimum_Splice_Offcenter', 
        'VRL_VHMC_MES_1BAP_SPLICE_MAX_OFF_CENTER' : 'Breaker_1_BTMO_Me:ured_maximum_Splice_Offcenter', 
        'VRL_VHMC_MES_1BAP_SPLICE_AVG_OFF_CENTER' : 'Breaker_1_BTMO_Me:ured_average_Splice_Offcenter', 
        'VRL_VHMC_MES_1BAP_SPLICE_MIN_WIDTH' : 'Breaker_1_BTMO_Me:ured_minimum_Splice_Width', 
        'VRL_VHMC_MES_1BAP_SPLICE_MAX_WIDTH' : 'Breaker_1_BTMO_Me:ured_maximum_Splice_Width', 
        'VRL_VHMC_MES_1BAP_SPLICE_AVERAGE_WIDTH' : 'Breaker_1_BTMO_Me:ured_average_Splice_Width', 
        'VRL_VHMC_MES_1BAP_SPLICE_AVG_OPEN_OVER_L' : 'Breaker_1_BTMO_Me:ured_average_Splice_Open_Overlap_Left', 
        'VRL_VHMC_MES_1BAP_SPLICE_AVG_OPEN_OVER_M' : 'Breaker_1_BTMO_Me:ured_average_Splice_Open_Overlap_Middle', 
        'VRL_VHMC_MES_1BAP_SPLICE_AVG_OPEN_OVER_R' : 'Breaker_1_BTMO_Me:ured_average_Splice_Open_Overlap_Right', 
        'VST_VHMC_MES_2BLO_IDENTIFIER' : 'Material_Code_of_Breaker_Material', 
        'VST_VHMC_MES_2BLO_CART_IDENTIFIER' : 'Cartridge_RFID_of_Breaker_2_Material_(C:ette_RFID_code)', 
        'VIN_VHMC_MES_2BLO_MATERIAL_STATUS' : 'Material_Status_of_Breaker_2_Material_(0_=_NOT_OK,_1_=_OK)', 
        'VRL_VHMC_MES_2BCU_TEMP_ME:URED' : 'Breaker_2_Cutter_Temperature', 
        'VRL_VHMC_MES_2BCU_TEMP_SETPOINT' : 'Breaker_2_Me:ured_Width_by_VVS(_by_camera)', 
        'VRL_VHMC_MES_BR2_WIDTH_ME:URED' : 'Breaker_2_Me:ured_Width_by_VVS(_by_camera)', 
        'VRL_VHMC_MES_BR2_WIDTH_SETPOINT' : 'Breaker_2_Width_Setpoint', 
        'VRL_VHMC_MES_BR2_LENGTH_ME:URED' : 'Breaker_2_Me:ured_Length_by_VVS(_by_camera)', 
        'VRL_VHMC_MES_BR2_LENGTH_SETPOINT' : 'Breaker_2_Length_Setpoint', 
        'VRL_VHMC_MES_BR2_LE_ANGLE_ME:URED' : 'Breaker_2_Me:ured_LE_Angle_by_VVS(_by_camera)', 
        'VRL_VHMC_MES_BR2_TE_ANGLE_ME:URED' : 'Breaker_2_Me:ured_TE_Angle_by_VVS(_by_camera)', 
        'VRL_VHMC_MES_BR2_ANGLE_SETPOINT' : 'Breaker_2_Angle_Setpoint', 
        'VRL_VHMC_MES_BR2_POS_WIDTH_OK' : 'Breaker_2_Pos_Width_OK_by_VVS(_by_camera)', 
        'VRL_VHMC_MES_BR2_ME:_LENGTH_AXIS' : 'Breaker_2_Me:ured_Length_by_Axis', 
        'VRL_VHMC_MES_BR2_USE_VVS_LENGTH' : 'Breaker_2_Use_VVS_Length_length_for_stretching', 
        'VRL_VHMC_MES_BR2_SPOT_POSITION' : 'Breaker_2_Spot_Position', 
        'VRL_VHMC_MES_2BPR_CYCLE_HOMING' : 'Breaker_2_Cycle_time_Homing', 
        'VRL_VHMC_MES_2BPR_CYCLE_LM' : 'Breaker_2_Cycle_time_Length_Me:ure', 
        'VRL_VHMC_MES_2BPR_CYCLE_CUTTING' : 'Breaker_2_Cycle_time_Cutting', 
        'VRL_VHMC_MES_2BPR_CYCLE_TRANSPORT' : 'Breaker_2_Cycle_time_Transport', 
        'VRL_VHMC_MES_2BPR_CYCLE_CART_EMPTY' : 'Breaker_2_Cycle_time_Cart_Empty_(c:ette_empty)', 
        'VRL_VHMC_MES_2BPR_CYCLE_MOVE_TO_GAP' : 'Breaker_2_Cycle_time_Move_to_Gap', 
        'VRL_VHMC_MES_2BPR_CYCLE_REMOVE' : 'Breaker_2_Cycle_time_Remove', 
        'VRL_VHMC_MES_2BPR_CYCLE_MAT_AT_FRONT' : 'Breaker_2_Cycle_time_Mat_At_Front', 
        'VRL_VHMC_MES_2BPR_CYCLE_TOTAL' : 'Breaker_2_Cycle_time_Total', 
        'VRL_VHMC_MES_2BAP_BODY_MIN_OFF_CENTER' : 'Breaker_2_BTMO_Me:ured_minimum_Body_Offcenter', 
        'VRL_VHMC_MES_2BAP_BODY_MAX_OFF_CENTER' : 'Breaker_2_BTMO_Me:ured_maximum_Body_Offcenter', 
        'VRL_VHMC_MES_2BAP_BODY_AVG_OFF_CENTER' : 'Breaker_2_BTMO_Me:ured_average_Body_Offcenter', 
        'VRL_VHMC_MES_2BAP_BODY_MIN_WIDTH' : 'Breaker_2_BTMO_Me:ured_minimum_Body_Width', 
        'VRL_VHMC_MES_2BAP_BODY_MAX_WIDTH' : '_Breaker_2_BTMO_Me:ured_maximum_Body_Width', 
        'VRL_VHMC_MES_2BAP_BODY_AVERAGE_WIDTH' : 'Breaker_2_BTMO_Me:ured_average_Body_Width_', 
        'VRL_VHMC_MES_2BAP_SPLICE_MIN_OFF_CENTER' : 'Breaker_2_BTMO_Me:ured_minimum_Splice_Offcenter', 
        'VRL_VHMC_MES_2BAP_SPLICE_MAX_OFF_CENTER' : 'Breaker_2_BTMO_Me:ured_maximum_Splice_Offcenter', 
        'VRL_VHMC_MES_2BAP_SPLICE_AVG_OFF_CENTER' : 'Breaker_2_BTMO_Me:ured_average_Splice_Offcenter', 
        'VRL_VHMC_MES_2BAP_SPLICE_MIN_WIDTH' : 'Breaker_2_BTMO_Me:ured_minimum_Splice_Width_', 
        'VRL_VHMC_MES_2BAP_SPLICE_MAX_WIDTH' : 'Breaker_2_BTMO_Me:ured_maximum_Splice_Width', 
        'VRL_VHMC_MES_2BAP_SPLICE_AVERAGE_WIDTH' : 'Breaker_2_BTMO_Me:ured_average_Splice_Width_', 
        'VRL_VHMC_MES_2BAP_SPLICE_AVG_OPEN_OVER_L' : 'Breaker_2_BTMO_Me:ured_average_Splice_Open_Overlap_Left', 
        'VRL_VHMC_MES_2BAP_SPLICE_AVG_OPEN_OVER_M' : 'Breaker_2_BTMO_Me:ured_average_Splice_Open_Overlap_Middle', 
        'VRL_VHMC_MES_2BAP_SPLICE_AVG_OPEN_OVER_R' : 'Breaker_2_BTMO_Me:ured_average_Splice_Open_Overlap_Right', 
        'VRL_VHMC_MES_CWAP_TENSION_OK' : 'Capstrip_Tension_OK_', 
        'VRL_VHMC_MES_CWAP_SPOT_POS' : 'Capstrip_Spot_Position', 
        'VST_VHMC_MES_CWLO_IDENTIFIER' : 'Material_Code_of_Capstrip_Material', 
        'VST_VHMC_MES_CWLO_CART_IDENTIFIER' : 'Cartridge_Barcode_of_Capstrip_Material_(c:ette_barcode)', 
        'VIN_VHMC_MES_CWLO_MATERIAL_STATUS' : 'Material_Status_of_Capstrip_Material_(0_=_NOT_OK,_1_=_OK)', 
        'VST_VHMC_MES_TDLO_IDENTIFIER' : 'Material_Code_of_Tread_', 
        'VST_VHMC_MES_TDLO_CART_IDENTIFIER' : 'Material_Cartridge_RFID_of_Tread_Material_(c:ette_RFID_code)', 
        'VIN_VHMC_MES_TDLO_MATERIAL_STATUS' : 'Material_Status_of_Tread_Material_(0_=_NOT_OK,_1=_OK)', 
        'VRL_VHMC_MES_TD_WIDTH_ME:URED' : 'Tread_Me:ured_Width_by_VVS_(by_camera)', 
        'VRL_VHMC_MES_TD_WIDTH_SETPOINT' : 'Tread_Width_Setpoint', 
        'VRL_VHMC_MES_TD_LENGTH_ME:URED' : 'Tread_Me:ured_Length_', 
        'VRL_VHMC_MES_TD_LENGTH_SETPOINT' : 'Tread_Length_Setpoint', 
        'VRL_VHMC_MES_TD_POS_WIDTH_OK' : 'Tread_Pos_Width_OK_by_VVS', 
        'VRL_VHMC_MES_TD_SPOT_POSITION' : 'Tread_Spot_Position_', 
        'VRL_VHMC_MES_TDPR_CYCLE_LM' : 'Tread_Preparation_Cycle_Time_Length_Me:ure_', 
        'VRL_VHMC_MES_TDPR_CYCLE_CUTTING' : 'Tread_Preparation_Cycle_Time_Cutting', 
        'VRL_VHMC_MES_TDPR_CYCLE_TRANSPORT' : 'Tread_Preparation_Cycle_Time_Transport', 
        'VRL_VHMC_MES_TDPR_CYCLE_CART_EMPTY' : 'Tread_Preparation_Cycle_Time_Cart_Empty_/_Shuttle_', 
        'VRL_VHMC_MES_TDPR_CYCLE_PILE_UP' : 'Tread_Preparation_Cycle_Time_Pile_Up', 
        'VRL_VHMC_MES_TDPR_CYCLE_MAT_AT_FRONT' : 'Tread_Preparation_Cycle_Time_Mat_At_Front', 
        'VRL_VHMC_MES_TDPR_CYCLE_TOTAL' : '_Tread_Preparation_Cycle_Time_Total_', 
        'VST_VHMC_MES_INLO_IDENTIFIER' : 'Material_Code_of_Innerliner_Material', 
        'VST_VHMC_MES_INLO_CART_IDENTIFIER' : 'Cartridge_RFID_of_Innerliner_Material_(C:ette_RFID_code)', 
        'VIN_VHMC_MES_INLO_MATERIAL_STATUS' : 'Material_Status_of_Innerliner_Material_(0_=_NOT_OK,_1_=_OK)', 
        'VST_VHMC_MES_SWLO_IDENTIFIER' : 'Material_Code_of_Sidewall_Material', 
        'VST_VHMC_MES_SWLO_CART_IDENTIFIER' : 'Cartridge_RFID_of_Sidewall_Material_(c:ette_RFID_code)', 
        'VIN_VHMC_MES_SWLO_MATERIAL_STATUS' : 'Material_Status_of_Sidewall_Material_(0_=_NOT_OK_1_=_OK)', 
        'VRL_VHMC_MES_PA_WIDTH_ME:URED' : 'Pre:sembly_Me:ured_Width_by_VVS_(by_camera)', 
        'VRL_VHMC_MES_PA_WIDTH_SETPOINT' : 'Pre:sembly_Width_Setpoint', 
        'VRL_VHMC_MES_IL_LENGTH_ME:URED' : 'Innerliner_Me:ured_Length_by_Axis', 
        'VRL_VHMC_MES_IL_LENGTH_SETPOINT' : 'Innerliner_Length_Setpoint', 
        'VRL_VHMC_MES_PA_ANGLE_ME:URED' : 'Pre:sembly_Angle_by_VVS_(by_camera)', 
        'VRL_VHMC_MES_PA_SPOT_POSITION' : 'Pre:sembly_Spot_Position', 
        'VRL_VHMC_MES_BARCODE_SPOT_POS' : 'Pre:sembly_Spot_Position_Barcode', 
        'VRL_VHMC_MES_BARCODE_TRAV_POS' : 'Pre:sembly_Traverse_Position_Barcode_on_SW', 
        'VRL_VHMC_MES_PAPR_CYCLE_LM' : 'Pre:sembly_Cycle_Time_Length_Me:urent', 
        'VRL_VHMC_MES_PAPR_CYCLE_CUTTING' : 'Pre:sembly_Cycle_Time_Cutting', 
        'VRL_VHMC_MES_PAPR_CYCLE_TRANSPORT' : 'Pre:sembly_Cycle_Time_Transport', 
        'VRL_VHMC_MES_PAPR_CYCLE_CART_EMPTY' : 'Pre:sembly_Cycle_Time_Cart_Empty', 
        'VRL_VHMC_MES_PAPR_CYCLE_MAT_AT_FRONT' : 'Pre:sembly_Cycle_Time_Material_at_Front', 
        'VRL_VHMC_MES_PAPR_CYCLE_TOTAL' : 'Preasembly_Cycle_Time_Total', 
        'VRL_VHMC_MES_BPCU_LFT_TEMP_ME:URED' : 'Bodyply_Cutter_Left_Heater_Temperature', 
        'VRL_VHMC_MES_BPCU_RHT_TEMP_ME:URED' : 'Bodyply_Cutter_Right_Heater_Temperature', 
        'VRL_VHMC_MES_BPCU_TEMP_SETPOINT' : 'Bodyply_Cutter_Heater_Temperature_Setpoint', 
        'VST_VHMC_MES_1PLO_IDENTIFIER' : 'Material_Code_of_Bodyply_1_Material', 
        'VST_VHMC_MES_1PLO_CART_IDENTIFIER' : 'Cartridge_RFID_of_Bodyply_1_Material_(_c:ette_RFID_code)', 
        'VIN_VHMC_MES_1PLO_MATERIAL_STATUS' : 'Material_Status_of_Bodyply_1_Material_(0_=_NOT_OK,_1_=_OK)', 
        'VRL_VHMC_MES_BP1_LENGTH_ME:URED' : 'Bodyply_1_Me:ured_Length_by_Axis', 
        'VRL_VHMC_MES_BP1_LENGTH_SETPOINT' : 'Bodyply_1_Length_Setpoint', 
        'VRL_VHMC_MES_BP1_WIDTH_SETPOINT' : 'Bodyply_1_Width_Setpoint', 
        'VRL_VHMC_MES_BP1_SPOT_POS' : 'Bodyply_1_Spot_Position', 
        'VRL_VHMC_MES_1PLO_CONTAINS_BP_1_OR_2' : 'Bodyply_1_Letoff_contains_Bodyply_1_or_2_material', 
        'VRL_VHMC_MES_BP1_MONO_OR_TWOPLY' : 'Bodyply_1_Mono_or_Two_Ply', 
        'VRL_VHMC_MES_BP1_TOTAL_SCRAP_CUTOUT' : 'Bodyply_1_Total_scrap_cutout_per_ply', 
        'VRL_VHMC_MES_BPPR_BP1_CYCLE_REST' : 'Bodyply_1_Cycle_Time_Rest', 
        'VRL_VHMC_MES_BPPR_BP1_CYCLE_LM' : 'Bodyply_1_Cycle_Time_Length_Me:ure', 
        'VRL_VHMC_MES_BPPR_BP1_CYCLE_CART_EMPTY' : 'Bodyply_1_Cycle_Time_Cart_Empty', 
        'VRL_VHMC_MES_BPPR_BP1_CYCLE_CUTTING' : 'Bodyply_1_Cycle_Time_Cutting', 
        'VRL_VHMC_MES_BPPR_BP1_CYCLE_CUT_SCRAP' : 'Bodyply_1_Cycle_Time_Cutting_Scrap', 
        'VRL_VHMC_MES_BPPR_BP1_CYCLE_REMOVE_SCRAP' : 'Bodyply_1_Cycle_Time_Remove_Scrap', 
        'VRL_VHMC_MES_BPPR_BP1_CYCLE_READY' : 'Bodyply_1_Cycle_Time_Ready', 
        'VRL_VHMC_MES_CCMO_BP1_LFT_SPLICE_LENGTH' : 'Bodyply_1_Me:ured_Left_Splice_Length', 
        'VRL_VHMC_MES_CCMO_BP1_MID_SPLICE_LENGTH' : 'Bodyply_1_Me:ured_Middle_Splice_Length', 
        'VRL_VHMC_MES_CCMO_BP1_RHT_SPLICE_LENGTH' : 'Bodyply_1_Me:ured_Right_Splice_Length', 
        'VST_VHMC_MES_2PLO_IDENTIFIER' : 'Material_Code_of_Bodyply_2_Material', 
        'VST_VHMC_MES_2PLO_CART_IDENTIFIER' : 'Cartridge_RFID_of_Bodyply_2_Material_(c:ette_RFID_code)', 
        'VIN_VHMC_MES_2PLO_MATERIAL_STATUS' : 'Material_Status_of_Bodyply_2_Material_(0_=_NOT_OK,_1_=_OK)', 
        'VRL_VHMC_MES_BP2_LENGTH_ME:URED' : 'Bodyply_2_Me:ured_Length_by_Axis', 
        'VRL_VHMC_MES_BP2_LENGTH_SETPOINT' : 'Bodyply_2_Length_Setpoint', 
        'VRL_VHMC_MES_BP2_WIDTH_SETPOINT' : 'Bodyply_2_Width_Setpoint', 
        'VRL_VHMC_MES_BP2_SPOT_POS' : 'Bodyply_2_Spot_Position', 
        'VRL_VHMC_MES_2PLO_CONTAINS_BP_1_OR_2' : 'Bodyply_2_Letoff_contains_Bodyply_1_or_2_material', 
        'VRL_VHMC_MES_BP2_MONO_OR_TWOPLY' : 'Bodyply_2_Mono_or_Two_Ply', 
        'VRL_VHMC_MES_BP2_TOTAL_SCRAP_CUTOUT' : 'Bodyply_2_Total_scrap_cutout_per_ply', 
        'VRL_VHMC_MES_BPPR_BP2_CYCLE_REST' : 'Bodyply_2_Cycle_Time_Rest', 
        'VRL_VHMC_MES_BPPR_BP2_CYCLE_LM' : 'Bodyply_2_Cycle_Time_Length_Me:ure', 
        'VRL_VHMC_MES_BPPR_BP2_CYCLE_CART_EMPTY' : 'Bodyply_2_Cycle_Time_Cart_Empty', 
        'VRL_VHMC_MES_BPPR_BP2_CYCLE_CUTTING' : 'Bodyply_2_Cycle_Time_Cutting', 
        'VRL_VHMC_MES_BPPR_BP2_CYCLE_CUT_SCRAP' : 'Bodyply_2_Cycle_Time_Cutting_Scrap', 
        'VRL_VHMC_MES_BPPR_BP2_CYCLE_REMOVE_SCRAP' : 'Bodyply_2_Cycle_Time_Remove_Scrap', 
        'VRL_VHMC_MES_BPPR_BP2_CYCLE_READY' : 'Bodyply_2_Cycle_Time_Ready', 
        'VRL_VHMC_MES_CCMO_BP2_LFT_SPLICE_LENGTH' : 'Bodyply_1_Me:ured_Left_Splice_Length', 
        'VRL_VHMC_MES_CCMO_BP2_MID_SPLICE_LENGTH' : 'Bodyply_1_Me:ured_Middle_Splice_Length', 
        'VRL_VHMC_MES_CCMO_BP2_RHT_SPLICE_LENGTH' : 'Bodyply_1_Me:ured_Right_Splice_Length', 
        'VRL_VHMC_MES_ISDS_CHECK_SPLICE_MODE' : 'Advanced_Bodyply_Splice_Check_modus_(see_PP184)', 
        'VRL_VHMC_MES_ISDS_NEW_SPOT_POS_BP1' : 'New_spot_position_Bodyply_1', 
        'VRL_VHMC_MES_ISDS_NEW_SPOT_POS_BP2' : 'New_spot_position_Bodyply_2', 
        'VRL_VHMC_MES_ISDS_AMOUNT_SPLICES_BP1' : 'Number_of_Stocksplices_in_Bodyply_1', 
        'VRL_VHMC_MES_ISDS_AMOUNT_SPLICES_BP2' : 'Number_of_Stocksplices_in_Bodyply_2', 
        'VRL_VHMC_MES_ISDS_STATUS' : 'Calculation_Result_(1_=_OK)', 
        'VRL_VHMC_MES_ISDS_SPLICE_INBAL_OLD' : 'Splice_inbalance_before_changing_spotpositions', 
        'VRL_VHMC_MES_ISDS_SPLICE_INBAL_NEW' : 'Splice_inbalance_after_changing_spotpositions', 
        'VRL_VHMC_MES_ISDS_M_SPLICE_POS_BP1' : 'Machine_splice_Bodyply_1_pos_in_degrees_in_relation_to_PA_splice', 
        'VRL_VHMC_MES_ISDS_S_SPLICE_1_POS_BP1' : 'Stock_splice_1_pos_of_Bodyply_1_in_degrees_in_relation_to_PA_splice_(999_=_Not_present)', 
        'VRL_VHMC_MES_ISDS_S_SPLICE_2_POS_BP1' : 'Stock_splice_2_pos_of_Bodyply_1_in_degrees_in_relation_to_PA_splice_(999_=_Not_present)', 
        'VRL_VHMC_MES_ISDS_S_SPLICE_3_POS_BP1' : 'Stock_splice_3_pos_of_Bodyply_1_in_degrees_in_relation_to_PA_splice_(999_=_Not_present)', 
        'VRL_VHMC_MES_ISDS_M_SPLICE_POS_BP2' : 'Machine_splice_Bodyply_2_pos_in_degrees_in_relation_to_PA_splice', 
        'VRL_VHMC_MES_ISDS_S_SPLICE_1_POS_BP2' : 'Stock_splice_1_pos_of_Bodyply_2_in_degrees_in_relation_to_PA_splice_(999_=_Not_present)', 
        'VRL_VHMC_MES_ISDS_S_SPLICE_2_POS_BP2' : 'Stock_splice_2_pos_of_Bodyply_2_in_degrees_in_relation_to_PA_splice_(999_=_Not_present)', 
        'VRL_VHMC_MES_ISDS_S_SPLICE_3_POS_BP2' : 'Stock_splice_3_pos_of_Bodyply_2_in_degrees_in relation_to_PA_splice_(999_=_Not_present)', 
        'VRL_VHMC_MES_CCDS_VVSC_CORR_VALUE_PA' : 'Carc:s_Drum_Shuttle_Correction_distance_PA', 
        'VRL_VHMC_MES_CCDS_VVSC_CORR_VALUE_BP1' : 'Carc:s_Drum_Shuttle_Correction_distance_BP1', 
        'VRL_VHMC_MES_CCDS_VVSC_CORR_VALUE_BP2' : 'Carc:s_Drum_Shuttle_Correction_distance_BP2', 
        'VST_VHMC_MES_BDLD_IDENTIFIER' : 'Material_Code_of_bead_Material', 
        'VST_VHMC_MES_BDLD_CART_IDENTIFIER' : 'Cartridge_RFID_of_bead_Material', 
        'VIN_VHMC_MES_BDLD_MATERIAL_STATUS' : 'Material_Status_of_bead_Material_(0_=_NOT_OK_1_=OK)', 
        'VST_VHMC_MES_SCLO_LEFT_IDENTIFIER' : 'Material_Code_of_Left_Chafer_Material', 
        'VST_VHMC_MES_SCLO_LEFT_CART_IDENTIFIER' : 'Cartridge_RFID_of_Left_Chafer_Material', 
        'VIN_VHMC_MES_SCLO_LEFT_MATERIAL_STATUS' : 'Material_Status_of_Left_Chafer_Material_(0_=_NOT_OK,_1_=_OK)', 
        'VST_VHMC_MES_SCLO_RIGHT_IDENTIFIER' : 'Material_Code_of_Right_Chafer_', 
        'VST_VHMC_MES_SCLO_RIGHT_CART_IDENTIFIER' : 'Material_Cartridge_RFID_of_Right_Chafer_', 
        'VIN_VHMC_MES_SCLO_RIGHT_MATERIAL_STATUS' : 'Material_Status_of_Right_Chafer_Material_(0_=_NOT_OK,_1_=_OK)', 
        'VRL_VHMC_MES_SCCU_LFT_TEMP_ME:URED' : 'Chafer_Cutter_Left_Heater_Temperature_Me:ured_', 
        'VRL_VHMC_MES_SCCU_RHT_TEMP_ME:URED' : 'Chafer_Cutter_Right_Heater_Temperature_Me:ured', 
        'VRL_VHMC_MES_SCCU_TEMP_SETPOINT' : 'Chafer_Cutter_Heater_Temperature_Setpoint', 
        'VRL_VHMC_MES_SCLW_LENGTH_ME:URED' : '_Chafer_Left_Me:ured_Length', 
        'VRL_VHMC_MES_SCRW_LENGTH_ME:URED' : 'Chafer_Right_Me:ured_Length', 
        'VRL_VHMC_MES_SCxW_LENGTH_SETPOINT' : 'Chafer_Length_Setpoint', 
        'VRL_VHMC_MES_SCCV_STEEL_OR_FABRIC' : 'Chafer_Material_(0_=_Steel,_1_=_Fabric)', 
        'VRL_VHMC_MES_SCCV_ANGLE' : 'Chafer_Angle_Setpoint', 
        'VRL_VHMC_MES_SCCV_WIDTH' : 'Chafer_Width_Setpoint', 
        'VST_VHMC_MES_FCLO_LEFT_IDENTIFIER' : 'Material_Code_of_Left_Fabric_Chafer_Material_(Chipper)', 
        'VST_VHMC_MES_FCLO_LEFT_CART_IDENTIFIER' : 'Cartridge_RFID_of_Left_Fabric_Chafer_Material_(Chipper)', 
        'VIN_VHMC_MES_FCLO_LEFT_MATERIAL_STATUS' : 'Material_Status_of_Left_Fabric_Chafer_Material_(0_=_NOT_OK,_1_=_OK)_(Chipper)', 
        'VST_VHMC_MES_FCLO_RIGHT_IDENTIFIER' : 'Material_Code_of_Right_Fabric_Chafer_Material_(Chipper)', 
        'VST_VHMC_MES_FCLO_RIGHT_CART_IDENTIFIER' : 'Cartridge_RFID_of_Right_Fabric_Chafer_Material_(Chipper)', 
        'VIN_VHMC_MES_FCLO_RIGHT_MATERIAL_STATUS' : 'Material_Status_of_Right_Fabric_Chafer_Material_(0=_NOT_OK_1_=_OK)_(Chipper)', 
        'VRL_VHMC_MES_FCXW_LENGTH_SETPOINT' : 'Fabric_Chafer_Length_Setpoint_(Chipper)', 
        'VRL_VHMC_MES_FCCV_WIDTH' : '_Fabric_Chafer_Width_Setpoint_(Chipper)', 
        'VRL_VHMC_MES_FCCV_THICKNESS' : '_Fabric_Chafer_Thickness_Setpoint_(Chipper)', 
        'VRL_VHMC_MES_CCDR_DRUM_TYPE' : '_Carc:s_Drum_Type', 
        'VST_VHMC_MES_RSLO_LEFT_IDENTIFIER' : 'Material_Code_of_Left_Rubber_strip_', 
        'VST_VHMC_MES_RSLO_LEFT_CART_IDENTIFIER' : 'Material_Cartridge_RFID_of_Left_Rubber_strip_', 
        'VIN_VHMC_MES_RSLO_LEFT_MATERIAL_STATUS' : 'Material_Status_of_Left_Rubber_strip_Material_(0_=_NOT_OK,_1_=_OK)', 
        'VST_VHMC_MES_RSLO_RIGHT_IDENTIFIER' : 'Material_Code_of_Right_Rubber_strip_', 
        'VST_VHMC_MES_RSLO_RIGHT_CART_IDENTIFIER' : 'Material_Cartridge_RFID_of_Right_Rubber_strip_Material', 
        'VIN_VHMC_MES_RSLO_RIGHT_MATERIAL_STATUS' : 'Material_Status_of_Right_Rubber_strip_Material_(0_=_NOT_OK,_1_=_OK)', 
        'VRL_VHMC_MES_RSCU_LFT_TEMP_ME:URED' : 'Rubber_Strip_Cutter_Left_Heater_Temperature_Me:ured', 
        'VRL_VHMC_MES_RSCU_RHT_TEMP_ME:URED' : 'Rubber_Strip_Cutter_Right_Heater_Temperature_Me:ured', 
        'VRL_VHMC_MES_RSCU_TEMP_SETPOINT' : 'Rubber_Strip_Cutter_Heater_Temperature_Setpoint_', 
        'VRL_VHMC_MES_RSXW_LENGTH_SETPOINT' : 'Rubber_Strip_Length_Setpoint', 
        'VRL_VHMC_MES_RSCV_WIDTH' : 'Rubber_Strip_Width_Setpoint', 
        'VRL_VHMC_MES_RSCV_THICKNESS' : 'Rubber_Strip_Thickness_Setpoint_', 
        'VRL_VHMC_MES_CCDR_DRUM_SIZE' : 'Carc:s_Drum_Size_(Inch)', 
        'VRL_VHMC_MES_CCDR_TURNUP_PRESSURE_MIN' : 'Carc:s_Drum_minimum_me:ured_Pressure_during_Turnup', 
        'VRL_VHMC_MES_CCDR_TURNUP_PRESSURE_MAX' : 'Carc:s_Drum_maximum_me:ured_Pressure_during_Turnup', 
        'VRL_VHMC_MES_CCDR_PRESHAPE_PRESSURE_MIN' : 'Carc:s_Drum_minimum_me:ured_Pressure_during_Preshape', 
        'VRL_VHMC_MES_CCDR_PRESHAPE_PRESSURE_MAX' : 'Carc:s_Drum_maximum_me:ured_Pressure_during_Preshape', 
        'VRL_VHMC_MES_CCDR_SHAPE_PRESSURE_MIN' : 'Carc:s_Drum_minimum_me:ured_Pressure_during_Shape', 
        'VRL_VHMC_MES_CCDR_SHAPE_PRESSURE_MAX' : 'Carc:s_Drum_maximum_me:ured_Pressure_during_Shape', 
        'VRL_VHMC_MES_CCDR_STITCH_TD_PRESSURE_MIN' : 'Carc:s_Drum_minimum_me:ured_Pressure_during_Tread_Stitching', 
        'VRL_VHMC_MES_CCDR_STITCH_TD_PRESSURE_MAX' : 'Carc:s_Drum_maximum_me:ured_Pressure_during_Tread_Stitching', 
        'VRL_VHMC_MES_CCDR_STITCH_SW_PRESSURE_MIN' : 'Carc:s_Drum_minimum_me:ured_Pressure_during_Sidewall_Stitching', 
        'VRL_VHMC_MES_CCDR_STITCH_SW_PRESSURE_MAX' : 'Carc:s_Drum_maximum_me:ured_Pressure_during_Sidewall_Stitching', 
        # 'VRL_VHMC_MES_BTPR_CYCLE_TIME_1BAP' : 'BT_Side_Cycle_time_Breaker_1_Application', 
        # 'VRL_VHMC_MES_BTPR_CYCLE_TIME_2BAP' : '_BT_Side_Cycle_time_Breaker_2_Application_', 
        # 'VRL_VHMC_MES_BTPR_CYCLE_TIME_CWAP' : 'BT_Side_Cycle_time_Capstrip_Application_', 
        # 'VRL_VHMC_MES_BTPR_CYCLE_TIME_TDAP' : 'BT_Side_Cycle_time_Tread_Application', 
        # 'VRL_VHMC_MES_BTPR_CYCLE_TIME_WAIT_CC' : 'BT_Side_Cycle_time_Wait_for_CC_Side', 
        # 'VRL_VHMC_MES_BTPR_CYCLE_TIME_BTRE' : 'BT_Side_Cycle_time_Remove_B&T_Package', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_PAAP' : 'CC_Side_Cycle_time_Pre-:sembly_Application_', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_STITCH_BP' : 'CC_Side_Cycle_time_BodyPly_Stitch_Splices', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_WAIT_BEADS' : 'CC_Side_Cycle_time_Wait_for_Beads', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_WAIT_BT' : 'CC_Side_Cycle_time_Wait_for_B&T_Package', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_STITCH_PA' : 'CC_Side_Cycle_time_Pre-:sembly_Stitch_Splice_', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_1PAP' : 'CC_Side_Cycle_time_Bodyply_1_Application', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_2PAP' : 'CC_Side_Cycle_time_Bodyply_2_Application', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_SCAP' : 'CC_Side_Cycle_time_Chafer_Application', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_FCAP' : 'CC_Side_Cycle_time_Chipper_Application', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_STITCH_FC' : 'CC_Side_Cycle_time_Chipper_Stitch_Splice', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_RSAP' : '_CC_Side_Cycle_time_Rubberstrip_Application', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_STITCH_RS' : 'CC_Side_Cycle_time_Rubberstrip_Stitch_Splice', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_BDSG' : 'CC_Side_Cycle_time_Bead_Setting', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_RLCY' : '_CC_Side_Cycle_time_Turn-Up_', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_SHAPE' : 'CC_Side_Cycle_time_Shaping', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_TDST' : 'CC_Side_Cycle_time_Tread_Stitching', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_SWST' : 'CC_Side_Cycle_time_Sidewall_Stitching', 
        # 'VRL_VHMC_MES_CCPR_CYCLE_TIME_GTRU' : 'CC_Side_Cycle_time_Green_Tyre_Removal'
        })
        return df_renamed

    def plot_counter(self, df, column: str, title: str = 'title'):
        count = Counter(df[column].tolist())
        df = pd.DataFrame.from_dict(count, orient='index')
        df.plot(kind='bar', figsize=(10, 5), title=title)
    
    def cycle_time(self, df, TBM):
        # Filter by one TBM
        df = df.loc[df['EquipmentID'] == TBM] 
        # Convert to datetime
        df['ProducedOn']= pd.to_datetime(df['ProducedOn'])
        df.sort_values(by='ProducedOn', ascending=True, inplace=True)
        # Create Strart time columns and drop NaT
        df['start_time'] = df['ProducedOn'].shift(1)
        df = df[df.start_time.notnull()]
        # Calculate Cycle Times 
        df['cycle_time_s'] = (df['ProducedOn']-df['start_time']).dt.seconds
        return df
    
    def cycle_time_looper(self, df):
        ''' Sort by time and get a start time & duration for each Green tyre. Generate cycle times for Each Tyre. '''
        TBMs = df.EquipmentID.unique()
        small_dfs = []

        for x in TBMs:
            small_df = self.cycle_time(df, x)
            small_dfs.append(small_df)

        return pd.concat(small_dfs, ignore_index=True)

    def allocator(self, df_cycle, df_alarms, df_cycle_start: str, df_cycle_end: str, alarm_timestamp: str = 'Timetamp', column_to_add_to_list: str = 'name_index'):
        ''' Allocates List of Occured Alarms to a Green Tyre ID based on start and end times '''
        d = {}
        i = 0 

        cycle_subset_df = df_cycle[['Id', df_cycle_start, df_cycle_end ]]
        cycle_subset_df.rename(columns = {df_cycle_start:'df_cycle_start', df_cycle_end:'df_cycle_end'}, inplace = True)
        
        # Conversion of Time Columns to Datetime
        # Also, Add half a second padding to account for error from rounding Alarm Timestamps
        cycle_subset_df['df_cycle_start'] = pd.to_datetime(cycle_subset_df['df_cycle_start']) - pd.to_timedelta(0.5, unit='s')
        cycle_subset_df['df_cycle_end'] = pd.to_datetime(cycle_subset_df['df_cycle_end']) + pd.to_timedelta(0.5, unit='s')
        df_alarms[alarm_timestamp] = pd.to_datetime(df_alarms[alarm_timestamp])


        length = len(cycle_subset_df)
        for row in cycle_subset_df.itertuples():
            # Get list of alarms in the time interval for a certain Green Tyre 
            # Could input start/end times as func parameters using: getattr(row, 'PAAP_Start_time') but is much slower
            list_df = df_alarms.loc[(df_alarms[alarm_timestamp] > row.df_cycle_start) & (df_alarms[alarm_timestamp] < row.df_cycle_end)]
            # Create list of alarms that were in that time interval
            list_of_alarm = list(list_df[column_to_add_to_list])
            # Append this list to the dictionary with the tyre ID 
            
            d[i] = {"Id": row.Id, "list_of_alarms": list_of_alarm}
            i = i + 1
            if i % 20 == 0:
                print(f'{bcolors.CYAN}Tyre Allocation Complete: {bcolors.ENDC}{round((i/length)*100,2)}%',  end ="\r")

        return pd.DataFrame.from_dict(d, "index")

    def view_tyre_before_and_after(self, num: int, df, df_tbm):
        ''' View the tyre that occured before and after a single Tyre based on producedOn Time'''
        p = bcolors()
        ind = df_tbm[df_tbm.ProducedOn.isin(df.iloc[[num]].ProducedOn.to_list())].index.tolist()
        p.printg(f'The PAAP Alarm Duration was {df.iloc[[num]].Duration.to_list()[0]}s and occured at {df.iloc[[num]].TimeStamp.to_list()[0]}')
        ind.append(ind[0] - 2)
        ind.append(ind[0] - 1)
        ind.append(ind[0] + 1)
        ind.append(ind[0] + 2)
        return df_tbm[df_tbm.index.isin(sorted(ind))]

    def view_before_and_after_tyre_selected_columns(self, num: int, df, df_tbm):
        df = self.view_tyre_before_and_after(num, df, df_tbm)[['ProducedOn', 'RecipeName', 'start_time', 'cycle_time_s', 'Id', 'PAAP_Start_time', 'PAAP_Finish_time', 'VRL_VHMC_MES_CCPR_CYCLE_TIME_PAAP']]
        return df

class Feature_Selection:
    '''Class for Feature Selection Workflow'''

    def alarm_one_hot_encoder(self, df, column_containing_lists: str = 'list_of_alarms'):
        '''create One Hot Encoding of the list of alarms'''
        mlb = MultiLabelBinarizer(sparse_output=True)

        df_ohe = df.join(
            pd.DataFrame.sparse.from_spmatrix(
                mlb.fit_transform(df[column_containing_lists]),
                index=df.index,
                columns=mlb.classes_))

        return df_ohe

    def mask_empty_lists(self, df, column_with_lists: str = 'list_of_alarms'):
        ''' Apply mask for list's with no alarms for this filter. I.e. get rid of Irrelevant tyres'''
        mask = df[column_with_lists].apply(lambda x:  len(x) != 0)
        df_filter = df[mask]
        return df_filter

    def mask_empty_lists_num(self, df, num_ent, column_with_lists: str = 'list_of_alarms'):
        ''' Apply mask for list's with no alarms for this filter. I.e. get rid of Irrelevant tyres'''
        mask = df[column_with_lists].apply(lambda x:  len(x) == num_ent)
        df_filter = df[mask]
        return df_filter

    def mask_empty_lists_morethan(self, df, column_with_lists: str = 'list_of_alarms'):
        ''' Apply mask for list's with no alarms for this filter. I.e. get rid of Irrelevant tyres'''
        mask = df[column_with_lists].apply(lambda x:  len(x) > 1)
        df_filter = df[mask]
        return df_filter

class Data_Functions:
    '''Class for Data Exploration'''
    def percentile_plotter(self, df, column: str):
        '''Plots the Percetiles 1 to 99'''
        d = []
        for percent in range(1, 100):
            d.append(
                {
                    'percentile': percent,
                    'cyle_time_s': np.percentile(df[column].to_list(), percent)
                }
            )
        plt.figure(figsize=(10, 6), dpi=80)
        sns.lineplot(data=pd.DataFrame(d), x="percentile", y="cyle_time_s")   

    def percentile_plotter_recipe(self, df, column: str, recipe: str):
        '''Plots the Percetiles 1 to 99 for a recipe'''
        d = []
        for percent in range(1, 100):
            d.append(
                {
                    'percentile': percent,
                    'cyle_time_s': np.percentile(df[df.RecipeName == recipe][column].to_list(), percent)
                }
            )
        plt.title(f'Percentiles for top 10 Recipes')
        sns.lineplot(data=pd.DataFrame(d), x="percentile", y='cyle_time_s', label=f'{recipe}')    
    
    def list_percetile_plotter(self, list, df, column: str):
        ''' Iterates through a list to plot percentiles of each.'''

        plt.figure(figsize=(15, 10), dpi=80)
        for i in list:
            self.percentile_plotter_recipe(df, column, i)
        plt.legend()

    def KDE_dist_plotter(self, series, smoothness = .4, xlabel: str = 'xlabel', ylabel: str = 'Probablity Density', title: str = 'title' ):
        ''' Plot KDE of Distribution'''
        plt.figure(figsize=(10, 6), dpi=80)
        # Plotting the KDE Plot
        sns.kdeplot(series, color='b', shade=True, bw_adjust=smoothness)
        # sns.kdeplot(alarm_join.loc[(alarm_join['Name']=='PRE-ASSEMBLY, LENGTH OUT OF TOLERANCE'),'Duration'][alarm_join.loc[(alarm_join['Name']=='PRE-ASSEMBLY, LENGTH OUT OF TOLERANCE'),'Duration'] > 100], color='r', shade=True, Label='PRE_ASSEMBLY_LENGTH_OUT_OF_TOLERANCE')
        # Setting the X and Y Label
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)

    def KDE_dist_plotter_multiple(self, list_of_series: list, label:list, smoothness = .4, xlabel: str = 'xlabel', ylabel: str = 'Probablity Density', title: str = 'title' ):
        ''' Plot KDE of Distribution'''
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(10, 6), dpi=80)
        # Plotting the KDE Plot
        for i in range(len(list_of_series)):
            sns.kdeplot(list_of_series[i], shade=True, bw_adjust=smoothness, label=label[i])
        # sns.kdeplot(alarm_join.loc[(alarm_join['Name']=='PRE-ASSEMBLY, LENGTH OUT OF TOLERANCE'),'Duration'][alarm_join.loc[(alarm_join['Name']=='PRE-ASSEMBLY, LENGTH OUT OF TOLERANCE'),'Duration'] > 100], color='r', shade=True, Label='PRE_ASSEMBLY_LENGTH_OUT_OF_TOLERANCE')
        # Setting the X and Y Label
        plt.legend()
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)

    def corr(self, df, var1: str, var2:str, method: str = 'pearson' ):
        ''' Correlation coedd between two variables in a dataframe. Methods = {'pearson', 'kendall', 'spearman'}'''
        return df[[var1, var2]].corr(method=method).to_numpy().min()

    def moments(self, series):
        ''' Prints 4 Moments of a statistical distribution'''
        p = bcolors()
        p.printg(f'Mean: {p.ENDC} {np.mean(series)}')
        p.printg(f'Variance: {p.ENDC} {np.var(series)}')
        p.printg(f'Skew: {p.ENDC} {sp.skew(series)}')
        p.printg(f'Kurtosis: {p.ENDC} {sp.kurtosis(series)}')

    def ridge(self, df_PA_tbm_join_Alarm, cycle_time_s: str = 'cycle_time_s', RecipeName: str = 'RecipeName' ):
        ridge_data = df_PA_tbm_join_Alarm[[cycle_time_s, RecipeName]]
        ridge_data_filter = ridge_data[ridge_data[cycle_time_s] < 300]
        count = ridge_data_filter.groupby(RecipeName).size()
        ridge_data_filter = pd.merge(count.to_frame(), ridge_data_filter,on=RecipeName)
        ridge_data_filter['count'] = ridge_data_filter[0].apply(str)
        ridge_data_filter[RecipeName] = ridge_data_filter[RecipeName] + ' (' + ridge_data_filter['count'] + ')'
        ridge_data_filter.drop([0, 'count'], axis=1, inplace=True)

        sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

        # Initialize the FacetGrid object
        pal = sns.cubehelix_palette(len(ridge_data_filter[RecipeName].unique()), start=1.4, rot=-.25, light=.7, dark=.4)
        g = sns.FacetGrid(ridge_data_filter, row=RecipeName, hue=RecipeName, aspect=15, height=.5, palette=pal)

        # Draw the densities in a few steps
        g.map(sns.kdeplot, cycle_time_s,
            bw_adjust=.5, clip_on=False,
            fill=True, alpha=1, linewidth=1.5)
        g.map(sns.kdeplot, cycle_time_s, clip_on=False, color="w", lw=2, bw_adjust=.5)

        # passing color=None to refline() uses the hue mapping
        # g.refline(y=0, linewidth=2, linestyle="-", color=None, clip_on=False)
        g.map(plt.axhline, y=0, linewidth=2, linestyle="-", color=None, clip_on=False)

        # Define and use a simple function to label the plot in axes coordinates
        def label(x, color, label):
            ax = plt.gca()
            ax.text(0, .2, label, fontweight="bold", color=color,
                    ha="left", va="center", transform=ax.transAxes)

        g.map(label, cycle_time_s)

        # Set the subplots to overlap
        g.fig.subplots_adjust(hspace=-.25)

        # Remove axes details that don't play well with overlap
        g.set_titles("")
        g.set(yticks=[], xlabel=cycle_time_s, ylabel="")
        g.despine(bottom=True, left=True)
        plt.show()
        
    def spearman(self, data1, data2): 
        # calculate spearman's correlation
        coef, pval = sp.spearmanr(data1, data2)
        p = bcolors()
        p.printg(f'Spearmans correlation coefficient: {p.ENDC} {coef}')

        # interpret the significance
        alpha = 0.05
        if pval > alpha:
            p.printg(f'Samples are uncorrelated (fail to reject H0) {p.ENDC} {pval}')
            print(f'The statistical test reports a positive correlation with a value of {round(pval,2)}. Which means that the likelihood of observing the data given that the samples are uncorrelated is very likely (e.g. 95% confidence) and that we accept the null hypothesis that the samples are uncorrelated.')
        else:
            p.printg(f'Samples are correlated (reject H0) {p.ENDC} {pval}')
            print(f'The statistical test reports a positive correlation with a value of {round(pval,2)}. The p-value is close to zero, which means that the likelihood of observing the data given that the samples are uncorrelated is very unlikely (e.g. 95% confidence) and that we can reject the null hypothesis that the samples are uncorrelated.')

    def kendall(self, data1, data2):
        coef, pval = sp.kendalltau(data1, data2)
        p = bcolors()
        p.printg(f'Kendall correlation coefficient: {p.ENDC} {coef}')
        # interpret the significance
        alpha = 0.05
        if pval > alpha:
            p.printg(f'Samples are uncorrelated (fail to reject H0) {p.ENDC} {pval}')
            print(f'The statistical test reports a positive correlation with a value of {round(pval,2)}. Which means that the likelihood of observing the data given that the samples are uncorrelated is very likely (e.g. 95% confidence) and that we accept the null hypothesis that the samples are uncorrelated.')
        else:
            p.printg(f'Samples are correlated (reject H0) {p.ENDC} {pval}')
            print(f'Running the example calculates the Kendall’s correlation coefficient as {round(pval,2)}, which is correlated. The p-value is close to zero, which means that the likelihood of observing the data given that the samples are uncorrelated is very unlikely (e.g. 95% confidence) and that we can reject the null hypothesis that the samples are uncorrelated.')
