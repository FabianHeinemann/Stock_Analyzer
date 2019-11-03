from model import *
import datetime


def main():
    # Create IndexList object
    index_list = IndexList(datetime.date(2019, 10, 22), datetime.date(2019, 10, 29))

    # Initialize the index list from source
    # DEBUG: source = "test"
    index_list.initialize_indexes(source="test")

    # Print output of all available data
    for i in index_list.list_indices():
        print(i)
        print(i.quotation_df)

    # Serialize index data to csv
    index_list.serialize_indexes(target="csv")


if __name__ == "__main__":
    main()
