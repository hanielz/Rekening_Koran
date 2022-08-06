from datetime import date

def fields(conn) :
        results = {}
        column = 0

        for d in conn.description :
            results[d[0]] = column
            column = column + 1 
        return results
def show_db():
    fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": 1234}]

    result = []
    for row in fake_items_db :
        temp= dict.fromkeys(["item_name"])
        temp["item_name"] = row[1]
    
    result.append(temp)
    return result

show = show_db()
print(show)



# print(fake_items_db)
