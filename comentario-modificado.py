import boto3
import uuid
import os
import json
from datetime import datetime

def lambda_handler(event, context):
    # Entrada (json)
    print(event)
    tenant_id = event['body']['tenant_id']
    texto = event['body']['texto']
    nombre_tabla = os.environ["TABLE_NAME"]
    bucket_name = os.environ["INGEST_BUCKET_NAME"]  # Nombre del bucket de S3

    # Generar un UUID para el comentario
    uuidv1 = str(uuid.uuid1())
    comentario = {
        'tenant_id': tenant_id,
        'uuid': uuidv1,
        'detalle': {
          'texto': texto
        }
    }

    # Guardar el comentario en DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(nombre_tabla)
    response = table.put_item(Item=comentario)

    # Guardar el comentario en S3 con un nombre de archivo específico
    s3_client = boto3.client('s3')
    file_name = f"{tenant_id}-comentario.json"  # Ajusta el nombre para que sea compatible con la URL
    comentario_json = json.dumps(comentario)

    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=comentario_json,
            ContentType='application/json',
            ACL='public-read'  # Hacer que el archivo sea público
        )
        # Construir la URL de acceso público
        file_url = f"https://{bucket_name}.s3.{os.environ['AWS_REGION']}.amazonaws.com/{file_name}"
        print(f"Comentario guardado en S3 y accesible en: {file_url}")
    except Exception as e:
        print(f"Error al guardar en S3: {e}")
        return {
            'statusCode': 500,
            'error': str(e)
        }

    # Salida (json)
    print(comentario)
    return {
        'statusCode': 200,
        'comentario': comentario,
        'response': response,
        's3_url': file_url
    }

