import psycopg2.pool

try:
    pool = psycopg2.pool.SimpleConnectionPool(1, 20,user="postgres.svpyjwfxsqwdyotemrzq", password="Faraz@9847",host="aws-0-ap-south-1.pooler.supabase.com"
                                              ,port="6543",database="postgres")
    connection = pool.getconn()
    print("Connection pool created successfully")
except Exception as e:
    print("Connection pool creation failed. Error: ", e)
