import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame

def sparkSqlQuery(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node Order
Order_node1722540245501 = glueContext.create_dynamic_frame.from_options(format_options={"quoteChar": "\"", "withHeader": True, "separator": ",", "optimizePerformance": False}, connection_type="s3", format="csv", connection_options={"paths": ["s3://sales-customer-dashboard/data/order/Orders_utf8.csv"]}, transformation_ctx="Order_node1722540245501")

# Script generated for node Customer
Customer_node1722539750004 = glueContext.create_dynamic_frame.from_options(format_options={"quoteChar": "\"", "withHeader": True, "separator": ",", "optimizePerformance": False}, connection_type="s3", format="csv", connection_options={"paths": ["s3://sales-customer-dashboard/data/customer/Customers_utf8.csv"], "recurse": True}, transformation_ctx="Customer_node1722539750004")

# Script generated for node Order (Change Schema)
OrderChangeSchema_node1722540319097 = ApplyMapping.apply(frame=Order_node1722540245501, mappings=[("order id", "string", "order_id", "varchar"), ("order date", "string", "order_date", "date"), ("customer id", "string", "customer_id", "varchar"), ("segment", "string", "segment", "string"), ("postal code", "string", "postal_code", "string"), ("product id", "string", "product_id", "string"), ("sales", "string", "sales", "float"), ("quantity", "string", "quantity", "int"), ("discount", "string", "discount", "float"), ("profit", "string", "profit", "float")], transformation_ctx="OrderChangeSchema_node1722540319097")

# Script generated for node Customer (Change Schema)
CustomerChangeSchema_node1722546110782 = ApplyMapping.apply(frame=Customer_node1722539750004, mappings=[("customer id", "string", "customer_id", "varchar"), ("customer name", "string", "customer_name", "string")], transformation_ctx="CustomerChangeSchema_node1722546110782")

# Script generated for node SQL Query
SqlQuery498 = '''
WITH first_order AS (SELECT customer_id, order_date,
    ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY order_date ASC) AS rank
FROM o)

SELECT c.customer_id, c.customer_name, fo.order_date AS first_order_date
FROM c LEFT JOIN first_order fo
ON c.customer_id = fo.customer_id
WHERE fo.rank = 1
'''
SQLQuery_node1722546169017 = sparkSqlQuery(glueContext, query = SqlQuery498, mapping = {"o":OrderChangeSchema_node1722540319097, "c":CustomerChangeSchema_node1722546110782}, transformation_ctx = "SQLQuery_node1722546169017")

# Script generated for node Customer_etl
Customer_etl_node1722727550044 = glueContext.getSink(path="s3://sales-customer-dashboard/output_data/", connection_type="s3", updateBehavior="UPDATE_IN_DATABASE", partitionKeys=[], compression="snappy", enableUpdateCatalog=True, transformation_ctx="Customer_etl_node1722727550044")
Customer_etl_node1722727550044.setCatalogInfo(catalogDatabase="tableau_db",catalogTableName="Customer_etl")
Customer_etl_node1722727550044.setFormat("json")
Customer_etl_node1722727550044.writeFrame(SQLQuery_node1722546169017)
job.commit()