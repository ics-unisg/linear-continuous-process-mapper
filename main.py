import dapp_fact
from core.data.data_loader import load_xes_log

# Initial Setup
try:
    file_name = "datasets/SepsisCases2020EventLog.xes"
    event_log = load_xes_log(file_name)

except Exception as e:
    print(f"Error during initial setup: {e}")


app = dapp_fact.create_app(event_log)

if __name__ == "__main__":
    app.run()