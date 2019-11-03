from model import *
import datetime

def main():
    # Create IndexList object
    list = IndexList("stocks.yaml", datetime.date(2019, 10, 22), datetime.date(2019, 10, 29))

    # Initialize the index list
    list.initialize_indexes(source="test")

    # Print output of all available data
    for i in list.list_indices():
        print(i)
        print(i.quotation_df)


if __name__ == "__main__":
    main()