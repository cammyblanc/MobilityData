class GoogleMobilityDf():
    def __init__(self):
        pass
    def execute(dtFilt,area):
        import os
        import pandas as pd
        import requests
        from io import BytesIO
        from io import StringIO
        import re

        urls=[
            'https://www.gstatic.com/covid19/mobility/Region_Mobility_Report_CSVs.zip',
             ]

        import requests, zipfile
        r = requests.get(urls[0], stream=True)

        filebytes = BytesIO(r.content)
        zipfile   = zipfile.ZipFile(filebytes)
        lstZip=zipfile.namelist()

        lstJP=[]
        for i in lstZip:
            try:
                lstJP.append(re.match(r'.*_JP_.*', i).group())
            except:
                None
                
        df=pd.DataFrame()
        for i in lstJP:
            zipopen = zipfile.open(i)
            strFile = zipopen.read()
            data = StringIO(strFile.decode("utf-8"))
            dfGgl = pd.read_csv(data, sep=",")
            df=pd.concat([df,dfGgl], axis=0).reset_index()
 
        lstColumns=['date',
                    'sub_region_1',
                    'retail_and_recreation_percent_change_from_baseline',
                    'grocery_and_pharmacy_percent_change_from_baseline',
                    'parks_percent_change_from_baseline',
                    'transit_stations_percent_change_from_baseline',
                    'workplaces_percent_change_from_baseline',
                    'residential_percent_change_from_baseline'
                   ]
        
        # df=df[df.sub_region_1.notna()==False].loc[:,lstColumns]
        df=df.fillna('Japan')
        df=df[df.sub_region_1==area].loc[:,lstColumns]
        df=df.reset_index(drop=True)
        df.columns=['dt','sub_region_1','mobitily_retail','mobility_grocery','mobility_parks','mobility_transit','mobility_work','mobility_residence']
        df.dt=pd.to_datetime(df['dt'])
        df=df[df.dt<dtFilt]
        df['mobility_av']=(df.mobility_transit+df.mobitily_retail)/2
 
        lstAv=list()
        lstMobAv=df.mobility_av.rolling(7).mean().shift(-3).fillna(method='bfill').dropna().tolist()
        
        for i in lstMobAv:
            lstAv.append(i)

        for i in [8,9,10]:
            lstAv.append(df.mobility_av.tail(i).mean())

        df['mobility_av_roll7']=pd.DataFrame(lstAv)

        return df