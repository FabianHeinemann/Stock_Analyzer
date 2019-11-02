from model import *
import datetime

def main():
    list = IndexList("stocks.yaml", datetime.date(2019, 10, 28), datetime.date(2019, 10, 29))
    list.initialize_indexes(source="web")
    indices = list.list_indices()
    for i in indices:
        print(i)


if __name__ == "__main__":
    main()