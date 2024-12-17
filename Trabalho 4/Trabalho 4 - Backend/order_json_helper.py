import json

class OrderJsonHelper:
    """Helper class for reading and writing JSON files."""

    JSON_FILE_NAME = "orders.json"

    @staticmethod
    def read_all_orders():
        """Reads data from the JSON file.

        Returns:
            The data loaded from the JSON file.
        """
        try:
            with open(OrderJsonHelper.JSON_FILE_NAME, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"Warning: '{OrderJsonHelper.JSON_FILE_NAME}' not found. Returning empty list.")
            return [] 

    @staticmethod
    def add_order(data):
        """Writes data to the JSON file.

        Args:
            data: The data to be written to the file.
        """
        orders = OrderJsonHelper.read_all_orders()
        orders.append(data)

        with open(OrderJsonHelper.JSON_FILE_NAME, 'w') as f:
            json.dump(orders, f, indent=2)

    @staticmethod
    def delete_order_by_id(object_id):
        """Deletes an object by its ID from the JSON file.

        Args:
            object_id: The ID of the object to be deleted.
        """
        orders = OrderJsonHelper.read_all_orders()
        # Filter out the object with the matching ID
        updated_orders = [obj for obj in orders if obj.get('order_id') != object_id]
        
        # Check if any object was actually removed
        if len(orders) == len(updated_orders):
            print(f"No object with ID {object_id} was found.")
        else:
            print(f"Object with ID {object_id} was deleted.")
            with open(OrderJsonHelper.JSON_FILE_NAME, 'w') as f:
                json.dump(updated_orders, f, indent=2)

    @staticmethod
    def verify_order_by_id(id_to_check):
        """Verify if the order exists.

        Args:
            object_id: The ID of the object to be verified.
        """
        orders = OrderJsonHelper.read_all_orders()
        return any(item["order_id"] == id_to_check for item in orders)
    
    @staticmethod
    def get_item_by_id(id_item):
        orders = OrderJsonHelper.read_all_orders()
        for item in orders:
            if item["order_id"] == id_item:
                return item  # Return the object if found
        return None  # Return None if no object with the specified id is found

    @staticmethod
    def update_order_status(order_id, status):
        orders = OrderJsonHelper.read_all_orders()
        for order in orders:
            if order["order_id"] == order_id:
                order["status"] = status
                OrderJsonHelper.write_all_orders(orders)
                return True  # Successfully decreased

        return False  # Item not found
    
    @staticmethod
    def write_all_orders(order):
        with open(OrderJsonHelper.JSON_FILE_NAME, "w") as file:
            json.dump(order, file, indent=4)