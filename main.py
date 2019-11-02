from model import *
import datetime


def main():

    list = IndexList("stocks.yaml")
    print(list.index_dict)
    list.initialize_indexes()
    indices = list.list_indices()
    for i in indices:
        print(i)


if __name__ == "__main__":
    main()