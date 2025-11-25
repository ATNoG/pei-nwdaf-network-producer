from time import sleep
from csv_reader import CsvReader
from sender import Sender

dataset_path = "dataset/hbahn/iperf_data.csv"
api_url = "https://webhook.site/d2c1b083-911c-435e-89f4-48467917c345"
interval = 0.1 #in seconds

def main():
    csv_reader = CsvReader()
    csv_reader.load_data_set(dataset_path)
    
    sender = Sender(csv_reader, api_url)

    while True:
        sleep(interval)
        success = sender.send_next_line()
        if not success:
            print("Sent everything")
            break

main()
