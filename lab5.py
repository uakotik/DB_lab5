from neo4j import GraphDatabase

class Store:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def create_item(self, id, name, price):
        with self.driver.session() as session:
            session.run("CREATE (i:Item {id: $id, name: $name, price: $price})", id=id, name=name, price=price)
    
    def create_customer(self, id, name):
        with self.driver.session() as session:
            session.run("CREATE (c:Customer {id: $id, name: $name})", id=id, name=name)
    
    def create_order(self, id, time):
        with self.driver.session() as session:
            session.run("CREATE (o:Order {id: $id, time: $time})", id=id, time=time)
    
    def customer_bought_order(self, customer_name, order_id):
        with self.driver.session() as session:
            session.run("""
            MATCH (c:Customer {name: $customer_name}), (o:Order {id: $order_id})
            CREATE (c)-[:BOUGHT]->(o)
            """, customer_name=customer_name, order_id=order_id)
    
    def order_contains_item(self, order_id, item_name):
        with self.driver.session() as session:
            session.run("""
            MATCH (o:Order {id: $order_id}), (i:Item {name: $item_name})
            CREATE (o)-[:CONTAINS]->(i)
            """, order_id=order_id, item_name=item_name)
    
    def customer_view_item(self, customer_name, item_id):
        with self.driver.session() as session:
            session.run("""
            MATCH (c:Customer {name: $customer_name}), (i:Item {id: $item_id})
            CREATE (c)-[:VIEWED]->(i)
            """, customer_name=customer_name, item_id=item_id)
    
    def find_items_in_order(self, order_id):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (o:Order {id: $order_id})-[:CONTAINS]->(i:Item)
            RETURN i.name
            """, order_id=order_id)
            return [record["i.name"] for record in result]
    
    def calculate_order_cost(self, order_id):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (o:Order {id: $order_id})-[:CONTAINS]->(i:Item)
            RETURN SUM(i.price) as total_cost
            """, order_id=order_id)
            return result.single()["total_cost"]
    
    def find_orders_by_customer(self, customer_name):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (c:Customer {name: $customer_name})-[:BOUGHT]->(o:Order)
            RETURN o.id
            """, customer_name=customer_name)
            return [record["o.id"] for record in result]
    
    def find_items_bought_by_customer(self, customer_name):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (c:Customer {name: $customer_name})-[:BOUGHT]->(o:Order)-[:CONTAINS]->(i:Item)
            RETURN i.name
            """, customer_name=customer_name)
            return [record["i.name"] for record in result]
    
    def count_items_bought_by_customer(self, customer_name):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (c:Customer {name: $customer_name})-[:BOUGHT]->(o:Order)-[:CONTAINS]->(i:Item)
            RETURN COUNT(i) as item_count
            """, customer_name=customer_name)
            return result.single()["item_count"]
    
    def total_amount_spent_by_customer(self, customer_name):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (c:Customer {name: $customer_name})-[:BOUGHT]->(o:Order)-[:CONTAINS]->(i:Item)
            RETURN SUM(i.price) as total_spent
            """, customer_name=customer_name)
            return result.single()["total_spent"]
    
    def find_most_bought_items(self):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (o:Order)-[:CONTAINS]->(i:Item)
            RETURN i.name, COUNT(o) as purchase_count
            ORDER BY purchase_count DESC
            """)
            return [(record["i.name"], record["purchase_count"]) for record in result]
    
    def find_items_viewed_by_customer(self, customer_name):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (c:Customer {name: $customer_name})-[:VIEWED]->(i:Item)
            RETURN i.name
            """, customer_name=customer_name)
            return [record["i.name"] for record in result]
    
    def find_items_bought_together(self, item_id):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (i:Item {id: $item_id})<-[:CONTAINS]-(o:Order)-[:CONTAINS]->(other:Item)
            RETURN other.name
            """, item_id=item_id)
            return [record["other.name"] for record in result]
    
    def find_customers_bought_item(self, item_id):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (i:Item {id: $item_id})<-[:CONTAINS]-(o:Order)<-[:BOUGHT]-(c:Customer)
            RETURN c.name
            """, item_id=item_id)
            return [record["c.name"] for record in result]
    
    def find_viewed_not_bought(self, customer_name):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (c:Customer {name: $customer_name})-[:VIEWED]->(i:Item)
            WHERE NOT EXISTS((c)-[:BOUGHT]->(:Order)-[:CONTAINS]->(i))
            RETURN i.name
            """, customer_name=customer_name)
            return [record["i.name"] for record in result]
    
    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

if __name__ == "__main__":
    store = Store("bolt://localhost:7687", "neo4j", "12345678")
    store.clear_database()

    
    store.create_item("1", "phone", 750)
    store.create_item("2", "laptop", 1000)
    store.create_item("3", "pc", 1500)
    store.create_item("4", "headset", 150)
    store.create_item("5", "mouse", 100)

    store.create_customer("1", "Bob")
    store.create_customer("2", "Mark")
    store.create_customer("3", "Amanda")


    store.create_order("1", "23:04")
    store.create_order("2", "23:04")
    store.create_order("3", "23:04")
    store.create_order("4", "23:04")
    

    store.customer_bought_order("Bob", "1")
    store.customer_bought_order("Mark", "2")
    store.customer_bought_order("Bob", "3")
    store.customer_bought_order("Amanda", "4")

    store.order_contains_item("1", "phone")
    store.order_contains_item("1", "laptop")
    store.order_contains_item("2", "laptop")
    store.order_contains_item("3", "headset")
    store.order_contains_item("4", "pc")


    store.customer_view_item("Bob", "1")
    store.customer_view_item("Bob", "2")
    store.customer_view_item("Bob", "3")
    store.customer_view_item("Bob", "4")
    store.customer_view_item("Mark", "1")
    store.customer_view_item("Mark", "2")
    store.customer_view_item("Mark", "4")
    store.customer_view_item("Mark", "5")
    store.customer_view_item("Amanda", "2")
    store.customer_view_item("Amanda", "4")
    store.customer_view_item("Amanda", "5")
    
    
    print("Предмети у замовленні: ",store.find_items_in_order("1"))
    print("Ціна замовлення: ",store.calculate_order_cost("2"))
    print("Замовлення покупця: ",store.find_orders_by_customer("Amanda"))
    print("Предмети куплені покупцем: ",store.find_items_bought_by_customer("Mark"))
    print("Кількість предметів куплених покупцем: ",store.count_items_bought_by_customer("Mark"))
    print("Сума потрачена покупцем: ",store.total_amount_spent_by_customer("Mark"))
    print("Загально кількість куплених предметів: ",store.find_most_bought_items())
    print("Предмети переглянуті покупцем: ",store.find_items_viewed_by_customer("Bob"))
    print("Предмети куплені разом зі вказаним: ",store.find_items_bought_together("1"))
    print("Покупці що купили даний предмет: ",store.find_customers_bought_item("2"))
    print("Переглянуті некуплені предмети: ",store.find_viewed_not_bought("Bob"))
    
