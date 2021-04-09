# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 15:03:25 2021

@author: Anthony Segura García
@contact: asegura@imn.ac.cr

Departamento de Red Meteorológica y Procesamiento de Datos
Instituto Meteorológico Nacional
"""

#se cargan las librerías necesarias
import pandas as pd
import numpy as np
from itertools import groupby
from datetime import datetime
from datetime import timedelta
import glob 

#Se deshabilita la alerta por copia de datos
pd.options.mode.chained_assignment = None

#Se cargan los datos
filenames = glob.glob("*.xlsx")
file = pd.read_excel(filenames[0], header=None, names=["fecha", "TEMP_C_Avg", "RH_Avg"])

file.TEMP_C_Avg = file.TEMP_C_Avg.round(1)

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
                print("\nLa estación ingresada es:", get_key(est),"\n")
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

T_mod = []
T_mod_out = pd.DataFrame()

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
            T_mod_val = file.loc[(file.fecha.ge(df_fecha_rango["fecha"][0])) & (file.fecha.le(df_fecha_rango["fecha"][1]))]
            T_mod_val["procedimiento"] = "se_suma_"+str(valor)
            T_mod.extend(T_mod_val.values)
        elif command_option == "R":
            file.loc[(file.fecha.ge(df_fecha_rango["fecha"][0])) & (file.fecha.le(df_fecha_rango["fecha"][1])), "Datos_NaN"] -= valor
            T_mod_val = file.loc[(file.fecha.ge(df_fecha_rango["fecha"][0])) & (file.fecha.le(df_fecha_rango["fecha"][1]))]
            T_mod_val["procedimiento"] = "se_resta_"+str(valor)
            T_mod.extend(T_mod_val.values)
        else:
            print("***** Error al ingresar la opción. Por favor ingrese la opción correcta. *****")
            
        T_mod_out = pd.DataFrame(T_mod)
        T_mod_out.columns = T_mod_val.keys()
        
        T_mod_out = T_mod_out[["fecha","TEMP_C_Avg","Datos_NaN","procedimiento"]].copy()
        
        T_mod_out = T_mod_out.rename(columns={"Datos_NaN":"Valor cambiado","TEMP_C_Avg":"Valor original"})
       
    else:
        print("***** Error al ingresar la opción. Por favor ingrese la opción correcta. *****")
    command = input(MAIN_PROMPT + "\n")
    
if T_mod_out.empty:
    print("No se sumó o restó ningún valor")
else:
    T_mod_out_date = []
    T_mod_out_hour = []

    for j in range(0, len(T_mod_out.fecha)):
        T_date = T_mod_out.fecha[j].date()
        T_mod_out_date.append(T_date.strftime('%d/%m/%Y'))
        
        T_hour = T_mod_out.fecha[j].time()
        T_mod_out_hour.append(T_hour.strftime('%H'))
        
    T_mod_out_file = pd.DataFrame()

    T_mod_out_file["cuenca"] = ""
    T_mod_out_file["estacion"] = ""
    
    T_mod_out_file["fechas"] = T_mod_out_date
    T_mod_out_file["horas"] = T_mod_out_hour
    
    T_mod_out_file["Valor original"] = T_mod_out[["Valor original"]].copy()
    T_mod_out_file["Valor cambiado"] = T_mod_out[["Valor cambiado"]].copy()
    
    T_mod_out_file["error"] = "ajuste_con_T_max_T_min" 
    
    T_mod_out_file["procedimiento"] = T_mod_out[["procedimiento"]].copy()
    
    T_mod_out_file["cuenca"] = est_cuenca
    T_mod_out_file["estacion"] = num_est
    
    T_mod_out_file.horas = T_mod_out_file.horas.replace('00','24')

    T_mod_index_out24 = T_mod_out_file.fechas.loc[T_mod_out_file.horas.eq('24')].index
    
    pd.options.mode.chained_assignment = None
    
    for i in T_mod_index_out24:
        T_mod_out_file.fechas[i] = (datetime.strptime(T_mod_out_file.fechas.loc[T_mod_out_file.horas.eq('24')][i],"%d/%m/%Y") - pd.Timedelta(days=1))
        T_mod_out_file.fechas[i] = T_mod_out_file.fechas[i].strftime('%d/%m/%Y')
        


##### Sumarle o restarle a la variable de Temperatura por rango de fechas #####

file["Datos_NaN_RH"] = file["RH_Avg"]

#Se cambian los valores negativos de T por -9.0
file.loc[file['TEMP_C_Avg'].lt(0), 'Datos_NaN'] = -9

##### Sumarle lo faltante a la humedad relativa para que llegue a 100 #####

#Se calcula el máximo de la serie de humedad relativa

D = pd.Timedelta(days = 7)

H_mod = []
H_mod_out = pd.DataFrame()

for x in range(0, round(len(file["fecha"])/149)):
    startT = file["fecha"][0] + x*D #+ timedelta(hours=7) 
    endT = startT + D - timedelta(hours=0, minutes=5)
    
    valor_max = file.RH_Avg.loc[(file.fecha.ge(startT)) & (file.fecha.le(endT))].max()
    
    valor_sum = 100 - valor_max
    
    file.loc[(file.fecha.ge(startT)) & (file.fecha.le(endT)), "Datos_NaN_RH"] += valor_sum
    H_mod_val = file.loc[(file.fecha.ge(startT)) & (file.fecha.le(endT))]
    H_mod_val["procedimiento"] = "se_suma_"+str(valor_sum)
    H_mod.extend(H_mod_val.values)
    
    H_mod_out = pd.DataFrame(H_mod)
    H_mod_out.columns = H_mod_val.keys()
    
    file["procedimiento"] = H_mod_out[["procedimiento"]].copy()
    
    file.loc[file.RH_Avg.le(0),"procedimiento"] = "valor_negativo"

#Se cambian los valores negativos de HR por -9.0
file.loc[file['RH_Avg'].lt(0), 'Datos_NaN_RH'] = -9
    
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
out_file_NaN = pd.DataFrame()

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

out_file_NaN = out_file[["T"]]

#Se cambian los valores NaN por -9 para el ingreso a la base de datos
out_file['T'] = out_file['T'].fillna(-9)

#Se cambia la hora 00 por la hora 24
out_file.horas = out_file.horas.replace('00','24')

#Se crea una lista con los índices donde se encuentran las horas 24
index_out24 = out_file.fechas.loc[out_file.horas.eq('24')].index

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

#Se crean los archivos de salida con los datos que se cambian
out_mod_file_T = out_file[["cuenca","estacion","fechas","horas"]].copy()
out_mod_file_T["T"] = out_file_NaN[["T"]].copy()
out_mod_file_T["Temp"] = file[["TEMP_C_Avg"]].copy()

#Se extraen los datos 
T_3_equal = []
index = []

for k,v in out_mod_file_T.groupby((out_mod_file_T['Temp'].shift() != out_mod_file_T['Temp']).cumsum()):
    if len(v) == 3:
        T_3_equal.extend(v.values)
        index.extend(v.index)
        

T_3_equal = pd.DataFrame(T_3_equal)
T_3_equal.columns = v.keys()
T_3_equal.index = index
T_3_equal = T_3_equal[["cuenca","estacion","fechas","horas","Temp","T"]]
T_3_equal = T_3_equal.rename(columns={"T":"Valor cambiado","Temp":"Valor original"})
T_3_equal["error"] = "3_valores_consecutivos_iguales" 
T_3_equal["procedimiento"] = "dato_suma_0.1"

out_mod_file_T = out_mod_file_T[out_mod_file_T['T'].isna()]
out_mod_file_T = out_mod_file_T[["cuenca","estacion","fechas","horas","Temp","T"]]
out_mod_file_T = out_mod_file_T.rename(columns={"T":"Valor cambiado","Temp":"Valor original"})
out_mod_file_T["error"] = "4_valores_consecutivos_iguales" 
out_mod_file_T["procedimiento"] = "dato_eliminado"

out_mod_file_T = pd.concat([out_mod_file_T, T_3_equal], ignore_index=True)


if T_mod_out.empty:
    print("Generando archivos de salida...")
else:
    out_mod_file_T = pd.concat([out_mod_file_T, T_mod_out_file], ignore_index=True)

out_mod_file_T.to_csv('modif_T'+str(est_num)+'_'+str(out_file_fecha_I)+
                str(out_file_fecha_F)+'_'+str(out_file_fecha_F_H)+'.csv', sep=",", na_rep="NaN", index=False)

out_mod_file_H = pd.DataFrame()
out_mod_file_H["Valor original"] = file['RH_Avg']
out_mod_file_H["cuenca"] = out_file_H['cuenca']
out_mod_file_H['estacion'] = out_file_H["estacion"]
out_mod_file_H['fechas'] = out_file_H["fechas"]
out_mod_file_H['horas'] = out_file_H["horas"]
out_mod_file_H['Valor cambiado'] = out_file_H["HR"]
out_mod_file_H["error"] = "ajuste_con_HR_max_HR_min" 
out_mod_file_H["procedimiento"] = file['procedimiento']

out_mod_file_H = out_mod_file_H[["cuenca","estacion","fechas","horas","Valor original","Valor cambiado","error","procedimiento"]]

out_mod_file_H .to_csv('modif_H'+str(est_num)+'_'+str(out_file_fecha_I)+
                str(out_file_fecha_F)+'_'+str(out_file_fecha_F_H)+'.csv', sep=",", na_rep="NaN", index=False)