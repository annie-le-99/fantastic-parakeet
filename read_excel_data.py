import pandas as pd

NUM_CUSTOMERS = 20  # Any number


def read_raw_data():
    """
        Read raw data from converted csv files.
    """
    # output_file = open("converted_file.csv", "w")
    output_file = open("converted_file_week2.csv", "w")
    # data_info_file = pd.read_csv("split_data/data_info.csv")
    # oversea_return_demand_info_df = pd.read_csv("split_data/oversea_return_demand_info.csv")
    # cust_return_demand_info_df = pd.read_csv("split_data/cust_return_demand_info.csv")
    # port_info_df = pd.read_csv("split_data/port_info.csv")
    # depot_depot_info_df = pd.read_csv("split_data/depot_depot_info.csv")
    # depot_info_df = pd.read_csv("split_data/depot_info.csv")
    cust_return_demand_info_df = pd.read_csv("weekly/converted_file_week2/cust_return_demand_info.csv")
    port_info_df = pd.read_csv("weekly/converted_file_week2/port_info.csv")
    depot_depot_info_df = pd.read_csv("weekly/converted_file_week2/depot_depot_info.csv")
    depot_info_df = pd.read_csv("weekly/converted_file_week2/depot_info.csv")

    # Init all node indices
    # Init node indices
    source_index = 0
    inventory_index = 1

    num_ports = len(port_info_df)
    port_index_start = inventory_index + 1
    port_indices = [idx for idx in range(port_index_start, port_index_start + num_ports)]

    num_depots = len(depot_info_df)
    depot_index_start = port_indices[-1] + 1
    depot_indices = [idx for idx in range(depot_index_start, depot_index_start + num_depots)]

    # num_customers = len(cust_return_demand_info_df)
    num_customers = NUM_CUSTOMERS
    customer_index_start = depot_indices[-1] + 1
    customer_indices = [idx for idx in range(customer_index_start, customer_index_start + num_customers)]

    sink_index = customer_indices[-1] + 1

    # >>>> Graph info <<<<
    output_file.writelines(["flow graph\n"])
    num_nodes = sink_index + 1
    output_file.writelines([f"{num_nodes}\n"])
    line = ""
    for i in range(num_nodes):
        line += f"{i} "
    line = line[:-1] + "\n"
    output_file.writelines([line])

    # >>>> Source -> Port, Inventory nodes <<<<
    # Get number of ports
    port_info_list = []

    # ports_start_index = inventory_index + 1
    total_demand = 0
    for idx in range(num_ports):
        port_info = port_info_df.iloc[idx]
        total_demand = cust_return_demand_info_df["cust demand"].sum()
        cost = 0
        elm = (port_indices[idx], total_demand, cost)
        port_info_list.append(elm)

    # Inventory info
    def calculate_inventory(x):
        res = x['cust demand'] - x['cust return']
        if res < 0:
            res = 0
        return res

    # inventories = cust_return_demand_info_df["cust demand"] - cust_return_demand_info_df["cust return"]
    inventories = cust_return_demand_info_df.apply(calculate_inventory, axis=1)
    inventories += 30
    total_inventory = inventories.sum()
    cost = 0
    inventory_elm = (inventory_index, total_inventory, cost)

    # Source node
    output_file.writelines([f"{source_index}\n"])
    lines = ["", "", ""]
    for line_index in range(3):
        # line_index == 1: adjacent nodes
        # line_index == 2: capacity
        # line_index == 3: cost
        for idx in range(len(port_info_list)):
            port_info = port_info_list[idx]
            lines[line_index] += f"{port_info[line_index]} "
        lines[line_index] += f"{inventory_elm[line_index]} "

        lines[line_index] = f"{lines[line_index][:-1]}\n"
    output_file.writelines(lines)

    # >>>> Inventory to depots <<<<
    output_file.writelines([f"{inventory_index}\n"])  # Write inventory index to file

    # Iterate all depots
    invent_depot_elm_list = []
    for depot_index in range(num_depots):
        cust_return_info = cust_return_demand_info_df.iloc[depot_index]
        # invent_depot_capacity = cust_return_info["cust demand"] - cust_return_info["cust return"]
        # if invent_depot_capacity < 0:
        #     invent_depot_capacity = 0
        # invent_depot_capacity += 30
        invent_depot_capacity = inventories[depot_index]

        cost = int(depot_info_df.iloc[depot_index]["depot inven cost"])

        elm = (depot_indices[depot_index], invent_depot_capacity, cost)
        invent_depot_elm_list.append(elm)

    lines = ["", "", ""]
    for line_index in range(3):
        # line_index == 1: adjacent nodes
        # line_index == 2: capacity
        # line_index == 3: cost
        for idx in range(len(invent_depot_elm_list)):
            elm = invent_depot_elm_list[idx]
            lines[line_index] += f"{elm[line_index]} "
        lines[line_index] = f"{lines[line_index][:-1]}\n"
    output_file.writelines(lines)

    # >>>> Port to depots <<<<

    # Get all depot infos
    for idx in range(num_ports):  # Iterate all ports
        port_info = port_info_list[idx]

        output_file.writelines([f"{port_indices[idx]}\n"])  # Write port index to file
        lines = ["", "", ""]

        # Iterate all depots
        port_capacity = port_info_df.iloc[idx]["port capa"]
        port_depot_capacity = int(port_capacity / num_depots)
        depot_elm_list = []
        for depot_index in range(num_depots):
            cost = int(depot_info_df.iloc[depot_index]["port trans depot cost road"])
            elm = (depot_indices[depot_index], port_depot_capacity, cost)
            depot_elm_list.append(elm)

        for line_index in range(3):
            # line_index == 1: adjacent nodes
            # line_index == 2: capacity
            # line_index == 3: cost
            for idx in range(len(depot_elm_list)):
                depot_elm = depot_elm_list[idx]
                lines[line_index] += f"{depot_elm[line_index]} "
            lines[line_index] = f"{lines[line_index][:-1]}\n"
        output_file.writelines(lines)

    # >>>> Depots to depots and customers <<<<
    for depot_index in range(num_depots):
        depot_depot_elm_list = []

        depot_capacity = depot_info_df.iloc[depot_index]["depot capa"]
        capacity = int(depot_capacity / num_customers)

        try:
            # To adjacent depot
            adjacent_depot_index = depot_depot_info_df.iloc[depot_index]["adj_depot"]
            adjacent_depot_index = depot_indices[adjacent_depot_index] - 1
            num_adjacent_depot = 1

            depot_capacity = depot_info_df.iloc[depot_index]["depot capa"]
            capacity = int(depot_capacity / (num_adjacent_depot + num_customers))

            depot_to_adj_depot_cost = depot_depot_info_df.iloc[depot_index]["depot trans depot cost"]

            depot_depot_elm = (adjacent_depot_index, capacity, depot_to_adj_depot_cost)
            depot_depot_elm_list.append(depot_depot_elm)
        except IndexError:
            pass

        # To customers
        for customer_index in range(num_customers):
            cost = 0  # Assume this cost is 0
            depot_depot_elm = (customer_indices[customer_index], capacity, cost)
            depot_depot_elm_list.append(depot_depot_elm)

        # Depot to sink
        cust_return_info = cust_return_demand_info_df.iloc[depot_index]
        # to_sink_capacity = cust_return_info["cust demand"] - cust_return_info["cust return"] + 30
        to_sink_capacity = inventories[depot_index]
        cost = 0  # Cost to sink node is 0
        depot_depot_elm = (sink_index, to_sink_capacity, cost)
        depot_depot_elm_list.append(depot_depot_elm)

        output_file.writelines([f"{depot_indices[depot_index]}\n"])
        lines = ["", "", ""]
        for line_index in range(3):
            # line_index == 1: adjacent nodes
            # line_index == 2: capacity
            # line_index == 3: cost
            for idx in range(len(depot_depot_elm_list)):
                depot_depot_elm = depot_depot_elm_list[idx]
                lines[line_index] += f"{depot_depot_elm[line_index]} "
            lines[line_index] = f"{lines[line_index][:-1]}\n"
        output_file.writelines(lines)

    # >>>> Customers to sink node <<<<
    for customer_index in range(num_customers):
        customer_2_sink_list = []
        capacity = int(total_demand / num_customers)
        cost = 0  # Cost to sink node is 0
        customer_2_sink_elm = (sink_index, capacity, cost)
        customer_2_sink_list.append(customer_2_sink_elm)

        output_file.writelines([f"{customer_indices[customer_index]}\n"])
        lines = ["", "", ""]
        for line_index in range(3):
            # line_index == 1: adjacent nodes
            # line_index == 2: capacity
            # line_index == 3: cost
            for idx in range(len(customer_2_sink_list)):
                customer_2_sink_elm = customer_2_sink_list[idx]
                lines[line_index] += f"{customer_2_sink_elm[line_index]} "
            lines[line_index] = f"{lines[line_index][:-1]}\n"
        output_file.writelines(lines)

    # >>>> Sink node <<<<
    output_file.writelines([f"{sink_index}\n"])
    lines = ["0\n", "0\n", "0\n"]
    output_file.writelines(lines)

    output_file.close()


def main():
    read_raw_data()


if __name__ == '__main__':
    main()
