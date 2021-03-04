# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 15:03:25 2021

@author: Anthony Segura García
@contact: asegura@imn.ac.cr

Departamento de Red Meteorológica y Procesamiento de Datos
Instituto Meteorológico Nacional
"""

import pandas as pd
import numpy as np
from itertools import groupby
from datetime import datetime
from datetime import timedelta
import glob 

#Se cargan los datos
filenames = glob.glob("*.xlsx")
file = pd.read_excel(filenames[0], header=None, names=["fecha", "TEMP_C_Avg", "RH_Avg"])

###### Ingreso de número de estación manualmente ######

#Se crea un diccionario con las estaciones que tienen Higrotermógrafo    
list_est = {'Santa Clara': 69579, 'Dulce Nombre': 73048, 'Sitio Mata': 73103, 'Finca 3, Llano Grande': 84125, 'Damas': 90009}

#Se crea una función que devuelve el nombre de la estación según el número
def get_key(val):
    for key, value in list_est.items():
         if val == value:
             return key

#Se ingresa el número de estación
def Est():
    while True:
        est = input("Por favor ingrese el número de la estación: " + "\n")
        try:        
            est = int(est)
            
            if est in list_est.values():
                print("\nLa estación ingresada es:", get_key(est))
                break
            else:
                print("***** Número de estación incorrecto, vuelva a ingresar el número de estación. *****")
                continue

        except ValueError:
            print("***** Dato ingresado incorrecto. *****")
            continue
        else:
            break
    return est

est_num = Est()

#Se guarda el número de cuenca y el número de estación por separado
est_cuenca = int(str(est_num)[:2])
num_est = int(str(est_num)[2:])

###### Ingreso de número de estación manualmente ######

###### Ingreso de fechas manualmente ######

def InputFechaFinal():
    while True:
        input_fecha = input("Por favor ingrese la fecha final de los datos en el siguiente formato YYYY-MM-DD-HH" + "\n")
        try:        
            fecha_final = str(input_fecha)
            
            if datetime.strptime(fecha_final,"%Y-%m-%d-%H"):
                print("\n" + "***** Fecha final ingresada correctamente. *****" + "\n")
            else:
                print("\n" + "***** El formato es incorrecto, vuelva a ingresar la fecha final de nuevo. *****" + "\n")
                continue
        except ValueError:
            print("\n" + "***** Dato ingresado incorrecto. *****" + "\n")
            continue
        else:
            break
    return fecha_final

def InputFecha():
    while True:
        input_fecha = input("Por favor ingrese la fecha de inicio de los datos en el siguiente formato YYYY-MM-DD-HH" + "\n")
        try:        
            fecha_inicial = str(input_fecha)
            
            if datetime.strptime(fecha_inicial,"%Y-%m-%d-%H"):
                print("\n" + "***** Fecha inicial ingresada correctamente. *****" + "\n")
                
                fecha_final = InputFechaFinal()
                
                fecha_inicial = datetime.strptime(fecha_inicial, "%Y-%m-%d-%H")
                fecha_final = datetime.strptime(fecha_final, "%Y-%m-%d-%H")
                
                if fecha_final > fecha_inicial:
                    print("\n" + "***** La fecha inicial de los datos es: ",fecha_inicial)
                    print("\n" + "***** La fecha final de los datos es: ",fecha_final, "\n")
                    break
                else:
                    print("\n" + "***** La fecha final es menor o igual que la fecha inicial, vuelva a ingresar ambas fechas. *****" + "\n")
                    continue 
            else:
                continue
        except ValueError:
            print("\n" + "***** El formato es incorrecto, vuelva a ingresar la fecha inicial de nuevo. *****" + "\n")
            continue
        else:
            break
    return fecha_inicial, fecha_final


fecha = InputFecha()

###### Ingreso de fechas manualmente ######

df_fecha = pd.DataFrame(fecha, columns=["fecha"])

# Completo las fechas leyendo cada hora
r = pd.date_range(start=df_fecha.fecha.min(), end=df_fecha.fecha.max(), freq='H')

#Realizo un cambio del índice del dataframe, siendo la fecha ahora el índice
df_fecha = df_fecha.set_index(["fecha"])

#Realizo un cambio de formato del índice a formato fecha
df_fecha.index = pd.DatetimeIndex(df_fecha.index)

#Reorganizo las fechas y relleno los datos de las fechas faltantes con NaN
df_fecha= df_fecha.reindex(r, fill_value=np.nan)

#Reintegro el índice y la columna fecha
df_fecha = df_fecha.set_index(df_fecha.index).reindex(r).rename_axis('fecha').reset_index()

#Extraigo los datos y la fecha
file = file.reindex(index=df_fecha.index)

dato = file["TEMP_C_Avg"]
file["fecha"] = df_fecha["fecha"]

##### Realizo una función para cambiar los valores iguales que se repiten #####

#Los agrupa en pares ordenados (x,y) donde 'x' es el número y 'y' es el número de veces que se repite consecutivamente
Contador = [(k, sum(1 for i in g)) for k,g in groupby(dato)]

#Si el número se repite más de 3 veces, cambia los valores por NaN
list1 = []
for i,j in Contador:
    if j > 3:
        list1.extend([np.nan]*j)
    else:
        list1.extend([i]*j)

#Si el número se repite 3 veces, cambia el valor del medio, sumándole 0.1
for i in range(0,len(list1)-2):
    if list1[i] == list1[i+1] and list1[i] == list1[i+2]:
        list1[i+1] = round(list1[i]+0.1,1)
       
file['Datos_NaN'] = list1

##### Realizo una función para cambiar los valores iguales que se repiten #####

##### Sumarle o restarle a la variable de Temperatura por rango de fechas #####

#Se ingresa el valor que quiere sumar o restar a la serie de temperatura
def Valor():
    while True:
        valor = input("Por favor ingrese el número del valor: " + "\n")
        try:        
            valor = float(valor)

        except ValueError:
            print("Dato ingresado incorrecto.")
            continue
        else:
            break
    return valor

#Se realiza la suma o resta del valor ingresado a la variable de temperatura
print("\n A continuación se solicitará si es necesario sumarle o restarle unidades a la temperatura... \n")

MAIN_PROMPT = "Ingrese 'C' para Continuar o 'S' para si desea Salir: "
command = input(MAIN_PROMPT)

OPT_PROMPT = "Ingrese 'S' para Sumar o 'R' para Restar el valor ingresado en el período: "

while not command == "S":
    if command == "C":
        
        fecha_rango = InputFecha()
        
        df_fecha_rango = pd.DataFrame(fecha_rango, columns=["fecha"])
                
        valor = Valor()
        
        command_option = input(OPT_PROMPT)
        
        if command_option == "S":
            file.loc[(file.fecha.ge(df_fecha_rango["fecha"][0])) & (file.fecha.le(df_fecha_rango["fecha"][1])), "Datos_NaN"] += valor
                        
        elif command_option == "R":
            file.loc[(file.fecha.ge(df_fecha_rango["fecha"][0])) & (file.fecha.le(df_fecha_rango["fecha"][1])), "Datos_NaN"] -= valor
        else:
            print("***** Error al ingresar la opción. Por favor ingrese la opción correcta. *****")

    else:
        print("***** Error al ingresar la opción. Por favor ingrese la opción correcta. *****")
    command = input(MAIN_PROMPT + "\n")

##### Sumarle o restarle a la variable de Temperatura por rango de fechas #####

file["Datos_NaN_RH"] = file["RH_Avg"]

#Se cambian los valores negativos de T por -9.0
file.loc[file['TEMP_C_Avg'].lt(0), 'Datos_NaN'] = -9

##### Sumarle lo faltante a la humedad relativa para que llegue a 100 #####

#Se calcula el máximo de la serie de humedad relativa

D = pd.Timedelta(days = 7)

for x in range(0, round(len(file["fecha"])/149)):
    startT = file["fecha"][0] + x*D #+ timedelta(hours=7) 
    endT = startT + D - timedelta(hours=0, minutes=5)
    
    valor_max = file.RH_Avg.loc[(file.fecha.ge(startT)) & (file.fecha.le(endT))].max()
    
    file.loc[(file.fecha.ge(startT)) & (file.fecha.le(endT)), "Datos_NaN_RH"] += (100 - valor_max)

#Se cambian los valores negativos de HR por -9.0
file.loc[file['RH_Avg'].lt(30), 'Datos_NaN_RH'] = -9
    
##### Máxima y mínima diaria #####

# List_days = [group[1] for group in file.groupby(file.fecha.dt.day)]
# T_max = List_days[i].TEMP_C_Avg.max()
# T_max_day.append(T_max)
    
# T_min = List_days[i].TEMP_C_Avg.min()
# T_min_day.append(T_min)

#Se crea un delta de un día
H_24 = pd.Timedelta(days = 1)

#Se crean diccionarios vacíos para guardar la fecha, y los valores máximosy mínimos diarios
Max_day = {}
Min_day = {}

#Se crea un loop que recorre el archivo, separando las fechas por días y extrayendo los datos
#de máxima y mínima, los cuales se guardan en los diccionarios antes creados
for x in range(0, round(len(file["fecha"])/24)):
    startT = file["fecha"][0] + x*H_24 #+ timedelta(hours=7) 
    endT = startT + H_24 - timedelta(seconds=1)
    
    day = startT.date()
    day = day.strftime('%d/%m/%Y')
    
    # print(startT, endT)
    
    T_valor_max = file.Datos_NaN.loc[(file.fecha.ge(startT)) & (file.fecha.le(endT))].max()
    HR_valor_max = file.Datos_NaN_RH.loc[(file.fecha.ge(startT)) & (file.fecha.le(endT))].max()
    
    Max_day[x] = [est_cuenca, num_est, day, 98, "", T_valor_max, HR_valor_max]
    
    T_valor_min = file.Datos_NaN[file.Datos_NaN.gt(0)].loc[(file.fecha.ge(startT)) & (file.fecha.le(endT))].min()
    HR_valor_min = file.Datos_NaN_RH[file.Datos_NaN_RH.gt(0)].loc[(file.fecha.ge(startT)) & (file.fecha.le(endT))].min()

    Min_day[x] = [est_cuenca, num_est, day, 99, "", T_valor_min, HR_valor_min]
    

##### Máxima y mínima diaria #####

##### Archivo de salida #####

#Se crean listas para guardar la fecha y la hora por separado    
out_date = []
out_hour = []

#Se guardan las fechas y horas por separado    
for i in range(0, len(file.fecha)):
    date = file.fecha[i].date()
    out_date.append(date.strftime('%d/%m/%Y'))
    
    hour = file.fecha[i].time()
    out_hour.append(hour.strftime('%H'))


#Se crea un dataframe vacío para los datos de salida
out_file = pd.DataFrame()

#Se crean columnas vacías para almacenar el número de cuenca y número de estación
out_file["cuenca"] = ""
out_file["estacion"] = ""

#Se crean columnas para almacenar la fecha, la hora y una columna vacía para el indicador m
out_file["fechas"] = out_date
out_file["horas"] = out_hour
out_file["m"] = " "

#Se crean columnas para almacenar los datos de T y HR
out_file["T"] = file[["Datos_NaN"]].copy()
out_file["HR"] = file[["Datos_NaN_RH"]].copy()

#Se almacenan el número de cuenca y de estación ingresados
out_file["cuenca"] = est_cuenca
out_file["estacion"] = num_est

#Se concatenan los valores de las máximas y mínimas al final del archivo
out_file = pd.concat([out_file, pd.DataFrame(Max_day.values(), columns=out_file.columns)], ignore_index=True)
out_file = pd.concat([out_file, pd.DataFrame(Min_day.values(), columns=out_file.columns)], ignore_index=True)

#Se cambia la hora 00 por la hora 24
out_file.horas = out_file.horas.replace('00','24')

#Se crea una lista con los índices donde se encuentran las horas 24
index_out24 = out_file.fechas.loc[out_file.horas.eq('24')].index

#Se deshabilita la alerta por copia de datos
pd.options.mode.chained_assignment = None

#Se resta un día en la hora 24
for i in index_out24:
    out_file.fechas[i] = (datetime.strptime(out_file.fechas.loc[out_file.horas.eq('24')][i],"%d/%m/%Y") - pd.Timedelta(days=1))
    out_file.fechas[i] = out_file.fechas[i].strftime('%d/%m/%Y')

#Crea los archivos de salida
out_file_fecha_I = fecha[0].strftime('%d%m%Y_%H_')
out_file_fecha_F = (fecha[1] - pd.Timedelta(days=1)).strftime('%d%m%Y')
out_file_fecha_F_H = (fecha[1] - pd.Timedelta(days=1)).strftime('%H')
out_file_fecha_F_H = str(out_file_fecha_F_H).replace('00','24')

out_file_T = out_file[["cuenca","estacion","fechas","horas","m","T"]].copy()
out_file_H = out_file[["cuenca","estacion","fechas","horas","m","HR"]].copy()

out_file_T.to_csv('T'+str(est_num)+'_'+str(out_file_fecha_I)+
                str(out_file_fecha_F)+'_'+str(out_file_fecha_F_H)+'.csv', sep=",", na_rep="NaN", index=False)

out_file_H.to_csv('H'+str(est_num)+'_'+str(out_file_fecha_I)+
                str(out_file_fecha_F)+'_'+str(out_file_fecha_F_H)+'.csv', sep=",", na_rep="NaN", index=False)
