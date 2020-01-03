from model import *
import datetime


def main():
    # Create IndexList object
    index_list = IndexList(datetime.date(2019, 10, 22), datetime.date(2019, 10, 29))

    # Populate the index list with test data
    index_list.initialize_indexes(source="test")

    # Print output of all available data
    for i in index_list.list_indices():
        print(i)
        print(i.quotation_df)

    # Serialize index data to db
    index_list.serialize_indexes(target="db")

    # For testing: Load this data again because we can
    index_list.initialize_indexes(source="db")

    # Print output of all available data
    for i in index_list.list_indices():
        print(i)
        print(i.quotation_df)


if __name__ == "__main__":
    main()
