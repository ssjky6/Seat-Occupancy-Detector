#Specify Session Ids
session_id_begin=31202 #3230 #31031   
session_id_end=31271 #3460 #31270

#Importing packages and libraries
import pyodbc
import pandas as pd
import os
import math
from datetime import datetime
import time
from plyer import notification
import requests #to extract the server path
import shutil #to save img locally

#logger initialistion
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

start=time.time()

#server variables
server = 'SGSCBWSQLAG1.in623.corpintra.net' 
database = 'Mpic_Sod_Prod_080321'#'mpic_sod_test_110121' 
username = 'testL' 
password = 'gesture@1234' 

#connection cursor 
connection = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = connection.cursor()
try:
    logger.info("Connected to DB: " + database + " @ " + server)
except pyodbc.Error as e:
    logger.error(str(e))
    exit(1)

################################################################################################################################################################################################################################################################################
#Function to Download Images
def fetch_img(img_url, filename):
    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(img_url, stream = True)
    mega_path="C:/Users/JHAANIK/Extract/SOD_24/DATA2/Images/" #Setting Downladed Images Directory Path
    filename=os.path.join(mega_path,filename)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
    
        # Open a local file with wb ( write binary ) permission.
        with open(filename,'wb') as f:
            shutil.copyfileobj(r.raw, f)
        
        #print('Image sucessfully Downloaded: ',filename)
    else:
        print('Image Couldn\'t be retreived')
################################################################################################################################################################################################################################################################################

COUNT=0 #Keep the count of no. of images

#"""
#Setting sql query
for i in range(session_id_begin, session_id_end, 2):
  sql_query_max= "select MAX(file_info_id) from dbo.Dataset_Info where session_info_id="+str(i)+" and occupant_position='Driver'"
  df_max=pd.read_sql(sql=sql_query_max, con=connection)

  sql_query_min= "select MIN(file_info_id) from dbo.Dataset_Info where session_info_id="+str(i)+" and occupant_position='Driver'"
  df_min=pd.read_sql(sql=sql_query_min, con=connection)

  #print(df_max)
  #print(df_min)
  #print('done')
  x=df_min.iat[0,0]
  y=df_max.iat[0,0]
  
  for j in range(x, y, 5): #skip 5 frames for data variance
    occupant_position="Driver"
    sql_query_img_path= "select DISTINCT(file_path),file_name from dbo.Dataset_Info where session_info_id="+str(i)+" and file_info_id="+str(j)+" and occupant_position='Driver'"
    df_img=pd.read_sql(sql=sql_query_img_path, con=connection)
    img_server_path=("http://sgsccccdl0115.in623.corpintra.net:8081"+str(df_img.iat[0,0]))
    img_name=df_img.iat[0,1]
    ##print(img_server_path)
    ##print(img_name)
    fetch_img(img_server_path, img_name)

    sql_query="select * from dbo.Dataset_Info where session_info_id="+str(i)+" and file_info_id="+str(j)

    #Getting data from sql into pandas
    df=pd.read_sql(sql=sql_query, con=connection)

    #Appending COCO Visulation Terms
    df.loc[df["Occlusion_Status"] == "FarOcclusion" ,"Occlusion_Status"]=1
    df.loc[df["Occlusion_Status"] == "Occluded" ,"Occlusion_Status"]=1
    df.loc[df["Occlusion_Status"] == "NearOcclusion" ,"Occlusion_Status"]=1
    df.loc[df["Occlusion_Status"] == "NotOccluded" ,"Occlusion_Status"]=2
    df.loc[df["Occlusion_Status"] == "NoOcclusion" ,"Occlusion_Status"]=2
    

    #driver
    df1=pd.DataFrame({'object_type_id':[121, 485, 479, 49, 482, 65 or 612, 64 or 611, 4, 483, 8, 3, 7, 2, 6, 1, 5, 109, 111, 487, 484, 481, 486, 480, 615]})
    new_df=df1.merge(df[["object_type_id","U","V","Occlusion_Status"]], on="object_type_id", how="left")
    x_min=new_df["U"].min()-120.0
    x_max=new_df["U"].max()+120.0
    y_min=new_df["V"].min()-70.0
    y_max=new_df["V"].max()+70.0
    if(math.isnan(x_min)):
        x_min=0.0
    if(math.isnan(x_max)):
        x_max=1599.9
    if(math.isnan(y_min)):
        y_min=0.0
    if(math.isnan(y_max)):
        y_max=1299.9
    new_df["U"]=new_df["U"].fillna(0)
    new_df.loc[new_df["U"] < 0 ,"U"]=0
    new_df.loc[new_df["U"] >= 1600 ,"U"]=1599.9
    new_df["V"]=new_df["V"].fillna(0)
    new_df.loc[new_df["V"] >= 1300 ,"V"]=1299.9
    new_df.loc[new_df["V"] < 0 ,"V"]=0
    new_df["Occlusion_Status"]=new_df["Occlusion_Status"].fillna(0)
    driver_U_max=new_df["U"].max()
    driver_V_max=new_df["V"].max()
    driver_check=driver_U_max+driver_V_max
    #print(df)
    #print(new_df)

    df_bb=pd.DataFrame({'object_type_id':[474, 530, 584]})
    new_df_bb=df_bb.merge(df[["object_type_id","centrex1","centrey1","centrex2", "centrey2"]], on="object_type_id", how="left")
    new_df_bb["centrex1"]=new_df_bb["centrex1"].fillna(0.0)
    new_df_bb["centrey1"]=new_df_bb["centrey1"].fillna(0.0)
    new_df_bb["centrex2"]=new_df_bb["centrex2"].fillna(0.0)
    new_df_bb["centrey2"]=new_df_bb["centrey2"].fillna(0.0)
    #print(new_df_bb)


    #passenger
    dfp=pd.DataFrame({'object_type_id':[122, 522, 516, 50, 519, 67 or 652, 66 or 651, 12, 520, 16, 11, 15, 10, 14, 9, 13, 113, 115, 524, 521, 518, 523, 517, 655]})
    new_dfp=dfp.merge(df[["object_type_id","U","V","Occlusion_Status"]], on="object_type_id", how="left")
    xp_min=new_dfp["U"].min()-120.0
    if(math.isnan(xp_min)):
        xp_min=0.0
    xp_max=new_dfp["U"].max()+120.0
    if(math.isnan(xp_max)):
        xp_max=1599.9
    yp_min=new_dfp["V"].min()-70.0
    if(math.isnan(yp_min)):
        yp_min=0.0
    yp_max=new_dfp["V"].max()+70.0
    if(math.isnan(yp_max)):
        yp_max=1299.9
    #print(xp_max, xp_min, yp_max, yp_min)
    new_dfp["U"]=new_dfp["U"].fillna(0)
    new_dfp.loc[new_dfp["U"] >= 1600 ,"U"]=1599.9
    new_dfp.loc[new_dfp["U"] < 0 ,"U"]=0
    new_dfp["V"]=new_dfp["V"].fillna(0)
    new_dfp.loc[new_dfp["V"] >= 1300 ,"V"]=1299.9
    new_dfp.loc[new_dfp["V"] < 0 ,"V"]=0
    new_dfp["Occlusion_Status"]=new_dfp["Occlusion_Status"].fillna(0)
    passenger_U_max=new_dfp["U"].max()
    passenger_V_max=new_dfp["V"].max()
    passenger_check=passenger_U_max+passenger_V_max
    #print(dfp)
    #print(new_dfp)

    dfp_bb=pd.DataFrame({'object_type_id':[511, 531, 624]})
    new_dfp_bb=dfp_bb.merge(df[["object_type_id","centrex1","centrey1","centrex2", "centrey2"]], on="object_type_id", how="left")
    new_dfp_bb["centrex1"]=new_dfp_bb["centrex1"].fillna(0.0)
    new_dfp_bb["centrey1"]=new_dfp_bb["centrey1"].fillna(0.0)
    new_dfp_bb["centrex2"]=new_dfp_bb["centrex2"].fillna(0.0)
    new_dfp_bb["centrey2"]=new_dfp_bb["centrey2"].fillna(0.0)
    #print(new_dfp_bb)


    #rear-middle passenger
    dfr=pd.DataFrame({'object_type_id':[179, 503, 498, 177, 264, 180  or 723, 178 or 722, 163, 501, 159, 161, 157, 164, 160, 162, 158, 191, 189, 505, 502, 500, 504, 499, 720]})
    new_dfr=dfr.merge(df[["object_type_id","U","V","Occlusion_Status"]], on="object_type_id", how="left")
    x_minr=new_dfr["U"].min()-120.0
    x_maxr=new_dfr["U"].max()+120.0
    y_minr=new_dfr["V"].min()-70.0
    y_maxr=new_dfr["V"].max()+70.0
    if(math.isnan(x_minr)):
        x_minr=0.0
    if(math.isnan(x_maxr)):
        x_maxr=1599.9
    if(math.isnan(y_minr)):
        y_minr=0.0
    if(math.isnan(y_maxr)):
        y_maxr=1299.9
    new_dfr["U"]=new_dfr["U"].fillna(0)
    new_dfr.loc[new_dfr["U"] < 0 ,"U"]=0
    new_dfr.loc[new_dfr["U"] >= 1600 ,"U"]=1599.9
    new_dfr["V"]=new_dfr["V"].fillna(0)
    new_dfr.loc[new_dfr["V"] < 0 ,"V"]=0
    new_dfr.loc[new_dfr["V"] >= 1300 ,"V"]=1299.9
    new_dfr["Occlusion_Status"]=new_dfr["Occlusion_Status"].fillna(0)
    rear_middle_passenger_U_max=new_dfr["U"].max()
    rear_middle_passenger_V_max=new_dfr["V"].max()
    rear_middle_passenger_check=rear_middle_passenger_U_max+rear_middle_passenger_V_max
    #print(dfr)
    #print(new_dfr)

    dfr_bb=pd.DataFrame({'object_type_id':[532, 493]})
    new_dfr_bb=dfr_bb.merge(df[["object_type_id","centrex1","centrey1","centrex2", "centrey2"]], on="object_type_id", how="left")
    new_dfr_bb["centrex1"]=new_dfr_bb["centrex1"].fillna(0.0)
    new_dfr_bb["centrey1"]=new_dfr_bb["centrey1"].fillna(0.0)
    new_dfr_bb["centrex2"]=new_dfr_bb["centrex2"].fillna(0.0)
    new_dfr_bb["centrey2"]=new_dfr_bb["centrey2"].fillna(0.0)
    #print(new_dfr_bb)
    
    
    #df2=pd.DataFrame({'bboxes/0':[0],  'bboxes/1':[0],  'bboxes/2':[0],  'bboxes/3':[0],  'keypoints/0/0':[new_df.iat[0,1]],  'keypoints/0/1':[new_df.iat[0,2]],	'keypoints/0/2':[new_df.iat[0,3]],  'keypoints/1/0':[new_df.iat[1,1]],  'keypoints/1/1':[new_df.iat[1,2]],	'keypoints/1/2':[new_df.iat[1,3]],	'keypoints/2/0':[new_df.iat[2,1]],	'keypoints/2/1':[new_df.iat[2,2]],	'keypoints/2/2':[new_df.iat[2,3]],	'keypoints/3/0':[new_df.iat[3,1]],	'keypoints/3/1':[new_df.iat[3,2]],	'keypoints/3/2':[new_df.iat[3,3]],	'keypoints/4/0':[new_df.iat[4,1]],	'keypoints/4/1':[new_df.iat[4,2]],	'keypoints/4/2':[new_df.iat[4,3]],	'keypoints/5/0':[new_df.iat[5,1]],	'keypoints/5/1':[new_df.iat[5,2]],	'keypoints/5/2':[new_df.iat[5,3]],	'keypoints/6/0':[new_df.iat[6,1]],	'keypoints/6/1':[new_df.iat[6,2]],	'keypoints/6/2':[new_df.iat[6,3]],	'keypoints/7/0':[new_df.iat[7,1]],	'keypoints/7/1':[new_df.iat[7,2]],	'keypoints/7/2':[new_df.iat[7,3]],	'keypoints/8/0':[new_df.iat[8,1]],	'keypoints/8/1':[new_df.iat[8,2]],	'keypoints/8/2':[new_df.iat[8,3]],	'keypoints/9/0':[new_df.iat[9,1]],	'keypoints/9/1':[new_df.iat[9,2]],	'keypoints/9/2':[new_df.iat[9,3]],	'keypoints/10/0':[new_df.iat[10,1]],	'keypoints/10/1':[new_df.iat[10,2]],	'keypoints/10/2':[new_df.iat[10,3]],	'keypoints/11/0':[new_df.iat[11,1]],	'keypoints/11/1':[new_df.iat[11,2]],	'keypoints/11/2':[new_df.iat[11,3]],	'keypoints/12/0':[new_df.iat[12,1]],	'keypoints/12/1':[new_df.iat[12,2]],	'keypoints/12/2':[new_df.iat[12,3]],	'keypoints/13/0':[new_df.iat[13,1]],	'keypoints/13/1':[new_df.iat[13,2]],	'keypoints/13/2':[new_df.iat[13,3]],	'keypoints/14/0':[new_df.iat[14,1]],	'keypoints/14/1':[new_df.iat[14,2]],	'keypoints/14/2':[new_df.iat[14,3]],	'keypoints/15/0':[new_df.iat[15,1]],	'keypoints/15/1':[new_df.iat[15,2]],	'keypoints/15/2':[new_df.iat[15,3]],	'keypoints/16/0':[new_df.iat[16,1]],	'keypoints/16/1':[new_df.iat[16,2]],	'keypoints/16/2':[new_df.iat[16,3]],	'keypoints/17/0':[new_df.iat[17,1]],	'keypoints/17/1':[new_df.iat[17,2]],	'keypoints/17/2':[new_df.iat[17,3]],	'keypoints/18/0':[new_df.iat[18,1]],	'keypoints/18/1':[new_df.iat[18,2]],	'keypoints/18/2':[new_df.iat[18,3]],	'keypoints/19/0':[new_df.iat[19,1]],	'keypoints/19/1':[new_df.iat[19,2]],	'keypoints/19/2':[new_df.iat[19,3]],	'keypoints/20/0':[new_df.iat[20,1]],	'keypoints/20/1':[new_df.iat[20,2]],	'keypoints/20/2':[new_df.iat[20,3]],	'keypoints/21/0':[new_df.iat[21,1]],	'keypoints/21/1':[new_df.iat[21,2]],	'keypoints/21/2':[new_df.iat[21,3]],	'keypoints/22/0':[new_df.iat[22,1]],	'keypoints/22/1':[new_df.iat[22,2]],	'keypoints/22/2':[new_df.iat[22,3]]})
    #print(df2)
    #print(df1)

    #driver only
    #"""
    hboxd=[new_df_bb.iat[1,1],new_df_bb.iat[1,2],min(new_df_bb.iat[1,3]+new_df_bb.iat[1,1], 1599.9),min(new_df_bb.iat[1,4]+new_df_bb.iat[1,2], 1299.9)]
    bboxd=[max(x_min,0.0), max(y_min, 0.0), min(x_max, 1600.0), min(y_max, 1299.9)]
    kpd=[[new_df.iat[0,1],new_df.iat[0,2],new_df.iat[0,3]], [new_df.iat[1,1],new_df.iat[1,2],new_df.iat[1,3]], [new_df.iat[2,1],new_df.iat[2,2],new_df.iat[2,3]], [new_df.iat[3,1],new_df.iat[3,2],new_df.iat[3,3]], [new_df.iat[4,1],new_df.iat[4,2],new_df.iat[4,3]], [new_df.iat[5,1],new_df.iat[5,2],new_df.iat[5,3]], [new_df.iat[6,1],new_df.iat[6,2],new_df.iat[6,3]], [new_df.iat[7,1],new_df.iat[7,2],new_df.iat[7,3]], [new_df.iat[8,1],new_df.iat[8,2],new_df.iat[8,3]], [new_df.iat[9,1],new_df.iat[9,2],new_df.iat[9,3]], [new_df.iat[10,1],new_df.iat[10,2],new_df.iat[10,3]], [new_df.iat[11,1],new_df.iat[11,2],new_df.iat[11,3]], [new_df.iat[12,1],new_df.iat[12,2],new_df.iat[12,3]], [new_df.iat[13,1],new_df.iat[13,2],new_df.iat[13,3]], [new_df.iat[14,1],new_df.iat[14,2],new_df.iat[14,3]], [new_df.iat[15,1],new_df.iat[15,2],new_df.iat[15,3]], [new_df.iat[16,1],new_df.iat[16,2],new_df.iat[16,3]], [new_df.iat[17,1],new_df.iat[17,2],new_df.iat[17,3]], [new_df.iat[18,1],new_df.iat[18,2],new_df.iat[18,3]], [new_df.iat[19,1],new_df.iat[19,2],new_df.iat[19,3]], [new_df.iat[20,1],new_df.iat[20,2],new_df.iat[20,3]], [new_df.iat[21,1],new_df.iat[21,2],new_df.iat[21,3]], [new_df.iat[22,1],new_df.iat[22,2],new_df.iat[22,3]], [new_df.iat[23,1],new_df.iat[23,2],new_df.iat[23,3]] ]
    #"""
    #df2=pd.DataFrame({"bboxes":[[[new_df_bb.iat[1,1],new_df_bb.iat[1,2],min(new_df_bb.iat[1,3]+new_df_bb.iat[1,1], 1599.9),min(new_df_bb.iat[1,4]+new_df_bb.iat[1,2], 1299.9)]]], "keypoints":[[[[new_df.iat[0,1],new_df.iat[0,2],new_df.iat[0,3]], [new_df.iat[1,1],new_df.iat[1,2],new_df.iat[1,3]], [new_df.iat[2,1],new_df.iat[2,2],new_df.iat[2,3]], [new_df.iat[3,1],new_df.iat[3,2],new_df.iat[3,3]], [new_df.iat[4,1],new_df.iat[4,2],new_df.iat[4,3]], [new_df.iat[5,1],new_df.iat[5,2],new_df.iat[5,3]], [new_df.iat[6,1],new_df.iat[6,2],new_df.iat[6,3]], [new_df.iat[7,1],new_df.iat[7,2],new_df.iat[7,3]], [new_df.iat[8,1],new_df.iat[8,2],new_df.iat[8,3]], [new_df.iat[9,1],new_df.iat[9,2],new_df.iat[9,3]], [new_df.iat[10,1],new_df.iat[10,2],new_df.iat[10,3]], [new_df.iat[11,1],new_df.iat[11,2],new_df.iat[11,3]], [new_df.iat[12,1],new_df.iat[12,2],new_df.iat[12,3]], [new_df.iat[13,1],new_df.iat[13,2],new_df.iat[13,3]], [new_df.iat[14,1],new_df.iat[14,2],new_df.iat[14,3]], [new_df.iat[15,1],new_df.iat[15,2],new_df.iat[15,3]], [new_df.iat[16,1],new_df.iat[16,2],new_df.iat[16,3]], [new_df.iat[17,1],new_df.iat[17,2],new_df.iat[17,3]], [new_df.iat[18,1],new_df.iat[18,2],new_df.iat[18,3]], [new_df.iat[19,1],new_df.iat[19,2],new_df.iat[19,3]], [new_df.iat[20,1],new_df.iat[20,2],new_df.iat[20,3]], [new_df.iat[21,1],new_df.iat[21,2],new_df.iat[21,3]], [new_df.iat[22,1],new_df.iat[22,2],new_df.iat[22,3]] ]]]}) #, [new_df.iat[23,1],new_df.iat[23,2],new_df.iat[23,3]] ]]]})
    #df2=pd.DataFrame({"bboxes":[[[max(x_min,0.0), max(y_min, 0.0), min(x_max, 1600.0), min(y_max, 1299.9)]]], "keypoints":[[[[new_df.iat[0,1],new_df.iat[0,2],new_df.iat[0,3]], [new_df.iat[1,1],new_df.iat[1,2],new_df.iat[1,3]], [new_df.iat[2,1],new_df.iat[2,2],new_df.iat[2,3]], [new_df.iat[3,1],new_df.iat[3,2],new_df.iat[3,3]], [new_df.iat[4,1],new_df.iat[4,2],new_df.iat[4,3]], [new_df.iat[5,1],new_df.iat[5,2],new_df.iat[5,3]], [new_df.iat[6,1],new_df.iat[6,2],new_df.iat[6,3]], [new_df.iat[7,1],new_df.iat[7,2],new_df.iat[7,3]], [new_df.iat[8,1],new_df.iat[8,2],new_df.iat[8,3]], [new_df.iat[9,1],new_df.iat[9,2],new_df.iat[9,3]], [new_df.iat[10,1],new_df.iat[10,2],new_df.iat[10,3]], [new_df.iat[11,1],new_df.iat[11,2],new_df.iat[11,3]], [new_df.iat[12,1],new_df.iat[12,2],new_df.iat[12,3]], [new_df.iat[13,1],new_df.iat[13,2],new_df.iat[13,3]], [new_df.iat[14,1],new_df.iat[14,2],new_df.iat[14,3]], [new_df.iat[15,1],new_df.iat[15,2],new_df.iat[15,3]], [new_df.iat[16,1],new_df.iat[16,2],new_df.iat[16,3]], [new_df.iat[17,1],new_df.iat[17,2],new_df.iat[17,3]], [new_df.iat[18,1],new_df.iat[18,2],new_df.iat[18,3]], [new_df.iat[19,1],new_df.iat[19,2],new_df.iat[19,3]], [new_df.iat[20,1],new_df.iat[20,2],new_df.iat[20,3]], [new_df.iat[21,1],new_df.iat[21,2],new_df.iat[21,3]], [new_df.iat[22,1],new_df.iat[22,2],new_df.iat[22,3]], [new_df.iat[23,1],new_df.iat[23,2],new_df.iat[23,3]] ]]]})
    
    #passenger only
    #"""
    kpp=[[new_dfp.iat[0,1],new_dfp.iat[0,2],new_dfp.iat[0,3]], [new_dfp.iat[1,1],new_dfp.iat[1,2],new_dfp.iat[1,3]], [new_dfp.iat[2,1],new_dfp.iat[2,2],new_dfp.iat[2,3]], [new_dfp.iat[3,1],new_dfp.iat[3,2],new_dfp.iat[3,3]], [new_dfp.iat[4,1],new_dfp.iat[4,2],new_dfp.iat[4,3]], [new_dfp.iat[5,1],new_dfp.iat[5,2],new_dfp.iat[5,3]], [new_dfp.iat[6,1],new_dfp.iat[6,2],new_dfp.iat[6,3]], [new_dfp.iat[7,1],new_dfp.iat[7,2],new_dfp.iat[7,3]], [new_dfp.iat[8,1],new_dfp.iat[8,2],new_dfp.iat[8,3]], [new_dfp.iat[9,1],new_dfp.iat[9,2],new_dfp.iat[9,3]], [new_dfp.iat[10,1],new_dfp.iat[10,2],new_dfp.iat[10,3]], [new_dfp.iat[11,1],new_dfp.iat[11,2],new_dfp.iat[11,3]], [new_dfp.iat[12,1],new_dfp.iat[12,2],new_dfp.iat[12,3]], [new_dfp.iat[13,1],new_dfp.iat[13,2],new_dfp.iat[13,3]], [new_dfp.iat[14,1],new_dfp.iat[14,2],new_dfp.iat[14,3]], [new_dfp.iat[15,1],new_dfp.iat[15,2],new_dfp.iat[15,3]], [new_dfp.iat[16,1],new_dfp.iat[16,2],new_dfp.iat[16,3]], [new_dfp.iat[17,1],new_dfp.iat[17,2],new_dfp.iat[17,3]], [new_dfp.iat[18,1],new_dfp.iat[18,2],new_dfp.iat[18,3]], [new_dfp.iat[19,1],new_dfp.iat[19,2],new_dfp.iat[19,3]], [new_dfp.iat[20,1],new_dfp.iat[20,2],new_dfp.iat[20,3]], [new_dfp.iat[21,1],new_dfp.iat[21,2],new_dfp.iat[21,3]], [new_dfp.iat[22,1],new_dfp.iat[22,2],new_dfp.iat[22,3]], [new_dfp.iat[23,1],new_dfp.iat[23,2],new_dfp.iat[23,3]] ]
    bboxp=[max(xp_min,0.0), max(yp_min, 0.0), min(xp_max, 1600.0), min(yp_max, 1299.9)]
    hboxp=[new_dfp_bb.iat[1,1],new_dfp_bb.iat[1,2],min(new_dfp_bb.iat[1,3]+new_dfp_bb.iat[1,1], 1599.9),min(new_dfp_bb.iat[1,4]+new_dfp_bb.iat[1,2], 1299.9)]
    #"""
    #df2=pd.DataFrame({"bboxes":[[[new_dfp_bb.iat[1,1],new_dfp_bb.iat[1,2],min(new_dfp_bb.iat[1,3]+new_dfp_bb.iat[1,1], 1599.9),min(new_dfp_bb.iat[1,4]+new_dfp_bb.iat[1,2], 1299.9)]]], "keypoints":[[[[new_dfp.iat[0,1],new_dfp.iat[0,2],new_dfp.iat[0,3]], [new_dfp.iat[1,1],new_dfp.iat[1,2],new_dfp.iat[1,3]], [new_dfp.iat[2,1],new_dfp.iat[2,2],new_dfp.iat[2,3]], [new_dfp.iat[3,1],new_dfp.iat[3,2],new_dfp.iat[3,3]], [new_dfp.iat[4,1],new_dfp.iat[4,2],new_dfp.iat[4,3]], [new_dfp.iat[5,1],new_dfp.iat[5,2],new_dfp.iat[5,3]], [new_dfp.iat[6,1],new_dfp.iat[6,2],new_dfp.iat[6,3]], [new_dfp.iat[7,1],new_dfp.iat[7,2],new_dfp.iat[7,3]], [new_dfp.iat[8,1],new_dfp.iat[8,2],new_dfp.iat[8,3]], [new_dfp.iat[9,1],new_dfp.iat[9,2],new_dfp.iat[9,3]], [new_dfp.iat[10,1],new_dfp.iat[10,2],new_dfp.iat[10,3]], [new_dfp.iat[11,1],new_dfp.iat[11,2],new_dfp.iat[11,3]], [new_dfp.iat[12,1],new_dfp.iat[12,2],new_dfp.iat[12,3]], [new_dfp.iat[13,1],new_dfp.iat[13,2],new_dfp.iat[13,3]], [new_dfp.iat[14,1],new_dfp.iat[14,2],new_dfp.iat[14,3]], [new_dfp.iat[15,1],new_dfp.iat[15,2],new_dfp.iat[15,3]], [new_dfp.iat[16,1],new_dfp.iat[16,2],new_dfp.iat[16,3]], [new_dfp.iat[17,1],new_dfp.iat[17,2],new_dfp.iat[17,3]], [new_dfp.iat[18,1],new_dfp.iat[18,2],new_dfp.iat[18,3]], [new_dfp.iat[19,1],new_dfp.iat[19,2],new_dfp.iat[19,3]], [new_dfp.iat[20,1],new_dfp.iat[20,2],new_dfp.iat[20,3]], [new_dfp.iat[21,1],new_dfp.iat[21,2],new_dfp.iat[21,3]], [new_dfp.iat[22,1],new_dfp.iat[22,2],new_dfp.iat[22,3]], [new_dfp.iat[23,1],new_dfp.iat[23,2],new_dfp.iat[23,3]] ]]]})
    #df2=pd.DataFrame({"bboxes":[[[max(xp_min,0.0), max(yp_min, 0.0), min(xp_max, 1600.0), min(yp_max, 1299.9)]]], "keypoints":[[[[new_dfp.iat[0,1],new_dfp.iat[0,2],new_dfp.iat[0,3]], [new_dfp.iat[1,1],new_dfp.iat[1,2],new_dfp.iat[1,3]], [new_dfp.iat[2,1],new_dfp.iat[2,2],new_dfp.iat[2,3]], [new_dfp.iat[3,1],new_dfp.iat[3,2],new_dfp.iat[3,3]], [new_dfp.iat[4,1],new_dfp.iat[4,2],new_dfp.iat[4,3]], [new_dfp.iat[5,1],new_dfp.iat[5,2],new_dfp.iat[5,3]], [new_dfp.iat[6,1],new_dfp.iat[6,2],new_dfp.iat[6,3]], [new_dfp.iat[7,1],new_dfp.iat[7,2],new_dfp.iat[7,3]], [new_dfp.iat[8,1],new_dfp.iat[8,2],new_dfp.iat[8,3]], [new_dfp.iat[9,1],new_dfp.iat[9,2],new_dfp.iat[9,3]], [new_dfp.iat[10,1],new_dfp.iat[10,2],new_dfp.iat[10,3]], [new_dfp.iat[11,1],new_dfp.iat[11,2],new_dfp.iat[11,3]], [new_dfp.iat[12,1],new_dfp.iat[12,2],new_dfp.iat[12,3]], [new_dfp.iat[13,1],new_dfp.iat[13,2],new_dfp.iat[13,3]], [new_dfp.iat[14,1],new_dfp.iat[14,2],new_dfp.iat[14,3]], [new_dfp.iat[15,1],new_dfp.iat[15,2],new_dfp.iat[15,3]], [new_dfp.iat[16,1],new_dfp.iat[16,2],new_dfp.iat[16,3]], [new_dfp.iat[17,1],new_dfp.iat[17,2],new_dfp.iat[17,3]], [new_dfp.iat[18,1],new_dfp.iat[18,2],new_dfp.iat[18,3]], [new_dfp.iat[19,1],new_dfp.iat[19,2],new_dfp.iat[19,3]], [new_dfp.iat[20,1],new_dfp.iat[20,2],new_dfp.iat[20,3]], [new_dfp.iat[21,1],new_dfp.iat[21,2],new_dfp.iat[21,3]], [new_dfp.iat[22,1],new_dfp.iat[22,2],new_dfp.iat[22,3]], [new_dfp.iat[23,1],new_dfp.iat[23,2],new_dfp.iat[23,3]] ]]]})

    #rear-middle passenger only
    #"""
    kpr=[[new_dfr.iat[0,1],new_dfr.iat[0,2],new_dfr.iat[0,3]], [new_dfr.iat[1,1],new_dfr.iat[1,2],new_dfr.iat[1,3]], [new_dfr.iat[2,1],new_dfr.iat[2,2],new_dfr.iat[2,3]], [new_dfr.iat[3,1],new_dfr.iat[3,2],new_dfr.iat[3,3]], [new_dfr.iat[4,1],new_dfr.iat[4,2],new_dfr.iat[4,3]], [new_dfr.iat[5,1],new_dfr.iat[5,2],new_dfr.iat[5,3]], [new_dfr.iat[6,1],new_dfr.iat[6,2],new_dfr.iat[6,3]], [new_dfr.iat[7,1],new_dfr.iat[7,2],new_dfr.iat[7,3]], [new_dfr.iat[8,1],new_dfr.iat[8,2],new_dfr.iat[8,3]], [new_dfr.iat[9,1],new_dfr.iat[9,2],new_dfr.iat[9,3]], [new_dfr.iat[10,1],new_dfr.iat[10,2],new_dfr.iat[10,3]], [new_dfr.iat[11,1],new_dfr.iat[11,2],new_dfr.iat[11,3]], [new_dfr.iat[12,1],new_dfr.iat[12,2],new_dfr.iat[12,3]], [new_dfr.iat[13,1],new_dfr.iat[13,2],new_dfr.iat[13,3]], [new_dfr.iat[14,1],new_dfr.iat[14,2],new_dfr.iat[14,3]], [new_dfr.iat[15,1],new_dfr.iat[15,2],new_dfr.iat[15,3]], [new_dfr.iat[16,1],new_dfr.iat[16,2],new_dfr.iat[16,3]], [new_dfr.iat[17,1],new_dfr.iat[17,2],new_dfr.iat[17,3]], [new_dfr.iat[18,1],new_dfr.iat[18,2],new_dfr.iat[18,3]], [new_dfr.iat[19,1],new_dfr.iat[19,2],new_dfr.iat[19,3]], [new_dfr.iat[20,1],new_dfr.iat[20,2],new_dfr.iat[20,3]], [new_dfr.iat[21,1],new_dfr.iat[21,2],new_dfr.iat[21,3]], [new_dfr.iat[22,1],new_dfr.iat[22,2],new_dfr.iat[22,3]], [new_dfr.iat[23,1],new_dfr.iat[23,2],new_dfr.iat[23,3]] ]
    bboxr=[max(x_minr,0.0), max(y_minr, 0.0), min(x_maxr, 1600.0), min(y_maxr, 1299.9)]
    hboxr=[new_dfr_bb.iat[1,1],new_dfr_bb.iat[1,2],min(new_dfr_bb.iat[1,3]+new_dfr_bb.iat[1,1], 1599.9),min(new_dfr_bb.iat[1,4]+new_dfr_bb.iat[1,2], 1299.9)]
    #"""
    #df2=pd.DataFrame({"bboxes":[[[new_dfp_bb.iat[1,1],new_dfp_bb.iat[1,2],min(new_dfp_bb.iat[1,3]+new_dfp_bb.iat[1,1], 1599.9),min(new_dfp_bb.iat[1,4]+new_dfp_bb.iat[1,2], 1299.9)]]], "keypoints":[[[[new_dfp.iat[0,1],new_dfp.iat[0,2],new_dfp.iat[0,3]], [new_dfp.iat[1,1],new_dfp.iat[1,2],new_dfp.iat[1,3]], [new_dfp.iat[2,1],new_dfp.iat[2,2],new_dfp.iat[2,3]], [new_dfp.iat[3,1],new_dfp.iat[3,2],new_dfp.iat[3,3]], [new_dfp.iat[4,1],new_dfp.iat[4,2],new_dfp.iat[4,3]], [new_dfp.iat[5,1],new_dfp.iat[5,2],new_dfp.iat[5,3]], [new_dfp.iat[6,1],new_dfp.iat[6,2],new_dfp.iat[6,3]], [new_dfp.iat[7,1],new_dfp.iat[7,2],new_dfp.iat[7,3]], [new_dfp.iat[8,1],new_dfp.iat[8,2],new_dfp.iat[8,3]], [new_dfp.iat[9,1],new_dfp.iat[9,2],new_dfp.iat[9,3]], [new_dfp.iat[10,1],new_dfp.iat[10,2],new_dfp.iat[10,3]], [new_dfp.iat[11,1],new_dfp.iat[11,2],new_dfp.iat[11,3]], [new_dfp.iat[12,1],new_dfp.iat[12,2],new_dfp.iat[12,3]], [new_dfp.iat[13,1],new_dfp.iat[13,2],new_dfp.iat[13,3]], [new_dfp.iat[14,1],new_dfp.iat[14,2],new_dfp.iat[14,3]], [new_dfp.iat[15,1],new_dfp.iat[15,2],new_dfp.iat[15,3]], [new_dfp.iat[16,1],new_dfp.iat[16,2],new_dfp.iat[16,3]], [new_dfp.iat[17,1],new_dfp.iat[17,2],new_dfp.iat[17,3]], [new_dfp.iat[18,1],new_dfp.iat[18,2],new_dfp.iat[18,3]], [new_dfp.iat[19,1],new_dfp.iat[19,2],new_dfp.iat[19,3]], [new_dfp.iat[20,1],new_dfp.iat[20,2],new_dfp.iat[20,3]], [new_dfp.iat[21,1],new_dfp.iat[21,2],new_dfp.iat[21,3]], [new_dfp.iat[22,1],new_dfp.iat[22,2],new_dfp.iat[22,3]], [new_dfp.iat[23,1],new_dfp.iat[23,2],new_dfp.iat[23,3]] ]]]})
    #df2=pd.DataFrame({"bboxes":[[[max(xp_min,0.0), max(yp_min, 0.0), min(xp_max, 1600.0), min(yp_max, 1299.9)]]], "keypoints":[[[[new_dfp.iat[0,1],new_dfp.iat[0,2],new_dfp.iat[0,3]], [new_dfp.iat[1,1],new_dfp.iat[1,2],new_dfp.iat[1,3]], [new_dfp.iat[2,1],new_dfp.iat[2,2],new_dfp.iat[2,3]], [new_dfp.iat[3,1],new_dfp.iat[3,2],new_dfp.iat[3,3]], [new_dfp.iat[4,1],new_dfp.iat[4,2],new_dfp.iat[4,3]], [new_dfp.iat[5,1],new_dfp.iat[5,2],new_dfp.iat[5,3]], [new_dfp.iat[6,1],new_dfp.iat[6,2],new_dfp.iat[6,3]], [new_dfp.iat[7,1],new_dfp.iat[7,2],new_dfp.iat[7,3]], [new_dfp.iat[8,1],new_dfp.iat[8,2],new_dfp.iat[8,3]], [new_dfp.iat[9,1],new_dfp.iat[9,2],new_dfp.iat[9,3]], [new_dfp.iat[10,1],new_dfp.iat[10,2],new_dfp.iat[10,3]], [new_dfp.iat[11,1],new_dfp.iat[11,2],new_dfp.iat[11,3]], [new_dfp.iat[12,1],new_dfp.iat[12,2],new_dfp.iat[12,3]], [new_dfp.iat[13,1],new_dfp.iat[13,2],new_dfp.iat[13,3]], [new_dfp.iat[14,1],new_dfp.iat[14,2],new_dfp.iat[14,3]], [new_dfp.iat[15,1],new_dfp.iat[15,2],new_dfp.iat[15,3]], [new_dfp.iat[16,1],new_dfp.iat[16,2],new_dfp.iat[16,3]], [new_dfp.iat[17,1],new_dfp.iat[17,2],new_dfp.iat[17,3]], [new_dfp.iat[18,1],new_dfp.iat[18,2],new_dfp.iat[18,3]], [new_dfp.iat[19,1],new_dfp.iat[19,2],new_dfp.iat[19,3]], [new_dfp.iat[20,1],new_dfp.iat[20,2],new_dfp.iat[20,3]], [new_dfp.iat[21,1],new_dfp.iat[21,2],new_dfp.iat[21,3]], [new_dfp.iat[22,1],new_dfp.iat[22,2],new_dfp.iat[22,3]], [new_dfp.iat[23,1],new_dfp.iat[23,2],new_dfp.iat[23,3]] ]]]})

    #passenger and both driver_old
    #df2=pd.DataFrame({"bboxes":[[[new_df_bb.iat[1,1],new_df_bb.iat[1,2],min(new_df_bb.iat[1,3]+new_df_bb.iat[1,1], 1599.9),min(new_df_bb.iat[1,4]+new_df_bb.iat[1,2], 1299.9)],[new_dfp_bb.iat[1,1],new_dfp_bb.iat[1,2],min(new_dfp_bb.iat[1,3]+new_dfp_bb.iat[1,1], 1599.9),min(new_dfp_bb.iat[1,4]+new_dfp_bb.iat[1,2], 1299.9)]]], "keypoints":[[[[new_df.iat[0,1],new_df.iat[0,2],new_df.iat[0,3]], [new_df.iat[1,1],new_df.iat[1,2],new_df.iat[1,3]], [new_df.iat[2,1],new_df.iat[2,2],new_df.iat[2,3]], [new_df.iat[3,1],new_df.iat[3,2],new_df.iat[3,3]], [new_df.iat[4,1],new_df.iat[4,2],new_df.iat[4,3]], [new_df.iat[5,1],new_df.iat[5,2],new_df.iat[5,3]], [new_df.iat[6,1],new_df.iat[6,2],new_df.iat[6,3]], [new_df.iat[7,1],new_df.iat[7,2],new_df.iat[7,3]], [new_df.iat[8,1],new_df.iat[8,2],new_df.iat[8,3]], [new_df.iat[9,1],new_df.iat[9,2],new_df.iat[9,3]], [new_df.iat[10,1],new_df.iat[10,2],new_df.iat[10,3]], [new_df.iat[11,1],new_df.iat[11,2],new_df.iat[11,3]], [new_df.iat[12,1],new_df.iat[12,2],new_df.iat[12,3]], [new_df.iat[13,1],new_df.iat[13,2],new_df.iat[13,3]], [new_df.iat[14,1],new_df.iat[14,2],new_df.iat[14,3]], [new_df.iat[15,1],new_df.iat[15,2],new_df.iat[15,3]], [new_df.iat[16,1],new_df.iat[16,2],new_df.iat[16,3]], [new_df.iat[17,1],new_df.iat[17,2],new_df.iat[17,3]], [new_df.iat[18,1],new_df.iat[18,2],new_df.iat[18,3]], [new_df.iat[19,1],new_df.iat[19,2],new_df.iat[19,3]], [new_df.iat[20,1],new_df.iat[20,2],new_df.iat[20,3]], [new_df.iat[21,1],new_df.iat[21,2],new_df.iat[21,3]], [new_df.iat[22,1],new_df.iat[22,2],new_df.iat[22,3]], [new_df.iat[23,1],new_df.iat[23,2],new_df.iat[23,3]] ], [[new_dfp.iat[0,1],new_dfp.iat[0,2],new_dfp.iat[0,3]], [new_dfp.iat[1,1],new_dfp.iat[1,2],new_dfp.iat[1,3]], [new_dfp.iat[2,1],new_dfp.iat[2,2],new_dfp.iat[2,3]], [new_dfp.iat[3,1],new_dfp.iat[3,2],new_dfp.iat[3,3]], [new_dfp.iat[4,1],new_dfp.iat[4,2],new_dfp.iat[4,3]], [new_dfp.iat[5,1],new_dfp.iat[5,2],new_dfp.iat[5,3]], [new_dfp.iat[6,1],new_dfp.iat[6,2],new_dfp.iat[6,3]], [new_dfp.iat[7,1],new_dfp.iat[7,2],new_dfp.iat[7,3]], [new_dfp.iat[8,1],new_dfp.iat[8,2],new_dfp.iat[8,3]], [new_dfp.iat[9,1],new_dfp.iat[9,2],new_dfp.iat[9,3]], [new_dfp.iat[10,1],new_dfp.iat[10,2],new_dfp.iat[10,3]], [new_dfp.iat[11,1],new_dfp.iat[11,2],new_dfp.iat[11,3]], [new_dfp.iat[12,1],new_dfp.iat[12,2],new_dfp.iat[12,3]], [new_dfp.iat[13,1],new_dfp.iat[13,2],new_dfp.iat[13,3]], [new_dfp.iat[14,1],new_dfp.iat[14,2],new_dfp.iat[14,3]], [new_dfp.iat[15,1],new_dfp.iat[15,2],new_dfp.iat[15,3]], [new_dfp.iat[16,1],new_dfp.iat[16,2],new_dfp.iat[16,3]], [new_dfp.iat[17,1],new_dfp.iat[17,2],new_dfp.iat[17,3]], [new_dfp.iat[18,1],new_dfp.iat[18,2],new_dfp.iat[18,3]], [new_dfp.iat[19,1],new_dfp.iat[19,2],new_dfp.iat[19,3]], [new_dfp.iat[20,1],new_dfp.iat[20,2],new_dfp.iat[20,3]], [new_dfp.iat[21,1],new_dfp.iat[21,2],new_dfp.iat[21,3]], [new_dfp.iat[22,1],new_dfp.iat[22,2],new_dfp.iat[22,3]], [new_dfp.iat[23,1],new_dfp.iat[23,2],new_dfp.iat[23,3]] ]]]})
    #df2=pd.DataFrame({"bboxes":[[[max(x_min,0.0), max(y_min, 0.0), min(x_max, 1600.0), min(y_max, 1299.9)],[max(xp_min,0.0), max(yp_min, 0.0), min(xp_max, 1600.0), min(yp_max, 1299.9)]]], "keypoints":[[[[new_df.iat[0,1],new_df.iat[0,2],new_df.iat[0,3]], [new_df.iat[1,1],new_df.iat[1,2],new_df.iat[1,3]], [new_df.iat[2,1],new_df.iat[2,2],new_df.iat[2,3]], [new_df.iat[3,1],new_df.iat[3,2],new_df.iat[3,3]], [new_df.iat[4,1],new_df.iat[4,2],new_df.iat[4,3]], [new_df.iat[5,1],new_df.iat[5,2],new_df.iat[5,3]], [new_df.iat[6,1],new_df.iat[6,2],new_df.iat[6,3]], [new_df.iat[7,1],new_df.iat[7,2],new_df.iat[7,3]], [new_df.iat[8,1],new_df.iat[8,2],new_df.iat[8,3]], [new_df.iat[9,1],new_df.iat[9,2],new_df.iat[9,3]], [new_df.iat[10,1],new_df.iat[10,2],new_df.iat[10,3]], [new_df.iat[11,1],new_df.iat[11,2],new_df.iat[11,3]], [new_df.iat[12,1],new_df.iat[12,2],new_df.iat[12,3]], [new_df.iat[13,1],new_df.iat[13,2],new_df.iat[13,3]], [new_df.iat[14,1],new_df.iat[14,2],new_df.iat[14,3]], [new_df.iat[15,1],new_df.iat[15,2],new_df.iat[15,3]], [new_df.iat[16,1],new_df.iat[16,2],new_df.iat[16,3]], [new_df.iat[17,1],new_df.iat[17,2],new_df.iat[17,3]], [new_df.iat[18,1],new_df.iat[18,2],new_df.iat[18,3]], [new_df.iat[19,1],new_df.iat[19,2],new_df.iat[19,3]], [new_df.iat[20,1],new_df.iat[20,2],new_df.iat[20,3]], [new_df.iat[21,1],new_df.iat[21,2],new_df.iat[21,3]], [new_df.iat[22,1],new_df.iat[22,2],new_df.iat[22,3]], [new_df.iat[23,1],new_df.iat[23,2],new_df.iat[23,3]] ], [[new_dfp.iat[0,1],new_dfp.iat[0,2],new_dfp.iat[0,3]], [new_dfp.iat[1,1],new_dfp.iat[1,2],new_dfp.iat[1,3]], [new_dfp.iat[2,1],new_dfp.iat[2,2],new_dfp.iat[2,3]], [new_dfp.iat[3,1],new_dfp.iat[3,2],new_dfp.iat[3,3]], [new_dfp.iat[4,1],new_dfp.iat[4,2],new_dfp.iat[4,3]], [new_dfp.iat[5,1],new_dfp.iat[5,2],new_dfp.iat[5,3]], [new_dfp.iat[6,1],new_dfp.iat[6,2],new_dfp.iat[6,3]], [new_dfp.iat[7,1],new_dfp.iat[7,2],new_dfp.iat[7,3]], [new_dfp.iat[8,1],new_dfp.iat[8,2],new_dfp.iat[8,3]], [new_dfp.iat[9,1],new_dfp.iat[9,2],new_dfp.iat[9,3]], [new_dfp.iat[10,1],new_dfp.iat[10,2],new_dfp.iat[10,3]], [new_dfp.iat[11,1],new_dfp.iat[11,2],new_dfp.iat[11,3]], [new_dfp.iat[12,1],new_dfp.iat[12,2],new_dfp.iat[12,3]], [new_dfp.iat[13,1],new_dfp.iat[13,2],new_dfp.iat[13,3]], [new_dfp.iat[14,1],new_dfp.iat[14,2],new_dfp.iat[14,3]], [new_dfp.iat[15,1],new_dfp.iat[15,2],new_dfp.iat[15,3]], [new_dfp.iat[16,1],new_dfp.iat[16,2],new_dfp.iat[16,3]], [new_dfp.iat[17,1],new_dfp.iat[17,2],new_dfp.iat[17,3]], [new_dfp.iat[18,1],new_dfp.iat[18,2],new_dfp.iat[18,3]], [new_dfp.iat[19,1],new_dfp.iat[19,2],new_dfp.iat[19,3]], [new_dfp.iat[20,1],new_dfp.iat[20,2],new_dfp.iat[20,3]], [new_dfp.iat[21,1],new_dfp.iat[21,2],new_dfp.iat[21,3]], [new_dfp.iat[22,1],new_dfp.iat[22,2],new_dfp.iat[22,3]], [new_dfp.iat[23,1],new_dfp.iat[23,2],new_dfp.iat[23,3]] ]]]})
    
    if(driver_check>0 and passenger_check==0 and rear_middle_passenger_check==0):
        dfb=pd.DataFrame({"bboxes":[[hboxd]], "keypoints": [[kpd]]})
        df2=pd.DataFrame({"bboxes":[[bboxd]], "keypoints": [[kpd]]})

    elif(driver_check==0 and passenger_check>0 and rear_middle_passenger_check==0):
        dfb=pd.DataFrame({"bboxes":[[hboxp]], "keypoints": [[kpp]]})
        df2=pd.DataFrame({"bboxes":[[bboxp]], "keypoints": [[kpp]]})

    elif(driver_check==0 and passenger_check==0 and rear_middle_passenger_check>0):
        dfb=pd.DataFrame({"bboxes":[[hboxr]], "keypoints": [[kpr]]})
        df2=pd.DataFrame({"bboxes":[[bboxr]], "keypoints": [[kpr]]})

    elif(driver_check>0 and passenger_check>0 and rear_middle_passenger_check==0):
        dfb=pd.DataFrame({"bboxes":[[hboxd, hboxp]], "keypoints": [[kpd, kpp]]})
        df2=pd.DataFrame({"bboxes":[[bboxd, bboxp]], "keypoints": [[kpd, kpp]]})

    elif(driver_check>0 and passenger_check==0 and rear_middle_passenger_check>0):
        dfb=pd.DataFrame({"bboxes":[[hboxd, hboxr]], "keypoints": [[kpd, kpr]]})
        df2=pd.DataFrame({"bboxes":[[bboxd, bboxr]], "keypoints": [[kpd, kpr]]})

    elif(driver_check==0 and passenger_check>0 and rear_middle_passenger_check>0):
        dfb=pd.DataFrame({"bboxes":[[hboxp, hboxr]], "keypoints": [[kpp, kpr]]})
        df2=pd.DataFrame({"bboxes":[[bboxp, bboxr]], "keypoints": [[kpp, kpr]]})

    elif(driver_check>0 and passenger_check>0 and rear_middle_passenger_check>0):
        dfb=pd.DataFrame({"bboxes":[[hboxd, hboxp, hboxr]], "keypoints": [[kpd, kpp, kpr]]})
        df2=pd.DataFrame({"bboxes":[[bboxd, bboxp, bboxr]], "keypoints": [[kpd, kpp, kpr]]})

    #Annoation File Export in Json Format#
    #df2.to_csv(os.environ["userprofile"] + "\\Extract\\SOD\\DATA\\ANNOTATIONS\\master.csv", index = False)
    df2.to_json(os.environ["userprofile"] + "\\Extract\\SOD_24\\DATA2\\annotations\\"+os.path.splitext(str(img_name))[0]+".json",orient='records', lines=True)
    dfb.to_json(os.environ["userprofile"] + "\\Extract\\SOD\\DATA2\\annotations\\"+os.path.splitext(str(img_name))[0]+".json",orient='records', lines=True)
    #Exporting the data on the Desktop(.to_csv for CSV Export, .to_json for CSV Export)
    #df.to_csv(os.environ["userprofile"] + "\\Extract\\SOD\\DATA\\" +os.path.splitext(str(img_name))[0]+ ".csv", index = False)

    COUNT=COUNT+1
    
  intermediate=time.time()
  print("Images and their respective Annotations Downloaded Count:",COUNT, "| COMPLETED SESSION ID:", i, "| Time Lapsed:", intermediate-start, " seconds")

end=time.time()
# Display Notifiction to User
notification.notify(title="Report Status!!!",  message=f"Tuhh...Duhh...Data has been successfully exported.\ \nTotal Images: {COUNT} in {end-start} seconds", timeout = 6000)
cursor.close()
connection.close()
