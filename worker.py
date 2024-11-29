# worker.py
import pika
import json
from tools.fetch_stock_info import Anazlyze_stock
from app import save_query

def start_worker():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()
    channel.queue_declare(queue='stock_analysis_queue', durable=True)

    def callback(ch, method, properties, body):
        message = json.loads(body)
        try:
            result = Anazlyze_stock(message['query'])
            save_query(message['username'], message['query'], result)
        except Exception as e:
            print(f"Error processing message: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='stock_analysis_queue', on_message_callback=callback)
    print("Worker started. Waiting for messages...")
    channel.start_consuming()

if __name__ == '__main__':
    start_worker()