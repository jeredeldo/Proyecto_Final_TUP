# En VS Code local o Databricks/colab con pyspark instalado
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, mean, when, lit

spark = SparkSession.builder \
    .appName("VientoEstacionesSpark") \
    .master("local[*]") \
    .getOrCreate()

# Cargar
df_sp = spark.read.option("delimiter", "\t").option("header", "true").csv("estaciones_viento_limpio.csv")  # o desde URL si preferís
df_icao_sp = spark.read.option("delimiter", ";").option("header", "true").csv("ICAO.csv")  # ajusta path

# Limpieza y promedio (usando DataFrame API)
df_sp = df_sp.filter(col("Valor Medio de").contains("Velocidad del Viento"))
df_sp = df_sp.withColumn("viento_promedio", mean(col("Ene"), col("Feb"), ...))  # o mejor:
months_expr = [when(col(m) != "S/D", col(m).cast("float")).otherwise(lit(None)) for m in ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']]
df_sp = df_sp.withColumn("viento_promedio", mean(*months_expr))

df_sp = df_sp.select("Estación", "viento_promedio")

# Join
df_final_sp = df_sp.join(df_icao_sp, "Estación", "left")

df_final_sp.show(20, False)

# Si querés exportar a pandas para graficar
df_pandas = df_final_sp.toPandas()
# ... luego usá plotly como arriba

spark.stop()