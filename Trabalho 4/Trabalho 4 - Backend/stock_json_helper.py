import json

class StockJsonHelper:
    """Helper class for reading and writing JSON files."""

    JSON_FILE_NAME = "stock.json"

    @staticmethod
    def read_all_stock():
        """Reads data from the JSON file.

        Returns:
            The data loaded from the JSON file.
        """
        try:
            with open(StockJsonHelper.JSON_FILE_NAME, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"Warning: '{StockJsonHelper.JSON_FILE_NAME}' not found. Returning empty list.")
            return []
        
    @staticmethod
    def increase_stock(id_item, quantity):
        stock = StockJsonHelper.read_all_stock()
        for item in stock:
            if item["stock_id"] == id_item:
                item["quantity"] = item["quantity"] + quantity
                StockJsonHelper.write_all_stock(stock)
                return True  # Successfully decreased

        return False  # Item not found

    @staticmethod
    def decrease_stock(id_item, quantity):
        stock = StockJsonHelper.read_all_stock()
        for item in stock:
            if item["stock_id"] == id_item:
                item["quantity"] = max(0, item["quantity"] - quantity)
                StockJsonHelper.write_all_stock(stock)
                return True  # Successfully decreased
            
        return False  # Item not found
    
    @staticmethod
    def verify_stock_by_id(id_to_check):
        """Verify if the order exists.

        Args:
            object_id: The ID of the object to be verified.
        """
        stock = StockJsonHelper.read_all_stock()
        return any(item["stock_id"] == id_to_check for item in stock)

    @staticmethod
    def write_all_stock(stock):
        with open(StockJsonHelper.JSON_FILE_NAME, "w") as file:
            json.dump(stock, file, indent=4)
